import pandas as pd
from helpers.db_utils import get_db_engine
from helpers.parse_arg import parse_date_from_args
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

def compute_last_year_same_day(dateobj):
    try:
        return dateobj.replace(year=dateobj.year - 1)
    except ValueError:
        return dateobj.replace(year=dateobj.year - 1, day=28)

def fetch_revenue_data(engine, target_date):
    selected_columns = ", ".join(COMPARE_COLUMNS + ["date"])
    query = f"""
        SELECT {selected_columns}
        FROM public.revenue_raw_data
        WHERE date = %(target_date)s;
    """
    return pd.read_sql_query(query, engine, params={"target_date": target_date})

def fetch_tax_realization_value(engine, target_date):
    query = """
        SELECT ca_voix_globale
        FROM public.tax_realization
        WHERE date = %(target_date)s;
    """
    df = pd.read_sql_query(query, engine, params={"target_date": target_date})
    if df.empty:
        return None
    return df.iloc[0].get("ca_voix_globale")

def calculate_relative_change(current_df, last_year_df, columns, dateobj, engine):
    """
    Return one row of raw relative changes (decimal) as a dictionary
    """
    if current_df.empty or last_year_df.empty:
        print("One of the dataframes is empty. Cannot calculate relative change.")
        return {}

    result = {}
    for col in columns:
        curr_val = current_df.iloc[0].get(col, 0) or 0
        last_val = last_year_df.iloc[0].get(col, 0) or 0

        if last_val == 0:
            result[col] = None
        else:
            result[col] = round((curr_val / last_val) - 1, 6)

    # Add ca_voix_globale from tax_realization
    current_voix = fetch_tax_realization_value(engine, dateobj)
    last_year_voix = fetch_tax_realization_value(engine, compute_last_year_same_day(dateobj))

    if current_voix is not None and last_year_voix is not None and last_year_voix != 0:
        result["ca_voix_globale"] = round((current_voix / last_year_voix) - 1, 4)
    else:
        result["ca_voix_globale"] = None

    result["date"] = dateobj.isoformat()
    return result

def run_etl():
    output_path = "benin_turnover_reporting/output"
    args = parse_date_from_args()
    dateobj = args.date_obj.date()
    last_year_date = compute_last_year_same_day(dateobj)
    engine = get_db_engine()

    print(f"Current requested date: {dateobj}, Last year same day: {last_year_date}")

    current_df = fetch_revenue_data(engine, dateobj)
    last_year_df = fetch_revenue_data(engine, last_year_date)
    print("Current data:")
    print(current_df.to_string(index=False))
    print("\nLast year data:")
    print(last_year_df.to_string(index=False))

    comparison_row = calculate_relative_change(current_df, last_year_df, COMPARE_COLUMNS, dateobj, engine)

    if comparison_row:
        df_to_save = pd.DataFrame([comparison_row])
        file_name = f"{output_path}/revenue_comparison_{dateobj}.csv"
        df_to_save.to_csv(file_name, index=False)
        print(f"Comparison saved to {file_name}")
    else:
        print("No data to write.")

if __name__ == "__main__":
    run_etl()
