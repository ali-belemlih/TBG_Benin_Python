from helpers.db_utils import get_db_connection

def get_uploaded_file_details(upload_id):
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT month, year, file_path
                FROM public.tbg_capex_project_details
                WHERE id = %s;
            """, (upload_id,))

            row = cur.fetchone()
            if row:
                month, year, file_path = row
                return month, year, file_path
            else:
                raise ValueError(f"No record found with id: {upload_id}")
    finally:
        conn.close()
