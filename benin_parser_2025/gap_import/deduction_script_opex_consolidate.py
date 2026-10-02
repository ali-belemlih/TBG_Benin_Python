import logging
import psycopg2
from helpers.db_utils import get_db_connection, get_version_id_by_name
from helpers.parse_arg import parse_arguments

# === Config ===
ADJUSTMENT_AMOUNT = 25_842_129.0
TBG_KEY = "Opex5"

# === Logging ===
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# === DB Setup ===
conn = get_db_connection()
cur = conn.cursor()

def fetch_with_headers(query, params):
    try:
        cur.execute(query, params)
        columns = [desc[0] for desc in cur.description]
        rows = cur.fetchall()
        return [dict(zip(columns, row)) for row in rows]
    except Exception as e:
        logger.error("Database query failed: %s", e)
        return []

def fetch_collapse_type_real_value(tbg_key, date):
    query = """
        SELECT
            ct.id AS type_id,
            ct.name AS type_name,
            ct.tbg_key AS type_tbg_key,
            ct.sage_source_key AS type_sage_source_key,
            cmd.date,
            cmd.real_value
        FROM collapse_types ct
        LEFT JOIN collapse_monthly_data cmd
            ON cmd.entity_type = 'type'
            AND cmd.entity_id = ct.id
            AND cmd.date = %s
        WHERE ct.tbg_key = %s
        ORDER BY cmd.date;
    """
    return fetch_with_headers(query, (date, tbg_key))

def update_real_value(tbg_key, date, new_value, version_id):
    update_query = """
        UPDATE collapse_monthly_data cmd
        SET real_value = %s,
            version_id = %s,
            updated_at = CURRENT_TIMESTAMP
        FROM collapse_types ct
        WHERE ct.tbg_key = %s
          AND cmd.entity_type = 'type'
          AND cmd.entity_id = ct.id
          AND cmd.date = %s;
    """
    try:
        cur.execute(update_query, (new_value, version_id, tbg_key, date))
        conn.commit()
        logger.info("✅ Updated real_value to %.2f for tbg_key=%s on date=%s", new_value, tbg_key, date)
    except Exception as e:
        conn.rollback()
        logger.error("❌ Failed to update real_value for %s on %s: %s", tbg_key, date, e)

def process_single_month(month_year, version_id):
    if len(month_year) != 6 or not month_year.isdigit():
        raise ValueError("month_year must be in MMYYYY format")

    month = month_year[:2]
    year = month_year[2:]
    date = f"{year}-{month}-01"

    logger.info("Processing tbg_key=%s for date=%s", TBG_KEY, date)

    result = fetch_collapse_type_real_value(TBG_KEY, date)

    if not result:
        logger.warning("No data found for tbg_key=%s on date=%s", TBG_KEY, date)
        return

    real_value = result[0].get('real_value') or 0.0
    adjusted_value = real_value - ADJUSTMENT_AMOUNT

    logger.info("Fetched real_value: %.2f | Adjusted by: %.2f | Final value: %.2f",
                real_value, ADJUSTMENT_AMOUNT, adjusted_value)

    update_real_value(TBG_KEY, date, adjusted_value, version_id)

if __name__ == "__main__":
    try:
        args = parse_arguments()
        month_year = args.month_year  # Format: MMYYYY
        version_id = get_version_id_by_name(args.version_id)

        process_single_month(month_year, version_id)

    except Exception as main_err:
        logger.critical("Script failed with error: %s", main_err)
    finally:
        cur.close()
        conn.close()
