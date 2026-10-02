import os
import pandas as pd

from helpers.db_utils import (
    get_db_connection,
    upsert_financial_data,
    get_version_id_by_name
)
from helpers.parse_arg import parse_arguments
from pathlib import Path

from .mapping.mobile_money_mapping import (
    financial_type_row_mapping,
    financial_metric_row_mapping,
    financial_submetric_row_mapping
)
from services.minio_factory import get_minio_service


# File name mapping (full month names)
FILE_MONTH_MAPPING = {
    '01': 'Janvier', '02': 'Février', '03': 'Mars', '04': 'Avril',
    '05': 'Mai', '06': 'Juin', '07': 'Juillet', '08': 'Août',
    '09': 'Septembre', '10': 'Octobre', '11': 'Novembre', '12': 'Décembre'
}

# Sheet processing mapping (abbreviated names)
MONTH_MAPPING = {
    '01': 'Janv', '02': 'Févr', '03': 'Mars', '04': 'Avr',
    '05': 'Mai', '06': 'Juin', '07': 'Juil', '08': 'Aout',
    '09': 'Sept', '10': 'Oct', '11': 'Nov', '12': 'Déc'
}


def col_to_index(col):
    """Convert Excel column letter to 0-based index"""
    return sum((ord(c.upper()) - ord('A') + 1) * (26 ** i) for i, c in enumerate(reversed(col))) - 1

def find_month_column(df, target_month, target_year):
    """Search for the column that matches the target month-year."""
    search_terms = [
        f"{FILE_MONTH_MAPPING[target_month]} {target_year}",   # e.g. "Mai 2025"
        f"{MONTH_MAPPING[target_month]} {target_year}",        # e.g. "Mai 2025" short
        f"{target_month}/{target_year}",                       # e.g. "05/2025"
        f"{target_month}-{target_year}",                       # e.g. "05-2025"
        f"{target_year}-{target_month}",                       # e.g. "2025-05"
    ]

    for row in range(5):  # check first few rows for header-like content
        for col in range(df.shape[1]):
            cell_value = str(df.iat[row, col]).strip().lower()
            for term in search_terms:
                if term.lower() in cell_value:
                    return col
    return None

def process_mobile_money_data(df, target_month, target_year, version_id):
    try:
        col_idx = find_month_column(df, target_month, target_year)
        if col_idx is None:
            raise ValueError(f"❌ Could not find column for {FILE_MONTH_MAPPING[target_month]} {target_year} in the Excel file.")

        target_month = int(target_month)  # ensure month is int
        date_value = f"{target_year}-{target_month:02d}-01"
        results = []

        # Month-based actual columns
        actual_columns = []
        if 4 <= target_month <= 5:
            actual_columns = ["actual1_value"]
        elif target_month == 6:
            actual_columns = ["actual1_value", "actual2_value"]
        elif 7 <= target_month <= 8:
            actual_columns = ["actual2_value"]
        elif target_month == 9:
            actual_columns = ["actual2_value", "actual3_value"]
        elif 10 <= target_month <= 12:
            actual_columns = ["actual3_value"]

        for idx, row in df.iterrows():
            row_number = idx + 1
            type_id = financial_type_row_mapping.get(row_number)
            metric_id = financial_metric_row_mapping.get(row_number)
            submetric_id = financial_submetric_row_mapping.get(row_number)

            if type_id or metric_id or submetric_id:    
                if len(row) > col_idx:
                    # Base values
                    real_value = row[col_idx] if pd.notna(row[col_idx]) else None
                    last_year_real_value = row[col_idx + 1] if pd.notna(row[col_idx + 1]) else None
                    budget_value = row[col_idx + 2] if pd.notna(row[col_idx + 2]) else None

                    # Dynamically extract actuals
                    actual_values = {}
                    for i, actual_label in enumerate(actual_columns):
                        val_idx = col_idx + 3 + i
                        val = row[val_idx] if len(row) > val_idx and pd.notna(row[val_idx]) else None
                        # Convert float integers to int
                        if isinstance(val, float) and val.is_integer():
                            val = int(val)
                        actual_values[actual_label] = val

                    # Convert IDs
                    type_id = int(type_id) if isinstance(type_id, float) and type_id.is_integer() else type_id
                    metric_id = int(metric_id) if isinstance(metric_id, float) and metric_id.is_integer() else metric_id
                    submetric_id = int(submetric_id) if isinstance(submetric_id, float) and submetric_id.is_integer() else submetric_id

                    # Convert base values to int if float integer
                    if isinstance(real_value, float) and real_value.is_integer(): real_value = int(real_value)
                    if isinstance(last_year_real_value, float) and last_year_real_value.is_integer(): last_year_real_value = int(last_year_real_value)
                    if isinstance(budget_value, float) and budget_value.is_integer(): budget_value = int(budget_value)

                    results.append({
                        "real_value": real_value,
                        "budget_value": budget_value,
                        "last_year_real_value": last_year_real_value,
                        **actual_values,
                        "financial_type_id": type_id,
                        "financial_metric_id": metric_id,
                        "financial_submetric_id": submetric_id,
                        "date": date_value,
                        "version_id": version_id
                    })

        result_df = pd.DataFrame(results)
        output_path = f"benin_parser_2025/reel_import/mobile_money_{target_month}{target_year}.csv"
        # result_df.to_csv(output_path, index=False)
        print(f"✅ CSV file for {date_value} generated successfully at: {output_path}")

        return result_df

    except Exception as e:
        print(f"Error processing mobile money data: {str(e)}")
        raise

