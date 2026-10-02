import os
import pandas as pd
from helpers.db_utils import get_db_connection, upsert_financial_data, get_version_id_by_name
from helpers.parse_arg import parse_arguments
from services.minio_factory import get_minio_service
from .mapping.mobile_money_mapping import financial_type_row_mapping, financial_metric_row_mapping, \
    financial_submetric_row_mapping

def extract_budget_data_for_month(df, month_num, year, version_id):
    """Extract budget data for a specific month from Mobile Money sheet"""
    # Define the month columns (R to AC, i.e., index 17 to 28)
    month_columns = list(range(17, 29))
    month_names = ['01', '02', '03', '04', '05', '06',
                   '07', '08', '09', '10', '11', '12']

    # Find the column index for the requested month (0-based)
    try:
        month_idx = month_names.index(month_num)
    except ValueError:
        raise ValueError(f"Invalid month number: {month_num}. Must be between 01-12")

    month_col = month_columns[month_idx]
    result_data = []

    for row in range(4, df.shape[0]):
        element = df.iloc[row, 3]  # Column D (index 3) contains element names
        budget = df.iloc[row, month_col]  # Monthly budget value

        # Skip only if element is empty
        if pd.isna(element):
            continue

        # Look up mapping values (Excel is 1-based)
        excel_row = row + 1
        financial_type_id = financial_type_row_mapping.get(excel_row)
        financial_metric_id = financial_metric_row_mapping.get(excel_row)
        financial_submetric_id = financial_submetric_row_mapping.get(excel_row)

        # Convert float IDs to integers if they exist
        financial_type_id = int(financial_type_id) if pd.notna(financial_type_id) else None
        financial_metric_id = int(financial_metric_id) if pd.notna(financial_metric_id) else None
        financial_submetric_id = int(financial_submetric_id) if pd.notna(financial_submetric_id) else None

        result_data.append({
            'date': f"{year}-{month_num}-01",  # Use the passed month_num
            'budget_value': budget,  # Keep null values
            'financial_type_id': financial_type_id,
            'financial_metric_id': financial_metric_id,
            'financial_submetric_id': financial_submetric_id,
            'version_id': version_id
        })

    # Convert to DataFrame
    result_df = pd.DataFrame(result_data)

    return result_df

def extract_annual_budget_data(df, year, version_id, month_num):
    """Extract annual budget data from column AD in Mobile Money sheet"""
    # Column AD is at index 29 (0-based)
    annual_col = 29
    result_data = []

    for row in range(4, df.shape[0]):
        element = df.iloc[row, 3]  # Column D (index 3) contains element names
        budget = df.iloc[row, annual_col]  # Annual budget value

        # Skip only if element is empty
        if pd.isna(element):
            continue

        # Look up mapping values (Excel is 1-based)
        excel_row = row + 1
        financial_type_id = financial_type_row_mapping.get(excel_row)
        financial_metric_id = financial_metric_row_mapping.get(excel_row)
        financial_submetric_id = financial_submetric_row_mapping.get(excel_row)

        # Convert float IDs to integers if they exist
        financial_type_id = int(financial_type_id) if pd.notna(financial_type_id) else None
        financial_metric_id = int(financial_metric_id) if pd.notna(financial_metric_id) else None
        financial_submetric_id = int(financial_submetric_id) if pd.notna(financial_submetric_id) else None

        result_data.append({
            'date': f"{year}-01-01",  # Use the passed month_num
            'budget_value': budget,  # Keep null values
            'financial_type_id': financial_type_id,
            'financial_metric_id': financial_metric_id,
            'financial_submetric_id': financial_submetric_id,
            'version_id': version_id
        })

    # Convert to DataFrame
    result_df = pd.DataFrame(result_data)

    return result_df

