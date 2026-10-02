import openpyxl
from datetime import datetime
import pandas as pd
from io import BytesIO
import re
from contextlib import closing

from helpers.db_utils import (
    get_db_connection,
    upsert_financial_data, 
    get_version_id_by_name
)
from tbg_formula.formula_evaluator import evaluate_tbg_formula
from tbg_formula.db_helper import get_tbg_report_mapping, find_tbg_key_in_table, get_adjusted_value_from_db
from helpers.parse_arg import parse_arguments
from services.minio_factory import get_minio_service

month_column_map = {1: 'B', 2: 'C', 3: 'D', 4: 'E',
                    5: 'F', 6: 'G', 7: 'H', 8: 'I',
                    9: 'J', 10: 'K', 11: 'L', 12: 'M'
                    }

def update_data_from_excel_file(date, file_bytes, version_id):
    # Load the workbook and first sheet
    wb = openpyxl.load_workbook(filename=BytesIO(file_bytes), data_only=True)
    if "Cash conso" not in wb.sheetnames:
        print(f"❌ Sheet 'Cash conso' not found in the Excel file.")
        return
    ws = wb["Cash conso"]

    # Extract month and year from the date string
    dt = datetime.strptime(date, "%Y-%m-%d")
    month = dt.month

    col_letter = month_column_map.get(month)
    if not col_letter:
        print(f"❌ Month {month} not supported.")
        return

    conn = get_db_connection()
    cur = conn.cursor()

    try:
        # 1️⃣ Insert data from row 11 (Variation de BFR opérationnel (+/-)) → metric_id 46
        row_11 = f"{col_letter}11"
        row_11_value = ws[row_11].value or 0.0
        print(f"📊 Row 11: ({row_11}): {row_11_value}")

        upsert_financial_data(
            cur, "financial_metrics_data",
            type_id=None,
            metric_id=46,
            submetric_id=None,
            date_value=date,
            real_value=row_11_value,
            version_id=version_id
        )

        # 2️⃣ Insert data from row 33 (Autres éléments non cash ) → metric_id 55
        row_33 = f"{col_letter}33"
        row_33_value = ws[row_33].value or 0.0
        print(f"📊 Row 33 ({row_33}): {row_33_value}")

        upsert_financial_data(
            cur, "financial_metrics_data",
            type_id=None,
            metric_id=55,
            submetric_id=None,
            date_value=date,
            real_value=row_33_value,
            version_id=version_id
        )

        conn.commit()
        print("✅ All data inserted successfully.")
    except Exception as e:
        conn.rollback()
        print(f"❌ Failed to insert data: {e}")
    finally:
        cur.close()
        conn.close()

NO_MULTIPLY_KEYS = {"FLUX16", "FLUX29", "FLUX33", "FLUX24"}

def process_cash_conso(date, version_id, report_type_id, is_adjustible_only=None):
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
                formula,
                is_adjustable,
                created_at,
                updated_at,
                sequence,
            ) = record

            if is_adjustible_only and not is_adjustable:
                continue

            base_record_found = find_tbg_key_in_table(conn, tbg_key)

            if not base_record_found:
                print("⚠ Warning: Base key '{}' not found. Skipping.".format(tbg_key))
                continue

            base_col_name, base_table, base_tbg_key_id = base_record_found
            print(f"==============={tbg_key}====================")

            final_result = evaluate_tbg_formula(
                conn,
                tbg_key,
                formula,
                version_id,
                cache,
                date,
                skip_adjustment=True
            )

            if final_result is not None:
                has_flux = bool(re.search(r'\bFLUX\d+\b', formula or ''))
                if not has_flux:
                    final_result = final_result * 1_000_000
            
            cache[tbg_key] = final_result if final_result is not None else 0

            found = find_tbg_key_in_table(conn, tbg_key)
            if found:
                col_name, table, key_id = found
                adjusted_value = get_adjusted_value_from_db(conn, key_id, table, col_name, version_id, date)
                if adjusted_value:
                    print(f"[ADJUSTED] {tbg_key}: multiplied={final_result}, adjusted={adjusted_value}, final={(final_result or 0) + adjusted_value}")
                    total_value = (final_result or 0) + adjusted_value
                    cache[tbg_key] = total_value

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
    return df_csv

def insert_data_to_db(result_df):
    conn = get_db_connection()
    cur = conn.cursor()
    print("Database connection successful!")

    for _, row in result_df.iterrows():
        type_id = row['financial_type_id']
        metric_id = row['financial_metric_id']
        submetric_id = row['financial_submetric_id']
        date_value = row['date']
        real_value = row['real_value']
        version_id = row['version_id']

        # Convert pandas NA/nan to None
        type_id = None if pd.isna(type_id) else type_id
        metric_id = None if pd.isna(metric_id) else metric_id
        submetric_id = None if pd.isna(submetric_id) else submetric_id
        real_value = 0 if pd.isna(real_value) else real_value

        if type_id is not None or metric_id is not None or submetric_id is not None:
            upsert_financial_data(
                cur=cur,
                table_name="financial_metrics_data",
                type_id=type_id,
                metric_id=metric_id,
                submetric_id=submetric_id,
                date_value=date_value,
                real_value=0 if real_value is None else real_value,  # no multiplication here
                version_id=version_id,
                budget_value=None,
            )

    conn.commit()
    cur.close()
    conn.close()
    print("Data insertion to database completed!")

if __name__ == "__main__":
    args = parse_arguments()
    target_month = args.month_year[:2]  # Extract MM from MMYYYY
    target_year = args.month_year[2:]  # Extract YYYY from MMYYYY
    date = f"{target_year}-{target_month}-01"  # Assuming 1st day of the month
    file_name = args.file_name.strip() if args.file_name else ""

    # Fetch version id
    version_id = get_version_id_by_name(args.version_id)
    report_type_id = 3
    minio_service = get_minio_service()

    try:
        # Run only if file is provided
        if file_name:
            object_path = f"{target_year}/{target_year}{target_month}/{file_name}"
            print(f"Fetching file from MinIO path: {object_path}")
            file_bytes = minio_service.get_file_bytes(object_name=object_path)
            update_data_from_excel_file(date, file_bytes, version_id)

        # Always run downstream processing
        df_cash_conso = process_cash_conso(date, version_id, report_type_id)
        insert_data_to_db(df_cash_conso)  # Uncomment when ready
        print("✅ Data successfully prepared for DB.")

    except Exception as e:
        print(f"❌ Error: {str(e)}")
