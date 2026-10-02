import os
import re
import logging
from datetime import datetime
import psycopg2
from dotenv import load_dotenv
import cx_Oracle
from delta_generation.mapping.sage_account_mapping import sage_accounts

load_dotenv()

# --- CONFIGURATION ---
SAGE_KEY_TABLES = [
    {"table": "financial_metrics", "id_col": "id", "map_key": "financial_metric_id"},
    {"table": "financial_submetrics", "id_col": "id", "map_key": "financial_submetric_id"},
    {"table": "financial_types", "id_col": "id", "map_key": "financial_type_id"},
    {"table": "collapse_types", "id_col": "id", "map_key": "entity_id", "type": "collapse_type"},
    {"table": "collapse_categories", "id_col": "id", "map_key": "entity_id", "type": "collapse_category"},
    {"table": "collapse_subcategories", "id_col": "id", "map_key": "entity_id", "type": "collapse_subcategory"},
]

# -------------------------------------------------------
# HELPERS
# -------------------------------------------------------
def get_db_connection(config):
    return psycopg2.connect(**config)

def get_txsnam(source_key: str):
    """Dynamic TXSNAM based on prefix."""
    if source_key.startswith("CAM"): return "YYCAMOBILE"
    if source_key.startswith("OPX"): return "YYOPEX"
    # Add more prefixes here as needed
    return "YYCAMOBILE" 

# -------------------------------------------------------
# PHASE 1: SAGE KEY LOGIC
# -------------------------------------------------------
def fetch_sage_key_cumul_oracle(moov_conn, source_key, year):
    txsnam = get_txsnam(source_key)
    query = """
    SELECT SUM(real_value) AS total_real_value
    FROM (
        SELECT
            MAX(CASE WHEN COL_0 = '0' AND AMTVAL_0 IS NOT NULL AND INSTR(AMTVAL_0, '-') > 0 
                THEN REGEXP_SUBSTR(AMTVAL_0, '[^-]+', 1, 1) END) AS sage_key,
            MAX(CASE WHEN COL_0 = '1' THEN TO_NUMBER(AMTVAL_0) END) AS real_value
        FROM MOOV.YEXPTDB
        WHERE VERSION_0 = 'YEXPTDB' AND IND_0 = '0'
          AND TXSNAM_0 = :txsnam AND YANNEE_0 = :year
        GROUP BY LIG_0, ymois_0, YANNEE_0
    ) WHERE sage_key = :source_key
    """
    with moov_conn.cursor() as cur:
        cur.execute(query, {"txsnam": txsnam, "year": year, "source_key": source_key})
        row = cur.fetchone()
        return row[0] if row and row[0] else 0.0

def run_sage_key_step(conn, moov_conn, version_id, year, date_value):
    print(">>> Starting Phase 1: Sage Key Delta Calculation")
    for config in SAGE_KEY_TABLES:
        with conn.cursor() as cur:
            cur.execute(f"SELECT {config['id_col']}, sage_source_key FROM {config['table']} WHERE sage_source_key IS NOT NULL")
            rows = cur.fetchall()
            
            for item_id, s_key in rows:
                # 1. Get Oracle YTD
                sage_cumul_raw = fetch_sage_key_cumul_oracle(moov_conn, s_key, year)
                final_sage_result = sage_cumul_raw / 1_000_000
                
                # 2. Build mapping for update logic
                mapping = {config['map_key']: item_id}
                if "type" in config:
                    mapping["entity_type"] = config["type"]

                # 3. Get existing PG cumul
                current_pg_cumul = fetch_cumulative_real_value(conn, mapping, date_value, version_id)
                
                # 4. Calc Delta
                delta = final_sage_result - current_pg_cumul
                
                # 5. Update
                update_sage_cumul(conn, mapping, sage_cumul_raw, date_value, version_id)
                update_delta_value(conn, mapping, delta, date_value, version_id)
                print(f"Updated Sage Key {s_key} (Table: {config['table']}): Delta {round(delta, 2)}")

# -------------------------------------------------------
# PHASE 2: ACCOUNT NUMBER LOGIC (Existing)
# -------------------------------------------------------
def extract_account_pairs(formula: str):
    return re.findall(r"\((\d+),\s*([A-Z0-9]+)\)", formula)

