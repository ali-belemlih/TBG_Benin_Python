import os
import re
import logging
from datetime import datetime
import psycopg2
from dotenv import load_dotenv
import cx_Oracle
from delta_generation.mapping.sage_account_mapping import sage_accounts
import time
load_dotenv()

# --- CONFIGURATION ---
SAGE_KEY_TABLES = [
    {"table": "financial_metric", "id_col": "id", "map_key": "financial_metric_id"},
    {"table": "financial_submetric", "id_col": "id", "map_key": "financial_submetric_id"},
    {"table": "financial_types", "id_col": "id", "map_key": "financial_type_id"},
    {"table": "collapse_types", "id_col": "id", "map_key": "entity_id", "type": "type"},
    {"table": "collapse_categories", "id_col": "id", "map_key": "entity_id", "type": "category"},
    {"table": "collapse_subcategories", "id_col": "id", "map_key": "entity_id", "type": "subcategory"},
]

# Initialize global hash for sage key cumulative values
sage_cuml_for_sage_key_hash = {}


# -------------------------------------------------------
# DB CONNECTION
# -------------------------------------------------------
def get_db_connection(db_config):
    return psycopg2.connect(**db_config)


def get_txsnam(source_key: str):
    """Dynamic TXSNAM based on prefix."""
    if source_key.startswith("CAM"): return "YYCAMOBILE"
    if source_key.startswith("OPX"): return "YYOPEX"
    if source_key.startswith("CPX"): return "CAPEXCONSO"
    if source_key.startswith("MBM"): return "YYMARGE"
    if source_key.startswith("PLC"): return "YYPLCONSO"

    return ""


def load_sage_key_delta_query():
    if os.getenv("ENVIRONMENT") == "TEST":
        return open("delta_generation/sql/sage_key_delta_query_psql.sql").read()
    return open("delta_generation/sql/sage_key_delta_query_oracle.sql").read()


def load_query():
    if os.getenv("ENVIRONMENT") == "TEST":
        return open("delta_generation/sql/delta_psql.sql").read()
    return open("delta_generation/sql/delta_oracle.sql").read()


# -------------------------------------------------------
# PHASE 1: SAGE KEY LOGIC
# -------------------------------------------------------
def fetch_sage_key_cumul_oracle(moov_conn, source_key, year, month):
    txsnam = get_txsnam(source_key)

    query = load_sage_key_delta_query()
    with moov_conn.cursor() as cur:
        if os.getenv("ENVIRONMENT") == 'TEST':
            cur.execute(query, (txsnam, str(year), str(month), source_key))
        else:
            cur.execute(query, {
                "txsnam": txsnam,
                "year": year,
                "month" : month,
                "sage_source_key": source_key
            }
                        )

        row = cur.fetchone()
        return row[1] if row and row[1] else 0.0


def run_sage_key_step(conn, moov_conn, version_id, year, date_value, month):
    print(">>> Starting Phase 1: Sage Key Delta Calculation")
    for config in SAGE_KEY_TABLES:
        with conn.cursor() as cur:
            cur.execute(
                f"SELECT {config['id_col']}, sage_source_key FROM {config['table']} WHERE sage_source_key IS NOT NULL")
            rows = cur.fetchall()

            for item_id, sage_key in rows:
                # 1. Get Oracle YTD
                sage_cumul_raw = fetch_sage_key_cumul_oracle(moov_conn, sage_key, year,month)
                final_sage_result = sage_cumul_raw / 1_000_000

                # 2. Build mapping for update logic
                mapping = {config['map_key']: item_id}
                if "type" in config:
                    mapping["entity_type"] = config["type"]

                # 3. Get existing PG cumul
                current_pg_cumul = fetch_cumulative_real_value(conn, mapping, date_value, version_id)

                # 4. Calc Delta
                delta = float(final_sage_result) - current_pg_cumul

                # 5. Store sage cumulative value for sage key hash Global Hash
                sage_cuml_for_sage_key_hash[sage_key] = final_sage_result

                # 6. Update
                update_sage_cumul(conn, mapping, final_sage_result, date_value, version_id)
                update_delta_value(conn, mapping, delta, date_value, version_id)
                print(f"Updated Sage Key {sage_key} (Table: {config['table']}, id : {item_id}): Delta {round(delta, 2)}")
                print(f"SAGE CUMUL VALUE : ",round(sage_cumul_raw,2))


# -------------------------------------------------------
# PARSE (acc,cpy) TOKENS
# Example: "(661100,MOM)"
# -------------------------------------------------------
def extract_account_pairs(formula: str):
    return re.findall(r"\((\d+),\s*([A-Z0-9]+)\)", formula)


