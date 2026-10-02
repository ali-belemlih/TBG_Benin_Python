import os
import pandas as pd
from helpers.db_utils import get_db_connection, upsert_collapse_financial_data, get_version_id_by_name
from helpers.parse_arg import parse_arguments
from services.minio_factory import get_minio_service
from benin_parser_2025.budget_import.mapping.collapse_CA_MOBILE_mapping import (
    collapse_types_row_mapping,
    collapse_categories_row_mapping,
    collapse_sub_categories_row_mapping
)

output_path = "benin_parser_2025/budget_import/output"

# Ensure output directory exists
os.makedirs(output_path, exist_ok=True)

zero_index = 1
# Identify key rows and columns
start_row = 5 - zero_index
category_column = 0
type_metric_submetric_column = 2
monthly_data_columns = list(range(3, 15))  # Columns D-O (Jan-Dec)
annual_data_column = 15  # Column P (ANNUEL)
month_row = 2 - zero_index
year_row = 3 - zero_index

# Month label to number mapping
month_map = {
    "Janvier": ("01", 3), "Février": ("02", 4), "Mars": ("03", 5),
    "Avril": ("04", 6), "Mai": ("05", 7), "Juin": ("06", 8),
    "Juillet": ("07", 9), "Août": ("08", 10), "Septembre": ("09", 11),
    "Octobre": ("10", 12), "Novembre": ("11", 13), "Décembre": ("12", 14)
}

# Reverse month map for looking up month names from numbers
reverse_month_map = {
    "01": "Janvier", "02": "Février", "03": "Mars", "04": "Avril",
    "05": "Mai", "06": "Juin", "07": "Juillet", "08": "Août",
    "09": "Septembre", "10": "Octobre", "11": "Novembre", "12": "Décembre"
}

def initialize_month_positions(df):
    """Initialize month positions from the dataframe."""
    months = df.iloc[month_row, monthly_data_columns].tolist()
    return {month_map[month][0]: (month_map[month][1], idx)
            for idx, month in enumerate(months) if month in month_map}

def get_financial_hierarchy_df(df, row_index):
    category_name = df.iloc[row_index, category_column]
    type_metric_submetric_name = df.iloc[row_index, type_metric_submetric_column]

    current_category = category_name.strip() if pd.notna(category_name) else None
    current_type_metric_submetric = type_metric_submetric_name.strip() if pd.notna(type_metric_submetric_name) else None

    return current_category, current_type_metric_submetric

def format_number(val):
    if pd.isna(val):
        return None
    try:
        val = float(val)
        if val.is_integer():
            return int(val)
        return float(val)
    except:
        return None