def fetch_oracle_cumulative(moov_conn, acc_0, cpy_0, month):
    # Uses your existing delta_oracle.sql logic
    query = open("delta_generation/sql/delta_oracle.sql").read()
    with moov_conn.cursor() as cur:
        cur.execute(query, {'acc_0': acc_0, 'cpy_0': cpy_0})
        row = cur.fetchone()
        if not row: return 0.0
        return sum((row[i] or 0) for i in range(3, 3 + month))

def run_account_number_step(version_id, conn, moov_conn, month, year, date_value):
    print(">>> Starting Phase 2: Account Number Delta Calculation")
    for mapping in sage_accounts:
        formula = mapping["formula"]
        account_pairs = extract_account_pairs(formula)
        resolved = {}

        for acc_0, cpy_0 in account_pairs:
            val = fetch_oracle_cumulative(moov_conn, acc_0, cpy_0, month)
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

        cumulative_real_value = fetch_cumulative_real_value(conn, mapping, date_value, version_id)
        delta_value = final_result - cumulative_real_value

        update_sage_cumul(conn, mapping, sage_cumul_value, date_value, version_id)
        update_delta_value(conn, mapping, delta_value, date_value, version_id)

# -------------------------------------------------------
# DB UPDATES & FETCH (SHARED)
# -------------------------------------------------------
# (Keeping your existing fetch_cumulative_real_value, update_delta_value, and update_sage_cumul functions here...)

def fetch_cumulative_real_value(conn, mapping, date_value, version_id):
    with conn.cursor() as cur:
        if "entity_id" in mapping:
            cur.execute("""SELECT COALESCE(real_value,0) FROM collapse_cumul_data 
                           WHERE entity_id=%s AND entity_type=%s AND date=%s AND version_id=%s""", 
                        (mapping["entity_id"], mapping["entity_type"], date_value, version_id))
        elif "financial_metric_id" in mapping:
            cur.execute("""SELECT COALESCE(real_value,0) FROM financial_cumulative_data 
                           WHERE financial_metric_id=%s AND date=%s AND version_id=%s""", 
                        (mapping["financial_metric_id"], date_value, version_id))
        elif "financial_submetric_id" in mapping:
            cur.execute("""SELECT COALESCE(real_value,0) FROM financial_cumulative_data 
                           WHERE financial_submetric_id=%s AND date=%s AND version_id=%s""", 
                        (mapping["financial_submetric_id"], date_value, version_id))
        else: return 0.0
        row = cur.fetchone()
        return row[0] if row else 0.0

def update_delta_value(conn, mapping, delta_value, date_value, version_id):
    # Same logic as your original script
    # ... (code omitted for brevity but remains the same)
    pass

def update_sage_cumul(conn, mapping, final_result, date_value, version_id):
    # Same logic as your original script
    # ... (code omitted for brevity but remains the same)
    pass

# -------------------------------------------------------
# MAIN EXECUTION
# -------------------------------------------------------
if __name__ == "__main__":
    import sys
    version_id = sys.argv[1]

    # DB Configs
    DB_CONFIG = {
        "dbname": os.getenv("DB_NAME"),
        "user": os.getenv("DB_USER"),
        "password": os.getenv("DB_PASSWORD"),
        "host": os.getenv("DB_HOST"),
        "port": os.getenv("DB_PORT"),
    }

    conn = get_db_connection(DB_CONFIG)

    # Initialize Oracle
    try:
        cx_Oracle.init_oracle_client(lib_dir="/home/digiwise/digiwise/oracle/instantclient_23_8")
    except: pass
    
    dsn = cx_Oracle.makedsn(os.getenv('ORACLE_DB_HOST'), os.getenv('ORACLE_DB_PORT'), service_name=os.getenv('ORACLE_DB_NAME'))
    moov_conn = cx_Oracle.connect(user=os.getenv("ORACLE_DB_USER"), password=os.getenv("ORACLE_DB_PASSWORD"), dsn=dsn)

    # Get Version Context
    with conn.cursor() as cur:
        cur.execute("SELECT month, year FROM tbg_version WHERE id=%s", (version_id,))
        month, year = cur.fetchone()

    date_val = datetime(int(year), int(month), 1)

    # RUN STEPS
    run_sage_key_step(conn, moov_conn, version_id, int(year), date_val)
    run_account_number_step(version_id, conn, moov_conn, month, year, date_val)

    conn.commit()
    conn.close()
    moov_conn.close()
    print("Process Complete.")