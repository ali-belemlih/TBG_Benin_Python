import pandas as pd
from helpers.db_utils import get_db_engine
from helpers.parse_arg import parse_date_from_args  # Accepts YYYY-MM-DD
from datetime import datetime

COMPARE_COLUMNS = [
    "ca_global",
    "ca_voix_classique",
    "ca_forfaits_voix",
    "ca_pass_bonus",
    "ca_data",
    "autres",
    "rechargement"
]

def fetch_monthly_avg(engine, year, month):
    selected_columns = ", ".join([f"AVG({col}) AS {col}" for col in COMPARE_COLUMNS])
    query = f"""
        SELECT {selected_columns}
        FROM public.revenue_raw_data
        WHERE EXTRACT(YEAR FROM date) = %(year)s AND EXTRACT(MONTH FROM date) = %(month)s;
    """
    df = pd.read_sql_query(query, engine, params={"year": year, "month": month})
    return df

def fetch_tax_realization_avg(engine, year, month):
    query = """
        SELECT AVG(ca_voix_globale) AS ca_voix_globale
        FROM public.tax_realization
        WHERE EXTRACT(YEAR FROM date) = %(year)s AND EXTRACT(MONTH FROM date) = %(month)s;
    """
    df = pd.read_sql_query(query, engine, params={"year": year, "month": month})
    return df.iloc[0]["ca_voix_globale"] if not df.empty else None

def calculate_relative_change(curr_df, last_df, columns, curr_voix, last_voix, year, month):
    if curr_df.empty or last_df.empty:
        print("One of the monthly dataframes is empty. Cannot calculate relative change.")
        return {}

    result = {}
    for col in columns:
        curr_val = curr_df.iloc[0].get(col, 0) or 0
        last_val = last_df.iloc[0].get(col, 0) or 0
        if last_val == 0:
            result[col] = None
        else:
            result[col] = round((curr_val / last_val) - 1, 6)

    # Special case: ca_voix_globale from different table
    if curr_voix is not None and last_voix is not None and last_voix != 0:
        result["ca_voix_globale"] = round((curr_voix / last_voix) - 1, 6)
    else:
        result["ca_voix_globale"] = None

    result["month"] = f"{month:02d}"
    result["year"] = year
    return result

def run_etl():
    output_path = "benin_turnover_reporting/output"
    args = parse_date_from_args()  # expects YYYY-MM-DD
    date_obj = args.date_obj.date()

    curr_year = date_obj.year
    curr_month = date_obj.month
    last_year = curr_year - 1
    engine = get_db_engine()

    print(f"Calculating for month: {curr_month}, year: {curr_year} and last year: {last_year}")

    # Fetch monthly averaged data
    curr_df = fetch_monthly_avg(engine, curr_year, curr_month)
    last_df = fetch_monthly_avg(engine, last_year, curr_month)

    # Fetch tax realization averages
    curr_voix = fetch_tax_realization_avg(engine, curr_year, curr_month)
    last_voix = fetch_tax_realization_avg(engine, last_year, curr_month)

    print("Current month average data:")
    print(curr_df.to_string(index=False))
    print("\nLast year same month average data:")
    print(last_df.to_string(index=False))

    comparison = calculate_relative_change(
        curr_df, last_df, COMPARE_COLUMNS, curr_voix, last_voix, curr_year, curr_month
    )

    if comparison:
        df_to_save = pd.DataFrame([comparison])
        file_name = f"{output_path}/revenue_comparison_avg_{curr_month:02d}_{curr_year}.csv"
        df_to_save.to_csv(file_name, index=False)
        print(f"Comparison saved to {file_name}")
    else:
        print("No data to write.")

if __name__ == "__main__":
    run_etl()