def insert_data_to_db(result_df):
    conn = get_db_connection()
    cur = conn.cursor()
    print("Database connection successful!")

    for _, row in result_df.iterrows():
        type_id = row.get('financial_type_id')
        metric_id = row.get('financial_metric_id')
        submetric_id = row.get('financial_submetric_id')
        date_value = row.get('date')
        version_id = row.get('version_id')

        # Convert pandas NA/nan to None
        type_id = None if pd.isna(type_id) else type_id
        metric_id = None if pd.isna(metric_id) else metric_id
        submetric_id = None if pd.isna(submetric_id) else submetric_id
        date_value = None if pd.isna(date_value) else date_value
        version_id = None if pd.isna(version_id) else version_id

        # Base financial fields
        value_fields = {
            "real_value": None if pd.isna(row.get('real_value')) else row.get('real_value'),
            "budget_value": None if pd.isna(row.get('budget_value')) else row.get('budget_value'),
            "last_year_real_value": None if pd.isna(row.get('last_year_real_value')) else row.get('last_year_real_value')
        }

        # Dynamically add any actual#_value columns
        for col in row.index:
            if col.startswith('actual') and col.endswith('_value'):
                value_fields[col] = None if pd.isna(row[col]) else row[col]

        if type_id is not None or metric_id is not None or submetric_id is not None:
            upsert_financial_data(
                cur=cur,
                table_name="financial_metrics_data",
                type_id=type_id,
                metric_id=metric_id,
                submetric_id=submetric_id,
                date_value=date_value,
                version_id=version_id,
                **value_fields  # pass all dynamic fields including actuals
            )

    conn.commit()
    cur.close()
    conn.close()
    print("✅ Data insertion to database completed!")


if __name__ == "__main__":
    args = parse_arguments()
    target_month = args.month_year[:2]  # Extract MM from MMYYYY
    target_year = args.month_year[2:]   # Extract YYYY from MMYYYY
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

            excel_df = minio_service.read_excel(
                        object_name=object_path, header=None
                    )
            result_df = process_mobile_money_data(excel_df, target_month, target_year, version_id)
            insert_data_to_db(result_df)  

        else:
            print("ℹ️ No file provided. Skipping Mobile Money Excel processing...")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        
