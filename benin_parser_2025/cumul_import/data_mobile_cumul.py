import pandas as pd
from helpers.db_utils import get_db_connection, upsert_cumulative_data, get_version_id_by_name
from helpers.parse_arg import parse_arguments
from pathlib import Path
from .mapping.data_mobile_cumul_mapping import financial_type_row_mapping, financial_metric_row_mapping
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
    '05': 'Mai', '06': 'Juin', '07': 'Juil', '08': 'Août',
    '09': 'Sept', '10': 'Oct', '11': 'Nov', '12': 'Déc'
}

def col_to_index(col):
    return sum((ord(c.upper()) - ord('A') + 1) * (26 ** i) for i, c in enumerate(reversed(col))) - 1

def find_month_column(df, target_month, target_year):
    """Search for the column that matches the target month-year."""
    search_terms = [
        "Cumulé"
    ]

    for row in range(5):  # check first few rows for header-like content
        for col in range(df.shape[1]):
            cell_value = str(df.iat[row, col]).strip().lower()
            for term in search_terms:
                if term.lower() in cell_value:
                    return col
    return None

def process_mobile_data(df, target_month, target_year, version_id):
    try:
        col_idx = find_month_column(df, target_month, target_year)
        if col_idx is None:
            raise ValueError(f"❌ Could not find column for {FILE_MONTH_MAPPING[target_month]} {target_year} in the Excel file.")

        date_value = f"{target_year}-{target_month}-01"
        results = []

        for idx, row in df.iterrows():
            row_number = idx + 1
            type_id = financial_type_row_mapping.get(row_number)
            metric_id = financial_metric_row_mapping.get(row_number)

            if type_id or metric_id:
                if len(row) > col_idx and pd.notna(row[col_idx]):
                    real_value = row[col_idx]
                    last_year_real_value = row[col_idx + 1]
                    budget_value = row[col_idx + 2]



                    # Convert values to appropriate types
                    real_value = int(real_value) if isinstance(real_value, float) and real_value.is_integer() else real_value
                    last_year_real_value = int(last_year_real_value) if isinstance(last_year_real_value, float) and last_year_real_value.is_integer() else last_year_real_value
                    budget_value = int(budget_value) if isinstance(budget_value, float) and budget_value.is_integer() else budget_value
                    type_id = int(type_id) if isinstance(type_id, float) and type_id.is_integer() else type_id
                    metric_id = int(metric_id) if isinstance(metric_id, float) and metric_id.is_integer() else metric_id

                    results.append({
                        'real_value': real_value,
                        'budget_value': budget_value,
                        'last_year_real_value': last_year_real_value,
                        'financial_type_id': type_id,
                        'financial_metric_id': metric_id,
                        'financial_submetric_id': None,
                        'date': date_value,
                        'version_id': version_id
                    })

        result_df = pd.DataFrame(results)
        output_path = f"benin_parser_2025/cumul_import/data_mobile_{target_month}{target_year}.csv"
        result_df.to_csv(output_path, index=False)
        print(f"✅ CSV file for {date_value} generated successfully at: {output_path}")

        return result_df
    except Exception as e:
        print(f"Error processing file: {str(e)}")
        raise

def insert_data_to_db(result_df):
    """Insert data from a DataFrame into the financial_cumulative_data table."""
    conn = get_db_connection()
    print("Database connection successful!")

    # Build the list of tuples expected by upsert_cumulative_data
    cumulative_data = []
    for _, row in result_df.iterrows():
        financial_type_id = None if pd.isna(row.get("financial_type_id")) else row["financial_type_id"]
        financial_metric_id = None if pd.isna(row.get("financial_metric_id")) else row["financial_metric_id"]
        financial_submetric_id = None if pd.isna(row.get("financial_submetric_id")) else row["financial_submetric_id"]
        date_value = row["date"]
        real_value = row.get("real_value")
        budget_value = row.get("budget_value")
        last_year_real_value = row.get("last_year_real_value")
        actual1_value = row.get("actual1_value")
        actual2_value = row.get("actual2_value")
        actual3_value = row.get("actual3_value")
        version_id = row["version_id"]

        cumulative_data.append((
            financial_type_id,
            financial_metric_id,
            financial_submetric_id,
            date_value,
            real_value,
            budget_value,
            last_year_real_value,
            actual1_value,
            actual2_value,
            actual3_value,
        ))

    # Use the new upsert method
    upsert_cumulative_data(conn, cumulative_data, version_id)

    conn.close()
    print("Data insertion to database completed!")


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

            excel_df = minio_service.read_excel(object_name=object_path, header=None)
            result_df = process_mobile_data(excel_df, target_month, target_year, version_id)
            insert_data_to_db(result_df)
        else:
            print("ℹ️ No file provided. Skipping Excel-based processing...")

    except Exception as e:
        print(f"❌ Error: {str(e)}")
