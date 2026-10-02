import psycopg2
from openpyxl import load_workbook
from helpers.parse_arg import parse_arguments
from helpers.db_utils import get_db_connection, get_version_id_by_name
from services.minio_factory import get_minio_service
from io import BytesIO

# --- CONFIGURATION ---
SHEET_NAME = 'Feuil1'
TBG_KEY = "Opex62"
MONTH_MAP = { "01": "C", "02": "D", "03": "E", "04": "F",
              "05": "G", "06": "H", "07": "I", "08": "J",
              "09": "K", "10": "L", "11": "M", "12": "N"
            }

# --- DB FUNCTIONS ---
def fetch_with_headers(conn, query, params):
    with conn.cursor() as cur:
        cur.execute(query, params)
        columns = [desc[0] for desc in cur.description]
        rows = cur.fetchall()
        return [dict(zip(columns, row)) for row in rows]

def fetch_collapse_type_data(conn, tbg_key, date):
    query = """
        SELECT
            ct.id AS type_id,
            ct.name AS type_name,
            ct.tbg_key AS type_tbg_key,
            ct.sage_source_key AS type_sage_source_key,
            cmd.date,
            cmd.real_value,
            cmd.budget_value,
            cmd.actual1_value,
            cmd.actual2_value,
            cmd.actual3_value,
            cmd.last_year_real_value
        FROM collapse_types ct
        LEFT JOIN collapse_monthly_data cmd
            ON cmd.entity_type = 'type'
            AND cmd.entity_id = ct.id
            AND cmd.date = %s
        WHERE ct.tbg_key = %s
        ORDER BY cmd.date;
    """
    return fetch_with_headers(conn, query, (date, tbg_key))

def update_real_value(conn, tbg_key, date, new_value, version_id):
    update_query = """
        UPDATE collapse_monthly_data cmd
        SET real_value = %s,
            version_id = %s,
            updated_at = CURRENT_TIMESTAMP
        FROM collapse_types ct
        WHERE cmd.entity_type = 'type'
          AND cmd.entity_id = ct.id
          AND ct.tbg_key = %s
          AND cmd.date = %s
    """
    with conn.cursor() as cur:
        cur.execute(update_query, (new_value, version_id, tbg_key, date))
    conn.commit()
    print(f"✅ Updated real_value = {new_value}, version_id = {version_id}, tbg_key = {tbg_key}, date = {date}")

# --- MAIN EXECUTION ---
def process_monthly_updates(month_year, version_id, file_name):
    target_month = month_year[:2]  # Extract MM from MMYYYY
    target_year = month_year[2:]   # Extract YYYY from MMYYYY
    minio_path = f"{target_year}/{target_year}{target_month}/{file_name}"
    print(f"📦 Fetching file from MinIO path: {minio_path}")

    minio_service = get_minio_service()
    file_bytes = minio_service.get_file_bytes(minio_path)

    wb = load_workbook(filename=BytesIO(file_bytes), data_only=True)
    sheet = wb[SHEET_NAME]

    standard_name = sheet["B2"].value
    print(f"\n📌 Standard Name: {standard_name}")
    print("📅 Starting monthly update process...\n")

    with get_db_connection() as conn:
        col_letter = MONTH_MAP[target_month]
        cell_ref = f"{col_letter}2"
        impact_value = sheet[cell_ref].value or 0
        date = f"{target_year}-{target_month}-01"

        try:
            result = fetch_collapse_type_data(conn, TBG_KEY, date)
            real_value = result[0].get("real_value") or 0
            updated_value = real_value - impact_value

            update_real_value(conn, TBG_KEY, date, updated_value, version_id)
        except Exception as e:
            print(f"❌ Error processing {date}: {e}")

if __name__ == "__main__":
    args = parse_arguments()
    version_id = get_version_id_by_name(args.version_id)
    process_monthly_updates(args.month_year, version_id, args.file_name)
