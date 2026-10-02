import os
import pandas as pd
from helpers.db_utils import get_db_connection, upsert_financial_data, get_version_id_by_name
from helpers.parse_arg import parse_arguments
from services.minio_factory import get_minio_service
from .mapping.data_mobile_mapping import financial_type_row_mapping, financial_metric_row_mapping

def format_value(val):
    if isinstance(val, float) and val.is_integer():
        return int(val)
    return val

def extract_monthly_data(df, year, version_id, month_column_map, target_month):
    budget_data = pd.DataFrame()

    # Only process the target month
    if target_month in month_column_map:
        col_index = month_column_map[target_month]
        month_budget_data = df.iloc[4:, col_index].reset_index(drop=True)

        month_budget_df = pd.DataFrame({
            'date': f"{year}-{target_month}-01",
            'budget_value': month_budget_data,
            'version_id': version_id
        })

        month_budget_df['excel_row'] = month_budget_df.index + 5

        month_budget_df['financial_type_id'] = month_budget_df['excel_row'].map(financial_type_row_mapping)
        month_budget_df['financial_metric_id'] = month_budget_df['excel_row'].map(financial_metric_row_mapping)
        month_budget_df['financial_submetric_id'] = None

        month_budget_df = month_budget_df.apply(lambda x: x.map(format_value) if x.dtype == 'float64' else x)
        month_budget_df = month_budget_df.drop(columns=['excel_row'])

        budget_data = pd.concat([budget_data, month_budget_df], ignore_index=True)

    return budget_data

def extract_annual_data(df, year, version_id, target_month):
    annual_budget_data = df.iloc[4:, 15].reset_index(drop=True)

    annual_budget_df = pd.DataFrame({
        'date': f"{year}-01-01",
        'budget_value': annual_budget_data,
        'version_id': version_id
    })

    annual_budget_df['excel_row'] = annual_budget_df.index + 5

    annual_budget_df['financial_type_id'] = annual_budget_df['excel_row'].map(financial_type_row_mapping)
    annual_budget_df['financial_metric_id'] = annual_budget_df['excel_row'].map(financial_metric_row_mapping)
    annual_budget_df['financial_submetric_id'] = None

    annual_budget_df = annual_budget_df.apply(lambda x: x.map(format_value) if x.dtype == 'float64' else x)
    annual_budget_df = annual_budget_df.drop(columns=['excel_row'])

    return annual_budget_df

def extract_data_mobile_budget(object_path, year, version_id, target_month):
    minio_service = get_minio_service()
    df = minio_service.read_excel(object_name=object_path, sheet_name='Data Mobile ', header=None)

    month_column_map = {
        '01': 3, '02': 4, '03': 5, '04': 6, '05': 7, '06': 8,
        '07': 9, '08': 10, '09': 11, '10': 12, '11': 13, '12': 14,
    }

    monthly_data = extract_monthly_data(df, year, version_id, month_column_map, target_month)
    annual_data = extract_annual_data(df, year, version_id, target_month)

    return monthly_data, annual_data

def save_monthly_to_db(monthly_df, version_id):
    conn = get_db_connection()
    cur = conn.cursor()

    try:
        skipped_rows = 0
        processed_rows = 0

        for _, row in monthly_df.iterrows():
            if pd.isna(row['financial_type_id']) and pd.isna(row['financial_metric_id']):
                skipped_rows += 1
                print(f"⏭️ Skipping monthly row (missing type_id and metric_id): {row.to_dict()}")
                continue

            type_id = int(row['financial_type_id']) if pd.notna(row['financial_type_id']) else None
            metric_id = int(row['financial_metric_id']) if pd.notna(row['financial_metric_id']) else None
            submetric_id = None

            print(f"📥 Inserting monthly data - Date: {row['date']}, Type ID: {type_id}, "
                  f"Metric ID: {metric_id}, Value: {row['budget_value']}, version_id: {version_id}")

            upsert_financial_data(
                cur=cur,
                table_name="financial_metrics_data",
                type_id=type_id,
                metric_id=metric_id,
                submetric_id=submetric_id,
                date_value=row['date'],
                budget_value=row['budget_value'],
                version_id=version_id
            )
            processed_rows += 1

        print(f"✅ Monthly data successfully saved to database (Processed: {processed_rows}, Skipped: {skipped_rows})")
        conn.commit()
    except Exception as e:
        conn.rollback()
        print(f"❌ Error saving monthly data to database: {str(e)}")
    finally:
        cur.close()
        conn.close()

def save_annual_to_db(annual_df, version_id):
    if annual_df.empty:
        print("⚠️ No annual data to save (not processing January)")
        return

    conn = get_db_connection()
    cur = conn.cursor()

    try:
        skipped_rows_annual = 0
        processed_rows_annual = 0

        for _, row in annual_df.iterrows():
            if pd.isna(row['financial_type_id']) and pd.isna(row['financial_metric_id']):
                skipped_rows_annual += 1
                print(f"⏭️ Skipping annual row (missing type_id and metric_id): {row.to_dict()}")
                continue

            type_id = int(row['financial_type_id']) if pd.notna(row['financial_type_id']) else None
            metric_id = int(row['financial_metric_id']) if pd.notna(row['financial_metric_id']) else None
            submetric_id = None

            print(f"📥 Inserting annual data - Date: {row['date']}, Type ID: {type_id}, "
                  f"Metric ID: {metric_id}, Value: {row['budget_value']}, version_id: {version_id}")

            upsert_financial_data(
                cur=cur,
                table_name="financial_annual_data",
                type_id=type_id,
                metric_id=metric_id,
                submetric_id=submetric_id,
                date_value=row['date'],
                budget_value=row['budget_value'],
                version_id=version_id
            )
            processed_rows_annual += 1

        print(f"✅ Annual data successfully saved to database (Processed: {processed_rows_annual}, Skipped: {skipped_rows_annual})")
        conn.commit()
    except Exception as e:
        conn.rollback()
        print(f"❌ Error saving annual data to database: {str(e)}")
    finally:
        cur.close()
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

        object_path = f"{year}/{year}01/{file_name}"

        print(f"⏳ Processing DATA MOBILE budget for month {month}, year {year}, version_id {version_id}...")

        # Extract data
        data_mobile_budget_df, annual_budget_df = extract_data_mobile_budget(object_path, year, version_id, month)

        # Save to CSV
        base_path = os.path.dirname(__file__)
        output_path = f"{base_path}/output"
        os.makedirs(output_path, exist_ok=True)

        monthly_csv_path = f"{output_path}/data_mobile_budget_{month_year}_{version_id}.csv"
        data_mobile_budget_df.to_csv(monthly_csv_path, index=False)
        print(f"✅ DATA MOBILE monthly budget extracted and saved to {monthly_csv_path}")

        # Only save annual CSV
        if not annual_budget_df.empty:
            annual_csv_path = f"{output_path}/data_mobile_annual_budget_{year}_{version_id}.csv"
            annual_budget_df.to_csv(annual_csv_path, index=False)
            print(f"✅ DATA MOBILE annual budget extracted and saved to {annual_csv_path}")

        # Save to database
        save_monthly_to_db(data_mobile_budget_df, version_id)
        save_annual_to_db(annual_budget_df, version_id)

        print("✅ All DATA MOBILE budget operations completed successfully!")

    except ValueError as ve:
        print(f"❌ Validation error: {str(ve)}")
    except Exception as e:
        print(f"❌ Fatal error in main process: {str(e)}")

if __name__ == "__main__":
    main()
