import os
import pandas as pd
from datetime import datetime
from openpyxl.reader.excel import load_workbook
from helpers.parse_arg import parse_arguments
from helpers.export_utils import read_json_mapping, normalize_month_key, get_version_for_tbg_export, excel_column_name, date_row_updater,header_row_updater
from helpers.db_utils import get_db_engine
from openpyxl.utils import get_column_letter, column_index_from_string
def monthly_column_hider(ws, sheet_name):
    if sheet_name in ["Data Mobile"]:
        ws.column_dimensions['AP'].hidden = False
        ws.column_dimensions['BO'].hidden = False
        print(f"::::::: HIDING COLUMN AO IN SHEET : {sheet_name} ::::::: hidden={ws.column_dimensions['AP'].hidden} ::::::")
        print(f"::::::: HIDING COLUMN AO IN SHEET : {sheet_name} ::::::: hidden={ws.column_dimensions['BO'].hidden} ::::::")
        return
    ws.column_dimensions['AO'].hidden = False
    ws.column_dimensions['BN'].hidden = False
    print(f"::::::: HIDING COLUMN AO IN SHEET : {sheet_name} ::::::: hidden={ws.column_dimensions['AO'].hidden} ::::::")
    print(f"::::::: HIDING COLUMN AO IN SHEET : {sheet_name} ::::::: hidden={ws.column_dimensions['BN'].hidden} ::::::")

def actual_column_hider(ws,flag):
    actual_cols = ['DA', 'DB', 'DC']
    acutual_percent_cols = ['DF', 'DG','DH']
    for i,(col,pct_col) in enumerate(zip(actual_cols, acutual_percent_cols), start = 1):
        if i!= flag:
            print(f"=========hiding columns {col, pct_col} for i , flag {i,flag} ===========")
            ws.column_dimensions[col].hidden = True
            ws.column_dimensions[pct_col].hidden = True
            print(f"::::::::::::::: COLUMN SUCCESSFULLY MADE HIDDEN = {col, pct_col}::::::::::::::")
            print(f"::::::::::::::: COLUMN SUCCESSFULLY MADE HIDDEN = {ws.column_dimensions[pct_col].hidden, ws.column_dimensions[pct_col].hidden }::::::::::::::")

def hide_non_required_annual_cols(ws, month_param):
    if 4<=int(month_param)<=5:
        actual_column_hider(ws,flag = 1)
    elif 6<=int(month_param)<=8:
        actual_column_hider(ws,flag = 2)
    elif 9<=int(month_param)<=12:
        actual_column_hider(ws,flag = 3)

def add_date_in_cover(wb,month, year):
    formatted_date = f"01/{month}/{year}"
    formatted_date = datetime.strptime(formatted_date, "%d/%m/%Y")
    if "Cover" in wb.sheetnames:
        cover_ws = wb["Cover"]
        cover_ws["E17"].value = formatted_date
    else:
        raise ValueError("Worksheet 'cover' not found in the template")

def update_actual_percent_header(ws, year_param, sheet_name):
    """
    Updates Actu 1/2/3 percentage header cells (DF, DG, DH) with year_param - 1.
    - Most sheets: row 5, format "Actu N /\n{year-1} (%)"
    - Data Mobile: row 4, format "{year-1}" only
    - Mobile Money: skipped (no annual section)
    """

    if sheet_name == "Mobile Money":
        return

    last_year = str(int(year_param) - 1)
    cols = ["DF", "DG", "DH"]

    if sheet_name == "Data Mobile":
        row = 4
        for col in cols:
            ws[f"{col}{row}"] = last_year
            print(f"✅ [{sheet_name}] Updated {col}{row} → '{last_year}'")
    else:
        row = 5
        for i, col in enumerate(cols, start=1):
            value = f"Actu {i} /\n{last_year} (%)"
            ws[f"{col}{row}"] = value
            print(f"✅ [{sheet_name}] Updated {col}{row} → '{value}'")

