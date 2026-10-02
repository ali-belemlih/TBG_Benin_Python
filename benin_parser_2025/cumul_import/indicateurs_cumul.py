import pandas as pd
from pathlib import Path
import psycopg2
import argparse
from helpers.formula_utils.evaluator import evaluate_formula
from helpers.parse_arg import parse_arguments
from helpers.db_utils import get_db_connection, get_version_id_by_name, upsert_financial_data
from helpers.formula_utils.excel_parser import calculate_formula
from benin_parser_2025.cumul_import.mapping.indicateurs_cumul_mapping import (
    cumul_reel_mapping,
    cumul_budget_mapping,
    cumul_last_year_real_mapping,
    actual1_mapping
)


def safe_int(val):
    try:
        return int(val) if pd.notna(val) else None
    except (ValueError, TypeError):   # fix #6 — no bare except
        return val


def calculate_real_value(formula, date, label, version_id=None, cache=None):
    conn = get_db_connection()
    cur = conn.cursor()
    try:                               # fix #3 — close connection after use
        return evaluate_formula(cur, formula, date, label, version_id, cache=cache or {})
    finally:
        cur.close()
        conn.close()


def process_mapping(mapping, date, label, version_id, computed_cache):
    results = []
    field_map = {
        "financial_type": "financial_type",
        "financial_metric": "financial_metric",
        "financial_submetric": "financial_submetric"
    }

    for row, data in mapping.items():
        table_name = data["type"]
        object_id = data["id"]
        formula = data.get("formula", {})

        # fix #4 — guard before accessing formula["data"]
        formula_data = formula.get("data", "")
        if "/month" in formula_data:
            formula["data"] = formula_data.replace("/month", f"/{int(date[5:7])}")

        if table_name in field_map:
            value_calculated = calculate_real_value(formula, date, label, version_id, cache=computed_cache)
            computed_cache[row] = value_calculated

            result = {
                "row": row,
                "financial_type_id": object_id if table_name == "financial_type" else None,
                "financial_metric_id": object_id if table_name == "financial_metric" else None,
                "financial_submetric_id": object_id if table_name == "financial_submetric" else None,
                label: value_calculated,
                "version_id": version_id,
                "date": date,
                field_map[table_name]: object_id
            }
            results.append(result)

    df_csv = pd.DataFrame(results)
    output_path = f'benin_parser_2025/cumul_import/indicateurs_cumul_{label}_{date}.csv'
    df_csv.to_csv(output_path, index=False)
    print(f"✅ CSV file for {label} - {date} generated at: {output_path}")
    return results


def insert_financial_data_to_db(df, version_id, value_type):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        for _, row in df.iterrows():
            type_id = safe_int(row.get("financial_type_id"))
            metric_id = safe_int(row.get("financial_metric_id"))
            submetric_id = safe_int(row.get("financial_submetric_id"))
            value = row.get(value_type) or None
            date_value = row.get("date")

            if type_id is not None or metric_id is not None or submetric_id is not None:
                update_field = {value_type: value}   # fix #1 — use value_type not label
                upsert_financial_data(
                    cur=cur,
                    table_name="financial_cumulative_data",
                    type_id=type_id,
                    metric_id=metric_id,
                    submetric_id=submetric_id,
                    date_value=date_value,
                    version_id=version_id,            # fix #2 — pass version_id
                    **update_field
                )

        conn.commit()
        print(f"✅ Successfully inserted {len(df)} records into financial_cumulative_data")
    except Exception as e:
        conn.rollback()
        print(f"❌ Database insertion error: {e}")
    finally:
        cur.close()
        conn.close()


if __name__ == "__main__":
    args = parse_arguments()
    month_year = args.month_year
    month = int(month_year[:2])
    year = month_year[2:]
    date = f"{year}-{month:02d}-01"
    version_id = get_version_id_by_name(args.version_id)

    # Base mappings
    mapping_sets = {
        "real_value": cumul_reel_mapping,
        "budget_value": cumul_budget_mapping,
        "last_year_real_value": cumul_last_year_real_mapping,
    }

    # fix #5 — cleaner month logic, no redundant branches
    if 4 <= month <= 6:
        mapping_sets["actual1_value"] = actual1_mapping
    if 7 <= month <= 9:
        mapping_sets["actual2_value"] = actual1_mapping
    if month == 9:
        mapping_sets["actual3_value"] = actual1_mapping
    if 10 <= month <= 12:
        mapping_sets["actual3_value"] = actual1_mapping

    all_results = []
    for label, mapping in mapping_sets.items():
        try:
            computed_cache = {}
            results = process_mapping(mapping, date, label, version_id, computed_cache)
            insert_financial_data_to_db(pd.DataFrame(results), version_id, label)
            all_results.extend(results)
        except Exception as e:
            print(f"❌ Error processing {label}: {e}")

    print("✅ All mappings processed.")