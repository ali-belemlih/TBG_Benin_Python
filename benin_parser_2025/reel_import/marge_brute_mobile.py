import sys
import openpyxl
import pandas as pd
from io import BytesIO
from datetime import datetime
from openpyxl.utils import get_column_letter
from helpers.db_utils import (
    get_db_connection,
    upsert_financial_data,
    get_version_id_by_name,
    get_calculation_field_value,
)
from helpers.formula_utils.evaluator import evaluate_formula
from helpers.parse_arg import parse_arguments
from .mapping.marge_brute_mobile_mapping import extraction_mapping
from services.minio_factory import get_minio_service
from contextlib import closing
from tbg_formula.formula_evaluator import evaluate_tbg_formula
from tbg_formula.db_helper import get_tbg_report_mapping, find_tbg_key_in_table


def update_data_from_estimations(date, version_id):
    conn = get_db_connection()
    cur = conn.cursor()

    try:
        # --- Fetch calculation field value (MB33) ---
        incoming_value = get_calculation_field_value(
            cur, "MB33", date, "INCOMING", version_id
        )
        print(f"📥 Incoming MB33: {incoming_value}")

        outgoing_value = get_calculation_field_value(
            cur, "MB33", date, "OUTGOING", version_id
        )
        print(f"📤 Outgoing MB33: {outgoing_value}")

        calc_val = incoming_value + outgoing_value
        print(
            f"🧮 MB33 total = INCOMING ({incoming_value}) + OUTGOING ({outgoing_value}) → {calc_val}"
        )

        # --- Normalize (if not already in millions) ---
        if abs(calc_val) > 1000:
            final_val = calc_val / 1_000_000
            print(f"🔄 Converted MB33 to millions: {final_val}")
        else:
            final_val = calc_val
            print(f"✅ MB33 already in millions: {final_val}")

        # --- Upsert into financial_metrics_data ---
        upsert_financial_data(
            cur,
            "financial_metrics_data",
            type_id=None,
            metric_id=73,
            submetric_id=None,
            date_value=date,
            real_value=final_val,
            version_id=version_id,
        )

        conn.commit()
        print(f"✅ Real value from MB33 inserted for metric_id=73, date={date}")

    except Exception as e:
        conn.rollback()
        print(f"❌ Failed to insert MB33 value into DB: {e}")
    finally:
        cur.close()
        conn.close()


def process_marge_brute_mobile(date, file_bytes, version_id):
    results = []
    workbook = openpyxl.load_workbook(filename=BytesIO(file_bytes), data_only=True)
    sheet = workbook[
        "RECAP"
    ]  # You can also specify the sheet by name: workbook["Sheet1"]

    # Get month index (1=Jan, 2=Feb, ...) and corresponding Excel column (B=2, C=3, ...)
    month_index = datetime.strptime(date, "%Y-%m-%d").month
    column_letter = get_column_letter(1 + month_index)

    for label, data in extraction_mapping.items():
        base_address = data["formula"].get("data")  # e.g., "B14"
        row = "".join(
            filter(str.isdigit, base_address)
        )  # Extract row number, e.g., "14"
        dynamic_address = (
            f"{column_letter}{row}"  # Replace column with month-specific letter
        )

        # Fetch value and safely handle None
        cell = sheet[dynamic_address]
        cell_value = -1 * (cell.value or 0.0) / 1_000_000

        # Determine which ID to use based on type
        type_id = data["id"] if data["type"] == "financial_type" else None
        metric_id = data["id"] if data["type"] == "financial_metric" else None
        submetric_id = data["id"] if data["type"] == "financial_submetric" else None

        result = {
            "financial_type_id": type_id,
            "financial_metric_id": metric_id,
            "financial_submetric_id": submetric_id,
            "real_value": cell_value,
            "date": date,
            "version_id": version_id,
        }
        results.append(result)

    df_csv = pd.DataFrame(results)
    # output_csv_path = f'benin_parser_2025/reel_import/marge_excel_{date}.csv'
    # df_csv.to_csv(output_csv_path, index=False)
    # print(f"✅ CSV file for {date} generated successfully at: {output_csv_path}")
    return df_csv

def process_marge_mapping(date, version_id, report_type_id, is_adjustible_only=None):
    results_list = []
    cache = {}

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
                print("⚠ Warning: Base key '{}' not found. Skipping.".format(tbg_key))
                continue

            base_col_name, base_table, base_tbg_key_id = base_record_found

            final_result = evaluate_tbg_formula(
                    conn,
                    tbg_key,
                    formula,
                    version_id,
                    cache
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

    output_csv_path = "benin_parser_2025/reel_import/outputs/marge_brute_mobile_{}.csv".format(date)
    # df_csv.to_csv(output_csv_path, index=False)

    print("📁 CSV saved: {}".format(output_csv_path))

    return df_csv


def insert_marge_data_to_db(result_df):
    conn = get_db_connection()
    cur = conn.cursor()

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
    target_month = sys.argv[1][:2]
    target_year = sys.argv[1][2:]
    date = f"{target_year}-{target_month}-01"  # Format: YYYY-MM-01
    extractions = sys.argv[3].strip() if len(sys.argv) > 3 else ""
    report_type_id = 6
    # fetch version id
    version_id = get_version_id_by_name(sys.argv[2])

    minio_service = get_minio_service()
    try:
        # Always run
        update_data_from_estimations(date, version_id)

        # Run only if extraction file provided
        if extractions:
            extractions_path = f"{target_year}/{target_year}{target_month}/{extractions}"
            print(f"Fetching Extraction from MinIO path: {extractions_path}")
            extractions_bytes = minio_service.get_file_bytes(object_name=extractions_path)
            df_marge = process_marge_brute_mobile(date, extractions_bytes, version_id)
            insert_marge_data_to_db(df_marge)
        else:
            print("ℹ️ No extraction file provided. Skipping Excel-based marge processing...")

        # Always run mapping
        df_marge_mapping = process_marge_mapping(date, version_id, report_type_id)
        insert_marge_data_to_db(df_marge_mapping)

        print("✅ Data successfully prepared and inserted into DB.")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