def update_actual_percent_header(ws, year_param, sheet_name):
    """
    Updates Actu 1/2/3 percentage header cells (DF, DG, DH) with year_param - 1.
    - Most sheets: row 5, format "Actu N /\n{year-1} (%)"
    - Data Mobile: row 4, format "{year-1}" only
    - Mobile Money: skipped (no annual section)
    """

    if sheet_name == "Mobile Money":
        return

    last_year = str(int(year_param) - 1)
    cols = ["DF", "DG", "DH"]

    if sheet_name == "Data Mobile":
        row = 4
        for col in cols:
            ws[f"{col}{row}"] = last_year
            print(f"✅ [{sheet_name}] Updated {col}{row} → '{last_year}'")
    else:
        row = 5
        for i, col in enumerate(cols, start=1):
            value = f"Actu {i} /\n{last_year} (%)"
            ws[f"{col}{row}"] = value
            print(f"✅ [{sheet_name}] Updated {col}{row} → '{value}'")
def update_budget_percent_header(ws, year_param, sheet_name):
    """
    Updates budget percentage header cell based on sheet name.
    For most sheets: 'Bud / {year_param - 1} (%)'
    For Mobile Money & Data Mobile: Just '{year_param - 1}'
    """

    # Sheet configurations: {sheet_name: {"cell": cell_address, "format": format_type}}
    SHEET_CONFIG = {
        "P&L conso": {"cell": "DE5", "format": "full"},
        "Opex Consolidés": {"cell": "DE5", "format": "full"},
        "CA Mobile": {"cell": "DE5", "format": "full"},
        "Marge Mobile": {"cell": "DE5", "format": "full"},
        "Trafic mobile": {"cell": "DE5", "format": "full"},
        "Parc Mobile": {"cell": "DE5", "format": "full"},
        "Parc Mobile ": {"cell": "DE5", "format": "full"},  # With trailing space
        "Indicateurs Mobile": {"cell": "DE5", "format": "full"},
        "Capex Consolidés": {"cell": "DE5", "format": "full"},
        "Cash conso": {"cell": "DE5", "format": "full"},
        "Mobile Money": {"cell": "DD4", "format": "year_only"},
        "Data Mobile": {"cell": "DE4", "format": "year_only"},
    }

    if sheet_name not in SHEET_CONFIG:
        print(f"⚠️ Sheet '{sheet_name}' not configured for budget percent header update")
        return

    config = SHEET_CONFIG[sheet_name]
    cell_address = config["cell"]
    format_type = config["format"]

    last_year = str(int(year_param) - 1)

    cell = ws[cell_address]
    old_value = cell.value

    if format_type == "full":
        cell.value = f"Bud /\n{last_year} (%)"
    elif format_type == "year_only":
        cell.value = last_year

    print(f"✅ [{sheet_name}] Updated {cell_address}: '{old_value}' → '{cell.value}'")
def update_year_headers_from_mapping_multiline(ws, month_data, year_param, sheet_name=None):

    current_year = str(int(year_param))
    last_year = str(int(year_param) - 1)

    sheets_with_last_year_only_evol = {"Data Mobile", "Mobile Money"}

    for month_key, details in month_data.items():
        start_col = details["start_col"]
        header_row = details["header_row_index"]
        sequence = details["sequence"]

        start_col_index = column_index_from_string(start_col)

        for i, col_type in enumerate(sequence):
            col_letter = excel_column_name(start_col_index + i)
            cell = ws[f"{col_letter}{header_row}"]

            if cell.value is None:
                continue

            text = str(cell.value)
            lines = text.split("\n")
            label = lines[1] if len(lines) > 1 else text  # e.g. "Réel", "Budget", "% Evol"

            if col_type == "real_value":
                if sheet_name in sheets_with_last_year_only_evol:
                    cell.value = f"{current_year}"
                else:
                    cell.value = f"{current_year}\nRéel"

            elif col_type == "budget_value":
                if sheet_name in sheets_with_last_year_only_evol:
                    cell.value = f"{current_year}"
                else:
                    cell.value = f"{current_year}\nBudget"

            elif col_type == "last_year_real_value":
                if sheet_name in sheets_with_last_year_only_evol:
                    cell.value = f"{last_year}"
                else:
                    cell.value = f"{last_year}\nRéel"


            elif col_type.startswith("actual"):
                if sheet_name == "Data Mobile":
                    cell.value = f"{current_year}"
                elif sheet_name == "Mobile Money":
                    cell.value = f"{label}"
                else:
                    cell.value = f"{current_year}\n{label}"

            elif col_type == "evol_percent":
                # YOUR CONFIRMED RULE:
                if sheet_name in sheets_with_last_year_only_evol:
                    cell.value = f"{last_year}"