# -------------------------------------------------------
# FETCH ORACLE CUMULATIVE VALUE
# -------------------------------------------------------
def fetch_oracle_cumulative(moov_conn, acc_0, cpy_0, month, year):
    query = load_query()
    with moov_conn.cursor() as cur:
        if os.getenv("ENVIRONMENT") == 'TEST':
            cur.execute(query, (year, year,acc_0, cpy_0))
        else:
            cur.execute(query, {
                'year': year,
                'acc_0': acc_0,
                'cpy_0': cpy_0
            })
        row = cur.fetchone()
        if not row:
            return 0.0

        # month columns start at index 3
        return sum((row[i] or 0) for i in range(3, 3 + month))


# -------------------------------------------------------
# FETCH PG CUMULATIVE VALUE
# -------------------------------------------------------
def fetch_cumulative_real_value(conn, mapping, date_value, version_id):
    with conn.cursor() as cur:
        if "entity_id" in mapping:
            cur.execute("""
                        SELECT COALESCE(real_value, 0)
                        FROM collapse_cumul_data
                        WHERE entity_id = %s
                          AND entity_type = %s
                          AND date =%s
                          AND version_id=%s
                        """, (mapping["entity_id"], mapping["entity_type"], date_value, version_id))

        elif "financial_metric_id" in mapping:
            cur.execute("""
                        SELECT COALESCE(real_value, 0)
                        FROM financial_cumulative_data
                        WHERE financial_metric_id = %s
                          AND date =%s
                          AND version_id=%s
                        """, (mapping["financial_metric_id"], date_value, version_id))

        elif "financial_submetric_id" in mapping:
            cur.execute("""
                        SELECT COALESCE(real_value, 0)
                        FROM financial_cumulative_data
                        WHERE financial_submetric_id = %s
                          AND date =%s
                          AND version_id=%s
                        """, (mapping["financial_submetric_id"], date_value, version_id))
        else:
            return 0.0

        row = cur.fetchone()
        return row[0] if row else 0.0


# -------------------------------------------------------
# UPDATE DELTA VALUE
# -------------------------------------------------------
def update_delta_value(conn, mapping, delta_value, date_value, version_id):
    with conn.cursor() as cur:
        if "entity_id" in mapping:
            cur.execute("""
                        UPDATE collapse_monthly_data
                        SET delta_value=%s,
                            updated_at=CURRENT_TIMESTAMP
                        WHERE entity_id = %s
                          AND entity_type = %s
                          AND date =%s
                          AND version_id=%s
                        """, (
                            delta_value,
                            mapping["entity_id"],
                            mapping["entity_type"],
                            date_value,
                            version_id
                        ))

        else:
            if mapping.get("financial_type_id"):
                cur.execute("""
                            UPDATE financial_metrics_data
                            SET delta_value=%s,
                                updated_at=CURRENT_TIMESTAMP
                            WHERE financial_type_id = %s
                            AND date =%s
                            AND version_id=%s
                            """, (delta_value, mapping.get("financial_type_id"), date_value, version_id))
            elif mapping.get("financial_metric_id"):
                cur.execute("""
                            UPDATE financial_metrics_data
                            SET delta_value=%s,
                                updated_at=CURRENT_TIMESTAMP
                            WHERE financial_metric_id = %s
                            AND date =%s
                            AND version_id=%s
                            """, (delta_value, mapping.get("financial_metric_id"), date_value, version_id))
            elif mapping.get("financial_submetric_id"):
                cur.execute("""
                            UPDATE financial_metrics_data
                            SET delta_value=%s,
                                updated_at=CURRENT_TIMESTAMP
                            WHERE financial_submetric_id = %s
                            AND date =%s
                            AND version_id=%s
                            """, (delta_value, mapping.get("financial_submetric_id"), date_value, version_id))
            else:
                print(f"Inside update_delta_value: No financial type, metric, or submetric found for mapping: {mapping}")
            
            # cur.execute("""
            #             UPDATE financial_metrics_data
            #             SET delta_value=%s,
            #                 updated_at=CURRENT_TIMESTAMP
            #             WHERE (%s IS NULL OR financial_metric_id = %s)
            #               AND (%s IS NULL OR financial_submetric_id = %s)
            #               AND (%s IS NULL OR financial_type_id = %s)
            #               AND date =%s
            #               AND version_id=%s
            #             """, (
            #                 delta_value,
            #                 mapping.get("financial_metric_id"),
            #                 mapping.get("financial_metric_id"),
            #                 mapping.get("financial_submetric_id"),
            #                 mapping.get("financial_submetric_id"),
            #                 mapping.get("financial_type_id"),
            #                 mapping.get("financial_type_id"),
            #                 date_value,
            #                 version_id
            #             ))


