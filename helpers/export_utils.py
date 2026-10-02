import json
import openpyxl
import pandas as pd
from openpyxl.styles import Alignment
from openpyxl.utils import column_index_from_string, get_column_letter
from helpers.db_utils import get_default_version_id
from datetime import datetime, date as dt_date

def read_json_mapping(json_mapping_file_path):
    """Reads a JSON file and returns the parsed data."""
    with open(json_mapping_file_path, "r", encoding="utf-8") as file:
        return json.load(file)

def clean_sequence_data(month_mapping):
    """Fixes incorrect nested list structure in 'sequence' for any months."""
    for month, details in month_mapping.items():
        if isinstance(details["sequence"], list) and len(details["sequence"]) == 1 and isinstance(details["sequence"][0], list):
            month_mapping[month]["sequence"] = details["sequence"][0]  # Flatten the list
    return month_mapping

def create_excel_workbook():
    """Creates a new Excel workbook and returns the worksheet."""
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "opex_consolidate"
    return wb, ws

def populate_headers(ws, month_mapping):
    """Populates month names in Row 2, merges cells, centers text, and adds corresponding column headers in Row 3."""
    for month, details in month_mapping.items():
        start_col = details["start_col"]
        col_index = column_index_from_string(start_col)  # Convert letter to column index
        sequence_length = len(details["sequence"])  # Number of columns to span

        # Compute the end column for merging
        end_col_index = col_index + sequence_length - 1

        # Merge the header row for the month
        ws.merge_cells(start_row=2, start_column=col_index, end_row=2, end_column=end_col_index)
        cell = ws.cell(row=2, column=col_index, value=month.capitalize())

        # Center align the merged cell text
        cell.alignment = Alignment(horizontal="center", vertical="center")

        # Populate sequence headers below the month name (Row 3)
        for i, header in enumerate(details["sequence"]):
            ws.cell(row=3, column=col_index + i, value=header)

def populate_category_data(ws, config_data_for_row):
    """Populates Column B with categories and submetrics."""
    for category, details in config_data_for_row.items():
        row_num = details["row_number"]
        ws[f"B{row_num}"] = category  # Write main category

        # Write submetrics (indented)
        for submetric, sub_row in details["submetrics"].items():
            ws[f"B{sub_row}"] = f"  - {submetric}"

def save_excel(wb, output_path):
    """Saves the Excel workbook to the given path."""
    wb.save(output_path)
    print(f"Excel file '{output_path}' created successfully!")

def create_row_report(config_data_for_row, month_data_for_cols, output_excel_path="expenses.xlsx"):
    """Main function to generate the Excel file with category data and month headers."""
    month_data_for_cols = clean_sequence_data(month_data_for_cols)  # Fix sequence structure
    wb, ws = create_excel_workbook()  # Create Excel file

    populate_headers(ws, month_data_for_cols)
    populate_category_data(ws, config_data_for_row)

    save_excel(wb, output_excel_path)

def excel_column_name(n):
    """Convert a 1-based column index to an Excel-style column name."""
    result = ""
    while n > 0:
        n, remainder = divmod(n - 1, 26)
        result = chr(65 + remainder) + result
    return result

def normalize_month_key(month):
    if not month:
        return None
    normalized = str(month).strip().lower()
    if normalized.isdigit():
        return normalized.zfill(2)
    month_map = {
        "jan": "01", "feb": "02", "mar": "03", "apr": "04",
        "may": "05", "jun": "06", "jul": "07", "aug": "08",
        "sep": "09", "oct": "10", "nov": "11", "dec": "12"
    }
    return month_map.get(normalized)

def get_version_for_tbg_export(normalized_month, month_param, year_param, version_id, engine):
    if not normalized_month:
        print("⚠️ Skipping invalid month.")
        return None

    if int(normalized_month) < int(month_param):
        version = get_default_version_id(normalized_month, year_param, engine)
        print(f"✅ Using latest version {version} for {normalized_month}/{year_param}")
        return version

    elif int(normalized_month) == int(month_param):
        final_version = version_id or get_default_version_id(normalized_month, year_param, engine)
        print(f"✅ Using version {final_version} for {normalized_month}/{year_param}")
        return final_version

    print(f"ℹ️ Skipping future month: {normalized_month}/{year_param}")
    return None

def normalize_key(key):
    return " ".join(str(key).replace("’", "'").strip().split()).lower()

def date_row_updater(ws, details, year_param):
    date_row_number = details["date_row"]

    # Pick the right column key
    col_key = details.get("start_col") or details.get("sheet_col")
    cell = ws[col_key][date_row_number - 1]
    cell_value = cell.value

    if isinstance(cell_value, (datetime, dt_date)):
        # Replace just the year while keeping month/day
        new_date = cell_value.replace(year=int(year_param))
    elif isinstance(cell_value, int):
        # Treat plain int as year → fallback to Jan 1st of that year
        new_date = datetime(int(year_param), 1, 1)
    elif isinstance(cell_value, str) and cell_value.isdigit():
        # Handle string year like "2025"
        new_date = datetime(int(cell_value), 1, 1).replace(year=int(year_param))
    else:
        raise ValueError(f"Unsupported date type: {type(cell_value)} ({cell_value})")

    cell.value = new_date

def header_row_updater(ws, sequence, start_col, year_param, header_row_index):
    start_col_index = sum((ord(c) - 64) * (26 ** j) for j, c in enumerate(reversed(start_col)))

    TEMP_TAG = "___TEMP_YEAR___"
    prev_year = str(int(year_param) - 1)       # e.g., 2024 if year_param is 2025
    prev_prev_year = str(int(year_param) - 2)  # e.g., 2023 if year_param is 2025

    for i, _ in enumerate(sequence):
        col_letter = excel_column_name(start_col_index + i)
        cell_address = f"{col_letter}{header_row_index}"
        cell_value = ws[cell_address].value

        if cell_value is not None:
            original_value = str(cell_value)

            # Apply replacements with temp tag
            updated_value = original_value.replace(prev_prev_year, TEMP_TAG)
            updated_value = updated_value.replace(prev_year, year_param)
            updated_value = updated_value.replace(TEMP_TAG, prev_year)

            # If it was originally an int and updated_value is digit-only, cast it back to int
            if isinstance(cell_value, int) and updated_value.isdigit():
                ws[cell_address] = int(updated_value)
            else:
                ws[cell_address] = updated_value
