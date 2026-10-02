import os
import pandas as pd
from openpyxl.reader.excel import load_workbook
from helpers.parse_arg import parse_arguments
from helpers.export_utils import read_json_mapping, normalize_month_key, get_version_for_tbg_export
from helpers.db_utils import get_db_engine


def build_query(file_path, replacements):
    with open(file_path, "r") as file:
        query = file.read()
        for key, value in replacements.items():
            query = query.replace(key, value)
    return query


def write_impact_data_to_sheet(ws, config_data, data_df, month_data):
    for _, row in data_df.iterrows():
        standard_name = row.get("standard_name")
        value = row.get("value")
        month = row.get("month")

        row_number = config_data.get(standard_name, {}).get("row_number")
        col_letter = month_data.get(month, {}).get("sheet_col")

        if row_number and col_letter:
            cell_address = f"{col_letter}{row_number}"
            try:
                ws[cell_address] = value
            except Exception as e:
                print(f"Error writing to Excel at {cell_address}: {e}")


def process_impact_sheet(sheet_data, wb, engine, month_param, year_param, version_id, sql_file_path):
    sheet_name = sheet_data["sheet_name"]
    sheet_mapping_path = sheet_data["sheet_mapping_path"]
    month_mapping_path = sheet_data["month_mapping_path"]

    print(f"Processing sheet '{sheet_name}'")

    if sheet_name not in wb.sheetnames:
        raise ValueError(f"Worksheet '{sheet_name}' not found in the template")

    ws = wb[sheet_name]
    config_data = read_json_mapping(sheet_mapping_path)
    month_data = read_json_mapping(month_mapping_path)

    for month_key, details in month_data.items():
        normalized_month = normalize_month_key(month_key)
        target_month = int(month_param)
        version = get_version_for_tbg_export(normalized_month, month_param, year_param, version_id, engine)

        replacements = {
            "{month_param}": month_key.capitalize(),
            "{year_param}": year_param,
            "{version_id}": str(version),
        }

        query = build_query(sql_file_path, replacements)
        df = pd.read_sql_query(query, engine)

        print(f"  -> Pulled {len(df)} rows for {month_key} (version {version_id})")

        write_impact_data_to_sheet(ws, config_data, df, month_data)


def main():
    args = parse_arguments()
    month_year = args.month_year
    version_id = args.version_id
    month_param, year_param = month_year[:2], month_year[2:]


    base_path = "benin_tbg_export"
    output_path = f"{base_path}/outputs/tbg_report_{month_year}.xlsx"
    sql_file_path = f"{base_path}/sql_files/impact_ifrs_query.sql"

    wb = load_workbook(output_path)
    sheets_to_process = read_json_mapping(f"{base_path}/configs/impact_config.json")
    engine = get_db_engine()

    try:
        for sheet in sheets_to_process:
            process_impact_sheet(sheet, wb, engine, month_param, year_param, version_id, sql_file_path)

        wb.save(output_path)
        print(f"✅ Financial report has been generated: {output_path}")

    except Exception as e:
        print(f"[ERROR] {str(e)}")


if __name__ == "__main__":
    main()