def update_annual_headers_from_mapping_multiline(ws, annual_data, year_param, sheet_name=None):

    current_year = str(int(year_param))
    last_year = str(int(year_param) - 1)

    sheets_with_last_year_only_evol = {"Data Mobile", "Mobile Money"}

    start_col = annual_data["annual"]["start_col"]
    header_row = annual_data["annual"]["header_row_index"]
    sequence = annual_data["annual"]["sequence"]

    start_col_index = column_index_from_string(start_col)

    for i, col_type in enumerate(sequence):
        col_letter = excel_column_name(start_col_index + i)
        cell = ws[f"{col_letter}{header_row}"]

        if cell.value is None:
            continue

        text = str(cell.value)
        lines = text.split("\n")
        label = lines[1] if len(lines) > 1 else text

        if col_type == "real_value":
            if sheet_name in sheets_with_last_year_only_evol:
                cell.value = f"{current_year}"
            else:
                cell.value = f"{current_year}\nRéel"

        elif col_type == "budget_value":
            if sheet_name in sheets_with_last_year_only_evol:
                cell.value = f"{current_year}"
            else:
                cell.value = f"{current_year}\nBudget"

        elif col_type == "last_year_real_value":
            if sheet_name in sheets_with_last_year_only_evol:
                cell.value = f"{last_year}"
            else:
                cell.value = f"{last_year}\nRéel"

        elif col_type.startswith("actual"):
            if sheet_name in sheets_with_last_year_only_evol:
                cell.value = f"{last_year}"
            else:
                cell.value = f"{current_year}\n{label}"

        elif col_type == "evol_percent":
            # YOUR CONFIRMED RULE:
            if sheet_name in sheets_with_last_year_only_evol:
                cell.value = f"{last_year}"


def hide_non_required_month_data(ws,month_data,month_param):
    for month_name, month_details in month_data.items():
        start_col = month_details["start_col"]
        sequence_length = len(month_details["sequence"])
        start_col_index = sum((ord(c) - 64) * (26 ** j) for j, c in enumerate(reversed(start_col)))

        if month_details["date"][5:7] != month_param:
            for offset in range(sequence_length+1):
                col_letter = excel_column_name(start_col_index + offset)
                ws.column_dimensions[col_letter].hidden = True

def get_value_based_on_sheet(sheet_name, row_number, row, mapped_column):
    value = row.get(mapped_column)
    if value is None:
        return None

    ecart_cols = ['ecart_actual1_value', 'ecart_actual2_value', 'ecart_actual3_value', 'ecart_budget']

    if sheet_name == 'P&L conso' and row_number in (42, 56):
        if mapped_column in ecart_cols:
            return value * 100

    if sheet_name == 'P&L conso' and row_number in (42, 56):
        if mapped_column in ecart_cols:
            return value * 100

    if sheet_name == 'Marge brute Mobile' and row_number == 61:
        if mapped_column in ecart_cols:
            return value * 100

    return value

def build_query(file_path, replacements):
    with open(file_path, "r") as file:
        query = file.read()
        for key, value in replacements.items():
            query = query.replace(key, value)
    return query

def excel_column_name(index):
    result = ""
    while index > 0:
        index, remainder = divmod(index - 1, 26)
        result = chr(65 + remainder) + result
    return result

