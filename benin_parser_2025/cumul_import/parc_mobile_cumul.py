import pandas as pd
from helpers.db_utils import (
    get_db_connection,
    upsert_financial_data,
    get_version_id_by_name,
    get_default_version_id
)
from helpers.formula_utils.evaluator import evaluate_formula
from helpers.parse_arg import parse_arguments
from .mapping.parc_mobile_mapping_cumul import REEL_DATA_MAPPING, BUDGET_MAPPING, LAST_YEAR_REEL_MAPPING, ACTUAL1_MAPPING


def process_initial_values(metric_ids, conn, cur, month, year, version_id):
    """
    For each metric_id:
    Fetch real_value, budget_value, last_year_real_value from financial_metrics_data
    using the default version for January (month=1) and insert all of them into
    financial_cumulative_data including all applicable actual columns.
    """
    metric_ids = [int(mid) for mid in metric_ids]
    default_version_id = int(get_default_version_id(month=1, year=year))
    if not default_version_id:
        print(f"⚠️ No default version found for month=1, year={year}")
        return

    date = f"{year}-{month:02d}-01"

    # Determine which actual columns apply for this month
    actual_columns = []
    if 4 <= month <= 6:
        actual_columns.append("actual1_value")
    if 7 <= month <= 9:
        actual_columns.append("actual2_value")
    if month == 9:
        actual_columns.append("actual3_value")
    if 10 <= month <= 12:
        actual_columns.append("actual3_value")

    for metric_id in metric_ids:
        try:
            cur.execute(
                """
                SELECT real_value, budget_value, last_year_real_value
                FROM financial_metrics_data
                WHERE financial_metric_id = %s
                  AND version_id = %s
                """,
                (metric_id, default_version_id)
            )
            row = cur.fetchone()
            if not row:
                print(f"⚠️ No data found for metric_id={metric_id}, default_version={default_version_id}")
                continue

            real_value, budget_value, last_year_real_value = row

            def to_native(val):
                if hasattr(val, "item"):
                    val = val.item()
                if val is None:
                    return None
                if isinstance(val, (int, float)):
                    return float(val)
                return val

            real_value = to_native(real_value)
            budget_value = to_native(budget_value)
            last_year_real_value = to_native(last_year_real_value)

            print(f"📦 Metric {metric_id} — default version {default_version_id}: "
                  f"real={real_value}, budget={budget_value}, last_year_real={last_year_real_value}")

            # Build SET clause dynamically for all actual columns
            actual_set_clause = ", ".join([f"{col} = %s" for col in actual_columns])
            actual_values = [real_value] * len(actual_columns)

            # Update real_value + all applicable actuals
            if actual_columns:
                cur.execute(
                    f"""
                    UPDATE financial_cumulative_data
                    SET real_value = %s,
                        {actual_set_clause}
                    WHERE financial_metric_id = %s
                      AND version_id = %s
                      AND date = %s
                    """,
                    [real_value] + actual_values + [metric_id, int(version_id), date]
                )
            else:
                cur.execute(
                    """
                    UPDATE financial_cumulative_data
                    SET real_value = %s
                    WHERE financial_metric_id = %s
                      AND version_id = %s
                      AND date = %s
                    """,
                    (real_value, metric_id, int(version_id), date)
                )
            print(f"✅ Updated real_value + {actual_columns or []} for metric {metric_id} ({cur.rowcount} rows)")

            # Update budget_value
            if budget_value is not None:
                cur.execute(
                    """
                    UPDATE financial_cumulative_data
                    SET budget_value = %s
                    WHERE financial_metric_id = %s
                      AND version_id = %s
                      AND date = %s
                    """,
                    (budget_value, metric_id, int(version_id), date)
                )
                print(f"✅ Updated budget_value for metric {metric_id} ({cur.rowcount} rows)")

            # Update last_year_real_value
            if last_year_real_value is not None:
                cur.execute(
                    """
                    UPDATE financial_cumulative_data
                    SET last_year_real_value = %s
                    WHERE financial_metric_id = %s
                      AND version_id = %s
                      AND date = %s
                    """,
                    (last_year_real_value, metric_id, int(version_id), date)
                )
                print(f"✅ Updated last_year_real_value for metric {metric_id} ({cur.rowcount} rows)")

            conn.commit()

        except Exception as e:
            conn.rollback()
            print(f"❌ Error processing metric_id={metric_id}: {str(e)}")

    print(f"🎯 Completed initial value updates for month={month}, year={year}, version={version_id}")


