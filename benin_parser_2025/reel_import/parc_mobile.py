import os
import openpyxl
from datetime import datetime
import pandas as pd

from io import BytesIO

from helpers.db_utils import (
    get_db_connection,
    upsert_financial_data, 
    get_version_id_by_name,
    get_default_version_id

)
from dateutil.relativedelta import relativedelta
from helpers.parse_arg import parse_arguments
from pathlib import Path
from .mapping.parc_mobile_mapping import initial_mapping, previous_month_mapping
from services.minio_factory import get_minio_service
from contextlib import closing
from tbg_formula.formula_evaluator import evaluate_tbg_formula
from tbg_formula.db_helper import get_tbg_report_mapping, find_tbg_key_in_table


def update_initial_values_from_excel(date, file_bytes, initial_mapping, version_id):
    # Create DB connection
    conn = get_db_connection()
    cur = conn.cursor()

    initial_values_cache = {}

    try:
        # Load workbook and specific sheet
        wb = openpyxl.load_workbook(filename=BytesIO(file_bytes), data_only=True)
        ws = wb["KPIs"]

        for row_key, mapping in initial_mapping.items():
            table_name = mapping["table_name"]
            submetric_id = mapping["financial_submetric_id"]
            kpi_key = mapping["kpi_key"]

            # Get the value from the Excel cell
            real_value = ws[kpi_key].value
            if kpi_key.startswith("G") and isinstance(real_value, (int, float)):
                real_value *= -1
            initial_values_cache[row_key] = real_value

            try:
                upsert_financial_data(
                    cur,
                    table_name=table_name,
                    type_id=None,
                    metric_id=None,
                    submetric_id=submetric_id,
                    date_value=date,
                    real_value=real_value,
                    version_id=version_id
                )
                print(f"✅ Upserted value for {row_key} (submetric_id={submetric_id}), date={date}")
            except Exception as inner_e:
                print(f"❌ Failed to upsert for {row_key} (submetric_id={submetric_id}): {inner_e}")

        conn.commit()
    except Exception as e:
        conn.rollback()
        print(f"❌ Fatal error: {e}")
    finally:
        cur.close()
        conn.close()
        wb.close()

    return initial_values_cache


def upsert_previous_month_values(date, previous_month_mapping, version_id):
    # Create DB connection
    conn = get_db_connection()
    cur = conn.cursor()

    cache = {}

    try:
        # Ensure date is a datetime object
        if isinstance(date, str):
            date = datetime.strptime(date, "%Y-%m-%d")

        # Get the previous month's date
        prev_month_date = date - relativedelta(months=1)

        # Get default version_id for previous month
        prev_month_version_id = int(get_default_version_id(prev_month_date.month, prev_month_date.year))
        print(f"📅 Previous month: {prev_month_date.date()}, Default version_id: {prev_month_version_id}")

        for row_key, mapping in previous_month_mapping.items():
            column_name = mapping["column_name"]
            value_id = mapping["value"]
            type_id = mapping["type_id"]

            # Prepare query using previous month's default version_id
            query = f"""
                SELECT real_value FROM financial_metrics_data
                WHERE {column_name} = %s
                AND version_id = %s
            """
            cur.execute(query, (value_id, prev_month_version_id))
            result = cur.fetchone()

            if result:
                real_value = result[0]
                cache[row_key] = real_value

                try:
                    upsert_financial_data(
                        cur,
                        table_name="financial_metrics_data",
                        type_id=None,
                        metric_id=type_id,
                        submetric_id=None,
                        date_value=date,
                        real_value=real_value,
                        version_id=version_id
                    )
                    print(f"✅ Upserted previous month value for {row_key} (id={value_id}), date={date}")
                except Exception as inner_e:
                    print(f"❌ Failed to upsert {row_key}: {inner_e}")
            else:
                print(f"⚠️ No data found for {row_key} (id={value_id}), prev_month_version_id={prev_month_version_id}")

        conn.commit()
    except Exception as e:
        conn.rollback()
        print(f"❌ Fatal error during previous month upsert: {e}")
    finally:
        cur.close()
        conn.close()

    return cache
def process_parc_mobile(date, report_type_id, version_id, full_cache=None):
    full_cache = full_cache or {}
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

            base_record_found = find_tbg_key_in_table(conn, tbg_key)

            if not base_record_found:
                print("⚠ Warning: Base key '{}' not found. Skipping.".format(tbg_key))
                continue

            base_col_name, base_table, base_tbg_key_id = base_record_found

            final_result = evaluate_tbg_formula(
                conn,
                tbg_key,
                formula,
                version_id,
                full_cache
            )

            results_list.append({
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
                "version_id": version_id
            })

    df_csv = pd.DataFrame(results_list)

    output_csv_path = "benin_parser_2025/reel_import/outputs/parc_mobile_{}.csv".format(date)
    # df_csv.to_csv(output_csv_path, index=False)

    print("📁 CSV file for {} generated successfully at: {}".format(date, output_csv_path))

    return df_csv

def insert_data_to_db(result_df):
    conn = get_db_connection()
    cur = conn.cursor()
    print("Database connection successful!")

    for _, row in result_df.iterrows():
        type_id = row['financial_type_id']
        metric_id = row['financial_metric_id']
        submetric_id = row.get('financial_submetric_id')
        date_value = row['date']
        real_value = row['real_value']
        version_id = row['version_id']

        # Convert pandas NA/nan to None
        type_id = None if pd.isna(type_id) else type_id
        metric_id = None if pd.isna(metric_id) else metric_id
        submetric_id = None if pd.isna(submetric_id) else submetric_id
        real_value = None if pd.isna(real_value) else real_value

        if type_id is not None or metric_id is not None or submetric_id is not None:
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
    file_name = args.file_name.strip() if args.file_name else ""

    # Fetch version id
    version_id = get_version_id_by_name(args.version_id)
    report_type_id = 10
    minio_service = get_minio_service()
    try:
        initial_cache = {}

        # Run only if file provided
        if file_name:
            object_path = f"{target_year}/{target_year}{target_month}/{file_name}"
            print(f"Fetching file from MinIO path: {object_path}")
            file_bytes = minio_service.get_file_bytes(object_name=object_path)
            initial_cache = update_initial_values_from_excel(date, file_bytes, initial_mapping, version_id)
        else:
            print("ℹ️ No file provided. Skipping initial Excel-based values...")

        # Always run previous month + main processing
        previous_month_cache = upsert_previous_month_values(date, previous_month_mapping, version_id)
        full_cache = {**initial_cache, **previous_month_cache}

        df_parc_mobile = process_parc_mobile(date, report_type_id, version_id, full_cache)
        insert_data_to_db(df_parc_mobile)

        print("✅ Data successfully prepared and inserted into DB.")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