def header_row_updater_annual(ws, sequence, start_col, year_param, header_row_index):
    start_col_index = column_index_from_string(start_col)
    total_cols_to_check = len(sequence) + 20  # Add buffer to handle overflow columns
    TEMP_TAG = "___TEMP_YEAR___"

    prev_year = str(int(year_param) - 1)       # e.g., 2024 if year_param = 2025
    prev_prev_year = str(int(year_param) - 2)  # e.g., 2023 if year_param = 2025

    for offset in range(total_cols_to_check):
        col_index = start_col_index + offset
        col_letter = excel_column_name(col_index)
        cell_address = f"{col_letter}{header_row_index}"
        cell_value = ws[cell_address].value

        if cell_value is not None:
            original_value = str(cell_value)

            # Step-by-step replacement with safety
            updated_value = original_value.replace(prev_prev_year, TEMP_TAG)
            updated_value = updated_value.replace(prev_year, year_param)
            updated_value = updated_value.replace(TEMP_TAG, prev_year)

            # Write back, keeping int format if needed
            if isinstance(cell_value, int) and updated_value.isdigit():
                ws[cell_address] = int(updated_value)
            else:
                ws[cell_address] = updated_value

def write_data_to_sheet(ws, data, config_data, sequence, start_col, sheet_name):
    for _, row in data.iterrows():
        category = row.get("type_name") or row.get("financial_type_name")
        metric_name = row.get("metric_name")
        submetric_name = row.get("submetric_name")

        row_number = None
        if metric_name and metric_name != "N/A":
            metrics = config_data.get(category, {}).get("metrics", {})
            if submetric_name and submetric_name != "N/A":
                row_number = metrics.get(metric_name, {}).get("submetrics", {}).get(submetric_name)
            else:
                row_number = metrics.get(metric_name, {}).get("row_number")
        elif category in config_data:
            row_number = config_data[category].get("row_number")

        if not row_number:
            continue

        start_col_index = sum((ord(c) - 64) * (26 ** j) for j, c in enumerate(reversed(start_col)))
        for i, col in enumerate(sequence):
            col_letter = excel_column_name(start_col_index + i)
            cell_address = f"{col_letter}{row_number}"
            if col in row:
                ws[cell_address] = get_value_based_on_sheet(sheet_name, row_number, row, col)

def update_actual_column(ws, sheet_name,month_param, year_param,cell_address):
    if sheet_name == "Data Mobile":
        ws[f"{cell_address[0]}4"] = "Actu2"
        ws[f"{cell_address[1]}4"] = "Actu3"
    elif sheet_name == "Mobile Money":
            ws[f"{cell_address[0]}4"] = "Actu2"
            ws[f"{cell_address[1]}4"] = "Actu3"
    else:
            ws[f"{cell_address[0]}5"] = f"Ecart /\nActu2"
            ws[f"{cell_address[1]}5"] = "Ecart /\nActu3"
def update_actual_column_name(ws, sheet_name, month_param, year_param):
    if sheet_name == "Data Mobile":
        update_actual_column(ws, sheet_name,month_param,year_param, ["AR","BQ"])
    elif sheet_name == "Mobile Money":
        update_actual_column(ws, sheet_name,month_param,year_param, ["AQ","BP"])
    else:
        update_actual_column(ws,sheet_name,month_param,year_param, ["AQ","BP"])

