import argparse
import os
import pandas as pd
import logging
from datetime import datetime, timedelta
from helpers.logger import setup_logging
from helpers.turnover_utils.db_utils import upsert_data_to_db

# Base paths
base_path = "benin_turnover_reporting"
input_file = os.path.join(base_path, "input", "Reporting CA journalier_  Avril 2025.xlsx")
output_dir = os.path.join(base_path, "outpust")

# Database table columns
DB_COLUMNS = ["id", "date", "ttc", "ht"]
CONFLICT_COLUMNS = ["date"]

# Mapping of Excel columns to database columns
COLUMN_MAPPING = {
    "Date": "date",
    "TTC": "ttc",
    "HT": "ht"
}

def find_header_row(file_path: str, sheet_name: str) -> int:
    """
    Detect the first row with at least 3 non-NaN values to consider as header.
    """
    try:
        preview = pd.read_excel(file_path, sheet_name=sheet_name, nrows=10, header=None)
        for index, row in preview.iterrows():
            if row.notna().sum() >= 3:
                return index
        logging.warning(f"No header row found in sheet '{sheet_name}', defaulting to row 0")
        return 0
    except Exception as e:
        logging.error(f"Error finding header row in '{sheet_name}': {e}")
        return 0

def excel_date_to_datetime(excel_date) -> datetime:
    """
    Convert Excel serial date or pandas Timestamp to Python datetime.
    Excel dates start from 1899-12-30 (not 1900-01-01 due to Excel's leap year bug).
    """
    try:
        if isinstance(excel_date, pd.Timestamp):
            return excel_date.to_pydatetime()
        elif isinstance(excel_date, (int, float)):
            base_date = datetime(1899, 12, 30)
            return base_date + timedelta(days=excel_date)
        else:
            logging.error(f"Unsupported date type: {type(excel_date)}")
            return None
    except (ValueError, TypeError) as e:
        logging.error(f"Error converting Excel date {excel_date}: {e}")
        return None

def extract_data(file_path: str, sheet_name: str) -> pd.DataFrame | None:
    """
    Extract data from the specified Excel sheet.
    Returns DataFrame with mapped columns.
    """
    try:
        header_row = find_header_row(file_path, sheet_name)
        logging.info(f"Detected header at row {header_row + 1}")

        df = pd.read_excel(file_path, sheet_name=sheet_name, header=header_row)

        # Drop unnamed columns
        df = df.loc[:, ~df.columns.astype(str).str.startswith("Unnamed")]

        date_column = "Date"
        if date_column not in df.columns:
            logging.error(f"Date column '{date_column}' not found in sheet '{sheet_name}'")
            return None

        # Convert Excel serial dates to datetime
        df[date_column] = df[date_column].apply(excel_date_to_datetime)
        # Ensure Date column is datetime
        df[date_column] = pd.to_datetime(df[date_column], errors='coerce')

        # Drop rows with invalid dates
        df = df.dropna(subset=[date_column])

        # Create a new DataFrame with all DB columns initialized to None
        result_df = pd.DataFrame(columns=DB_COLUMNS)

        # Map Excel columns to database columns
        for excel_col, db_col in COLUMN_MAPPING.items():
            if excel_col in df.columns:
                result_df[db_col] = df[excel_col]
            else:
                logging.warning(f"Column '{excel_col}' not found in Excel data, setting '{db_col}' to None")
                result_df[db_col] = None

        # Generate id column (example: use row index + 1 as id)
        result_df['id'] = range(1, len(result_df) + 1)

        # Convert numeric columns to appropriate types
        result_df['id'] = pd.to_numeric(result_df['id'], errors='coerce').round().astype('Int64')
        result_df['ttc'] = pd.to_numeric(result_df['ttc'], errors='coerce').round().astype('Int64')
        result_df['ht'] = pd.to_numeric(result_df['ht'], errors='coerce').round().astype('Int64')

        return result_df

    except Exception as error:
        logging.error(f"Failed processing sheet '{sheet_name}': {error}")
        return None

def process_data(date_arg=None):
    """
    Process data from PAYGO DATA sheet, save to CSV, and upsert into DB.
    """
    sheet_name = "PAYGO DATA"
    output_filename = "paygo_data_extracted.csv"
    output_path = os.path.join(output_dir, output_filename)

    logging.info(f"Starting processing for file: {input_file}, sheet: {sheet_name}")
    if date_arg:
        logging.info(f"Date argument provided: {date_arg}")

    df = extract_data(input_file, sheet_name)
    if df is not None:
        # Save to CSV
        df.to_csv(output_path, index=False)
        logging.info(f"Saved {len(df)} rows from '{sheet_name}' to '{output_path}'")

        # Upsert data into database
        try:
            success = upsert_data_to_db(df, 'paygo_data', DB_COLUMNS, CONFLICT_COLUMNS)
            if success:
                logging.info(f"Data for sheet '{sheet_name}' successfully upserted into database")
            else:
                logging.error(f"Failed to upsert data for sheet '{sheet_name}' into database")
            return success
        except Exception as e:
            logging.error(f"Failed to upsert data for sheet '{sheet_name}': {e}")

    else:
        logging.error(f"No data extracted from sheet '{sheet_name}'")
        return False

def main():
    parser = argparse.ArgumentParser(description="Extract data from Excel and upsert into DB.")
    parser.add_argument("--date", type=str, help="Optional: Date in DDMMYYYY format", default=None)

    args = parser.parse_args()

    os.makedirs(output_dir, exist_ok=True)
    setup_logging(base_path)
    process_data(args.date)

if __name__ == "__main__":
    main()