def insert_budget_data_to_db(df, table_name, version_id):
    """Insert budget data into the specified database table"""
    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        total_records = len(df)
        processed_records = 0

        print(f"\nStarting database insertion for {total_records} records into {table_name} (version_id: {version_id})...")
        for idx, row in df.iterrows():
            print(f"Processing record {processed_records + 1}/{total_records}: "
                  f"type_id={row['financial_type_id']}, "
                  f"metric_id={row['financial_metric_id']}, "
                  f"submetric_id={row['financial_submetric_id']}, "
                  f"date={row['date']}, "
                  f"budget_value={row['budget_value']}, "
                  f"version_id={version_id}")

            # Insert/update the data
            upsert_financial_data(
                cur=cur,
                table_name=table_name,
                type_id=row['financial_type_id'] if pd.notna(row['financial_type_id']) else None,
                metric_id=row['financial_metric_id'] if pd.notna(row['financial_metric_id']) else None,
                submetric_id=row['financial_submetric_id'] if pd.notna(row['financial_submetric_id']) else None,
                date_value=row['date'],
                budget_value=row['budget_value'] if pd.notna(row['budget_value']) else None,
                version_id=version_id
            )
            processed_records += 1

        conn.commit()
        print(f"\n✅ Successfully processed {processed_records}/{total_records} records")

    except Exception as e:
        print(f"\n❌ Error inserting budget data into {table_name}: {e}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()

def main():
    try:
        # Parse command line arguments
        args = parse_arguments()
        month_year = args.month_year
        version_id = get_version_id_by_name(args.version_id)
        #version_id = args.version_id
        file_name = args.file_name

        # Validate month_year (ensure it's 6 digits)
        if len(month_year) != 6 or not month_year.isdigit():
            raise ValueError("month_year must be in MMYYYY format (e.g., 032025)")

        month = month_year[:2]
        year = month_year[2:]

        # Construct MinIO object path
        object_path = f"{year}/{year}01/{file_name}"

        # Initialize MinIO service and read Excel file
        minio_service = get_minio_service()
        df = minio_service.read_excel(object_name=object_path, sheet_name='Mobile Money', header=None)

        # Process monthly data for the specified month
        output_path_monthly = f"{os.path.dirname(__file__)}/output/mobile_money_budget_{month_year}_{version_id}.csv"
        os.makedirs(os.path.dirname(output_path_monthly), exist_ok=True)

        print(f"\nExtracting monthly data for {year}-{month}-01 (version_id: {version_id})...")
        monthly_budget_data = extract_budget_data_for_month(df, month, year, version_id)

        if monthly_budget_data.empty:
            print(f"No monthly data found for {year}-{month}-01")
        else:
            # Convert float IDs to integers in the DataFrame
            for col in ['financial_type_id', 'financial_metric_id', 'financial_submetric_id']:
                monthly_budget_data[col] = monthly_budget_data[col].astype('Int64')

            # Save monthly data to CSV
            monthly_budget_data.to_csv(output_path_monthly, index=False)
            print(f"\nSaved {len(monthly_budget_data)} monthly records to {output_path_monthly}")

            # Insert monthly data into database
            insert_budget_data_to_db(monthly_budget_data, "financial_metrics_data", version_id)

        # Process annual data
        output_path_annual = f"{os.path.dirname(__file__)}/output/mobile_money_annual_budget_{year}_{version_id}.csv"

        print(f"\nExtracting annual budget data for {year} (version_id: {version_id})...")
        annual_budget_data = extract_annual_budget_data(df, year, version_id, month)

        if annual_budget_data.empty:
            print(f"No annual data found for year {year}")
        else:
            # Convert float IDs to integers in the DataFrame
            for col in ['financial_type_id', 'financial_metric_id', 'financial_submetric_id']:
                annual_budget_data[col] = annual_budget_data[col].astype('Int64')

            # Save annual data to CSV
            annual_budget_data.to_csv(output_path_annual, index=False)
            print(f"\nSaved {len(annual_budget_data)} annual records to {output_path_annual}")

            # Insert annual data into database
            insert_budget_data_to_db(annual_budget_data, "financial_annual_data", version_id)

        print("✅ All Mobile Money budget operations completed successfully!")

    except ValueError as ve:
        print(f"❌ Validation error: {str(ve)}")
    except Exception as e:
        print(f"❌ Fatal error in main process: {str(e)}")

if __name__ == "__main__":
    main()
