import os
import pandas as pd
from openpyxl.reader.excel import load_workbook
from helpers.parse_arg import parse_arguments
from helpers.export_utils import read_json_mapping, normalize_month_key, get_version_for_tbg_export, date_row_updater
from helpers.db_utils import get_db_engine


def build_query_from_file(file_path, replacements):
    with open(file_path, "r") as f:
        query = f.read()
        for key, value in replacements.items():
            query = query.replace(key, value)
    return query

def write_value_to_excel(ws, config_data, row, col_letter):
    resource_type = row.get("resource_type_name")
    resource_subtype = row.get("resource_subtype_name")
    value = row.get("value")

    resource_config = config_data.get(resource_type)
    if not resource_config:
        return

    row_number = resource_config.get("row_number")

    if resource_subtype and "resource_subtype_name" in resource_config:
        subtype_mapping = resource_config["resource_subtype_name"]
        row_number = subtype_mapping.get(resource_subtype, row_number)

    if row_number:
        cell_address = f"{col_letter}{row_number}"
        ws[cell_address] = value

def process_sheet(sheet_config, wb, engine, year_param, month_param, version_id, sql_file_path):
    sheet_name = sheet_config["sheet_name"]
    sheet_mapping_path = sheet_config["sheet_mapping_path"]
    month_mapping_path = sheet_config["month_mapping_path"]

    config_data = read_json_mapping(sheet_mapping_path)
    month_mappings = read_json_mapping(month_mapping_path)

    if sheet_name in wb.sheetnames:
        ws = wb[sheet_name]
    else:
        raise ValueError(f"Worksheet '{sheet_name}' not found in the template.")

    for month_key, details in month_mappings.items():
        normalized_month = normalize_month_key(month_key)
        target_month = int(month_param)
        version = get_version_for_tbg_export(normalized_month, month_param, year_param, version_id, engine)

        replacements = {
            "{month_param}": month_key.capitalize(),
            "{year_param}": year_param,
            "{version_id}": str(version),
        }

        query = build_query_from_file(sql_file_path, replacements)
        df = pd.read_sql_query(query, engine)

        print(f"  -> Pulled {len(df)} rows for {month_key} (version {version_id})")

        col_letter = details.get("sheet_col", "A")
        for _, row in df.iterrows():
            write_value_to_excel(ws, config_data, row, col_letter)
        date_row_updater(ws,details, year_param)

def main():
    args = parse_arguments()
    month_year = args.month_year
    version_id = args.version_id
    month_param, year_param = month_year[:2], month_year[2:]

    base_path = "benin_tbg_export"
    output_path = f"{base_path}/outputs/tbg_report_{month_year}.xlsx"
    sql_file_path = f"{base_path}/sql_files/rh_sql_query.sql"

    wb = load_workbook(output_path)
    sheets_to_process = read_json_mapping(f"{base_path}/configs/rh_config.json")
    engine = get_db_engine()

    try:
        for sheet_config in sheets_to_process:
            print(f"Processing sheet '{sheet_config['sheet_name']}'")
            process_sheet(sheet_config, wb, engine, year_param, month_param, version_id, sql_file_path)

        wb.save(output_path)
        print(f"\n✅ Financial report generated: {output_path}")

    except Exception as e:
        print(f"[ERROR] {str(e)}")

if __name__ == "__main__":
    main()
