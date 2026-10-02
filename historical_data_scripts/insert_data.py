from datetime import datetime
from typing import Dict

import pandas as pd
import os
import subprocess
import sys

from helpers.db_utils import get_db_engine

# Required columns for each table (excluding id, created_at, updated_at)
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
    "financial_annual_data": [
        "financial_type_id", "financial_metric_id", "financial_submetric_id", "date",
        "real_value", "budget_value", "actual1_value", "actual2_value", "actual3_value",
        "last_year_real_value", "parent_id", "version_id"
    ],
    "financial_metrics_data": [
        "financial_type_id", "financial_metric_id", "financial_submetric_id", "date",
        "real_value", "budget_value", "actual1_value", "actual2_value", "actual3_value",
        "last_year_real_value", "parent_id", "version_id"
    ]

}

def execute_all_modules(base_path="historical_data_scripts/tbg_scripts"):
    scripts = [
        "data_mobile", "pnl_conso", "opex_conso", "ca_mobile",
        "capex_conso", "cash_conso", "indicateurs", 
        "marge_brute", "parc_mobile", "trafic_mobile"
    ]

    # Convert directory path 'path/to/dir' to module path 'path.to.dir'
    base_module = base_path.replace("/", ".")
    
    print(f"--- Starting Batch Execution from {base_module} ---")

    for script in scripts:
        module_path = f"{base_module}.{script}"
        print(f"\n🚀 Running: {module_path} ...")
        
        try:
            # Execute using the module interface
            result = subprocess.run(
                [sys.executable, "-m", module_path], 
                check=False
            )
            
            if result.returncode != 0:
                print(f"❌ {script} failed with exit code {result.returncode}")
                print("Stopping batch execution to prevent data misalignment.")
                return False
            
            print(f"✅ Finished {script}")
            
        except Exception as e:
            print(f"🚨 Unexpected error running {script}: {e}")
            return False

    print("\n✨ All modules executed successfully.")
    return True

def get_id_mappings(engine):
    """Fetches key-to-id mappings from the database."""
    with engine.connect() as conn:
        types = pd.read_sql("SELECT tbg_key, id FROM financial_types", conn).set_index('tbg_key')['id'].to_dict()
        metrics = pd.read_sql("SELECT tbg_key, id FROM financial_metric", conn).set_index('tbg_key')['id'].to_dict()
        submetrics = pd.read_sql("SELECT tbg_key, id FROM financial_submetric", conn).set_index('tbg_key')['id'].to_dict()
    return types, metrics, submetrics

def generate_version_by_month(date_val):
    if pd.isna(date_val):
        raise ValueError("Invalid date encountered: Date cannot be null when generating version IDs.")
    
    try:
        # Accessing .month assumes date_val is a pandas Timestamp or datetime object
        month = date_val.month
        return f"{month}"
    except AttributeError:
        raise ValueError(f"Invalid date format: {date_val} is not a valid date object.")

