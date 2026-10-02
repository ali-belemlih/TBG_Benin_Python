import os
import pandas as pd
from pathlib import Path
from io import BytesIO
import openpyxl
import json

from helpers.db_utils import (
    get_db_connection,
    upsert_financial_data,
    get_version_id_by_name,
    upsert_collapse_financial_data
)
from services.minio_factory import get_minio_service


def load_sheet_config(sheet_key):
    config_path = Path(__file__).resolve().parent / "configs" / "sheet_configs.json"
    with open(config_path, "r") as f:
        all_configs = json.load(f)
    return all_configs.get(sheet_key)


def process_financial_sheet(
    sheet,
    target_month,
    target_year,
    version_id,
    mappings,
    mode="monthly",
    output_prefix="sheet",
    custom_column_index=None,
    custom_month_column_map=None,
    category_fallback=False,
    start_row_offset=4
):
    df_raw = pd.DataFrame(sheet.values)
    # Determine the column index
    if mode == "monthly":
        default_map = {"04": 5, "05": 6, "06": 7}
        column_map = custom_month_column_map if custom_month_column_map else default_map
        column_index = column_map.get(target_month)
        if column_index is None:
            raise ValueError(f"Unsupported month: {target_month}")
    elif mode == "annual":
        column_index = custom_column_index if custom_column_index is not None else 14
    else:
        raise ValueError("Mode must be 'monthly' or 'annual'")

    data_rows = df_raw.iloc[start_row_offset:, :]
    df = pd.DataFrame()
    if category_fallback:
        df["category"] = data_rows.iloc[:, 0].fillna(data_rows.iloc[:, 1])  # A then B
    else:
        df["category"] = data_rows.iloc[:, 1]  # B
    df["actu1_value"] = data_rows.iloc[:, column_index]

    row_offset = start_row_offset + 1
    df = df.reset_index(drop=True)

    results = []
    for idx, row in df.iterrows():
        row_number = idx + row_offset
        category = str(row["category"]).strip() if pd.notna(row["category"]) else None
        value = row["actu1_value"]
        print(f"Fetched Value for row_number {row_number}: {value} & category: {category}")
        if not category:
            continue

        date_str = f"{target_year}-01-01" if mode == "annual" else f"{target_year}-{target_month}-01"

        result = {
            "Row Number": row_number,
            "financial_type_id": mappings["financial_type_row_mapping"].get(row_number),
            "financial_metric_id": mappings["financial_metric_row_mapping"].get(row_number),
            "financial_submetric_id": mappings["financial_submetric_row_mapping"].get(row_number),
            "entity_type": None,
            "entity_id": None,
            "actu1_value": value,
            "date": date_str,
            "version_id": version_id
        }

        collapse_types = mappings.get('collapse_types_mapping', {})
        collapse_categories = mappings.get('collapse_categories_mapping', {})
        collapse_subcategories = mappings.get('collapse_subcategories_mapping', {})

        if row_number in collapse_types:
            result["entity_type"] = "type"
            result["entity_id"] = collapse_types[row_number]
        elif row_number in collapse_categories:
            result["entity_type"] = "category"
            result["entity_id"] = collapse_categories[row_number]
        elif row_number in collapse_subcategories:
            result["entity_type"] = "subcategory"
            result["entity_id"] = collapse_subcategories[row_number]

        if not (
            result["financial_type_id"]
            or result["financial_metric_id"]
            or result["financial_submetric_id"]
            or result["entity_id"]
        ):
            continue

        results.append(result)

    df_result = pd.DataFrame(results)
    mode_tag = "annual" if mode == "annual" else "metrics"
    output_path = f"benin_parser_2025/actu1_import/actu1_{output_prefix}_{mode_tag}_{target_month}.csv"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df_result.to_csv(output_path, index=False)
    print(f"✅ CSV generated: {output_path}")
    return df_result


