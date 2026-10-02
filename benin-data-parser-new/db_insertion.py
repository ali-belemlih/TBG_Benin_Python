import argparse
from datetime import datetime
from typing import Dict

import pandas as pd
import os

from helpers.db_utils import get_db_engine


def parse_arguments():
    parser = argparse.ArgumentParser(description='Process data based on TBG Version!')
    parser.add_argument('version_id', type=str, help='Version to process (e.g., TBG_20250401_124714)')
    return parser.parse_args()


TABLE_COLUMNS = {
    "collapse_annual_data": [
        "entity_id", "entity_type", "date", "real_value", "budget_value",
        "actual1_value", "actual2_value", "actual3_value",
        "last_year_real_value", "version_id"
    ],
    "collapse_monthly_data": [
        "entity_id", "entity_type", "date", "real_value", "budget_value",
        "actual1_value", "actual2_value", "actual3_value",
        "last_year_real_value", "version_id"
    ],
    "collapse_cumul_data": [
        "entity_id", "entity_type", "date", "real_value", "budget_value",
        "actual1_value", "actual2_value", "actual3_value",
        "last_year_real_value", "version_id"
    ],
    "financial_annual_data": [
        "financial_type_id", "financial_metric_id", "financial_submetric_id", "date",
        "real_value", "budget_value", "actual1_value", "actual2_value", "actual3_value",
        "last_year_real_value", "parent_id", "version_id"
    ],
    "financial_metrics_data": [
        "financial_type_id", "financial_metric_id", "financial_submetric_id", "date",
        "real_value", "budget_value", "actual1_value", "actual2_value", "actual3_value",
        "last_year_real_value", "parent_id", "version_id"
    ],
    "financial_cumulative_data": [
        "financial_type_id", "financial_metric_id", "financial_submetric_id", "date",
        "real_value", "budget_value", "actual1_value", "actual2_value", "actual3_value",
        "last_year_real_value", "parent_id", "version_id"
    ],
}

def insert_to_table(df, table_name, engine):
    print(f"  Inserting into table: {table_name}")
    try:
        columns = TABLE_COLUMNS[table_name]

        # Add missing expected columns with None
        for col in columns:
            if col not in df.columns:
                df[col] = None

        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'], format='%m-%d-%Y', errors='coerce').dt.date

        df['created_at'] = datetime.now()
        df['updated_at'] = datetime.now()

        df_filtered = df[columns + ["created_at", "updated_at"]]
        df_filtered.to_sql(table_name, engine, if_exists='append', index=False)
        print(f"  ✓ Inserted {len(df_filtered)} rows into {table_name}")

    except Exception as e:
        print(f"  ✗ Failed to insert into {table_name}: {e}")


def process_non_collapsible_files(
        folder_path: str,
        version_id: int,
        table_config: Dict[str, str],
        engine
):
    annual_files, monthly_files = 0, 0

    for file_name in os.listdir(folder_path):
        if not file_name.endswith('.csv'):
            continue
        if file_name.startswith('cumulative_'):   # handled by process_cumul_reports
            continue

        file_path = os.path.join(folder_path, file_name)
        print(f"================= Reading file: {file_name} =================")

        try:
            df = pd.read_csv(file_path)
            df['version_id'] = version_id

            if file_name.startswith('annual_'):
                print(f"  → ANNUAL FILE")
                insert_to_table(df, table_config['ANNUAL_TABLE'], engine)
                annual_files += 1
            else:
                print(f"  → MONTHLY FILE")
                insert_to_table(df, table_config['MONTHLY_TABLE'], engine)
                monthly_files += 1

        except Exception as e:
            print(f"  ✗ Error reading {file_name}: {e}")

    print(f"============ PROCESSED {annual_files} ANNUAL FILES ===========")
    print(f"============ PROCESSED {monthly_files} MONTHLY FILES ===========")


# ── Collapsible files ─────────────────────────────────────────────────────────

def process_collapsible_files(
        folder_path: str,
        version_id: int,
        table_config: Dict[str, str],
        engine
):
    annual_files, monthly_files, cumul_files = 0, 0, 0

    for file_name in os.listdir(folder_path):
        if not file_name.endswith('.csv'):
            continue

        file_path = os.path.join(folder_path, file_name)
        print(f"================= Reading file: {file_name} =================")

        try:
            df = pd.read_csv(file_path)
            df['version_id'] = version_id

            if file_name.startswith('annual_'):
                print(f"  → ANNUAL FILE")
                insert_to_table(df, table_config['COLLAPSE_ANNUAL_TABLE'], engine)
                annual_files += 1

            elif file_name.startswith('cumulative_'):
                print(f"  → CUMULATIVE FILE")
                insert_to_table(df, table_config['COLLAPSE_CUMULATIVE_TABLE'], engine)
                cumul_files += 1

            else:
                print(f"  → MONTHLY FILE")
                insert_to_table(df, table_config['COLLAPSE_MONTHLY_TABLE'], engine)
                monthly_files += 1

        except Exception as e:
            print(f"  ✗ Error reading {file_name}: {e}")

    print(f"============ PROCESSED {annual_files} ANNUAL FILES ===========")
    print(f"============ PROCESSED {monthly_files} MONTHLY FILES ===========")
    print(f"============ PROCESSED {cumul_files} CUMULATIVE FILES ===========")


# ── Cumulative files (non-collapsible) ────────────────────────────────────────

def process_cumul_reports(
        folder_path: str,
        version_id: int,
        table_config: Dict[str, str],
        engine
):
    cumul_files = 0

    for file_name in os.listdir(folder_path):
        if not file_name.endswith('.csv'):
            continue
        if not file_name.startswith('cumulative_'):
            continue

        file_path = os.path.join(folder_path, file_name)
        print(f"================= Reading file: {file_name} =================")

        try:
            df = pd.read_csv(file_path)
            df['version_id'] = version_id
            print(f"  → CUMULATIVE FILE")
            insert_to_table(df, table_config['CUMULATIVE_TABLE'], engine)
            cumul_files += 1

        except Exception as e:
            print(f"  ✗ Error reading {file_name}: {e}")

    print(f"============ PROCESSED {cumul_files} CUMULATIVE FILES ===========")


# ── Main ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    engine     = get_db_engine()
    args       = parse_arguments()
    version_id = args.version_id

    non_collapsible_files_path = "benin-data-parser-new/2025/may_output"
    collapsible_files_path     = "benin-data-parser-new/2025/may_collapsible_output"

    table_config = {
        "ANNUAL_TABLE":              "financial_annual_data",
        "MONTHLY_TABLE":             "financial_metrics_data",
        "CUMULATIVE_TABLE":          "financial_cumulative_data",
        "COLLAPSE_ANNUAL_TABLE":     "collapse_annual_data",
        "COLLAPSE_MONTHLY_TABLE":    "collapse_monthly_data",
        "COLLAPSE_CUMULATIVE_TABLE": "collapse_cumul_data",
    }

    process_non_collapsible_files(non_collapsible_files_path, version_id, table_config, engine)
    process_collapsible_files(collapsible_files_path, version_id, table_config, engine)
    process_cumul_reports(non_collapsible_files_path, version_id, table_config, engine)