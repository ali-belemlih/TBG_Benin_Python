from helpers.db_utils import get_db_connection, get_version_id_by_name, upsert_financial_data
import logging
from helpers.parse_arg import parse_arguments
from .mapping.pnl_conso_cumul_mapping import financial_type_pnl_conso_cumul_mapping, pnl_actual_cumul_mapping
import pandas as pd


def resolve_cr_references(formula_str: str, source_map: dict, cache: dict, cur, date: str, version_id, value_type):
    for key, source in source_map.items():
        if key in cache:
            value = cache[key]
        else:
            table = source["table_name"]
            column = source["column_name"]
            id_val = source["value"]
            query = f"""
                SELECT {value_type} FROM {table}
                WHERE {column} = %s AND date = %s AND version_id = %s
                ORDER BY updated_at DESC LIMIT 1
            """
            cur.execute(query, (id_val, date, version_id))
            result = cur.fetchone()
            value = result[0] if result else 0
            cache[key] = value
        formula_str = formula_str.replace(key, str(value))
    if "/month" in formula_str:
        month_number = int(date[5:7])
        formula_str = formula_str.replace("/month", f"/{month_number}")
    return formula_str


def sum_real_values_by_month(row_num: int, cache: dict, month_limit: int) -> float:
    MONTH_COLUMNS = {
        1: "D", 2: "J", 3: "P", 4: "V", 5: "AD", 6: "AL",
        7: "AU", 8: "BC", 9: "BK", 10: "BT", 11: "CB", 12: "CJ"
    }
    total = 0
    for m in range(1, month_limit + 1):
        col = MONTH_COLUMNS[m]
        key = f"{col}{row_num}"
        value = cache.get(key)
        if value is not None:
            total += value
    return total


def fetch_monthly_values(row_num, table_type, object_id, year, cursor, month_limit, value_type):
    month_map = {
        1: "D", 2: "J", 3: "P", 4: "V", 5: "AD", 6: "AL",
        7: "AU", 8: "BC", 9: "BK", 10: "BT", 11: "CB", 12: "CJ"
    }
    column = f"{table_type}_id"
    cumulative_total = 0
    for version_id in range(1, month_limit + 1):
        query = f"""
            SELECT EXTRACT(MONTH FROM date)::int AS month, COALESCE({value_type}, 0)
            FROM financial_metrics_data
            WHERE {column} = %s
              AND EXTRACT(YEAR FROM date) = %s
              AND version_id = %s
            ORDER BY month
        """
        cursor.execute(query, (object_id, year, version_id))
        for month, value in cursor.fetchall():
            if month == version_id:
                col = month_map.get(month)
                if col:
                    computed_key = f"{col}{row_num}"
                    cumulative_total += value
                    yield computed_key, value
    yield f"CR{row_num}", cumulative_total


def calculate_real_value(formula: str, date: str, source_map: dict, version_id, value_type, cache=None):
    cache = cache or {}
    conn = get_db_connection()
    with conn:
        cur = conn.cursor()
        resolved_formula = resolve_cr_references(formula, source_map, cache, cur, date, version_id, value_type)
        try:
            return eval(resolved_formula)
        except Exception as e:
            print(f"❌ Evaluation error in formula '{resolved_formula}': {e}")
            return 0.0


def get_value_from_formula(row_num, data, date, month_limit, computed_cache, version_id, value_type):
    table_type = data["type"]
    object_id = data["id"]
    formula_entry = data.get("formula", {})
    formula = formula_entry.get("data", "") if isinstance(formula_entry, dict) else formula_entry
    source_map = formula_entry.get("source", {}) if isinstance(formula_entry, dict) else {}

    if formula.startswith("+") or formula.startswith("="):
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                for key, val in fetch_monthly_values(
                    row_num, table_type, object_id, int(date[:4]), cur, int(date[5:7]), value_type
                ):
                    computed_cache[key] = val
        return sum_real_values_by_month(row_num, computed_cache, month_limit)
    else:
        return calculate_real_value(formula, date, source_map, version_id, value_type, computed_cache)


def process_pnl_conso_mapping(date: str, version_id, mapping, value_type):
    results = []
    computed_cache = {}
    month_limit = int(date[5:7])

    for row_num, data in mapping.items():
        try:
            value = get_value_from_formula(row_num, data, date, month_limit, computed_cache, version_id, value_type)
            computed_cache[f"CR{row_num}"] = value
            results.append({
                "financial_type_id": data["id"] if data["type"] == "financial_type" else None,
                "financial_metric_id": data["id"] if data["type"] == "financial_metric" else None,
                "financial_submetric_id": data["id"] if data["type"] == "financial_submetric" else None,
                f"{value_type}": value,
                "version_id": version_id,
                "date": date
            })
        except Exception as e:
            print(f"❌ Error in formula for row {row_num}: {str(e)}")

    df = pd.DataFrame(results)
    output_path = f"benin_parser_2025/cumul_import/outputs/pnl_conso_cumul_{value_type}_{date}.csv"
    df.to_csv(output_path, index=False)
    print(f"CSV file for {date} generated successfully at: {output_path}")
    return df


