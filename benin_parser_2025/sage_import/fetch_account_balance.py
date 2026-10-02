import os
from dotenv import load_dotenv
import psycopg2
import cx_Oracle

MONTH_COLUMNS = { 1: 'january', 2: 'february', 3: 'march', 4: 'april',
                  5: 'may', 6: 'june', 7: 'july', 8: 'august', 9: 'september',
                  10: 'octomber', 11: 'november', 12: 'december',
                }

def load_query():
    if os.getenv("ENVIRONMENT") == 'TEST':
        path = 'benin_parser_2025/sql_queries/update_accounts_psql.sql'
    else:
        path = 'benin_parser_2025/sql_queries/update_accounts_oracle.sql'
    with open(path, "r") as file:
        return file.read()

def fetch_account_balance_value(acc_0, cpy_0, month=None, year=None):
    if os.getenv("ENVIRONMENT") == 'TEST':
        conn = psycopg2.connect(
            host=os.getenv("ORACLE_DB_HOST"),
            dbname=os.getenv("ORACLE_DB_NAME"),
            user=os.getenv("ORACLE_DB_USER"),
            password=os.getenv("ORACLE_DB_PASSWORD"),
            port=os.getenv("ORACLE_DB_PORT")
        ) # For test environment.
    else:
        try:
            cx_Oracle.init_oracle_client(lib_dir="/home/digiwise/digiwise/oracle/instantclient_23_8")
        except Exception as e:
            print("⚠️ Oracle client already initialized or not needed:", e)

        dsn = cx_Oracle.makedsn(
            os.getenv('ORACLE_DB_HOST'),
            os.getenv('ORACLE_DB_PORT'),
            service_name=os.getenv('ORACLE_DB_NAME')
        )

        conn = cx_Oracle.connect(
            user=os.getenv("ORACLE_DB_USER"),   
            password=os.getenv("ORACLE_DB_PASSWORD"),
            dsn=dsn
        )

    query = load_query()
    with conn.cursor() as cur:
        if os.getenv("ENVIRONMENT") == 'TEST':
            cur.execute(query, (acc_0, cpy_0))
        else:
            cur.execute(query, {
                'acc_0': acc_0,
                'cpy_0': cpy_0,
                'target_year': year
            })
        row = cur.fetchone()
        if not row:
            return None

        if month:
            month = int(month)
            if not 1 <= month <= 12:
                raise ValueError
            month_key = MONTH_COLUMNS.get(month)
            if not month_key:
                raise ValueError(f"Invalid month: {month}")
            col_index = list(MONTH_COLUMNS.values()).index(month_key) + 3
        else:
            col_index = 15

        return float(row[col_index]) if row[col_index] is not None else 0.0
