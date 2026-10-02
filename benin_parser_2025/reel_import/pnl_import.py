import sys
import pandas as pd

from helpers.db_utils import (
    get_db_connection,
    upsert_financial_data,
    get_version_id_by_name,
    get_calculation_field_value,
)
from contextlib import closing
from tbg_formula.formula_evaluator import evaluate_tbg_formula
from tbg_formula.db_helper import get_tbg_report_mapping, find_tbg_key_in_table


def update_real_value_from_cart_esim(date, version_id):
    conn = get_db_connection()
    cur = conn.cursor()

    try:
        # --- Fetch existing real_value from DB ---
        cur.execute(
            """
            SELECT real_value
            FROM financial_metrics_data
            WHERE financial_metric_id = %s AND date = %s AND version_id = %s
        """,
            (84, date, version_id),
        )
        row = cur.fetchone()
        db_real_value = row[0] if row else 0.0
        print(f"📦 Existing DB value: {db_real_value}")

        # --- Fetch calculation field value (using TBG KEY = PL30) ---
        cart_esim = get_calculation_field_value(
            cur, "PL30", date, "CART E SIM", version_id
        )
        activation = get_calculation_field_value(
            cur, "PL30", date, "ACTIVATION", version_id
        )

        calc_value = (cart_esim + activation)/1_000_000
        print(
            f"🧮 PL30 total = CART E SIM ({cart_esim}) + ACTIVATION ({activation}) → {calc_value}"
        )

        # --- Final total = db value + calculation field value ---
        total = db_real_value + calc_value
        print(f"➕ New total = {db_real_value} + {calc_value} = {total}")

        # Upsert total
        upsert_financial_data(
            cur,
            "financial_metrics_data",
            type_id=None,
            metric_id=84,
            submetric_id=None,
            date_value=date,
            real_value=total,
            version_id=version_id,
        )
        conn.commit()
        print(f"✅ Updated total value for metric_id=84 inserted.")
    except Exception as e:
        conn.rollback()
        print(f"❌ Failed to update DB: {e}")
    finally:
        cur.close()
        conn.close()

def update_real_value_from_tbg_ifrs(date, version_id):
    conn = get_db_connection()
    cur = conn.cursor()

    try:
        # --- Get cell value from calculation fields (TBG Key = PL46) ---
        cell_value = get_calculation_field_value(
            cur, "PL46", date, "TBG IFRS", version_id
        )
        print(f"📊 Raw cell_value from PL46: {cell_value}")

        # --- Ensure it's in millions ---
        # Assume: if absolute value > 1000, then it's in base units, so convert
        real_value = -1 * (cell_value / 1_000_000)

        # --- Upsert ---
        upsert_financial_data(
            cur,
            "financial_metrics_data",
            type_id=None,
            metric_id=None,
            submetric_id=22,
            date_value=date,
            real_value=real_value,
            version_id=version_id,
        )
        conn.commit()
        print(
            f"✅ Real value from PL46 inserted for financial_submetric_id=22, date={date}"
        )

    except Exception as e:
        conn.rollback()
        print(f"❌ Failed to insert Excel value into DB: {e}")
    finally:
        cur.close()
        conn.close()