def insert_to_table(df, table_name, engine):
    print(f"Inserting into table: {table_name}")
    try:
        columns = TABLE_COLUMNS[table_name]

        type_map, metric_map, sub_map = get_id_mappings(engine)

        if 'financial_type_key' in df.columns:
            df['financial_type_id'] = df['financial_type_key'].map(type_map)

        if 'financial_metric_key' in df.columns:
            df['financial_metric_id'] = df['financial_metric_key'].map(metric_map)

        if 'financial_submetric_key' in df.columns:
            df['financial_submetric_id'] = df['financial_submetric_key'].map(sub_map)

        if 'date' in df.columns:
            df['date_dt'] = pd.to_datetime(df['date'], format='%m-%d-%Y', errors='coerce')
            df['version_id'] = df['date_dt'].apply(generate_version_by_month)
            df['date'] = df['date_dt'].dt.date

        # Add missing expected columns with None
        for col in columns:
            if col not in df.columns:
                df[col] = None

        # Define numeric columns that should be cleaned
        numeric_columns = [
            'real_value', 'budget_value', 'actual1_value', 'actual2_value', 
            'actual3_value', 'last_year_real_value'
        ]
        
        # Clean numeric columns: replace "-" strings and empty strings with None, then convert to numeric
        for col in numeric_columns:
            if col in df.columns:
                # If column is object/string type, replace "-" and empty strings first
                if df[col].dtype == 'object':
                    df[col] = df[col].replace({'-': None, '': None})
                # Convert to numeric, coercing errors (including "-" strings if not already replaced) to NaN
                df[col] = pd.to_numeric(df[col], errors='coerce')
                # Convert NaN to None for SQL NULL
                df[col] = df[col].where(pd.notna(df[col]), None)

        df['created_at'] = datetime.now()
        df['updated_at'] = datetime.now()


        # Filter only needed columns (to avoid issues with unexpected CSV fields)
        df_filtered = df[columns + ["created_at", "updated_at"]]

        # Insert (exclude ID so DB auto-increments it)
        df_filtered.to_sql(table_name, engine, if_exists='append', index=False)
        print(f" Inserted {len(df_filtered)} rows into {table_name}")

    except Exception as e:
        print(f" Failed to insert into {table_name}: {e}")

def process_non_collapsible_files(folder_path: str, table_config: Dict[str, str], engine):
    annual_files,monthly_files = 0,0
    for file_name in os.listdir(folder_path):
        if file_name.endswith('.csv'):
            file_path = os.path.join(folder_path, file_name)
            print(f"================= Reading file: {file_name} =================== ")

            try:
                df = pd.read_csv(file_path)
                if file_name.startswith('annual_'):
                    print(f"{file_name} is an ANNUAL FILE")
                    insert_to_table(df, table_config['ANNUAL_TABLE'], engine)
                    annual_files+=1
                else:
                    print(f"{file_name} is an Monthly FILE")
                    insert_to_table(df,table_config['MONTHLY_TABLE'], engine)
                    monthly_files+=1

            except Exception as e:
                print(f"========== Error reading {file_name}: {e}===========")

    print(f"============ PROCESSED {annual_files} ANNUAL FILES===========")
    print(f"============ PROCESSED {monthly_files} MONTHLY FILES===========")

def process_collapsible_files(folder_path : str,version_id : int, table_config : Dict[str, str], engine):
    annual_files,monthly_files = 0,0
    for file_name in os.listdir(folder_path):
        if file_name.endswith('.csv'):
            file_path = os.path.join(folder_path, file_name)
            print(f"================= Reading file: {file_name} =================== ")

            try:
                df = pd.read_csv(file_path)
                df['version_id'] = version_id
                if file_name.startswith('annual_'):
                    print(f"{file_name} is an ANNUAL FILE")
                    insert_to_table(df, table_config['COLLAPSE_ANNUAL_TABLE'], engine)
                    annual_files+=1
                else:
                    print(f"{file_name} is an Monthly FILE")
                    insert_to_table(df,table_config['COLLAPSE_MONTHLY_TABLE'], engine)
                    monthly_files+=1

            except Exception as e:
                print(f"========== Error reading {file_name}: {e}===========")

    print(f"============ PROCESSED {annual_files} ANNUAL FILES===========")
    print(f"============ PROCESSED {monthly_files} MONTHLY FILES===========")


if __name__ == "__main__":
    execute_all_modules()
    engine = get_db_engine()
    file_path = "historical_data_scripts/ca_outputs"
    # collapsible_files_path_to_upload_path = "benin-data-parser-new/2025/may_collapsible_output"

    table_config = {
        "ANNUAL_TABLE" : "financial_annual_data",
        "MONTHLY_TABLE" : "financial_metrics_data",
        "COLLAPSE_ANNUAL_TABLE" : "collapse_annual_data",
        "COLLAPSE_MONTHLY_TABLE" : "collapse_monthly_data"
    }

    process_non_collapsible_files(file_path, table_config, engine)
    # process_collapsible_files(collapsible_files_path_to_upload_path, version_id, table_config, engine)