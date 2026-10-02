import os
import psycopg2

tables = ["financial_types", "financial_metric", "financial_submetric", "collapse_types", "collapse_categories", "collapse_subcategories"]
# tables = ["financial_types", "financial_metric", "financial_submetric"]

conn = None  # Initialize here to avoid NameError in finally

# Configuration
base_path = 'benin_parser_2025/sage_import/'
# mapping_tsv_path = f"{base_path}/tbg_sage_key_mapping/sage_to_tbg_key_mapping_opex.tsv"
# mapping_tsv_path = f"{base_path}/tbg_sage_key_mapping/sage_to_tbg_key_mapping_capex.tsv"
# mapping_tsv_path = f"{base_path}/tbg_sage_key_mapping/sage_to_tbg_key_mapping_marge_mobile.tsv"
mapping_tsv_path = f"{base_path}/tbg_sage_key_mapping/sage_to_tbg_key_mapping_pnl.tsv"

# Database connection details (modify as needed)
DB_CONFIG = {
    "dbname": "digiwise_db",
    "user": "",
    "password": "",
    "host": "",
    "port": "",
}

try:
    # Establish DB connection
    conn = psycopg2.connect(
        dbname=DB_CONFIG['dbname'],
        user=DB_CONFIG['user'],
        password=DB_CONFIG['password'],
        host=DB_CONFIG['host'],
        port=DB_CONFIG['port']
    )
    cursor = conn.cursor()

    with open(mapping_tsv_path, "r") as file:
        for line in file:
            parts = line.strip().split("\t")
            if len(parts) != 2:  # Skip lines that don't have exactly 2 values
                print(f"Skipping line: {line}")
                continue
            tbg_key, sage_source_key = parts
            print(f"sage_source_key: {sage_source_key} tbg_key: {tbg_key}")

            for table in tables:
                query = f"UPDATE {table} SET sage_source_key = %s WHERE tbg_key = %s;"
                cursor.execute(query, (sage_source_key, tbg_key))

    conn.commit()

except psycopg2.Error as e:
    print(f"Database error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
finally:
    if conn:
        conn.close()