def process_and_insert_data(target_month, version_id, df, month_positions, target_year):
    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # Get the column index for the target month
        col_info = month_positions.get(target_month)
        if not col_info:
            raise ValueError(f"No data found for month: {target_month}")

        col_index, _ = col_info
        formatted_date = f"{target_year}-{target_month}-01"

        for index, row in df.iterrows():
            if index < start_row:
                continue

            current_category, current_type_metric_submetric = get_financial_hierarchy_df(df, index)

            if str(current_category).strip().upper() == "END" or pd.isna(current_category) or pd.isna(
                    current_type_metric_submetric):
                continue

            if str(current_category).strip().upper() == "CA MOBILE":
                updated_index = index + zero_index

                # Process monthly data
                monthly_col_value = row[col_index]
                if not isinstance(monthly_col_value, str) or (
                        'Budget' not in monthly_col_value and 'Actu' not in monthly_col_value):
                    monthly_value = format_number(monthly_col_value)

                    # Insert monthly data
                    if updated_index in collapse_types_row_mapping:
                        upsert_collapse_financial_data(
                            cur=cur,
                            table_name="collapse_monthly_data",
                            entity_id=collapse_types_row_mapping[updated_index],
                            entity_type="type",
                            date_value=formatted_date,
                            budget_value=monthly_value,
                            version_id=version_id
                        )
                    if updated_index in collapse_categories_row_mapping:
                        upsert_collapse_financial_data(
                            cur=cur,
                            table_name="collapse_monthly_data",
                            entity_id=collapse_categories_row_mapping[updated_index],
                            entity_type="category",
                            date_value=formatted_date,
                            budget_value=monthly_value,
                            version_id=version_id
                        )
                    if updated_index in collapse_sub_categories_row_mapping:
                        upsert_collapse_financial_data(
                            cur=cur,
                            table_name="collapse_monthly_data",
                            entity_id=collapse_sub_categories_row_mapping[updated_index],
                            entity_type="subcategory",
                            date_value=formatted_date,
                            budget_value=monthly_value,
                            version_id=version_id
                        )

                # Process annual data
                annual_col_value = row[annual_data_column]
                if not isinstance(annual_col_value, str) or (
                        'Budget' not in annual_col_value and 'Actu' not in annual_col_value):
                    annual_value = format_number(annual_col_value)

                    # Insert annual data
                    if updated_index in collapse_types_row_mapping:
                        upsert_collapse_financial_data(
                            cur=cur,
                            table_name="collapse_annual_data",
                            entity_id=collapse_types_row_mapping[updated_index],
                            entity_type="type",
                            date_value=f"{target_year}-01-01",
                            budget_value=annual_value,
                            version_id=version_id
                        )
                    if updated_index in collapse_categories_row_mapping:
                        upsert_collapse_financial_data(
                            cur=cur,
                            table_name="collapse_annual_data",
                            entity_id=collapse_categories_row_mapping[updated_index],
                            entity_type="category",
                            date_value=f"{target_year}-01-01",
                            budget_value=annual_value,
                            version_id=version_id
                        )
                    if updated_index in collapse_sub_categories_row_mapping:
                        upsert_collapse_financial_data(
                            cur=cur,
                            table_name="collapse_annual_data",
                            entity_id=collapse_sub_categories_row_mapping[updated_index],
                            entity_type="subcategory",
                            date_value=f"{target_year}-01-01",
                            budget_value=annual_value,
                            version_id=version_id
                        )

        conn.commit()
        print(f"✅ Data for {reverse_month_map[target_month]}-{target_year} (monthly and annual) successfully upserted")

    except Exception as e:
        print(f"Error: {e}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()

def generate_csv_files(target_month, version_id, df, month_positions, target_year):
    monthly_csv_data = []
    annual_csv_data = []

    # Get the column index for the target month
    col_info = month_positions.get(target_month)
    if not col_info:
        print(f"No data found for month: {target_month}")
        return

    col_index, _ = col_info
    formatted_date = f"{target_year}-{target_month}-01"

    for index, row in df.iterrows():
        if index < start_row:
            continue

        current_category, current_type_metric_submetric = get_financial_hierarchy_df(df, index)

        if str(current_category).strip().upper() == "END" or pd.isna(current_category) or pd.isna(
                current_type_metric_submetric):
            continue

        if str(current_category).strip().upper() == "CA MOBILE":
            updated_index = index + zero_index

            # Process monthly data
            monthly_col_value = row[col_index]
            if not isinstance(monthly_col_value, str) or (
                    'Budget' not in monthly_col_value and 'Actu' not in monthly_col_value):
                monthly_value = format_number(monthly_col_value)

                if updated_index in collapse_types_row_mapping:
                    monthly_csv_data.append({
                        "entity_id": collapse_types_row_mapping[updated_index],
                        "entity_type": "type",
                        "date": formatted_date,
                        "budget_value": monthly_value,
                        "version_id": version_id
                    })
                if updated_index in collapse_categories_row_mapping:
                    monthly_csv_data.append({
                        "entity_id": collapse_categories_row_mapping[updated_index],
                        "entity_type": "category",
                        "date": formatted_date,
                        "budget_value": monthly_value,
                        "version_id": version_id
                    })
                if updated_index in collapse_sub_categories_row_mapping:
                    monthly_csv_data.append({
                        "entity_id": collapse_sub_categories_row_mapping[updated_index],
                        "entity_type": "subcategory",
                        "date": formatted_date,
                        "budget_value": monthly_value,
                        "version_id": version_id
                    })

            # Process annual data
            annual_col_value = row[annual_data_column]
            if not isinstance(annual_col_value, str) or (
                    'Budget' not in annual_col_value and 'Actu' not in annual_col_value):
                annual_value = format_number(annual_col_value)

                if updated_index in collapse_types_row_mapping:
                    annual_csv_data.append({
                        "entity_id": collapse_types_row_mapping[updated_index],
                        "entity_type": "type",
                        "date": formatted_date,
                        "budget_value": annual_value,
                        "version_id": version_id
                    })
                if updated_index in collapse_categories_row_mapping:
                    annual_csv_data.append({
                        "entity_id": collapse_categories_row_mapping[updated_index],
                        "entity_type": "category",
                        "date": formatted_date,
                        "budget_value": annual_value,
                        "version_id": version_id
                    })
                if updated_index in collapse_sub_categories_row_mapping:
                    annual_csv_data.append({
                        "entity_id": collapse_sub_categories_row_mapping[updated_index],
                        "entity_type": "subcategory",
                        "date": formatted_date,
                        "budget_value": annual_value,
                        "version_id": version_id
                    })

    # Generate monthly CSV
    if monthly_csv_data:
        df_monthly_csv = pd.DataFrame(monthly_csv_data)
        monthly_output_csv_path = f'{output_path}/CA_Mobile_budget_{target_month}_{target_year}.csv'
        df_monthly_csv.to_csv(monthly_output_csv_path, index=False)
        print(f"✅ Monthly CSV file for {reverse_month_map[target_month]}-{target_year} generated at: {monthly_output_csv_path}")
    else:
        print(f"⚠️ No monthly data found for {reverse_month_map[target_month]}-{target_year}")

    # Generate annual CSV
    if annual_csv_data:
        df_annual_csv = pd.DataFrame(annual_csv_data)
        annual_output_csv_path = f'{output_path}/CA_Mobile_budget_annual_{target_year}.csv'
        df_annual_csv.to_csv(annual_output_csv_path, index=False)
        print(f"✅ Annual CSV file for {reverse_month_map[target_month]}-{target_year} generated at: {annual_output_csv_path}")
    else:
        print(f"⚠️ No annual data found for {reverse_month_map[target_month]}-{target_year}")

if __name__ == "__main__":
    args = parse_arguments()
    target_month = args.month_year[:2]  # Extract MM from MMYYYY
    target_year = args.month_year[2:]   # Extract YYYY from MMYYYY
    version_id = get_version_id_by_name(args.version_id)
    #version_id = args.version_id
    file_name = args.file_name

    object_path = f"{target_year}/{target_year}01/{file_name}"

    minio_service = get_minio_service()
    df = minio_service.read_excel(object_name=object_path, header=None)

    # Initialize month positions after loading the dataframe
    month_positions = initialize_month_positions(df)

    print(f"\nProcessing data for {reverse_month_map[target_month]}-{target_year}...")

    # Process data only for the specified month
    generate_csv_files(target_month, version_id, df, month_positions, target_year)
    process_and_insert_data(target_month, version_id, df, month_positions, target_year)
