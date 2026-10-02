import os
import psycopg2
from psycopg2.extras import execute_batch
import logging
from dotenv import load_dotenv
import pandas as pd
from helpers.db_utils import get_db_connection


def upsert_data_to_db(df, table_name, db_columns, conflict_columns):
    """
    Upserts data into the database - updates if exists, inserts if new.

    Args:
        df: DataFrame containing data to upsert
        table_name: Name of the target table
        db_columns: List of column names in the target table
        conflict_columns: List of column names that define uniqueness (used in ON CONFLICT clause)
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Define type conversion mapping based on your schema
        type_conversion = {
            'float(8)': {
                'cols': ['ca_global', 'ca_voix_classique', 'ca_forfaits_voix',
                         'ca_pass_bonus', 'ca_data', 'moov_sayaa', 'autres',
                         'rechargement', 'ratio_conso_rechargement',
                         'ratio_reconnexions_gross_add', 'trafic_voix',
                         'trafic_data_ko'],
                'converter': lambda x: pd.to_numeric(x, errors='coerce').astype('float64')
            },
            'int(4)': {
                'cols': ['parc_abonnes_global', 'parc_journalier', 'gross_add',
                         'churn', 'net_add', 'reconnexions', 'parc_attache',
                         'parc_global_data', 'parc_attache_data', 'parc_data_2g',
                         'parc_data_3g', 'parc_data_4g'],
                'converter': lambda x: pd.to_numeric(x, errors='coerce').round().astype('Int64')
            }
        }

        # Apply type conversions
        for dtype, config in type_conversion.items():
            for col in config['cols']:
                if col in df.columns:
                    try:
                        df[col] = config['converter'](df[col])
                        # Log conversion issues
                        if df[col].isna().any() and not df[col].isna().all():
                            problematic = df[df[col].isna()][col].index.tolist()
                            logging.warning(
                                f"Conversion issues in column '{col}': "
                                f"{len(problematic)} values couldn't be converted to {dtype}"
                            )
                    except Exception as e:
                        logging.error(f"Error converting column '{col}' to {dtype}: {e}")
                        raise

        # Prepare SQL UPSERT statement
        columns = ", ".join(db_columns)
        placeholders = ", ".join(["%s"] * len(db_columns))
        conflict_clause = ", ".join(conflict_columns)

        # Create the SET part for UPDATE
        set_clause = ", ".join([f"{col} = EXCLUDED.{col}" for col in db_columns if col not in conflict_columns])

        upsert_query = f"""
            INSERT INTO {table_name} ({columns}) 
            VALUES ({placeholders})
            ON CONFLICT ({conflict_clause}) 
            DO UPDATE SET {set_clause}
        """

        # Prepare data for upsert
        data = []
        for _, row in df.iterrows():
            record = []
            for col in db_columns:
                val = row.get(col)
                # Convert pandas NA to None for PostgreSQL
                if pd.isna(val):
                    record.append(None)
                else:
                    record.append(val)
            data.append(tuple(record))

        # Execute batch upsert
        execute_batch(cursor, upsert_query, data)
        conn.commit()
        logging.info(f"Successfully upserted {len(data)} records into table '{table_name}'")
        return True

    except Exception as error:
        logging.error(f"Failed to upsert data into database: {error}")
        if 'conn' in locals():
            conn.rollback()
        return False
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()
