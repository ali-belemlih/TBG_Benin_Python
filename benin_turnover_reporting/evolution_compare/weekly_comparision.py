import pandas as pd
from helpers.db_utils import get_db_engine
from helpers.parse_arg import parse_date_from_args  # expects YYYY-MM-DD

# Required metrics from revenue_raw_data
COMPARE_COLUMNS = [
    "ca_global",
    "ca_voix_classique",
    "ca_forfaits_voix",
    "moov_sayaa",
    "ca_pass_bonus",
    "ca_data",
    "autres",
    "rechargement",
    "trafic_voix",
    "trafic_data_ko",
    "parc_attache",
    "parc_attache_data"
]

def get_revenue_lag_subquery(columns):
    lagged_columns = ",\n                ".join(columns)
    lag_columns = ",\n                ".join([
        f"LAG({col}, 7) OVER (ORDER BY date) AS prev_{col}" for col in columns
    ])
    return f"""
        SELECT
            date,
            {lagged_columns},
            {lag_columns}
        FROM public.revenue_raw_data
    """

def get_tax_lag_subquery():
    return """
        SELECT
            date,
            ca_voix_globale,
            LAG(ca_voix_globale, 7) OVER (ORDER BY date) AS prev_ca_voix_globale
        FROM public.tax_realization
    """

def fetch_weekly_relative_change(engine, target_date):
    # Generate relative change expressions for revenue columns
    revenue_select_cols = ",\n    ".join([
        f"ROUND(({col}::NUMERIC / NULLIF(prev_{col}, 0)::NUMERIC) - 1, 6) AS rel_change_{col}"
        for col in COMPARE_COLUMNS
    ])

    revenue_cte = get_revenue_lag_subquery(COMPARE_COLUMNS)
    tax_cte = get_tax_lag_subquery()

    query = f"""
        WITH revenue AS (
            {revenue_cte}
        ),
        tax AS (
            {tax_cte}
        ),
        joined AS (
            SELECT
                r.date,
                r.date - INTERVAL '7 days' AS prev_date,
                {", ".join([f"r.{col}" for col in COMPARE_COLUMNS])},
                {", ".join([f"r.prev_{col}" for col in COMPARE_COLUMNS])},
                t.ca_voix_globale,
                t.prev_ca_voix_globale,
                -- Derived ratios
                (r.ca_global::NUMERIC / NULLIF(r.rechargement, 0)::NUMERIC) AS ratio_consumption,
                (r.prev_ca_global::NUMERIC / NULLIF(r.prev_rechargement, 0)::NUMERIC) AS prev_ratio_consumption
            FROM revenue r
            LEFT JOIN tax t ON r.date = t.date
        )
        SELECT
            date,
            prev_date,
            {revenue_select_cols},
            ROUND((ca_voix_globale::NUMERIC / NULLIF(prev_ca_voix_globale, 0)::NUMERIC) - 1, 6) AS rel_change_ca_voix_globale,
            ROUND((ratio_consumption / NULLIF(prev_ratio_consumption, 0)), 6) AS rel_change_ratio_consumption
        FROM joined
        WHERE date = %(target_date)s;
    """

    df = pd.read_sql_query(query, engine, params={"target_date": target_date})
    return df

def run_etl():
    output_path = "benin_turnover_reporting/output"
    args = parse_date_from_args()  # expects YYYY-MM-DD
    date_obj = args.date_obj.date()

    engine = get_db_engine()
    print(f"Fetching 7-day relative change for: {date_obj} vs {date_obj - pd.Timedelta(days=7)}")

    result_df = fetch_weekly_relative_change(engine, date_obj)

    if not result_df.empty:
        print("✅ Weekly relative change:")
        print(result_df.to_string(index=False))
        file_name = f"{output_path}/weekly_relative_change_{date_obj}.csv"
        result_df.to_csv(file_name, index=False)
        print(f"📦 Saved to: {file_name}")
    else:
        print("⚠️ No data available for the target date or its previous 7th day.")

if __name__ == "__main__":
    run_etl()