# -------------------------------------------------------
# UPDATE  SAGE_CUMUL VALUE
# -------------------------------------------------------
def update_sage_cumul(conn, mapping, final_result, date_value, version_id):
    with conn.cursor() as cur:
        if "entity_id" in mapping:
            print(f'=== FINAL RESULT : {final_result}, == entity_id : {mapping["entity_id"]}== '
                  f'entity_type : {mapping["entity_type"]} =====')
            cur.execute("""
                        UPDATE collapse_monthly_data
                        SET sage_cumul_value=%s,
                            updated_at=CURRENT_TIMESTAMP
                        WHERE entity_id = %s
                          AND entity_type = %s
                          AND date =%s
                          AND version_id=%s
                        """, (
                            final_result,
                            mapping["entity_id"],
                            mapping["entity_type"],
                            date_value,
                            version_id
                        ))

        else:
            if mapping.get("financial_type_id"):
                cur.execute("""
                            UPDATE financial_metrics_data
                            SET sage_cumul_value=%s,
                                updated_at=CURRENT_TIMESTAMP
                            WHERE financial_type_id = %s
                            AND date =%s
                            AND version_id=%s
                            """, (final_result, mapping.get("financial_type_id"), date_value, version_id))
            elif mapping.get("financial_metric_id"):
                cur.execute("""
                            UPDATE financial_metrics_data
                            SET sage_cumul_value=%s,
                                updated_at=CURRENT_TIMESTAMP
                            WHERE financial_metric_id = %s
                            AND date =%s
                            AND version_id=%s
                            """, (final_result, mapping.get("financial_metric_id"), date_value, version_id))
            elif mapping.get("financial_submetric_id"):
                cur.execute("""
                            UPDATE financial_metrics_data
                            SET sage_cumul_value=%s,
                                updated_at=CURRENT_TIMESTAMP
                            WHERE financial_submetric_id = %s
                            AND date =%s
                            AND version_id=%s
                            """, (final_result, mapping.get("financial_submetric_id"), date_value, version_id))
            else:
                print(f"Inside update_sage_cumul: No financial type, metric, or submetric found for mapping: {mapping}")
            # cur.execute("""
            #             UPDATE financial_metrics_data
            #             SET sage_cumul_value=%s,
            #                 updated_at=CURRENT_TIMESTAMP
            #             WHERE (%s IS NULL OR financial_metric_id = %s)
            #               AND (%s IS NULL OR financial_submetric_id = %s)
            #               AND (%s IS NULL OR financial_type_id = %s)
            #               AND date =%s
            #               AND version_id=%s
            #             """, (
            #                 final_result,
            #                 mapping.get("financial_metric_id"),
            #                 mapping.get("financial_metric_id"),
            #                 mapping.get("financial_submetric_id"),
            #                 mapping.get("financial_submetric_id"),
            #                 mapping.get("financial_type_id"),
            #                 mapping.get("financial_type_id"),
            #                 date_value,
            #                 version_id
            #             ))


def fetch_sage_key(conn, mapping):
    """
    Fetch sage_source_key from appropriate master table
    based on mapping structure.
    """

    with conn.cursor() as cur:

        # Collapse entities
        if "entity_id" in mapping:

            entity_type = mapping.get("entity_type")

            if entity_type == "type":
                cur.execute("""
                            SELECT sage_source_key
                            FROM collapse_types
                            WHERE id = %s
                            """, (mapping["entity_id"],))

            elif entity_type == "category":
                cur.execute("""
                            SELECT sage_source_key
                            FROM collapse_categories
                            WHERE id = %s
                            """, (mapping["entity_id"],))

            elif entity_type == "subcategory":
                cur.execute("""
                            SELECT sage_source_key
                            FROM collapse_subcategories
                            WHERE id = %s
                            """, (mapping["entity_id"],))

            else:
                return None

        # Financial Metric
        elif "financial_metric_id" in mapping:
            cur.execute("""
                        SELECT sage_source_key
                        FROM financial_metric
                        WHERE id = %s
                        """, (mapping["financial_metric_id"],))

        # Financial Submetric
        elif "financial_submetric_id" in mapping:
            cur.execute("""
                        SELECT sage_source_key
                        FROM financial_submetric
                        WHERE id = %s
                        """, (mapping["financial_submetric_id"],))

        # Financial Type
        elif "financial_type_id" in mapping:
            cur.execute("""
                        SELECT sage_source_key
                        FROM financial_types
                        WHERE id = %s
                        """, (mapping["financial_type_id"],))

        else:
            return None

        row = cur.fetchone()
        return row[0] if row and row[0] else None


