import os
import sys
import pandas as pd
from services.minio_factory import get_minio_service
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from helpers.parse_arg import parse_arguments
from helpers.db_utils import get_db_connection, upsert_financial_data, get_version_id_by_name
from .mapping_utils import get_financial_hierarchy

# Parse command line arguments
args = parse_arguments()
target_month = args.month_year[:2]  # Extract MM from MMYYYY
year = args.month_year[2:]   # Extract YYYY from MMYYYY
file_name = args.file_name
version_id = get_version_id_by_name(args.version_id)
object_path = f"{year}/{year}01/{file_name}"

minio_service = get_minio_service()
df = minio_service.read_excel(object_name=object_path, header=None)

zero_index = 1  # Row numbers in required rows and mapping is based on 1-indexed but in loop below it is 0-indexed

# Identify key rows and columns
start_row = 5 - zero_index  # Data starts from this row (0-indexed)
category_column = 0  # Column A (financial_categories.name)
type_metric_submetric_column = 2  # Column C (financial_types, financial_metric, financial_submetric)
data_columns = list(range(3, 15 + 1))  # Columns D to P (financial data)
month_row = 2 - zero_index  # Row 2 (Jan to Dec, Cumu, ANNUEL)

# Extract month/year information
months = df.iloc[month_row, data_columns].tolist()

# Convert month names to their respective numbers (using French month names)
month_map = {
    "Janvier": "01", "Février": "02", "Mars": "03", "Avril": "04", "Mai": "05", "Juin": "06",
    "Juillet": "07", "Août": "08", "Septembre": "09", "Octobre": "10", "Novembre": "11", "Décembre": "12",
    "ANNUEL": "ANNUEL"  # Include special cases
}

# Reverse mapping from month number to French name
month_num_to_name = {
    "01": "Janvier", "02": "Février", "03": "Mars", "04": "Avril", "05": "Mai", "06": "Juin",
    "07": "Juillet", "08": "Août", "09": "Septembre", "10": "Octobre", "11": "Novembre", "12": "Décembre"
}

def process_data():
    """
    Process the data for the specified month and generate a CSV file.
    Returns a list of dictionaries containing the processed data.
    """
    processed_data = []
    target_month_name = month_num_to_name.get(target_month)

    # Initialize CSV file
    csv_file = f"financial_data_{target_month}{year}.csv"
    with open(csv_file, 'w') as f:
        f.write("category_name,table_name,type_id,metric_id,submetric_id,date_value,budget_value,version_id\n")

    current_category = None
    for index, row in df.iterrows():
        if index < start_row:
            continue  # Skip headers

        category_name = row[category_column]
        type_metric_submetric_name = row[type_metric_submetric_column]

        # Skip empty rows
        if pd.isna(category_name) or pd.isna(type_metric_submetric_name):
            continue

        type_metric_submetric_name = type_metric_submetric_name.strip()

        # If "END" is encountered, reset category
        if str(category_name).strip().upper() == "END":
            current_category = None
            continue

        # If a new category appears, update the current category
        if not pd.isna(category_name):
            current_category = category_name.strip()

        # Skip Opex Consolidés
        if current_category == "Opex Consolidés":
            continue

        # Get financial hierarchy
        type_id, metric_id, submetric_id = get_financial_hierarchy(row, current_category)

        if type_id is None and metric_id is None and submetric_id is None:
            continue

        # Process financial data only for the target month
        for col_index, budget_value in zip(data_columns, row[data_columns]):
            month_label = months[col_index - data_columns[0]]

            # Skip if not the target month (unless it's ANNUEL)
            if month_label != target_month_name and month_label != "ANNUEL":
                continue

            # Determine the correct table
            if month_label == "ANNUEL":
                table_name = "financial_annual_data"
                date_value = f"{year}-01-01"  # Annual assumes January 1st
            else:
                table_name = "financial_metrics_data"
                date_value = f"{year}-{target_month}-01"

            # Apply specific business rules
            # if current_category == "Marge brute Mobile" and type_id == 28:
            #     budget_value /= 100
            # elif current_category == "P&L consolidé":
            #     if metric_id == 88:
            #         budget_value /= 100
            #     elif submetric_id == 14:
            #         budget_value /= 100
            #     elif submetric_id == 18:
            #         budget_value /= 100
            #     elif submetric_id == 20:
            #         budget_value /= 100

            if pd.isna(budget_value):
                budget_value = None

            # Prepare data record
            record = {
                "category_name": current_category,
                "table_name": table_name,
                "type_id": type_id,
                "metric_id": metric_id,
                "submetric_id": submetric_id,
                "date_value": date_value,
                "budget_value": budget_value,
                "version_id": version_id
            }
            processed_data.append(record)

            # Append to CSV file
            with open(csv_file, 'a') as f:
                csv_row = f"{current_category},{table_name},{type_id},{metric_id},{submetric_id},{date_value},{budget_value},{version_id}\n"
                f.write(csv_row)

    print(f"Data processing completed! CSV file generated: {csv_file}")
    return processed_data

def insert_data_to_db(processed_data):
    """
    Insert processed data into the database
    """
    if not processed_data:
        print("No data to insert!")
        return

    conn = get_db_connection()
    cur = conn.cursor()

    try:
        for record in processed_data:
            upsert_financial_data(
                cur,
                record["table_name"],
                record["type_id"],
                record["metric_id"],
                record["submetric_id"],
                record["date_value"],
                budget_value=record["budget_value"],
                version_id=record["version_id"]
            )
        conn.commit()
        print(f"Successfully inserted {len(processed_data)} records into the database!")
    except Exception as e:
        conn.rollback()
        print(f"Error inserting data: {str(e)}")
    finally:
        cur.close()
        conn.close()

# Main execution
if __name__ == "__main__":
    # Process data and generate CSV
    data_to_insert = process_data()

    # Insert data into database
    insert_data_to_db(data_to_insert)
