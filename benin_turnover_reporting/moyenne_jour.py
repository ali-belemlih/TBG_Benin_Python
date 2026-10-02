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
    "moov_sayaa",
    "autres",
    "rechargement",
    "parc_attache"
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

def run_etl():
    output_path = "benin_turnover_reporting/output"
    args = parse_date_from_args()  # expects YYYY-MM-DD
    date_obj = args.date_obj.date()

    curr_year = date_obj.year
    curr_month = date_obj.month
    engine = get_db_engine()

    print(f"Calculating for month: {curr_month}, year: {curr_year}")
    curr_df = fetch_monthly_avg(engine, curr_year, curr_month)
    print("Current month average data:")
    print(curr_df.to_string(index=False))
    curr_df.to_csv(f"{output_path}/moyenne_jour_{curr_year}_{curr_month}.csv", index = False)

if __name__ == "__main__":
    run_etl()
