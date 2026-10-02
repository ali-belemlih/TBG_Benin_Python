import sys
import pandas as pd
from datetime import datetime

from tbg_formula.formula_evaluator import evaluate_tbg_formula
from tbg_formula.db_helper import get_tbg_report_mapping, find_tbg_key_in_table
from helpers.db_utils import (
    get_db_connection, 
    upsert_collapse_financial_data, 
    get_version_id_by_name, 
    upsert_financial_data, 
    get_real_or_budget_value
)
from helpers.formula_utils.excel_parser import calculate_formula
from .mapping.ca_mobile_mapping import ca_mobile_sheet_mapping
from services.minio_factory import get_minio_service
from contextlib import closing

def update_values_from_sage_query(date, version_id, sage_version):
    metric_id = 64
    type_id = None
    submetric_id = None
    date_value = date

    ymois = str(date.month)
    yannee = str(date.year)

    conn = get_db_connection()
    cur = conn.cursor()

    try:
        query = """
            SELECT amtval_0
            FROM public.sage_yexptdb
            WHERE txsnam_0 = 'YYCAMOBILE'
              AND version_0 = 'YEXPTDB'
              AND ind_0 = '0'
              AND col_0 IN ('0', '1')
              AND ymois_0 = %s
              AND yannee_0 = %s
              AND lig_0 = '145'
              AND sage_version = %s
        """
        cur.execute(query, (ymois, yannee, sage_version))
        results = cur.fetchall()

        if not results:
            print("No records found in public.sage_yexptdb for the given filters.")
            return

        total_amtval = float(results[1][0]) / 1_000_000

        print(f"[update_values_from_sage_query] Total AMTVAL_0 = {total_amtval}")

        upsert_financial_data(
            cur=cur,
            table_name="financial_metrics_data",
            type_id=type_id,
            metric_id=metric_id,
            submetric_id=submetric_id,
            date_value=date_value,
            real_value=total_amtval,
            version_id=version_id,
            budget_value=None
        )
        conn.commit()
        print(f"[upsert_financial_data] metric_id={metric_id}, real_value={total_amtval}")

    except Exception as e:
        print(f"Error in update_values_from_sage_query: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()

def process_ca_mobile_data(date, file_bytes, version_id, cur):
    results = []

    for mapping in ca_mobile_sheet_mapping.values():
        formula = mapping["formula"]["data"]
        sheet_name = mapping["sheet"]
        entity_type = mapping.get("entity_type", None)
        entity_id = mapping.get("entity_id", None)
        column_name = mapping.get("column_name", None)

        try:
            db_value = get_real_or_budget_value(cur, mapping, date, 'real_value', version_id)
            formula_value = calculate_formula(formula, sheet_name, file_bytes) / 1_000_000
            if sheet_name == "Crédits secours" or sheet_name == 'COLOCALISATION':
                result = formula_value
            else:
                result = formula_value + db_value
        except Exception as e:
            print(f"Error processing entity_id {entity_id} with formula {formula}: {e}")
            result = None

        results.append({
            "financial_type_id": mapping.get("value") if column_name == "financial_type_id" else None,
            "entity_id" : entity_id,
            "entity_type": entity_type,
            "real_value": result,
            "date": date,
            "version_id" : version_id
        })

    df_csv = pd.DataFrame(results)
    output_csv_path = f'benin_parser_2025/reel_import/ca_mobile_sheet_{date}.csv'
    df_csv.to_csv(output_csv_path, index=False)
    print(f"✅ CSV file for {date} generated successfully at: {output_csv_path}")
    return df_csv

def process_ca_mobile_mapping(date, version_id, report_type_id, is_adjustible_only=None):

    results_list = []
    cache = {}

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

            base_record = find_tbg_key_in_table(conn, tbg_key)
            if not base_record:
                continue

            base_col_name, base_table, base_tbg_key_id = base_record

            final_result = evaluate_tbg_formula(
                conn,
                tbg_key,
                formula,
                version_id,
                cache
            )
            print(f"Result for {tbg_key}: {final_result}")
            results_list.append({
                "label": "real_value",
                "financial_type_id": base_tbg_key_id if base_table == "financial_types" else None,
                "financial_metric_id": base_tbg_key_id if base_table == "financial_metric" else None,
                "financial_submetric_id": base_tbg_key_id if base_table == "financial_submetric" else None,
                "entity_type": (
                    "type" if base_table == "collapse_types"
                    else "category" if base_table == "collapse_categories"
                    else "subcategory" if base_table == "collapse_subcategories"
                    else None
                ),
                "entity_id": (
                    base_tbg_key_id if base_col_name in [
                        "collapse_type_id",
                        "collapse_category_id",
                        "collapse_subcategory_id"
                    ] else None
                ),
                "real_value": final_result,
                "date": date,
                "version_id": version_id
            })

    return pd.DataFrame(results_list)

def insert_ca_mobile_data_to_db(result_df):
    conn = get_db_connection()
    cur = conn.cursor()
    print("Database connection successful!")

    for _, row in result_df.iterrows():
        type_id = row.get("financial_type_id") or None
        metric_id = row.get("financial_metric_id") or None
        submetric_id = row.get('financial_submetric_id') or None
        entity_id = row.get("entity_id") or None
        entity_type = row.get("entity_type") or None
        date_value = row['date']
        real_value = row['real_value']
        version_id = row['version_id']

        # Convert pandas NA/nan to None
        type_id = None if pd.isna(type_id) else type_id
        metric_id = None if pd.isna(metric_id) else metric_id
        submetric_id = None if pd.isna(submetric_id) else submetric_id
        real_value = None if pd.isna(real_value) else real_value
        entity_id = int(entity_id) if isinstance(entity_id, float) and entity_id.is_integer() else entity_id

        if type_id is not None or metric_id is not None or submetric_id is not None:
            upsert_financial_data(
                cur=cur,
                table_name="financial_metrics_data",
                type_id=type_id,
                metric_id=metric_id,
                submetric_id=submetric_id,
                date_value=date_value,
                real_value=real_value,
                version_id = version_id,
                budget_value=None
            )

        if entity_type is not None or entity_id is not None:
            upsert_collapse_financial_data(
                cur, "collapse_monthly_data",
                entity_id, entity_type,
                date_value,
                real_value=real_value,
                version_id = version_id
            )

    conn.commit()
    print("Data insertion to database completed!")

if __name__ == "__main__":
    target_month = sys.argv[1][:2]
    target_year = sys.argv[1][2:]
    date_obj = datetime.strptime(sys.argv[1], "%m%Y")
    date = date_obj.strftime("%Y-%m-01")
    report_type_id = 5

    file_name = sys.argv[3].strip() if len(sys.argv) > 3 else ""
    sage_version = sys.argv[4]

    object_path = f"{target_year}/{target_year}{target_month}/{file_name}" if file_name else None
    if object_path:
        print(f"Fetching file from MinIO path: {object_path}")
    try:
        # Setup
        version_id = get_version_id_by_name(sys.argv[2])
        minio_service = get_minio_service()

        # DB Connection
        conn = get_db_connection()
        with conn:
            cur = conn.cursor()

            # Process DB & Excel data
            # update_values_from_sage_query(date_obj, version_id, sage_version)

            # Run only if file provided
            if file_name:
                file_bytes = minio_service.get_file_bytes(object_path)
                df_sheet = process_ca_mobile_data(date, file_bytes, version_id, cur)
                insert_ca_mobile_data_to_db(df_sheet)

            df_mapping = process_ca_mobile_mapping(date, version_id, report_type_id)
            insert_ca_mobile_data_to_db(df_mapping)

        cur.close()
        conn.close()
    except Exception as e:
        print(f"[ERROR] An exception occurred: {e}")
