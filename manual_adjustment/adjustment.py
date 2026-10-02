import sys
from psycopg2 import sql
from subprocess import run
from datetime import datetime
from helpers.db_utils import get_db_connection, upsert_financial_data, upsert_cashflow_month_data, upsert_collapse_financial_data
from benin_parser_2025.reel_import.capex_conso import process_capex_conso, insert_capex_data_to_db
from benin_parser_2025.reel_import.ca_mobile import process_ca_mobile_mapping, insert_ca_mobile_data_to_db
from benin_parser_2025.reel_import.opex_conso import process_opex_conso, insert_opex_data_to_db
from benin_parser_2025.reel_import.pnl_import import process_pnl_import, insert_pnl_data_to_db
from benin_parser_2025.reel_import.indicateurs_mobile import process_indicateurs_mobile, insert_indicateurs_to_db
from benin_parser_2025.reel_import.cash_conso import process_cash_conso, insert_data_to_db
from benin_parser_2025.reel_import.marge_brute_mobile import process_marge_mapping, insert_marge_data_to_db
from benin_parser_2025.reel_import.realise import process_realise_tbg_formulas, insert_cashflow_data_to_db, update_current_year_total, update_special_entities_current_year_total


months = {1:'jan', 2:'feb', 3:'mar', 4:'apr',
           5:'may', 6:'jun', 7:'jul', 8:'aug',
           9:'sep', 10:'oct', 11:'nov', 12:'dec'
}

def get_manual_adjustments(cur, adjustment_id):
    try:
        if not isinstance(adjustment_id, int):
            raise ValueError(f"Invalid adjustment_id: '{adjustment_id}' must be an integer")

        cur.execute("""
            SELECT reel_edits, reel_type, report_name, tbg_version,
                   month, year
            FROM tbg_reel_status_history
            WHERE id = %s
        """, (adjustment_id,))

        row = cur.fetchone()
        if row:
            reel_edits, reel_type, report_name, version_id, month, year = row
            return reel_edits or [], reel_type, report_name, version_id, month, year
        else:
            raise ValueError(f"No adjustment found with ID: {adjustment_id}")

    except Exception as e:
        raise RuntimeError(f"Error fetching manual adjustment with ID {adjustment_id}: {e}")

def get_collapsed_entity_info(cur, tbg_key):
    try:
        cur.execute("SELECT id FROM collapse_types WHERE tbg_key = %s", (tbg_key,))
        result = cur.fetchone()
        if result:
            return "type", result[0]

        cur.execute("SELECT id FROM collapse_categories WHERE tbg_key = %s", (tbg_key,))
        result = cur.fetchone()
        if result:
            return "category", result[0]

        cur.execute("SELECT id FROM collapse_subcategories WHERE tbg_key = %s", (tbg_key,))
        result = cur.fetchone()
        if result:
            return "subcategory", result[0]

        raise ValueError(f"❌ No matching collapsed entity found for TBG key: {tbg_key}")
    except Exception as e:
        raise RuntimeError(f"Error retrieving collapsed entity info for TBG key '{tbg_key}': {e}")

def get_cashflow_entity_info(cur, tbg_key):
    try:
        cur.execute("SELECT id FROM cashflow_sections WHERE tbg_key = %s", (tbg_key,))
        result = cur.fetchone()
        if result:
            return "section", result[0]

        cur.execute("SELECT id FROM cashflow_categories WHERE tbg_key = %s", (tbg_key,))
        result = cur.fetchone()
        if result:
            return "category", result[0]

        cur.execute("SELECT id FROM cashflow_subcategories WHERE tbg_key = %s", (tbg_key,))
        result = cur.fetchone()
        if result:
            return "subcategory", result[0]

        raise ValueError(f"❌ No matching cashflow entity found for TBG key: {tbg_key}")
    except Exception as e:
        raise RuntimeError(f"Error retrieving cashflow entity info for TBG key '{tbg_key}': {e}")

def get_financial_entity_info(cur, tbg_key):
    """
    Returns (entity_column, entity_id) like ('financial_metric_id', 12) based on tbg_key match.
    Raises an error if no match is found.
    """
    try:
        cur.execute("SELECT id FROM financial_types WHERE tbg_key = %s", (tbg_key,))
        result = cur.fetchone()
        if result:
            return "financial_type_id", result[0]

        cur.execute("SELECT id FROM financial_metric WHERE tbg_key = %s", (tbg_key,))
        result = cur.fetchone()
        if result:
            return "financial_metric_id", result[0]

        cur.execute("SELECT id FROM financial_submetric WHERE tbg_key = %s", (tbg_key,))
        result = cur.fetchone()
        if result:
            return "financial_submetric_id", result[0]

        raise ValueError(f"❌ No matching financial entity found for TBG key: {tbg_key}")
    except Exception as e:
        raise RuntimeError(f"Error retrieving financial entity info for TBG key '{tbg_key}': {e}")

