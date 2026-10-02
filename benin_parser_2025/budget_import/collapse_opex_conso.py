import os
import pandas as pd
from helpers.db_utils import get_db_connection, upsert_collapse_financial_data, get_version_id_by_name
from helpers.parse_arg import parse_arguments
from .mapping.collapse_OPEX_CONSO_mapping import collapse_type_row_mapping
from services.minio_factory import get_minio_service


BASE_PATH = os.path.dirname(__file__)
SHEET_NAME = "TBG"


def generate_budget_dataframe(object_path, month, year, version_id):
    """Generate budget dataframes for monthly and annual data from Excel using mapping"""
    try:
        # Initialize MinIO service
        minio_service = get_minio_service()

        # Read Excel from MinIO with no header (we'll access columns/rows by index)
        df = minio_service.read_excel(object_name=object_path, sheet_name=SHEET_NAME, header=None)

        monthly_output_rows = []
        annual_output_rows = []
        excel_month_col = int(month)  # Convert to int for column index (1-12)
        excel_annual_col = 13  # Column N (0-based index for annual data)

        for row_num, entity_id in collapse_type_row_mapping.items():
            excel_row_idx = row_num - 1  # Adjust for 0-index
            row_name = df.iloc[excel_row_idx, 0]

            # If name is missing, keep as empty string (still include)
            entity_type = row_name if pd.notna(row_name) else ""

            # Get monthly budget value
            monthly_budget_value = None
            if excel_month_col < len(df.columns):
                cell_value = df.iloc[excel_row_idx, excel_month_col]
                # Check if value is not NaN and not a literal dash
                if pd.notna(cell_value):
                    # Convert to string to check for literal '-'
                    cell_str = str(cell_value).strip()
                    if cell_str != '-':
                        try:
                            monthly_budget_value = float(cell_value)
                        except (ValueError, TypeError):
                            monthly_budget_value = None

            monthly_output_rows.append({
                "entity_id": entity_id,
                "entity_type": "type",
                "date": f"{year}-{month}-01",
                "budget_value": monthly_budget_value,
                "version_id": version_id
            })

            # Get annual budget value from column N
            annual_budget_value = None
            if excel_annual_col < len(df.columns):
                cell_value = df.iloc[excel_row_idx, excel_annual_col]
                # Check if value is not NaN and not a literal dash
                if pd.notna(cell_value):
                    # Convert to string to check for literal '-'
                    cell_str = str(cell_value).strip()
                    if cell_str != '-':
                        try:
                            annual_budget_value = float(cell_value)
                        except (ValueError, TypeError):
                            annual_budget_value = None

            annual_output_rows.append({
                "entity_id": entity_id,
                "entity_type": "type",
                "date": f"{year}-01-01",  # Use the passed month for annual data
                "budget_value": annual_budget_value,
                "version_id": version_id
            })

        # Convert to DataFrames
        monthly_df = pd.DataFrame(monthly_output_rows)
        annual_df = pd.DataFrame(annual_output_rows)

        # Ensure date column is datetime
        monthly_df["date"] = pd.to_datetime(monthly_df["date"])
        if not annual_df.empty:
            annual_df["date"] = pd.to_datetime(annual_df["date"])

        return monthly_df, annual_df

    except Exception as e:
        print(f"Error generating budget data: {str(e)}")
        raise


def generate_csv(dataframe, month_year, version_id, is_annual=False):
    """Generate CSV file from the dataframe with month_year and version_id in filename"""
    try:
        suffix = "annual" if is_annual else month_year
        output_file = f"{BASE_PATH}/output/OPEX_CONSO_budget_{suffix}_{version_id}.csv"
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        dataframe.to_csv(output_file, index=False)
        print(f"✅ CSV file generated: {output_file}")
        return True
    except Exception as e:
        print(f"❌ Error generating CSV file: {str(e)}")
        return False


def insert_data_to_db(monthly_df, annual_df, version_id):
    """Insert monthly and annual data into database"""
    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # Process monthly data
        monthly_processed_count = 0
        monthly_inserted_count = 0
        monthly_null_count = 0

        for _, row in monthly_df.iterrows():
            budget_value = row['budget_value']
            if pd.isna(budget_value):
                budget_value = None

            print(f"Inserting monthly -> entity_id: {row['entity_id']}, budget_value: {budget_value}, version_id: {version_id}")
            upsert_collapse_financial_data(
                cur,
                table_name="collapse_monthly_data",
                entity_id=row['entity_id'],
                entity_type=row['entity_type'],
                date_value=row['date'],
                budget_value=budget_value,
                version_id=version_id
            )

            monthly_processed_count += 1
            if budget_value is None:
                monthly_null_count += 1
            else:
                monthly_inserted_count += 1

        # Process annual data
        annual_processed_count = 0
        annual_inserted_count = 0
        annual_null_count = 0

        if not annual_df.empty:
            for _, row in annual_df.iterrows():
                budget_value = row['budget_value']
                if pd.isna(budget_value):
                    budget_value = None

                print(f"Inserting annual -> entity_id: {row['entity_id']}, budget_value: {budget_value}, version_id: {version_id}")
                upsert_collapse_financial_data(
                    cur,
                    table_name="collapse_annual_data",
                    entity_id=row['entity_id'],
                    entity_type=row['entity_type'],
                    date_value=row['date'],
                    budget_value=budget_value,
                    version_id=version_id
                )

                annual_processed_count += 1
                if budget_value is None:
                    annual_null_count += 1
                else:
                    annual_inserted_count += 1

        conn.commit()
        print(f"✅ Database operation completed:")
        print(f"   - Monthly records processed: {monthly_processed_count}")
        print(f"   - Monthly records with values inserted: {monthly_inserted_count}")
        print(f"   - Monthly records with NULL values: {monthly_null_count}")
        if not annual_df.empty:
            print(f"   - Annual records processed: {annual_processed_count}")
            print(f"   - Annual records with values inserted: {annual_inserted_count}")
            print(f"   - Annual records with NULL values: {annual_null_count}")

        return True

    except Exception as e:
        print(f"❌ Error inserting data into database: {str(e)}")
        if conn:
            conn.rollback()
        return False
    finally:
        if conn:
            conn.close()


def main():
    try:
        # Parse command line arguments
        args = parse_arguments()
        month_year = args.month_year
        file_name = args.file_name
        month = month_year[:2]
        year = month_year[2:]

        # Validate month_year (ensure it's 6 digits)
        if len(month_year) != 6 or not month_year.isdigit():
            raise ValueError("month_year must be in MMYYYY format (e.g., 032025)")

        version_id = get_version_id_by_name(args.version_id)
        #version_id = args.version_id
        object_path = f"{year}/{year}01/{file_name}"

        print(f"⏳ Processing data for month {month}, year {year}, version_id {version_id}...")

        # Step 1: Generate the budget dataframes for monthly and annual data
        monthly_df, annual_df = generate_budget_dataframe(object_path, month, year, version_id)

        # Step 2: Generate CSV files
        if not generate_csv(monthly_df, month_year, version_id, is_annual=False):
            return
        if not annual_df.empty and not generate_csv(annual_df, f"{year}", version_id, is_annual=True):
            return

        # Step 3: Insert data into database
        if not insert_data_to_db(monthly_df, annual_df, version_id):
            return

        print("✅ All operations completed successfully!")

    except ValueError as ve:
        print(f"❌ Validation error: {str(ve)}")
    except Exception as e:
        print(f"❌ Fatal error in main process: {str(e)}")


if __name__ == "__main__":
    main()
