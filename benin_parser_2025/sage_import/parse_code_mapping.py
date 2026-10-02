import pandas as pd
import psycopg2
import csv
from db_config import DB_CONFIG  # Import database configuration

# Configuration to update for different reports
base_path = 'benin-parser-2025/reel_import/sage_import'

# category_name = "P&L conso" # From financial_categories table
# data_tsv_path = f"{base_path}/tbg_sage_key_mapping/tbg_key_mapping_pnl.tsv"
# mapping_tsv_path = f"{base_path}/tbg_sage_key_mapping/sage_to_tbg_key_mapping_pnl.tsv"

# category_name = "Marge brute Mobile"
# data_tsv_path = f"{base_path}/tbg_sage_key_mapping/tbg_key_mapping_marge_mobile.tsv"
# mapping_tsv_path = f"{base_path}/tbg_sage_key_mapping/sage_to_tbg_key_mapping_marge_mobile.tsv"

# category_name = "Opex Consolidés"
# data_tsv_path = f"{base_path}/tbg_sage_key_mapping/tbg_key_mapping_opex.tsv"
# mapping_tsv_path = f"{base_path}/tbg_sage_key_mapping/sage_to_tbg_key_mapping_opex.tsv"

category_name = "Capex Consolidés"
data_tsv_path = f"{base_path}/tbg_sage_key_mapping/tbg_key_mapping_capex.tsv"
mapping_tsv_path = f"{base_path}/tbg_sage_key_mapping/sage_to_tbg_key_mapping_capex.tsv"


def print_dict(my_dict, elements=2):
    count = 0
    for key, value in my_dict.items():
        print(f"{key}: {value}")
        count += 1
        if count == elements:
            break
    print("--------------------------------")


def load_tsv_to_dict(file_path, key_column, value_column, starts_with_key=None):
    """Loads data from a TSV file into a dictionary."""
    data_dict = {}
    try:
        with open(file_path, 'r', encoding='utf-8') as infile:  # Explicit encoding
            for line in infile:
                line = line.strip()
                if not line:
                    continue
                parts = line.split('\t')
                
                if len(parts) > max(key_column, value_column):
                    key = parts[key_column].strip()
                    value = parts[value_column].strip()
                    if starts_with_key is None or key.startswith(starts_with_key):
                        data_dict[key] = value
                else:
                    print(f"Warning: Insufficient columns in line: {line.strip()} in file: {file_path}")
    except FileNotFoundError:
        print(f"Error: File not found at {file_path}")
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
    return data_dict


def create_combined_mapping(data_tsv_path, mapping_tsv_path):
    """Creates the combined mapping dictionary."""
    ca_to_name_mapping = load_tsv_to_dict(data_tsv_path, key_column=1, value_column=0)
    ca_to_cam_mapping = load_tsv_to_dict(mapping_tsv_path, key_column=0, value_column=1)

    combined_mapping = {}

    for ca_key, name in ca_to_name_mapping.items():
        combined_mapping[name] = {
            "tbg_key": ca_key,
            "sage_source_key": ca_to_cam_mapping.get(ca_key, None)
        }

    return combined_mapping

def select_query(table):
    if table == 'financial_types':
        query = f"""
            SELECT ft.name
            FROM financial_types ft
            JOIN financial_categories fc ON ft.financial_category_id = fc.id
            WHERE fc.name = %s
        """
    elif table == 'financial_metric':
        query = f"""
            SELECT fm.name
            FROM financial_metric fm
            JOIN financial_types ft ON fm.financial_type_id = ft.id
            JOIN financial_categories fc ON ft.financial_category_id = fc.id
            WHERE fc.name = %s
        """
    elif table == 'financial_submetric':
        query = f"""
            SELECT fsm.name
            FROM financial_submetric fsm
            JOIN financial_metric fm ON fsm.financial_metric_id = fm.id
            JOIN financial_types ft ON fm.financial_type_id = ft.id
            JOIN financial_categories fc ON ft.financial_category_id = fc.id
            WHERE fc.name = %s
        """
    
    return query

def get_filtered_names_from_db(conn, tables_to_check):
    """
    Retrieves names from the specified tables,
    filtering by financial_categories.name.
    """
    all_names = pd.Series()
    for table in tables_to_check:
        try:

            df_names = pd.read_sql_query(select_query(table), conn, params=(category_name,))
            all_names = pd.concat([all_names, df_names['name']])
        except psycopg2.Error as e:
            print(f"Error reading table '{table}': {e}")
        except Exception as e:
            print(f"Unexpected error reading table '{table}': {e}")

    return all_names.value_counts()

def print_to_csv(combined_mapping):
    csv_output_path = f"{base_path}/combined_mapping.csv"
    try:
        with open(csv_output_path, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['name', 'tbg_key', 'sage_source_key']) # Write header
            for name, keys in combined_mapping.items():
                writer.writerow([name, keys['tbg_key'], keys['sage_source_key']])
        print(f"Combined mapping saved to {csv_output_path}")
    except IOError as e:
        print(f"Error writing CSV file: {e}")

def insert_data_to_db(conn, combined_mapping, tables_to_check, existing_names):
    """Updates data in the database if name matches, otherwise skips."""
    data_to_process = []
    for name, data in combined_mapping.items():
        if name in existing_names and existing_names[name] == 1:
            data_to_process.append({'name': name, 'tbg_key': data['tbg_key'], 'sage_source_key': data['sage_source_key']})
        else:
            print(f"Skipping {name}")

    if data_to_process:
        cursor = conn.cursor()
        for table in tables_to_check:
            # Moved the query selection outside the try block
            try:
                existing_table_names_df = pd.read_sql_query(select_query(table), conn, params=(category_name,))
                existing_table_names = set(existing_table_names_df['name'])
                data_to_process_df = pd.DataFrame(data_to_process)

                data_to_update_df = data_to_process_df[data_to_process_df['name'].isin(existing_table_names)]

                if not data_to_update_df.empty:
                    for _, row in data_to_update_df.iterrows():
                        cursor.execute(
                            f"UPDATE {table} SET tbg_key = %s, sage_source_key = %s WHERE name = %s",
                            (row['tbg_key'], row['sage_source_key'], row['name'])
                        )
                    conn.commit()
                    print(f"Updated {len(data_to_update_df)} rows in '{table}'.")
                else:
                    print(f"No matching names found to update in '{table}'.")

            except psycopg2.Error as e:
                conn.rollback()  # Rollback on error
                print(f"Error updating table '{table}': {e}")
            except Exception as e:
                conn.rollback()
                print(f"Unexpected error updating table '{table}': {e}")
        cursor.close()
    else:
        print("No data to process for the database.")

if __name__ == "__main__":
    # Configuration
    tables_to_check = ['financial_types', 'financial_submetric', 'financial_metric']

    try:
        # Establish database connection
        conn = psycopg2.connect(
            dbname=DB_CONFIG['dbname'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password'],
            host=DB_CONFIG['host'],
            port=DB_CONFIG['port']
        )

        # Create combined mapping
        combined_mapping = create_combined_mapping(data_tsv_path, mapping_tsv_path)
        print("Combined Mapping:")
        # print_dict(combined_mapping, elements=5)

        # Get existing names from the database
        existing_names = get_filtered_names_from_db(conn, tables_to_check)

        # print("Existing Names:")
        # print_dict(existing_names, elements=5)
        # print(existing_names)

        # print_to_csv(combined_mapping)

        # Insert unique mappings
        insert_data_to_db(conn, combined_mapping, tables_to_check, existing_names)

    except psycopg2.Error as e:
        print(f"Database connection error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

    finally:
        if conn:
            conn.close()
