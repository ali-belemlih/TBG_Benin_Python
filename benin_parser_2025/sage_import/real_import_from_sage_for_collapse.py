import pandas as pd
from psycopg2.extras import RealDictCursor
from helpers.db_utils import get_db_connection, upsert_collapse_financial_data, get_version_id_by_name
from helpers.parse_arg import parse_arguments

CATEGORIES = ["YYCAMOBILE", "YYOPEX"]

def get_month_from_sage_version(conn, sage_version):
    with conn.cursor() as cur:
        cur.execute("""
            SELECT month
            FROM import_sources
            WHERE file_name = %s
            LIMIT 1
        """, (sage_version,))

        row = cur.fetchone()
        return row[0] if row else None

def fetch_sage_data(category_name, sage_version):
    query = f"""
    SELECT
        TO_CHAR(TO_DATE(YANNEE_0 || LPAD(ymois_0, 2, '0') || '01', 'YYYYMMDD'), 'YYYY-MM-DD') AS date,
        MAX(CASE WHEN COL_0 = '0' THEN SPLIT_PART(AMTVAL_0, '-', 1) END) AS sage_sage_source_key,
        MAX(CASE WHEN COL_0 = '1' THEN AMTVAL_0 END) AS real_value,
        LIG_0
    FROM sage_yexptdb
    WHERE VERSION_0 = 'YEXPTDB'
      AND IND_0 = '0'
      AND TXSNAM_0 = '{category_name}'
      AND COL_0 IN ('0', '1')
      AND sage_version = '{sage_version}'
    GROUP BY LIG_0, ymois_0, YANNEE_0
    ORDER BY LIG_0, ymois_0;
    """
    with get_db_connection() as conn:
        return pd.read_sql(query, conn)

def get_matching_ids(cursor, sage_source_key):
    cursor.execute("SELECT id FROM collapse_types WHERE sage_source_key = %s", (sage_source_key,))
    record = cursor.fetchone()
    type = 'type'
    if not record:
        cursor.execute("SELECT id FROM collapse_categories WHERE sage_source_key = %s", (sage_source_key,))
        record = cursor.fetchone()
        type = 'category'
        if not record:
            cursor.execute("SELECT id FROM collapse_subcategories WHERE sage_source_key = %s", (sage_source_key,))
            record = cursor.fetchone()
            type = 'subcategory'

    return (
        record['id'] if record else None,
        type
    )

def process_category(category_name, version_id, sage_version):
    df = fetch_sage_data(category_name, sage_version)

    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            for _, row in df.iterrows():
                sage_source_key = row['sage_sage_source_key']

                if sage_source_key is None or not sage_source_key:
                    continue

                date = row['date']
                try:
                    real_value = float(row['real_value'])
                except (ValueError, TypeError):
                    # print(f"Skipping invalid real_value for key: {sage_source_key} date: {date}")
                    continue

                # Convert to millions
                real_value /= 1_000_000

                entity_id, entity_type = get_matching_ids(cursor, sage_source_key)

                if entity_id and entity_type:
                    upsert_collapse_financial_data(
                        cursor,
                        table_name="collapse_monthly_data",
                        entity_id=entity_id,
                        entity_type=entity_type,
                        date_value=date,
                        real_value=real_value,
                        version_id=version_id
                    )
            conn.commit()

def main():
    args = parse_arguments()
    version_id = get_version_id_by_name(args.version_id)
    sage_version = args.sage_version
    conn = get_db_connection()
    month = get_month_from_sage_version(conn, sage_version)
    conn.close()

    for category in CATEGORIES:
        # if category.startswith('YY') and month in [1, 2, 3]:
        #     category = category[2:]
        process_category(category, version_id, sage_version)

if __name__ == "__main__":
    main()
