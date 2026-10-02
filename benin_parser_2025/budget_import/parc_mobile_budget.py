import pandas as pd
from helpers.db_utils import get_db_connection, upsert_financial_data, get_version_id_by_name
from helpers.formula_utils.evaluator import evaluate_formula
from helpers.parse_arg import parse_arguments
from .mapping.parc_mobile_formula_mapping import monthly_budget_mapping ,annual_budget_mapping

def calculate_budget_value(formula, date, version_id = None, cache=None):
    conn = get_db_connection()
    cur = conn.cursor()
    return evaluate_formula(cur, formula, date, "budget_value", version_id, cache=cache or {})

def process_parc_monthly_budget_mobile(date,version_id):
    results = []
    computed_cache = {}
    field_map = {
        "financial_type": "financial_type",
        "financial_metric": "financial_metric",
        "financial_submetric": "financial_submetric"
    }

    for label, data in monthly_budget_mapping.items():
        table_name = data["type"]
        id = data["id"]
        formula = data.get("formula", "")

        if table_name in field_map:
            budget_value = calculate_budget_value(formula, date, version_id, cache=computed_cache)
            computed_cache[label] = budget_value
            result = {
                "label": label,
                "financial_type": None,
                "financial_metric": None,
                "financial_submetric": None,
                "budget_value": budget_value,
                "date": date,
                "version_id" : version_id
            }
            result[field_map[table_name]] = id
            results.append(result)

    # df_csv = pd.DataFrame(results)
    # output_csv_path = f'benin_parser_2025/budget_import/parc_monthly_buget_data_{date}.csv'
    # df_csv.to_csv(output_csv_path, index=False)
    # print(f"✅ CSV file for {date} generated successfully at: {output_csv_path}")
    return results

def process_parc_annual_budget_mobile(date,version_id):
    results = []
    computed_cache = {}
    field_map = {
        "financial_type": "financial_type",
        "financial_metric": "financial_metric",
        "financial_submetric": "financial_submetric"
    }

    for label, data in annual_budget_mapping.items():
        table_name = data["type"]
        id = data["id"]
        formula = data.get("formula", "")

        if table_name in field_map:
            budget_value = calculate_budget_value(formula, date, version_id, cache=computed_cache)
            computed_cache[label] = budget_value

            result = {
                "label": label,
                "financial_type": None,
                "financial_metric": None,
                "financial_submetric": None,
                "budget_value": budget_value,
                "date": date,
                "version_id" : version_id
            }
            result[field_map[table_name]] = id
            results.append(result)

    # df_csv = pd.DataFrame(results)
    # output_csv_path = f'benin_parser_2025/budget_import/parc_annual_buget_data_{date}.csv'
    # df_csv.to_csv(output_csv_path, index=False)
    # print(f"✅ CSV file for {date} generated successfully at: {output_csv_path}")
    return results

def insert_financial_data_to_db(table_name, data_list):
    """Inserts extracted financial data into the database."""
    conn = get_db_connection()
    cur = conn.cursor()

    try:
        for data in data_list:
            type_id = data.get("financial_type") or None
            metric_id = data.get("financial_metric") or None
            submetric_id = data.get("financial_submetric") or None
            budget_value = data.get("budget_value") or None
            date_value = data.get("date", "2026-01-01")  # Default to fixed date if missing
            version_id = data.get('version_id')
            # Ensure all IDs are valid integers or None

            type_id = int(type_id) if isinstance(type_id, float) and type_id.is_integer() else type_id
            metric_id = int(metric_id) if isinstance(metric_id, float) and metric_id.is_integer() else metric_id
            submetric_id = int(submetric_id) if isinstance(submetric_id, float) and submetric_id.is_integer() else submetric_id

            # Insert data into DB
            upsert_financial_data(
                cur, table_name,
                type_id, metric_id, submetric_id,
                date_value,
                budget_value=budget_value,
                version_id = version_id
            )

        conn.commit()  # Commit only after all inserts

    except Exception as e:
        conn.rollback()  # Rollback on error
        print(f"❌ Database insertion error: {e}")

    finally:
        cur.close()
        conn.close()

def main():
    args = parse_arguments()
    month = args.month_year[:2]
    year = args.month_year[2:]
    month_date = f"{year}-{month}-01"
    annual_date = f"{year}-01-01"

    try:
        version_id = get_version_id_by_name(args.version_id)

        df_monthly = process_parc_monthly_budget_mobile(month_date, version_id)
        df_annual = process_parc_annual_budget_mobile(annual_date, version_id)

        insert_financial_data_to_db('financial_metrics_data', df_monthly)
        insert_financial_data_to_db('financial_annual_data', df_annual)

        print("✅ Data successfully prepared and inserted into DB.")

    except Exception as e:
        print(f"❌ Error occurred during processing: {e}")

if __name__ == "__main__":
    main()
