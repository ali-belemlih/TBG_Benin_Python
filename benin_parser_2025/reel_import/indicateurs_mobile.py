from helpers.db_utils import (
    get_db_connection, 
    upsert_financial_data, 
    get_version_id_by_name
)
from helpers.parse_arg import parse_arguments
from contextlib import closing
from tbg_formula.formula_evaluator import evaluate_tbg_formula
from tbg_formula.db_helper import get_tbg_report_mapping, find_tbg_key_in_table


def process_indicateurs_mobile(date, version_id, report_type_id, is_adjustible_only=None):
    cache = {}
    results_list = []

    with closing(get_db_connection()) as conn:

        fetched_mapping = get_tbg_report_mapping(conn, report_type_id)

        if not fetched_mapping:
            print("❌ No record found for the passed report type.")
            return []

        for record in fetched_mapping:
            (
                formula_id,
                tbg_key,
                report_type_id,
                formula_type,
                account_details,
                include_sage,
                formula,          # index 6
                is_adjustable,    # index 7
                created_at,
                updated_at,
                sequence,
            ) = record

            if is_adjustible_only and not is_adjustable:
                continue

            base_record_found = find_tbg_key_in_table(conn, tbg_key)

            if not base_record_found:
                print("⚠ Warning: Base key '{}' not found. Skipping.".format(tbg_key))
                continue

            base_col_name, base_table, base_tbg_key_id = base_record_found

            final_result = evaluate_tbg_formula(
                conn,
                tbg_key,
                formula,
                version_id,
                cache
            )

            results_list.append({
                "financial_type_id": base_tbg_key_id
                if base_col_name == "financial_type_id"
                else None,
                "financial_metric_id": base_tbg_key_id
                if base_col_name == "financial_metric_id"
                else None,
                "financial_submetric_id": base_tbg_key_id
                if base_col_name == "financial_submetric_id"
                else None,
                "real_value": final_result,
                "date": date,
                "version_id": version_id
            })

    return results_list


def insert_indicateurs_to_db(data_list):
    """Inserts extracted financial data into the database."""
    conn = get_db_connection()
    cur = conn.cursor()

    try:
        for data in data_list:
            type_id = data.get("financial_type_id") or None
            metric_id = data.get("financial_metric_id") or None
            submetric_id = data.get("financial_submetric_id") or None
            real_value = data.get("real_value") or None
            date_value = data.get("date", "2026-01-01")  # Default if missing
            version_id = data.get('version_id')

            type_id = int(type_id) if isinstance(type_id, float) and type_id.is_integer() else type_id
            metric_id = int(metric_id) if isinstance(metric_id, float) and metric_id.is_integer() else metric_id
            submetric_id = int(submetric_id) if isinstance(submetric_id, float) and submetric_id.is_integer() else submetric_id

            upsert_financial_data(
                cur, "financial_metrics_data",
                type_id, metric_id, submetric_id,
                date_value,
                real_value=real_value,
                version_id=version_id
            )

        conn.commit()
    except Exception as e:
        conn.rollback()
        print(f"❌ Database insertion error: {e}")
    finally:
        cur.close()
        conn.close()


if __name__ == "__main__":
    args = parse_arguments()
    month = args.month_year[:2]
    year = args.month_year[2:]
    date = f"{year}-{month}-01"  # Assuming 1st day of the month

    version_id = get_version_id_by_name(args.version_id)
    report_type_id = 11

    try:
        df_indicateurs = process_indicateurs_mobile(date, version_id, report_type_id)
        insert_indicateurs_to_db(df_indicateurs)
    except Exception as e:
        print(f"❌ Error: {str(e)}")
