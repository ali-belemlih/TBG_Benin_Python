import sys
import pandas as pd

from tbg_formula.formula_evaluator import evaluate_tbg_formula
from tbg_formula.db_helper import get_tbg_report_mapping, find_tbg_key_in_table
from helpers.db_utils import (
    get_db_connection,
    upsert_financial_data,
    get_version_id_by_name,
    get_real_or_budget_value,
    upsert_collapse_financial_data,
    get_sage_real_value,
    get_calculation_field_value,
)
from contextlib import closing

def update_real_values_from_sage_query(date, version_id, sage_version):
    conn = get_db_connection()
    with conn.cursor() as cur:
        # --- OPX765 + OPX091 -> entity_id=135 ---
        value_765 = get_sage_real_value(cur, sage_version, "OPX765") / 1_000_000
        value_091 = get_sage_real_value(cur, sage_version, "OPX091") / 1_000_000
        total_135 = value_765 + value_091

        upsert_collapse_financial_data(
            cur=cur,
            table_name="collapse_monthly_data",
            entity_id=135,
            entity_type="type",
            date_value=date,
            real_value=total_135,
            version_id=version_id,
        )
        print(
            f"[collapse_monthly_data] entity_id=135: OPX765 ({value_765}) + OPX091 ({value_091}) = {total_135}"
        )

        # --- Get existing value for entity_id=99 ---
        cur.execute(
            """
            SELECT real_value
            FROM collapse_monthly_data
            WHERE entity_type = 'type'
              AND entity_id = 99
              AND version_id = %s
              AND date = %s;
        """,
            (version_id, date),
        )
        row = cur.fetchone()
        existing_99 = float(row[0]) if row and row[0] is not None else 0.0

        # --- OPX035 + existing_99 -> entity_id=91 ---
        value_035 = get_sage_real_value(cur, sage_version, "OPX035") / 1_000_000
        total_99 = existing_99 + value_035
        # Due to some reason we were adding value_035 to the current value of entity_id=99, but as per meeting with Assane and customer on 18/02/2026, we don't need this
        upsert_collapse_financial_data(
            cur=cur,
            table_name="collapse_monthly_data",
            entity_id=99,
            entity_type="type",
            date_value=date,
            real_value=existing_99,
            version_id=version_id,
        )
        print(
            f"[collapse_monthly_data] entity_id=91: existing ({existing_99}) + OPX035 ({value_035}) = {total_99}"
        )

    conn.commit()
    conn.close()

def process_opex_conso(date, version_id, report_type_id, is_adjustible_only=None):
    cache = {}
    results_list = []

    with closing(get_db_connection()) as conn:

        fetched_mapping = get_tbg_report_mapping(conn, report_type_id)

        for record in fetched_mapping:
            (
                formula_id,
                tbg_key,
                report_type_id,
                formula_type,
                account_details,
                include_sage,
                formula,
                is_adjustable,
                created_at,
                updated_at,
                sequence,
            ) = record

            if is_adjustible_only and not is_adjustable:
                continue

            base_record_found = find_tbg_key_in_table(conn, tbg_key)

            if not base_record_found:
                print(f"⚠ Warning: Base key '{tbg_key}' not found. Skipping.")
                continue

            base_col_name, base_table, base_tbg_key_id = base_record_found
            print(f"TBG Key: {tbg_key}")
            final_result = evaluate_tbg_formula(
                conn,
                tbg_key,
                formula,
                version_id,
                cache
            )

            print(f"✅ Final result for [{tbg_key}] = {final_result}")

            results_list.append(
                {
                    "label": "real_value",
                    "financial_type_id": base_tbg_key_id if base_col_name == "financial_type_id" else None,
                    "financial_metric_id": base_tbg_key_id if base_col_name == "financial_metric_id" else None,
                    "financial_submetric_id": base_tbg_key_id if base_col_name == "financial_submetric_id" else None,
                    "entity_type": "type" if base_col_name == "collapse_type_id" else None,
                    "entity_id": base_tbg_key_id if base_col_name == "collapse_type_id" else None,
                    "real_value": final_result,
                    "date": date,
                    "version_id": version_id,
                }
            )

    df_result = pd.DataFrame(results_list)

    output_csv_path = f"benin_parser_2025/reel_import/outputs/opex_conso_{date}.csv"
    # df_result.to_csv(output_csv_path, index=False)

    print(f"📁 CSV file for {date} generated successfully at: {output_csv_path}")

    return df_result