def calculate_value(formula, date, label, version_id=None, cache=None):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        return evaluate_formula(cur, formula, date, label, version_id, cache=cache or {})
    finally:
        cur.close()
        conn.close()


def process_mapping(mapping, date, label, computed_cache=None, version_id=None):
    results = []
    if computed_cache is None:
        computed_cache = {}
    field_map = {
        "financial_type": "financial_type_id",
        "financial_metric": "financial_metric_id",
        "financial_submetric": "financial_submetric_id"
    }
    for data_label, data in mapping.items():
        table_name = data["type"]
        object_id = data["id"]
        formula = data.get("formula", {})

        formula_data = formula.get("data", "")
        if "/month" in formula_data:
            month_int = int(date.split("-")[1])
            formula["data"] = formula_data.replace("/month", f"/{month_int}")

        value = calculate_value(formula, date, label, version_id, cache=computed_cache)
        computed_cache[data_label] = value

        result = {
            "row": data_label,
            "financial_type_id": None,
            "financial_metric_id": None,
            "financial_submetric_id": None,
            f"{label}": value,
            "date": date,
            "mapping_type": label,
            "version_id": version_id
        }
        if table_name in field_map:
            result[field_map[table_name]] = object_id

        results.append(result)

    return pd.DataFrame(results)


def save_to_csv(df, date, version_id, label):
    output_csv_path = f'benin_parser_2025/cumul_import/outputs/parc_mobile_{label}_{date}_v{version_id}.csv'
    df.to_csv(output_csv_path, index=False)
    print(f"✅ CSV saved for {label} {date} (version {version_id}) at: {output_csv_path}")


def insert_data_to_db(result_df, version_id, label):
    conn = get_db_connection()
    cur = conn.cursor()
    print("Database connection successful!")
    try:
        for _, row in result_df.iterrows():
            type_id = row['financial_type_id']
            metric_id = row['financial_metric_id']
            submetric_id = row.get('financial_submetric_id')
            date_value = row['date']
            value = row[f'{label}']

            type_id = None if pd.isna(type_id) else type_id
            metric_id = None if pd.isna(metric_id) else metric_id
            submetric_id = None if pd.isna(submetric_id) else submetric_id
            value = None if pd.isna(value) else value

            if type_id is not None or metric_id is not None or submetric_id is not None:
                update_field = {label: value}
                upsert_financial_data(
                    cur=cur,
                    table_name="financial_cumulative_data",
                    type_id=type_id,
                    metric_id=metric_id,
                    submetric_id=submetric_id,
                    date_value=date_value,
                    version_id=version_id,
                    **update_field
                )

        conn.commit()
        print(f"✅ Data insertion completed for {label} ({len(result_df)} records)")
    except Exception as e:
        conn.rollback()
        print(f"❌ DB insertion error for {label}: {e}")
    finally:
        cur.close()
        conn.close()


if __name__ == "__main__":
    args = parse_arguments()
    month = int(args.month_year[:2])
    year = args.month_year[2:]
    date = f"{year}-{month:02d}-01"
    version_id = get_version_id_by_name(args.version_id)

    mapping_sets = {
        "real_value": REEL_DATA_MAPPING,
        "budget_value": BUDGET_MAPPING,
        "last_year_real_value": LAST_YEAR_REEL_MAPPING,
    }

    if 4 <= month <= 6:
        mapping_sets["actual1_value"] = ACTUAL1_MAPPING
    if 7 <= month <= 9:
        mapping_sets["actual2_value"] = ACTUAL1_MAPPING
    if month == 9:
        mapping_sets["actual3_value"] = ACTUAL1_MAPPING
    if 10 <= month <= 12:
        mapping_sets["actual3_value"] = ACTUAL1_MAPPING

    conn = get_db_connection()
    cur = conn.cursor()

    try:
        metric_ids = [141, 143]
        process_initial_values(metric_ids, conn, cur, month=month, year=year, version_id=version_id)

        for label, mapping in mapping_sets.items():
            computed_cache = {}
            print(f"\nProcessing {label} mapping...")
            results_df = process_mapping(mapping, date, label, computed_cache, version_id)
            # save_to_csv(results_df, date, version_id, label)
            print(f"Inserting data for {label}...")
            insert_data_to_db(results_df, version_id, label)

        print("✅ All mappings processed successfully.")

    except Exception as e:
        print(f"❌ Error processing mappings: {str(e)}")

    finally:
        cur.close()
        conn.close()