import pandas as pd
from datetime import datetime
from helpers.db_utils import get_db_connection, upsert_financial_data, get_version_id_by_name
from helpers.formula_utils.evaluator import evaluate_formula
from helpers.actual_helper import parse_arguments
from benin_parser_2025.actu1_import.main_driver import run, load_sheet_config
from .mapping.parc_mobile_mapping import (
    financial_type_row_mapping,
    financial_metric_row_mapping,
    financial_submetric_row_mapping,
    annual_actual_mapping,
    monthly_actual_mapping,  # ✅ Added
)

# -------------------------
# Step 1: Run Monthly + Annual imports
# -------------------------
def run_imports(args):
    config = load_sheet_config("parc_mobile")

    mappings = {
        "financial_type_row_mapping": financial_type_row_mapping,
        "financial_metric_row_mapping": financial_metric_row_mapping,
        "financial_submetric_row_mapping": financial_submetric_row_mapping
    }

    # Monthly
    run(
        sheet_name=config["sheet_name"],
        mappings=mappings,
        mode="monthly",
        args=args,
        output_prefix="parc_mobile",
        db_table_name=config["monthly"]["table"],
        custom_month_column_map=config["monthly"]["column_map"],
        category_fallback=config["category_fallback"],
        start_row_offset=config["start_row_offset"]
    )

    # Annual
    run(
        sheet_name=config["sheet_name"],
        mappings=mappings,
        mode="annual",
        args=args,
        output_prefix="parc_mobile",
        db_table_name=config["annual"]["table"],
        custom_column_index=config["annual"]["column_index"],
        category_fallback=config["category_fallback"],
        start_row_offset=config["start_row_offset"]
    )


# -------------------------
# Step 2: Actual2 Value Calculation
# -------------------------
def calculate_actual_value(formula, date, actual_type='actual2_value', version_id=None, cache=None):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        return evaluate_formula(cur, formula, date, actual_type, version_id, cache=cache or {})
    finally:
        cur.close()
        conn.close()


def process_parc_actual_data(mapping, date, version_id, actual_type, mode="annual"):
    """
    Generic processor for actual2 values.
    mode = "annual" -> uses financial_annual_data
    mode = "monthly" -> uses financial_metric_data
    """
    results = []
    computed_cache = {}
    field_map = {
        "financial_type": "financial_type",
        "financial_metric": "financial_metric",
        "financial_submetric": "financial_submetric"
    }

    for label, data in mapping.items():
        table_name = data["type"]
        entity_id = data["id"]
        formula = data.get("formula", "")

        if table_name in field_map:
            actual_value = calculate_actual_value(formula, date, f"{actual_type}_value", version_id, cache=computed_cache)
            computed_cache[label] = actual_value
            result = {
                "row_number": label,
                "financial_type": None,
                "financial_metric": None,
                "financial_submetric": None,
                f"{actual_type}_value": actual_value,
                "date": date,
                "version_id": version_id
            }
            result[field_map[table_name]] = entity_id
            results.append(result)

    # Export to CSV
    df_csv = pd.DataFrame(results)
    output_csv_path = f'benin_parser_2025/actu1_import/parc_{mode}_actual_data_{date}.csv'
    df_csv.to_csv(output_csv_path, index=False)
    print(f"✅ CSV file for {mode} {date} generated successfully at: {output_csv_path}")

    return results


def insert_financial_data_to_db(mode, data_list, actual_type="actual2"):
    """
    Dynamically insert financial actual data into DB.
    
    Parameters:
        mode (str): 'annual' or 'monthly'
        data_list (list[dict]): list of data rows to insert
        actual_type (str): which actual type column to insert (e.g., 'actual1', 'actual2', 'actual3')
    """
    # Determine target table
    table_name = "financial_annual_data" if mode == "annual" else "financial_metrics_data"
    actual_field = f"{actual_type}_value"

    conn = get_db_connection()
    cur = conn.cursor()
    try:
        for data in data_list:
            type_id = data.get("financial_type") or None
            metric_id = data.get("financial_metric") or None
            submetric_id = data.get("financial_submetric") or None
            actual_value = data.get(actual_field) or None
            date_value = data.get("date", "2026-01-01")
            version_id = data.get("version_id")

            # Normalize IDs (handle NaN or float IDs)
            for key in ("type_id", "metric_id", "submetric_id"):
                val = locals()[key]
                if isinstance(val, float) and val.is_integer():
                    locals()[key] = int(val)

            # Perform upsert
            upsert_financial_data(
                cur,
                table_name,
                type_id,
                metric_id,
                submetric_id,
                date_value,
                version_id=version_id,
                **{actual_field: actual_value}  # ✅ dynamically insert actual type field
            )

        conn.commit()
        print(f"✅ Successfully inserted {len(data_list)} records into {table_name} ({actual_type}).")

    except Exception as e:
        conn.rollback()
        print(f"❌ Database insertion error while inserting {actual_type} data: {e}")
    finally:
        cur.close()
        conn.close()


# -------------------------
# Step 3: Orchestration
# -------------------------
def main():
    args = parse_arguments()

    # Step 1: Run imports
    run_imports(args)

    # Step 2: Parse month_year argument
    try:
        dt = datetime.strptime(args.month_year, "%m%Y")
        actual_type = args.actual_type
        target_year = dt.year
        month = dt.month

        annual_date = f"{target_year}-01-01"     # e.g. "2025-01-01"
        monthly_date = dt.strftime("%Y-%m-%d")   # keep as full YYYY-MM-DD

    except Exception as e:
        print(f"❌ Invalid --month_year format: {args.month_year}. Expected YYYY-MM-DD")
        raise e

    try:
        version_id = get_version_id_by_name(args.version_id)

        # ---- Annual run ----
        df_annual = process_parc_actual_data(
            annual_actual_mapping,
            annual_date,
            version_id,
            actual_type,
            mode="annual"
        )
        insert_financial_data_to_db("annual", df_annual, actual_type)

        # ---- Monthly run ----
        df_monthly = process_parc_actual_data(
            monthly_actual_mapping,
            monthly_date,
            version_id,
            actual_type,
            mode="monthly"
        )
        insert_financial_data_to_db("monthly", df_monthly, actual_type)

        print("✅ All steps (monthly + annual) completed successfully.")

    except Exception as e:
        print(f"❌ Error occurred during processing: {e}")



if __name__ == "__main__":
    main()