month_column_map = {
    1: "C",
    2: "D",
    3: "E",
    4: "F",
    5: "G",
    6: "H",
    7: "I",
    8: "J",
    9: "K",
    10: "L",
    11: "M",
    12: "N",
}


def update_real_value_from_calculation_field(date, version_id):
    conn = get_db_connection()
    cur = conn.cursor()

    source_info = {
        "table_name": "collapse_monthly_data",
        "entity_type": "type",
        "entity_id": 54,
    }

    try:
        # --- Fetch current DB value ---
        db_value = get_real_or_budget_value(
            cur, source_info, date, "real_value", version_id
        )
        print(f"📦 Existing DB value: {db_value}")

        # --- Fetch calculation field value (Opex62) ---
        calc_val = get_calculation_field_value(
            cur, "Opex62", date, "IMPACT IFRS", version_id
        )
        print(f"📊 Raw calculation field (Opex62): {calc_val}")

        # --- Normalize (if not already in millions) ---
        if abs(calc_val) > 1000:
            calc_val = calc_val / 1_000_000
            print(f"🔄 Converted Opex62 to millions: {calc_val}")
        else:
            print(f"✅ Opex62 already in millions: {calc_val}")

        # --- Compute final value ---
        final_real_value = db_value - calc_val
        print(f"🧮 Final real_value = {db_value} - {calc_val} = {final_real_value}")

        # --- Upsert into collapse_monthly_data ---
        upsert_collapse_financial_data(
            cur=cur,
            table_name="collapse_monthly_data",
            entity_id=54,
            entity_type="type",
            date_value=date,
            real_value=final_real_value,
            version_id=version_id,
        )

        conn.commit()
        print(f"✅ Real value from Opex62 inserted for entity_id=54, date={date}")

    except Exception as e:
        conn.rollback()
        print(f"❌ Failed to update real value from Opex62: {e}")
    finally:
        cur.close()
        conn.close()


def insert_opex_data_to_db(result_df):
    conn = get_db_connection()
    cur = conn.cursor()
    print("Database connection successful!")

    for _, row in result_df.iterrows():
        type_id = row["financial_type_id"]
        metric_id = row["financial_metric_id"]
        submetric_id = row.get("financial_submetric_id")
        entity_type = row.get("entity_type")
        entity_id = row.get("entity_id")
        date_value = row["date"]
        real_value = row["real_value"]
        version_id = row["version_id"]

        # Convert pandas NA/nan to None
        type_id = None if pd.isna(type_id) else type_id
        metric_id = None if pd.isna(metric_id) else metric_id
        submetric_id = None if pd.isna(submetric_id) else submetric_id
        entity_type = None if pd.isna(entity_type) else entity_type
        entity_id = None if pd.isna(entity_id) else entity_id
        real_value = None if pd.isna(real_value) else real_value

        if type_id is not None or metric_id is not None or submetric_id is not None:
            upsert_financial_data(
                cur=cur,
                table_name="financial_metrics_data",
                type_id=type_id,
                metric_id=metric_id,
                submetric_id=submetric_id,
                date_value=date_value,
                real_value=real_value,
                version_id=version_id,
            )
        elif entity_type is not None or entity_id is not None:
            upsert_collapse_financial_data(
                cur,
                table_name="collapse_monthly_data",
                entity_id=entity_id,
                entity_type=entity_type,
                date_value=date_value,
                real_value=real_value,
                version_id=version_id,
            )

    conn.commit()
    cur.close()
    conn.close()
    print("Data insertion to database completed!")


if __name__ == "__main__":
    target_month = sys.argv[1][:2]
    target_year = sys.argv[1][2:]
    date = f"{target_year}-{target_month}-01"  # Format: YYYY-MM-01
    sage_version = sys.argv[3]

    report_type_id = 4

    # fetch version id
    version_id = get_version_id_by_name(sys.argv[2])

    try:
        update_real_value_from_calculation_field(date, version_id)
        # update_real_values_from_sage_query(date, version_id, sage_version)
        df_opex = process_opex_conso(date, version_id, report_type_id)
        insert_opex_data_to_db(df_opex)
        print("✅ Data successfully prepared and inserted into DB.")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
