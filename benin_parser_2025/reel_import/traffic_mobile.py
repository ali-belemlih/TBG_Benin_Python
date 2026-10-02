import os
import pandas as pd

from helpers.db_utils import get_db_connection, upsert_financial_data, get_version_id_by_name

from services.minio_factory import get_minio_service
from helpers.parse_arg import parse_arguments
from pathlib import Path
from .mapping.traffic_mobile_mapping import financial_type_row_mapping, financial_metric_row_mapping, financial_submetric_row_mapping

FILE_MONTH_MAPPING = {
    '01': 'Janvier', '02': 'Février', '03': 'Mars', '04': 'Avril',
    '05': 'Mai', '06': 'Juin', '07': 'Juillet', '08': 'Août',
    '09': 'Septembre', '10': 'Octobre', '11': 'Novembre', '12': 'Décembre'
}

# Financial Data Structure
FINANCIAL_STRUCTURE = {
    "financial_type": [1, 49],
    "financial_metric": [3, 12, 21, 30, 39, 51, 58],
    "financial_submetric": [
        (4, 11), (13, 20), (22, 29), (31, 38), (40, 47), (52, 57), (59, 64)
    ]
}

def process_trafic_sheet(df, date, version_id):
    df = df.iloc[:65, [0, 3]]
    results = []

    for index, (name_cell, value_cell) in df.iterrows():
        row_number = index + 1
        category_name = str(name_cell).strip() if pd.notna(name_cell) else None
        real_value = value_cell if pd.notna(value_cell) else None

        if not category_name:
            continue

        result = {
            "financial_type_id": None,
            "financial_metric_id": None,
            "financial_submetric_id": None,
            "real_value": real_value,
            "date": date,
            "version_id" : version_id
        }

        if index in FINANCIAL_STRUCTURE["financial_type"]:
            result["financial_type_id"] = financial_type_row_mapping.get(row_number)
        elif index in FINANCIAL_STRUCTURE["financial_metric"]:
            result["financial_metric_id"] = financial_metric_row_mapping.get(row_number)
        elif any(start <= index <= end for start, end in FINANCIAL_STRUCTURE["financial_submetric"]):
            result["financial_submetric_id"] = financial_submetric_row_mapping.get(row_number)
        else:
            continue  # Skip unknown rows

        results.append(result)

    df_csv = pd.DataFrame(results)
    output_csv_path = f'benin_parser_2025/reel_import/outputs/Trafic_Mobile_{date}.csv'
    # df_csv.to_csv(output_csv_path, index=False)
    print(f"✅ CSV file for {date} generated successfully at: {output_csv_path}")
    return df_csv

def insert_data_to_db(result_df):
    conn = get_db_connection()
    cur = conn.cursor()

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
                version_id = version_id,
                budget_value=None
            )

    conn.commit()
    cur.close()
    conn.close()
    print("Data insertion to database completed!")

if __name__ == "__main__":
    args = parse_arguments()
    target_month = args.month_year[:2]  # Extract MM from MMYYYY
    target_year = args.month_year[2:]   # Extract YYYY from MMYYYY
    date = f"{target_year}-{target_month}-01"
    file_name = args.file_name.strip() if args.file_name else ""

    # Fetch version id
    version_id = get_version_id_by_name(args.version_id)

    if target_month not in FILE_MONTH_MAPPING:
        print("Invalid month provided. Please provide a valid MMYYYY format.")
        exit(1)

    minio_service = get_minio_service()
    try:
        if file_name:
            object_path = f"{target_year}/{target_year}{target_month}/{file_name}"
            print(f"Fetching file from MinIO path: {object_path}")

            excel_df = minio_service.read_excel(object_name=object_path, sheet_name="TRAFIC", header=None)
            df_trafic = process_trafic_sheet(excel_df, date, version_id)
            insert_data_to_db(df_trafic)

            print("✅ Data successfully inserted into DB.")
        else:
            print("ℹ️ No file provided. Skipping TRAFIC Excel processing...")

    except Exception as e:
        print(f"❌ Error: {str(e)}")