def insert_data_to_db(dataframe: pd.DataFrame, table_name: str, mode, actual_type):
    conn = get_db_connection()
    cur = conn.cursor()

    for _, row in dataframe.iterrows():
        type_id = None if pd.isna(row.get("financial_type_id")) else row["financial_type_id"]
        metric_id = None if pd.isna(row.get("financial_metric_id")) else row["financial_metric_id"]
        submetric_id = None if pd.isna(row.get("financial_submetric_id")) else row["financial_submetric_id"]
        value = None if pd.isna(row.get("actu1_value")) else row["actu1_value"]
        entity_type = None if pd.isna(row.get("entity_type")) else row["entity_type"]
        entity_id = None if pd.isna(row.get("entity_id")) else row["entity_id"]

           # 🧹 Clean and convert numeric strings like "249 080" → 249080.0
        if isinstance(value, str):
            value = value.replace(" ", "").replace(",", "")
            if value.strip() == "":
                value = None
            else:
                try:
                    value = float(value)
                except ValueError:
                    print(f"⚠️ Skipping invalid numeric value: {value}")
                    continue


        if any([type_id, metric_id, submetric_id]):
            upsert_financial_data(
                cur=cur,
                table_name=table_name,
                type_id=type_id,
                metric_id=metric_id,
                submetric_id=submetric_id,
                date_value=row["date"],
                 **{f"{actual_type}_value": value},
                version_id=row["version_id"],
                budget_value=None
            )
        elif entity_type and entity_id:
            collapse_table = "collapse_monthly_data" if mode == "monthly" else "collapse_annual_data"
            upsert_collapse_financial_data(
                cur,
                table_name=collapse_table,
                entity_id=entity_id,
                entity_type=entity_type,
                date_value=row["date"],
                 **{f"{actual_type}_value": value},
                version_id=row["version_id"]
            )

    conn.commit()
    cur.close()
    conn.close()
    print(f"✅ Data inserted into table: {table_name}")


def run(
    sheet_name,
    mappings,
    mode,
    args,
    output_prefix,
    db_table_name,
    custom_column_index=None,
    custom_month_column_map=None,
    category_fallback=False,
    start_row_offset=4
):
    target_month = args.month_year[:2]
    target_year = args.month_year[2:]
    version_id = get_version_id_by_name(args.version_id)
    file_name = args.file_name
    actual_type = args.actual_type
    month_map = {
        'actual1': 4,
        'actual2': 6,
        'actual3': 9
    }
    month = month_map.get(actual_type)
    if month is None:
        raise ValueError(f"Unsupported actual_type: {actual_type}")

    # The file is uploaded with the version being imported (e.g. 202606 for June),
    # so look there first, then fall back to the actual type's default folder.
    candidate_paths = list(dict.fromkeys([
        f"{target_year}/{target_year}{target_month}/{file_name}",
        f"{target_year}/{target_year}{month:02d}/{file_name}",
    ]))

    try:
        minio_service = get_minio_service()
        file_bytes = None
        for object_path in candidate_paths:
            print(f"📥 Fetching file from MinIO path: {object_path}")
            try:
                file_bytes = minio_service.get_file_bytes(object_name=object_path)
                break
            except Exception as e:
                print(f"⚠️ Not found at {object_path}: {e}")
        if file_bytes is None:
            raise FileNotFoundError(f"File not found in MinIO at any of: {candidate_paths}")

        wb = openpyxl.load_workbook(filename=BytesIO(file_bytes), data_only=True)
        sheet = wb[sheet_name]

        df = process_financial_sheet(
            sheet=sheet,
            target_month=target_month,
            target_year=target_year,
            version_id=version_id,
            mappings=mappings,
            mode=mode,
            output_prefix=output_prefix,
            custom_column_index=custom_column_index,
            custom_month_column_map=custom_month_column_map,
            category_fallback=category_fallback,
            start_row_offset=start_row_offset
        )

        if not df.empty:
            insert_data_to_db(df, db_table_name, mode, actual_type)

    except Exception as e:
        print(f"❌ Processing failed: {str(e)}")
        raise