def update_data_from_impact_ifrs(date, version_id):
    conn = get_db_connection()
    cur = conn.cursor()

    try:
        # --- Fetch calculation field values ---
        calc_val_pl30 = get_calculation_field_value(
            cur, "PL30", date, "IMPACT IFRS", version_id
        )  # maps to metric_id=84
        calc_val_pl41 = get_calculation_field_value(
            cur, "PL41", date, "IMPACT IFRS", version_id
        )  # maps to metric_id=86

        print(f"📊 Calculation values → PL30={calc_val_pl30}, PL41={calc_val_pl41}")

        # --- Fetch current DB values ---
        def fetch_existing_metric_value(metric_id):
            cur.execute(
                """
                SELECT real_value
                FROM financial_metrics_data
                WHERE financial_metric_id = %s AND version_id = %s
            """,
                (metric_id, version_id),
            )
            row = cur.fetchone()
            return row[0] if row and row[0] is not None else 0.0

        db_val_metric84 = fetch_existing_metric_value(84)
        db_val_metric86 = (
            fetch_existing_metric_value(86) * -1
        )  # invert sign as per business rule
        print(f"📦 DB values → metric84={db_val_metric84}, metric86={db_val_metric86}")

        # --- Normalize calculation values (ensure in millions) ---
        def normalize_to_millions(value):
            return value / 1_000_000

        norm_calc_val_84 = normalize_to_millions(calc_val_pl30)
        norm_calc_val_86 = normalize_to_millions(calc_val_pl41)

        # --- Compute totals (DB + calculation field) ---
        final_val_metric84 = db_val_metric84 + norm_calc_val_84
        final_val_metric86 = db_val_metric86 + norm_calc_val_86
        print(
            f"🧮 Totals → metric84={final_val_metric84}, metric86={final_val_metric86}"
        )

        # --- Upsert results ---
        upsert_financial_data(
            cur,
            "financial_metrics_data",
            type_id=None,
            metric_id=84,
            submetric_id=None,
            date_value=date,
            real_value=final_val_metric84,
            version_id=version_id,
        )

        upsert_financial_data(
            cur,
            "financial_metrics_data",
            type_id=None,
            metric_id=86,
            submetric_id=None,
            date_value=date,
            real_value=final_val_metric86,
            version_id=version_id,
        )

        conn.commit()
        print("✅ Impact IFRS values updated successfully.")

    except Exception as e:
        conn.rollback()
        print(f"❌ Failed to insert calculation field values into DB: {e}")
    finally:
        cur.close()
        conn.close()

def process_pnl_import(date, version_id, report_type_id, is_adjustible_only=None):
    results_list = []
    cache = {}

    with closing(get_db_connection()) as conn:

        fetched_mapping = get_tbg_report_mapping(conn, report_type_id)

        if not fetched_mapping:
            print("❌ No record found for the passed report type.")
            return pd.DataFrame()

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
                print("⚠ Base TBG key '{}' not found. Skipping...".format(tbg_key))
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

    df_csv = pd.DataFrame(results_list)

    output_csv_path = "benin_parser_2025/reel_import/outputs/pnl_{}.csv".format(date)
    # df_csv.to_csv(output_csv_path, index=False)

    print("✅ CSV file for {} generated successfully at: {}".format(date, output_csv_path))

    return df_csv


def insert_pnl_data_to_db(result_df):
    conn = get_db_connection()
    cur = conn.cursor()
    print("Database connection successful!")

    for _, row in result_df.iterrows():
        type_id = row["financial_type_id"]
        metric_id = row["financial_metric_id"]
        submetric_id = row.get("financial_submetric_id")
        date_value = row["date"]
        real_value = row["real_value"]
        version_id = row["version_id"]

        # Convert pandas NA/nan to None
        type_id = None if pd.isna(type_id) else type_id
        metric_id = None if pd.isna(metric_id) else metric_id
        submetric_id = None if pd.isna(submetric_id) else submetric_id
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
                budget_value=None,
            )

    conn.commit()
    cur.close()
    conn.close()
    print("Data insertion to database completed!")


if __name__ == "__main__":
    target_month = sys.argv[1][:2]
    target_year = sys.argv[1][2:]
    date = f"{target_year}-{target_month}-01"  # Format: YYYY-MM-01
    report_type_id = 1
    # fetch version id
    version_id = get_version_id_by_name(sys.argv[2])
    try:
        update_real_value_from_tbg_ifrs(date, version_id)
        update_real_value_from_cart_esim(date, version_id)
        update_data_from_impact_ifrs(date, version_id)
        df_pnl_import = process_pnl_import(date, version_id, report_type_id)
        insert_pnl_data_to_db(df_pnl_import)
        print("✅ Data successfully prepared and inserted into DB.")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
