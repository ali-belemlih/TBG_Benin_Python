import os
import sys
import time
import argparse
import logging
from datetime import datetime, timedelta
import pandas as pd
from helpers.logger import setup_logging
from helpers.turnover_utils.db_utils import upsert_data_to_db  # Updated import

# Base paths
base_path = "benin_turnover_reporting"
input_file = os.path.join(base_path, "input", "Reporting CA journalier_  Avril 2025.xlsx")
output_dir = os.path.join(base_path, "output")

# Database table columns
DB_COLUMNS = [
    "jour", "date", "observations", "ca_global", "ca_voix_classique", "ca_forfaits_voix",
    "ca_pass_bonus", "ca_data", "moov_sayaa", "autres", "rechargement", "ratio_conso_rechargement",
    "parc_abonnes_global", "parc_journalier", "gross_add", "churn", "net_add", "reconnexions",
    "ratio_reconnexions_gross_add", "parc_attache", "parc_global_data", "parc_attache_data",
    "parc_data_2g", "parc_data_3g", "parc_data_4g", "trafic_voix", "trafic_data_ko"
]

# Columns that define uniqueness for upsert (date is likely the primary key)
CONFLICT_COLUMNS = ["date"]  # Added conflict columns for upsert

# Mapping of Excel columns to database columns
COLUMN_MAPPING = {
    "Jour": "jour",
    "Observations": "observations",
    "Date": "date",
    "CA global": "ca_global",
    "CA voix classique": "ca_voix_classique",
    "CA Forfaits voix": "ca_forfaits_voix",
    "CA Pass Bonus": "ca_pass_bonus",
    "CA data": "ca_data",
    "Moov Sayaa": "moov_sayaa",
    "Autres": "autres",
    "Rechargement": "rechargement",
    "Ratio Conso/Rechargement": "ratio_conso_rechargement",
    "Parc attaché  ": "parc_attache",
    "Parc abonnés global": "parc_abonnes_global",
    "Parc journalier": "parc_journalier",
    "Gross add": "gross_add",
    "Churn": "churn",
    "Net Add": "net_add",
    "Reconnexions": "reconnexions",
    "Ratio Reconnexions/ Gross add": "ratio_reconnexions_gross_add",
    "Parc global data": "parc_global_data",
    "Parc attaché data": "parc_attache_data",
    "Parc data 2G": "parc_data_2g",
    "Parc data 3G": "parc_data_3g",
    "Parc data 4G": "parc_data_4g",
    "Trafic voix": "trafic_voix",
    "Trafic data (Ko)": "trafic_data_ko"
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

def parse_date_input(date_str: str) -> datetime | None:
    """
    Convert DDMMYYYY string to datetime object.
    """
    try:
        return datetime.strptime(date_str, "%d%m%Y")
    except ValueError:
        logging.error(f"Invalid date format. Expected DDMMYYYY, got '{date_str}'")
        return None

def extract_data(file_path: str, sheet_name: str, target_date: datetime = None) -> pd.DataFrame | None:
    """
    Extract data from the specified Excel sheet, optionally filtered by date.
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

        # Filter by date if specified
        if target_date is not None:
            df = df[df[date_column].dt.date == target_date.date()]
            if df.empty:
                logging.warning(f"No records found for {target_date.strftime('%d/%m/%Y')} in sheet '{sheet_name}'")
                return None

        # Create a new DataFrame with all DB columns initialized to None
        result_df = pd.DataFrame(columns=DB_COLUMNS)

        # Map Excel columns to database columns
        for excel_col, db_col in COLUMN_MAPPING.items():
            if excel_col in df.columns:
                result_df[db_col] = df[excel_col]
            else:
                logging.warning(f"Column '{excel_col}' not found in Excel data, setting '{db_col}' to None")
                result_df[db_col] = None

        return result_df

    except Exception as error:
        logging.error(f"Failed processing sheet '{sheet_name}': {error}")
        return None

def process_single_date(target_date: datetime):
    """
    Process data for a single date - creates separate CSV and upserts into DB
    """
    output_filename = f"donnees_brutes_{target_date.strftime('%Y%m%d')}.csv"
    output_path = os.path.join(output_dir, output_filename)
    sheets_to_process = {"Données brutes": output_path}

    logging.info(f"Starting processing for file: {input_file}, date: {target_date.strftime('%d/%m/%Y')}")

    start_total = time.time()
    results = {}

    for sheet_name, output_csv in sheets_to_process.items():
        df = extract_data(input_file, sheet_name, target_date)
        if df is not None:
            # Save to CSV
            df.to_csv(output_csv, index=False)
            logging.info(f"Saved {len(df)} rows from '{sheet_name}' to '{output_csv}'")

            # Upsert data into database
            success = upsert_data_to_db(df, 'revenue_raw_data', DB_COLUMNS, CONFLICT_COLUMNS)
            if success:
                logging.info(f"Data for sheet '{sheet_name}' successfully upserted into database")
            else:
                logging.error(f"Failed to upsert data for sheet '{sheet_name}' into database")
            results[sheet_name] = df

    total_duration = time.time() - start_total
    logging.info(f"Completed processing in {total_duration:.2f} seconds")

    success_count = sum(df is not None for df in results.values())
    logging.info(f"Successfully processed {success_count}/{len(sheets_to_process)} sheet(s)")

    return results

def process_all_dates():
    """
    Process all dates - creates a single CSV and upserts data into DB date by date
    """
    output_filename = "donnees_brutes_complete.csv"
    output_path = os.path.join(output_dir, output_filename)
    sheets_to_process = {"Données brutes": output_path}

    logging.info(f"Starting processing for all dates in file: {input_file}")

    start_total = time.time()
    results = {}

    for sheet_name, output_csv in sheets_to_process.items():
        df = extract_data(input_file, sheet_name)
        if df is not None:
            # Save complete data to CSV
            df.to_csv(output_csv, index=False)
            logging.info(f"Saved {len(df)} rows from '{sheet_name}' to '{output_csv}'")

            # Process each date separately for DB upsertion
            date_column = "date"
            if date_column not in df.columns:
                logging.error(f"Date column not found in the processed data")
                return None

            unique_dates = df[date_column].dt.date.unique()
            logging.info(f"Found {len(unique_dates)} unique dates in the data")

            for date in unique_dates:
                date_df = df[df[date_column].dt.date == date]
                if not date_df.empty:
                    logging.info(f"Processing data for date: {date.strftime('%d/%m/%Y')}")
                    success = upsert_data_to_db(date_df, 'revenue_raw_data', DB_COLUMNS, CONFLICT_COLUMNS)
                    if success:
                        logging.info(f"Data for {date.strftime('%d/%m/%Y')} successfully upserted into database")
                    else:
                        logging.error(f"Failed to upsert data for {date.strftime('%d/%m/%Y')} into database")

            results[sheet_name] = df

    total_duration = time.time() - start_total
    logging.info(f"Completed processing in {total_duration:.2f} seconds")

    success_count = sum(df is not None for df in results.values())
    logging.info(f"Successfully processed {success_count}/{len(sheets_to_process)} sheet(s)")

    return results

def main():
    parser = argparse.ArgumentParser(description="Extract data from Excel and upsert into DB.")
    parser.add_argument("date", type=str, nargs='?', help="Optional: Date in DDMMYYYY format", default=None)

    args = parser.parse_args()

    os.makedirs(output_dir, exist_ok=True)
    setup_logging(base_path)

    if args.date:
        target_date = parse_date_input(args.date)
        if not target_date:
            sys.exit(1)
        process_single_date(target_date)
    else:
        process_all_dates()

if __name__ == "__main__":
    main()