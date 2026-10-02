import os
import sys
import pandas as pd
from .mapping_utils import get_financial_hierarchy
from helpers.db_utils import get_db_connection, upsert_financial_data, get_version_id_by_name
from helpers.parse_arg import parse_arguments
from services.minio_factory import get_minio_service

# Constants
ZERO_INDEX = 1
START_ROW = 7 - ZERO_INDEX
MONTH_ROW = 4 - ZERO_INDEX
CATEGORY = "Opex Consolidés"
TYPE_METRIC_SUBMETRIC_COL = 2
DATA_COLS = list(range(3, 16))

MONTH_MAP = {
    "JANVIER": "01", "FEVRIER": "02", "MARS": "03", "AVRIL": "04",
    "MAI": "05", "JUIN": "06", "JUILLET": "07", "AOÛT": "08",
    "SEPTEMBRE": "09", "OCTOBRE": "10", "NOVEMBRE": "11", "DÉCEMBRE": "12",
    "Total Annuel": "ANNUEL"
}

def parse_months(df):
    return df.iloc[MONTH_ROW, DATA_COLS].tolist()

def determine_table_and_date(month_label, year, target_month):
    # Use the target_month from input for both monthly and annual data
    month_number = target_month
    if month_label == "Total Annuel":
        return "financial_annual_data", f"{year}-01-01"

    month_number_from_label = MONTH_MAP.get(month_label)
    if not month_number_from_label:
        print(f"Error: Unknown month label '{month_label}'")
        return None, None
    return "financial_metrics_data", f"{year}-{month_number}-01"

def process_excel_data(df, months, target_month, year, version_id):
    conn = get_db_connection()
    cur = conn.cursor()

    for index, row in df.iterrows():
        if index < START_ROW:
            continue

        type_label = row[TYPE_METRIC_SUBMETRIC_COL]
        if pd.isna(type_label):
            continue

        type_label = type_label.strip()
        type_id, metric_id, submetric_id = get_financial_hierarchy(row, CATEGORY)

        if all(v is None for v in [type_id, metric_id, submetric_id]):
            continue

        for col_index, budget_value in zip(DATA_COLS, row[DATA_COLS]):
            month_label = months[col_index - DATA_COLS[0]]
            month_number = MONTH_MAP.get(month_label)

            # Process annual data for "Total Annuel" regardless of target month
            # Process monthly data only if month_number matches target_month
            if month_label != "Total Annuel" and month_number != target_month:
                continue

            table_name, date_value = determine_table_and_date(month_label, year, target_month)
            if not table_name:
                continue

            if pd.isna(budget_value):
                budget_value = None

            upsert_financial_data(
                cur, table_name, type_id, metric_id, submetric_id,
                date_value,
                budget_value=budget_value,
                version_id=version_id
            )

    conn.commit()
    cur.close()
    conn.close()
    print("Data insertion completed!")

def main():
    args = parse_arguments()
    # Parse month_year (e.g., "032025" -> month="03", year="2025")
    if len(args.month_year) != 6:
        raise ValueError("month_year must be in MMYYYY format (e.g., 032025)")
    target_month = args.month_year[:2]
    year = args.month_year[2:]
    file_name = args.file_name

    # Validate month
    if not (1 <= int(target_month) <= 12):
        raise ValueError("Month must be between 01 and 12")

    version_id = get_version_id_by_name(args.version_id)
    #version_id = args.version_id
    object_path = f"{year}/{year}01/{file_name}"

    minio_service = get_minio_service()
    excel_df = minio_service.read_excel(object_name=object_path, sheet_name='Opex Consolidés', header=None)

    months = parse_months(excel_df)

    print(f"Processing for month: {target_month}, year: {year}")
    process_excel_data(excel_df, months, target_month, year, version_id)

if __name__ == "__main__":
    main()
