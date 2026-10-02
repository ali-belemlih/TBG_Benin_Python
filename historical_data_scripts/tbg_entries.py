import csv
import os
import logging
from helpers.db_utils import get_db_connection

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Mapping filenames to your DB Category IDs
CATEGORY_MAPPING = {
    "pnl_conso.csv": 1,
    "opex_conso.csv": 4,
    "ca_mobile.csv": 5,
    "marge_brute.csv": 6,
    "trafic_mobile.csv": 7,
    "mobile_money.csv": 8,
    "data_mobile.csv": 9,
    "parc_mobile.csv": 10,
    "capex_conso.csv": 2,
    "cash_conso.csv": 3,
    "indicateurs.csv": 11
}

def import_all_csvs(folder_path):
    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # Iterate through all files in the directory
        for file_name in os.listdir(folder_path):
            if not file_name.endswith('.csv'):
                continue
            
            # Identify the Category ID
            category_id = CATEGORY_MAPPING.get(file_name)
            if not category_id:
                logging.warning(f"Skipping {file_name}: No category ID mapping found.")
                continue

            file_path = os.path.join(folder_path, file_name)
            logging.info(f"=== Starting Import: {file_name} (Category ID: {category_id}) ===")

            # Maps to store IDs for foreign key lookups within the scope of this file
            type_ids = {}
            metric_ids = {}

            with open(file_path, mode='r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    level = row['level'].strip().lower()
                    name = row['name'].strip()
                    seq = int(row['sequence'])
                    tbg = row['tbg_key'].strip()
                    parent = row['parent_tbg'].strip()

                    if level == 'type':
                        cur.execute("""
                            INSERT INTO public.financial_types (name, sequence_id, financial_category_id, tbg_key, created_at, updated_at)
                            VALUES (%s, %s, %s, %s, NOW(), NOW()) RETURNING id;
                        """, (name, seq, category_id, tbg))
                        type_ids[tbg] = cur.fetchone()[0]

                    elif level == 'metric':
                        # Link to Type parent
                        cur.execute("""
                            INSERT INTO public.financial_metric (name, sequence_id, financial_type_id, tbg_key, created_at, updated_at)
                            VALUES (%s, %s, %s, %s, NOW(), NOW()) RETURNING id;
                        """, (name, seq, type_ids[parent], tbg))
                        metric_ids[tbg] = cur.fetchone()[0]

                    elif level == 'submetric':
                        # Link to Metric parent
                        parent_id = metric_ids.get(parent)
                        if not parent_id:
                            logging.error(f"Parent Metric '{parent}' not found for submetric '{tbg}' in {file_name}")
                            continue

                        cur.execute("""
                            INSERT INTO public.financial_submetric (name, sequence_id, financial_metric_id, tbg_key, created_at, updated_at)
                            VALUES (%s, %s, %s, %s, NOW(), NOW());
                        """, (name, seq, parent_id, tbg))

            logging.info(f"=== Successfully Finished: {file_name} ===")

        conn.commit()
        logging.info("All transactions committed successfully.")

    except Exception as e:
        if conn:
            conn.rollback()
        logging.error(f"CRITICAL ERROR: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    CSV_FOLDER = 'historical_data_scripts/tbg_entries'
    import_all_csvs(CSV_FOLDER)