# -------------------------------------------------------
# MAIN DELTA CALCULATION
# -------------------------------------------------------
def calculate_delta(version_id, conn, moov_conn, month, year, date_value):
    for mapping in sage_accounts:
        formula = mapping["formula"]

        account_pairs = extract_account_pairs(formula)
        resolved = {}

        for acc_0, cpy_0 in account_pairs:
            val = fetch_oracle_cumulative(
                moov_conn,
                acc_0,
                cpy_0,
                month,
                year
            )
            resolved[f"({acc_0},{cpy_0})"] = val

        calc_formula = formula
        for key, value in resolved.items():
            calc_formula = calc_formula.replace(key, f"({value})")

        try:
            sage_cumul_value = eval(calc_formula)
            final_result = sage_cumul_value / 1_000_000
        except Exception as e:
            logging.error(f"Formula error {formula}: {e}")
            continue

        cumulative_real_value = fetch_cumulative_real_value(
            conn,
            mapping,
            date_value,
            version_id
        )

        sage_key = fetch_sage_key(conn, mapping)
        # If a metric has Sage Key as well as Account Number, we need to add the Sage Key Cumul to the Account Number Cumul
        # If Sage Key is not present, we don't need to add it to the Account Number Cumul
        if sage_key and sage_key in sage_cuml_for_sage_key_hash:
            print(f" ===== SAGE KEY : {sage_key} &&&&& SAGE VALUE : {sage_cuml_for_sage_key_hash[sage_key]}=====")
            final_result = float(sage_cuml_for_sage_key_hash[sage_key]) + final_result

        delta_value = final_result - cumulative_real_value

        update_sage_cumul(
            conn,
            mapping,
            final_result,
            date_value,
            version_id
        )

        update_delta_value(
            conn,
            mapping,
            delta_value,
            date_value,
            version_id
        )

        print("--------------------------------------------------")
        print("Mapping:", mapping)
        print("Final Result:", round(final_result, 2))
        print("Cumulative:", round(cumulative_real_value, 2))
        print("DELTA WRITTEN:", round(delta_value, 2))
        print("SAGE CUMULATIVE VALUE : ", round(sage_cumul_value, 2))

    # conn.commit()


# -------------------------------------------------------
# BOOTSTRAP
# -------------------------------------------------------
if __name__ == "__main__":
    import sys
    start_time = time.time()
    print(f"======== DELTA GENERATION STARTED =======")
    version_id = sys.argv[1]

    DB_CONFIG = {
        "dbname": os.getenv("DB_NAME"),
        "user": os.getenv("DB_USER"),
        "password": os.getenv("DB_PASSWORD"),
        "host": os.getenv("DB_HOST"),
        "port": os.getenv("DB_PORT"),
    }

    conn = get_db_connection(DB_CONFIG)

    if os.getenv("ENVIRONMENT") == 'TEST':
        moov_conn = psycopg2.connect(
            host=os.getenv("ORACLE_DB_HOST"),
            dbname=os.getenv("ORACLE_DB_NAME"),
            user=os.getenv("ORACLE_DB_USER"),
            password=os.getenv("ORACLE_DB_PASSWORD"),
            port=os.getenv("ORACLE_DB_PORT")
        )  # For test environment.
    else:
        try:
            cx_Oracle.init_oracle_client(lib_dir="/home/digiwise/digiwise/oracle/instantclient_23_8")
        except Exception as e:
            print("⚠️ Oracle client already initialized or not needed:", e)

        dsn = cx_Oracle.makedsn(
            os.getenv('ORACLE_DB_HOST'),
            os.getenv('ORACLE_DB_PORT'),
            service_name=os.getenv('ORACLE_DB_NAME')
        )

        moov_conn = cx_Oracle.connect(
            user=os.getenv("ORACLE_DB_USER"),
            password=os.getenv("ORACLE_DB_PASSWORD"),
            dsn=dsn
        )

    with conn.cursor() as cur:
        cur.execute(
            "SELECT month, year FROM tbg_version WHERE id=%s",
            (int(version_id),)
        )
        row = cur.fetchone()
        if not row:
            raise ValueError(f"============== NO VERSION FOUND FOR THE REQUESTED ID {version_id}==============")
        month, year = row
    print(f"============== month : {month}, year : {year} ===================")

    date_val = datetime(int(year), int(month), 1)

    # RUN STEPS
    run_sage_key_step(conn, moov_conn, version_id, int(year), date_val,month)
    calculate_delta(version_id, conn, moov_conn, month, year, date_val)

    conn.commit()
    conn.close()
    moov_conn.close()

    print(f"============ DELTA GENERATION FINISHED, TIME ELAPSED : {round(time.time() - start_time, 2)} ==============")