def process_sheet(sheet_data, wb, engine, year, month_year, base_path, version_id):
    sheet_name = sheet_data["sheet_name"].strip()
    sheet_name_in_excel = {
        "Marge brute Mobile": "Marge Mobile",
        "Parc Mobile": "Parc Mobile ",
    }.get(sheet_name, sheet_name)

    print(f"Processing sheet: {sheet_name_in_excel}")

    if sheet_name_in_excel not in wb.sheetnames:
        raise ValueError(f"Worksheet {sheet_name_in_excel} not found in the template")

    ws = wb[sheet_name_in_excel]
    ws.column_dimensions['C'].hidden = True
    config_data = read_json_mapping(sheet_data["sheet_mapping_path"])
    month_data = read_json_mapping(sheet_data["month_mapping_path"])
    annual_data = read_json_mapping(sheet_data["annual_mapping_path"])
    month_param = month_year[:2]  # For example, "01" for January
    year_param = month_year[2:]  # For example, "2025"

    for month_key, details in month_data.items():
        date_row_updater(ws,details, year_param)
    for month_key, details in month_data.items():
        sequence = details['sequence']
        start_col = details["start_col"]
        header_row_index = details["header_row_index"]
        header_row_updater(ws, sequence,start_col, year_param, header_row_index)
    update_year_headers_from_mapping_multiline(ws, month_data, year_param, sheet_name_in_excel)
    if sheet_name == "Cash conso":
        sheet_name = "Cash Conso"
    for month_key, details in month_data.items():
        loop_month = details['date'][5:7]
        if int(loop_month) > int(month_param):
            continue
        normalized_month = normalize_month_key(month_key)
        version = get_version_for_tbg_export(normalized_month, month_param, year_param, version_id, engine)

        date_to_process = f"{year_param}-{details['date'][5:7]}-{details['date'][8:]}"
        start_col = details["start_col"]
        sequence = details["sequence"]

        for query_file in [
            "financial_type_query.sql",
            "financial_metric_query.sql",
            "financial_submetric_query.sql"]:
            query_path = os.path.join(base_path, "sql_files", query_file)
            query = build_query(query_path, {
                "{date_param}": date_to_process,
                "{sheet_name_param}": sheet_name,
                "{version_id}": str(version),
            })
            df = pd.read_sql_query(query, engine)
            # df["real_value"] = df["effective_real_value"]
            write_data_to_sheet(ws, df, config_data, sequence, start_col, sheet_name)
    # Annual queries
    start_col = annual_data["annual"]["start_col"]
    sequence = annual_data["annual"]["sequence"]
    header_row_index = annual_data["annual"]["header_row_index"]
    header_row_updater_annual(ws, sequence,start_col, year_param, header_row_index)
    update_annual_headers_from_mapping_multiline(
        ws,
        annual_data,
        year_param,
        sheet_name_in_excel
    )

    for query_file in [
        "annual_financial_type_query.sql",
        "annual_financial_metric_query.sql",
        "annual_financial_submetrics_query.sql"
    ]:
        query_path = os.path.join(base_path, "sql_files", query_file)
        query = build_query(query_path, {
            "{sheet_name_param}": sheet_name,
            "{version_id}": str(version_id),
        })
        df = pd.read_sql_query(query, engine)
        # df["real_value"] = df["effective_real_value"]
        write_data_to_sheet(ws, df, config_data, sequence, start_col, sheet_name)

    if sheet_name == "Mobile Money":
        start_col = column_index_from_string("CY")
        end_col = column_index_from_string("DG")

        for col in range(start_col, end_col + 1):
            col_letter = get_column_letter(col)
            ws.column_dimensions[col_letter].hidden = True
    monthly_column_hider(ws, sheet_name)
    hide_non_required_month_data(ws, month_data, month_param)
    hide_non_required_annual_cols(ws, month_param)
    update_actual_column_name(ws, sheet_name, month_param, year_param)
    update_budget_percent_header(ws, year_param, sheet_name_in_excel)
    update_actual_percent_header(ws, year_param, sheet_name_in_excel)



if __name__ == "__main__":
    args = parse_arguments()
    month_year = args.month_year
    version_id = args.version_id
    month, year = month_year[:2], month_year[2:]

    base_path = "benin_tbg_export"
    output_path = f"{base_path}/outputs/tbg_report_{month_year}.xlsx"

    wb = load_workbook(f"{base_path}/template/tbg-template.xlsx", keep_links=False)
    sheets_to_process = read_json_mapping(f"{base_path}/configs/config.json")
    engine = get_db_engine()

    for sheet in sheets_to_process:
        process_sheet(sheet, wb, engine, year, month_year, base_path, version_id)
    add_date_in_cover(wb,month, year)

    wb.save(output_path)
    print(f"Export completed and saved to: {output_path}")
