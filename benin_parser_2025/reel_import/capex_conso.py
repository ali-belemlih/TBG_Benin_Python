import pandas as pd
from helpers.db_utils import (
    get_db_connection, 
    upsert_financial_data, 
    get_version_id_by_name
)
from helpers.formula_utils.evaluator import evaluate_formula
from helpers.parse_arg import parse_arguments
from contextlib import closing
from tbg_formula.formula_evaluator import evaluate_tbg_formula
from tbg_formula.db_helper import get_tbg_report_mapping, find_tbg_key_in_table

def calculate_real_value(formula, date, version_id, cache=None):
    conn = get_db_connection()
    cur = conn.cursor()
    cache = cache or {}
    cache_key = f"calc_real_value_{formula}_{date}_{version_id}"

    if cache_key in cache:
        return cache[cache_key]

    value = evaluate_formula(
        cur, formula, date, "real_value", version_id=version_id, cache=cache
    )
    cache[cache_key] = value
    return value

def process_capex_conso(date, version_id, report_type_id, is_adjustible_only=None):
    cache = {}
    results_list = []

    with closing(get_db_connection()) as conn:

        fetched_mapping = get_tbg_report_mapping(conn, report_type_id)

        if not fetched_mapping:
            print("❌ No record found for the passed report type.")
            return pd.DataFrame()

        for record in fetched_mapping:
            (
                formula_id,
                tbg_key,
                report_type_id,
                formula_type,
                account_details,
                include_sage,
                formula,          # index 6
                is_adjustable,    # index 7
                created_at,
                updated_at,
                sequence,
            ) = record

            if is_adjustible_only and not is_adjustable:
                continue

            base_record_found = find_tbg_key_in_table(conn, tbg_key)

            if not base_record_found:
                print(f"⚠ Warning: Base key '{tbg_key}' not found. Skipping.")
                continue

            base_col_name, base_table, base_tbg_key_id = base_record_found

            final_result = evaluate_tbg_formula(
                conn,
                tbg_key,
                formula,
                version_id,
                cache
            )

            print(f"✅ Final result for [{tbg_key}] = {final_result}")
            # ---- Append result ----
            results_list.append(
                {
                    "financial_type_id": base_tbg_key_id
                    if base_col_name == "financial_type_id"
                    else None,
                    "financial_metric_id": base_tbg_key_id
                    if base_col_name == "financial_metric_id"
                    else None,
                    "financial_submetric_id": base_tbg_key_id
                    if base_col_name == "financial_submetric_id"
                    else None,
                    "real_value": final_result,
                    "date": date,
                    "version_id": version_id,
                }
            )

    df_csv = pd.DataFrame(results_list)

    output_csv_path = "benin_parser_2025/reel_import/outputs/capex_conso_{}.csv".format(date)
    # df_csv.to_csv(output_csv_path, index=False)

    print("📁 CSV file for {} generated successfully at: {}".format(date, output_csv_path))

    return df_csv

def insert_capex_data_to_db(result_df):
    conn = get_db_connection()
    cur = conn.cursor()
    print("Database connection successful!")

    for _, row in result_df.iterrows():
        type_id = row["financial_type_id"]
        metric_id = row["financial_metric_id"]
        submetric_id = row.get("financial_submetric_id")
        date_value = row["date"]
        real_value = row["real_value"]
        version_id = row["version_id"]

        # Convert pandas NA/nan to None
        type_id = None if pd.isna(type_id) else type_id
        metric_id = None if pd.isna(metric_id) else metric_id
        submetric_id = None if pd.isna(submetric_id) else submetric_id
        real_value = None if pd.isna(real_value) else real_value

        if (
            type_id is not None
            or metric_id is not None
            or submetric_id is not None
        ):
            upsert_financial_data(
                cur=cur,
                table_name="financial_metrics_data",
                type_id=type_id,
                metric_id=metric_id,
                submetric_id=submetric_id,
                date_value=date_value,
                real_value=real_value,
                version_id=version_id,
                budget_value=None,
            )

    conn.commit()
    cur.close()
    conn.close()
    print("Data insertion to database completed!")


if __name__ == "__main__":
    args = parse_arguments()
    target_month = args.month_year[:2]
    target_year = args.month_year[2:]
    date = f"{target_year}-{target_month}-01"  # Format: YYYY-MM-01
    report_type_id = 2
    version_id = get_version_id_by_name(args.version_id)

    try:
        df_capex = process_capex_conso(date, version_id, report_type_id)
        insert_capex_data_to_db(df_capex)
    except Exception as e:
        print(f"❌ Error: {str(e)}")