def apply_manual_updates(adjustments, reel_type, month_key, year, version_id):
    date = datetime(year, int(month_key), 1)
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:

            def fetch_and_update(table, column_name, where_clause, where_params, added_value):
                """Helper to fetch a value, add, and update in a single pattern."""
                query = sql.SQL("SELECT {col} FROM {tbl} WHERE {where}") \
                    .format(
                        col=sql.Identifier(column_name),
                        tbl=sql.Identifier(table),
                        where=sql.SQL(where_clause)
                    )
                cur.execute(query, where_params)
                result = cur.fetchone()
                new_value = (result[0] if result and result[0] else 0) + added_value
                print(f"New Value after update: {new_value}")
                return new_value

            for update in adjustments:
                tbg_key = update["tbg_key"]
                added_value = update.get("added_value", 0)

                if not isinstance(added_value, (int, float)):
                    raise ValueError(f"❌ Invalid added_value for TBG key {tbg_key}: {added_value}")

                if reel_type == 'cashflow':
                    entity_type, entity_id = get_cashflow_entity_info(cur, tbg_key)
                    if entity_type is None or entity_id is None:
                        raise ValueError(f"❌ No matching collapsed entity for TBG key: {tbg_key}")

                    month_col = months.get(int(month_key))
                    if not month_col:
                        raise ValueError(f"❌ Invalid month key: {month_key}")

                    adjusted_month_col = f"adjusted_{month_col}"  # e.g. adjusted_apr, adjusted_may

                    value = fetch_and_update(
                        table="cashflow_data",
                        column_name=adjusted_month_col,
                        where_clause="entity_type = %s AND entity_id = %s AND version_id = %s",
                        where_params=(entity_type, entity_id, version_id),
                        added_value=added_value
                    )

                    upsert_cashflow_month_data(
                        cur,
                        entity_id=entity_id,
                        entity_type=entity_type,
                        year=year,
                        month=adjusted_month_col,
                        value=value,
                        version_id=version_id
                    )
                    # TODO: update the current_year_total as well

                else:
                    sub_type = "collapsible" if update.get("isCollapsible", False) else "financial"

                    if sub_type == "collapsible":
                        entity_type, entity_id = get_collapsed_entity_info(cur, tbg_key)
                        if entity_type is None or entity_id is None:
                            raise ValueError(f"❌ No matching collapsed entity for TBG key: {tbg_key}")

                        value = fetch_and_update(
                            table="collapse_monthly_data",
                            column_name="adjusted_value",
                            where_clause="entity_type = %s AND entity_id = %s AND version_id = %s",
                            where_params=(entity_type, entity_id, version_id),
                            added_value=added_value
                        )

                        upsert_collapse_financial_data(
                            cur=cur,
                            table_name="collapse_monthly_data",
                            entity_id=entity_id,
                            entity_type=entity_type,
                            date_value=date,
                            adjusted_value=value,
                            version_id=version_id
                        )

                    elif sub_type == "financial":
                        column, entity_id = get_financial_entity_info(cur, tbg_key)
                        if column is None or entity_id is None:
                            raise ValueError(f"❌ No matching financial entity for TBG key: {tbg_key}")

                        value = fetch_and_update(
                            table="financial_metrics_data",
                            column_name="adjusted_value",
                            where_clause=f"{column} = %s AND version_id = %s",
                            where_params=(entity_id, version_id),
                            added_value=added_value
                        )

                        upsert_financial_data(
                            cur=cur,
                            table_name="financial_metrics_data",
                            type_id=entity_id if column == 'financial_type_id' else None,
                            metric_id=entity_id if column == 'financial_metric_id' else None,
                            submetric_id=entity_id if column == 'financial_submetric_id' else None,
                            date_value=date,
                            adjusted_value=value,
                            version_id=version_id,
                        )

                    else:
                        raise ValueError(f"❌ Unknown reel_type/sub_type: {sub_type}")

        conn.commit()

    except Exception as e:
        conn.rollback()
        raise RuntimeError(f"Failed to apply manual updates: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    adjustment_id = int(sys.argv[1])

    conn = get_db_connection()
    with conn.cursor() as cur:
        # Fetch details from tbg_reel_status_history
        adjustments, reel_type, report_name, version_id, month, year = get_manual_adjustments(cur, adjustment_id)

        # Apply the updates
        apply_manual_updates(adjustments, reel_type, month, year, version_id)

    # Generate the date string
    date = f"{year}-{str(month).zfill(2)}-01"
    report_name_upper = report_name.upper()
    month_year = f"{str(month).zfill(2)}{year}"

    # Main report processors
    report_processors = {
        "CAPEX CONSOLIDÉS": {
            "func": process_capex_conso,
            "func_args": (date, version_id, 2, True),
            "db_func": insert_capex_data_to_db,
            "db_args": lambda df: (df,),
            "success_msg": "✅ CapexConso recalculation and DB insertion complete.",
            "error_msg": "❌ Error during CapexConso post-processing:"
        },
        "CA MOBILE": {
            "func": process_ca_mobile_mapping,
            "func_args": (date, version_id, 5, True),
            "db_func": insert_ca_mobile_data_to_db,
            "db_args": lambda df: (df,),
            "success_msg": "✅ CA Mobile recalculation and DB insertion complete.",
            "error_msg": "❌ Error during CA Mobile post-processing:"
        },
        "OPEX CONSOLIDÉS": {
            "func": process_opex_conso,
            "func_args": (date, version_id, 4, True),
            "db_func": insert_opex_data_to_db,
            "db_args": lambda df: (df,),
            "success_msg": "✅ Opex Conso recalculation and DB insertion complete.",
            "error_msg": "❌ Error during Opex Conso post-processing:"
        },
        "REALISE DE TRESORERIE": {
            "func": process_realise_tbg_formulas,
            "func_args": (month_year, date, version_id, 1000, True),
            "db_func": insert_cashflow_data_to_db,
            "db_args": lambda df: (df, month_year),
            "success_msg": "✅ Realise recalculation and DB insertion complete.",
            "error_msg": "❌ Error during Realise post-processing:"
        }
    }

    # Step 1: Process main report
    processor = report_processors.get(report_name_upper)
    print(f"processor_name: {processor}")
    if processor:
        try:
            df = processor["func"](*processor["func_args"])
            processor["db_func"](*processor["db_args"](df))
            print(processor["success_msg"])
        except Exception as e:
            raise RuntimeError(f"{processor['error_msg']} {e}")
    else:
        print(f"⚠️ No processing logic defined for report: {report_name} — skipping...")

    # Step 2: Process Marge Brute
    try:
        df_marge = process_marge_mapping(date, version_id, 6, True)
        insert_marge_data_to_db(df_marge)
        print("✅ Marge Brute Import processing and DB insertion complete.")
    except Exception as e:
        raise RuntimeError(f"❌ Error during PnL Import post-processing: {e}")

    # Step 3: Process Pnl Conso
    try:
        df_pnl_import = process_pnl_import(date, version_id, 1, True)
        insert_pnl_data_to_db(df_pnl_import)
        print("✅ PnL Import processing and DB insertion complete.")
    except Exception as e:
        raise RuntimeError(f"❌ Error during PnL Import post-processing: {e}")

    # Step 4: Process Indicateurs Mobile
    try:
        df_indicateurs = process_indicateurs_mobile(date, version_id, 11, True)
        insert_indicateurs_to_db(df_indicateurs)
        print("✅ Indicateurs Mobile processing and DB insertion complete.")
    except Exception as e:
        raise RuntimeError(f"❌ Error during Indicateurs Mobile post-processing: {e}")

    # Step 5: Process Cash Consolide
    try:
        df_cash_conso = process_cash_conso(date, version_id, 3, True)
        insert_data_to_db(df_cash_conso)
        print("✅ Cash Consolide processing and DB insertion complete.")
    except Exception as e:
        raise RuntimeError(f"❌ Error during Cash Consolide post-processing: {e}")

    # Step 6: Get version_name from DB and run final import command
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            cur.execute("SELECT version_name FROM tbg_version WHERE id = %s", (version_id,))
            result = cur.fetchone()
            if not result:
                raise ValueError(f"❌ Could not find version_name for version_id: {version_id}")
            version_name = result[0]
    except Exception as e:
        raise RuntimeError(f"❌ Error fetching version_name: {e}")
    finally:
        conn.close()

    # Step 7: Run final command
    monthyear = f"{str(month).zfill(2)}{year}"
    print(f"📦 Executing final import command for {monthyear} {version_name}...")
    run(["python3", "-m", "benin_parser_2025.import_cumul", monthyear, version_name], check=True)
    print("✅ Cumulative import completed.")

    # --- update the current year total ---
    print("⚙️ Updating current_year_total for all rows...")
    update_current_year_total(version_id, int(year), int(month))

    print("⚙️ Updating current_year_total for specific entities...")
    conn = get_db_connection()
    try:
        update_special_entities_current_year_total(conn, version_id, year, month)
    finally:
        conn.close()
