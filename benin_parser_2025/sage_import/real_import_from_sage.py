import pandas as pd
from psycopg2.extras import RealDictCursor
from helpers.db_utils import get_db_connection, upsert_financial_data, get_version_id_by_name
from helpers.parse_arg import parse_arguments

CATEGORIES = ["YYCAMOBILE", "CAPEXCONSO", "YYMARGE", "YYPLCONSO"]

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

def get_matching_ids(cursor, metric_name, category_name):
    cursor.execute("SELECT id FROM financial_types WHERE sage_source_key = %s", (metric_name,))
    type_id = cursor.fetchone()

    cursor.execute("SELECT id FROM financial_submetric WHERE sage_source_key = %s", (metric_name,))
    submetric_id = cursor.fetchone()

    cursor.execute("SELECT id FROM financial_metric WHERE sage_source_key = %s", (metric_name,))
    metric_id = cursor.fetchone()

    return (
        type_id['id'] if type_id else None,
        submetric_id['id'] if submetric_id else None,
        metric_id['id'] if metric_id else None
    )

def process_category(category_name, version_id, sage_version):
    print(f"\n--- Processing category: {category_name} version: {version_id} ---")
    df = fetch_sage_data(category_name, sage_version)
    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            for _, row in df.iterrows():
                metric_name = row.get('sage_sage_source_key')

                if not metric_name:
                    continue

                date = row['date']
                try:
                    real_value = float(row['real_value'])
                except (ValueError, TypeError):
                    continue

                # Convert to millions
                real_value /= 1_000_000

                type_id, submetric_id, metric_id = get_matching_ids(cursor, metric_name, category_name)

                if any([type_id, submetric_id, metric_id]):
                    upsert_financial_data(
                        cur=cursor,
                        table_name="financial_metrics_data",
                        type_id=type_id,
                        metric_id=metric_id,
                        submetric_id=submetric_id,
                        date_value=date,
                        real_value=real_value,
                        version_id = version_id
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