def safe_int(val):
    try:
        return int(val) if pd.notna(val) else None
    except:
        return val


def insert_data_to_db(df, version_id, value_type):
    print("inserting function===================")
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        for _, row in df.iterrows():
            type_id = safe_int(row.get("financial_type_id"))
            metric_id = safe_int(row.get("financial_metric_id"))
            submetric_id = safe_int(row.get("financial_submetric_id"))
            value = row.get(f"{value_type}")
            date_value = row.get("date")

            # ✅ Dynamically pass only the relevant value_type kwarg
            upsert_financial_data(
                cur, "financial_cumulative_data",
                type_id, metric_id, submetric_id,
                date_value,
                version_id=version_id,
                **{value_type: value}
            )
            logging.info(f"============INSERTED {value}============")

        conn.commit()
        print(f"✅ Successfully inserted {len(df)} records into financial_cumulative_data")
    except Exception as e:
        conn.rollback()
        print(f"❌ Database insertion error: {e}")
    finally:
        cur.close()
        conn.close()


def process_submetric_percent(label, conn, cur, date, version_id):
    submetric_ids = [14, 18, 20]
    try:
        for submetric_id in submetric_ids:
            update_query = f"""
                UPDATE financial_cumulative_data
                SET {label} = {label} / %s
                WHERE date = %s
                  AND financial_submetric_id = %s
                  AND version_id = %s
            """
            cur.execute(update_query, (int(version_id), date, submetric_id, version_id))
            print(f"Updated {label} for submetric ID {submetric_id}: {label} / {version_id} for date {date}")
        conn.commit()
    except Exception as e:
        print(f"❌ Error processing submetric {label}: {str(e)}")
        conn.rollback()
    print(f"✅ Updated submetric {label} successfully for date {date}.")


def process_metric_percent(label, conn, cur, date, version_id):
    metric_ids = [88]
    try:
        for metric_id in metric_ids:
            update_query = f"""
                UPDATE financial_cumulative_data
                SET {label} = {label} / %s
                WHERE date = %s
                  AND financial_metric_id = %s
                  AND version_id = %s
            """
            cur.execute(update_query, (int(version_id), date, metric_id, version_id))
            print(f"Updated {label} for metric ID {metric_id}: {label} / {version_id} for date {date}")
        conn.commit()
    except Exception as e:
        print(f"❌ Error processing metric {label}: {str(e)}")
        conn.rollback()
    print(f"✅ Updated metric {label} successfully for date {date}.")


if __name__ == "__main__":
    args = parse_arguments()
    month_year = args.month_year
    month = int(month_year[:2])
    year = month_year[2:]
    date = f"{year}-{month:02d}-01"
    version_id = get_version_id_by_name(args.version_id)

    # Base mappings
    mapping_sets = {
        "real_value": financial_type_pnl_conso_cumul_mapping,
        "budget_value": financial_type_pnl_conso_cumul_mapping,
        "last_year_real_value": financial_type_pnl_conso_cumul_mapping,
    }

    # Determine which actual columns to include based on month
    if 4 <= month <= 5:
        mapping_sets["actual1_value"] = pnl_actual_cumul_mapping
    elif month == 6:
        mapping_sets["actual1_value"] = pnl_actual_cumul_mapping
        mapping_sets["actual2_value"] = pnl_actual_cumul_mapping
    elif 7 <= month <= 8:
        mapping_sets["actual2_value"] = pnl_actual_cumul_mapping
    elif month == 9:
        mapping_sets["actual2_value"] = pnl_actual_cumul_mapping
        mapping_sets["actual3_value"] = pnl_actual_cumul_mapping
    elif 10 <= month <= 12:
        mapping_sets["actual3_value"] = pnl_actual_cumul_mapping

    # ✅ Execute once before the loop
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        print("⚙️ Processing submetric and metric percentages...")
        process_submetric_percent("real_value", conn, cur, date, version_id)
        process_metric_percent("real_value", conn, cur, date, version_id)
        print("✅ Submetric and metric percentages processed.")
    except Exception as e:
        print(f"❌ Error processing percentages: {e}")
    finally:
        cur.close()
        conn.close()

    # Process each mapping label
    for label, mapping in mapping_sets.items():
        try:
            print(f"\nProcessing {label} mapping...")
            df = process_pnl_conso_mapping(date, version_id, mapping, label)
            print(df.to_string(index=False))
            insert_data_to_db(df, version_id, label)
        except Exception as e:
            print(f"❌ Error processing {label}: {e}")

    print("✅ All mappings processed successfully.")