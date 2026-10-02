from typing import List, Dict, Any

import pandas as pd
from helpers.db_utils import get_db_engine
from helpers.dormant_utils.db_utils import insert_dormant_data
from helpers.logger_utils import get_logger
from services.minio_factory import get_minio_service

logger = get_logger(__name__, log_filename="moov_money.log", clear_log=True)

def calculate_first_date(df: pd.DataFrame) -> pd.Series:
    date_col = 'Date'
    df[date_col] = pd.to_datetime(df[date_col])
    first_dates = df.groupby('MSISDN')[date_col].min()
    return df['MSISDN'].map(first_dates)


def calculate_follow_up_status(df: pd.DataFrame) -> pd.Series:
    df = df.copy()
    date_col = 'Date'
    df[date_col] = pd.to_datetime(df[date_col])
    first_date_col = 'First_Operation_Date'
    df[first_date_col] = calculate_first_date(df)

    df['txn_count'] = df.groupby(['MSISDN', date_col]).cumcount() + 1

    def get_status(row):
        if row[date_col] == row[first_date_col] and row['txn_count'] == 1:
            return True
        elif row[date_col] > row[first_date_col] + pd.Timedelta(days=30):
            return True
        else:
            return False

    return df.apply(get_status, axis=1)


def filter_dates(df: pd.DataFrame, date_to_process: str) -> pd.DataFrame:
    logger.info(f"Date to process: {date_to_process}")
    if not date_to_process:
        return df.copy()

    try:
        date_to_process = pd.to_datetime(date_to_process).date()
        print(f"Date to Process: {date_to_process}")
        df['Date'] = pd.to_datetime(df['Date'])
        return df[df['Date'].dt.date >= date_to_process]
    except Exception as e:
        logger.error(f"Error filtering dates: {e}")
        raise

def transform_excel_data(df: pd.DataFrame, date_to_process: str) -> List[Dict[str, Any]]:
    logger.info(f"🧾 Processing {len(df)} rows from 'DATAMM' sheet...")

    try:
        df = filter_dates(df, date_to_process)
        logger.info(f"Rows after date filtering: {len(df)}")

        if len(df) == 0:
            logger.warning("⚠️ No data found after date filtering")
            return []

        # Clean column names
        df.columns = [col.strip() for col in df.columns]
        logger.info(f"Columns in DataFrame: {df.columns.tolist()}")

        required_columns = ['Date', 'MSISDN', 'Type','AMOUNT']
        missing_cols = [col for col in required_columns if col not in df.columns]
        if missing_cols:
            raise ValueError(f"Missing required columns: {missing_cols}")

        df['MSISDN'] = df['MSISDN'].astype(str).str.replace(r'\.0$', '', regex=True)
        df['AMOUNT'] = pd.to_numeric(df['AMOUNT'], errors='coerce')
        df = df.dropna(subset=['MSISDN', 'AMOUNT'])

        # Calculate derived fields
        df['amount_status'] = df['AMOUNT'].apply(lambda x: True if x >= 500 else False)
        df['first_operation_date'] = calculate_first_date(df)
        df['followup_status_within_7_days'] = calculate_follow_up_status(df)

        df['client_uniqueness'] = df.duplicated(subset=['Date', 'MSISDN'], keep=False)
        df['client_uniqueness'] = df['client_uniqueness'].apply(lambda x: False if x else True)

        df['Date'] = pd.to_datetime(df['Date'])
        df['first_operation_date'] = pd.to_datetime(df['first_operation_date'])

        df['client_ok_nok'] = df.apply(
            lambda row: True if (
                    row['Date'] == row['first_operation_date'] and row['client_uniqueness'] == True)
            else (True if (row['Date'] > row['first_operation_date'] + pd.Timedelta(days=30)) else False),
            axis=1
        )

        transformed = []
        for _, row in df.iterrows():
            try:
                transaction_date = pd.to_datetime(row['Date'])
                first_op_date = pd.to_datetime(row['first_operation_date'])
                amount_value = pd.to_numeric(row['AMOUNT'], errors='coerce')
                transformed.append({
                    'transaction_date': transaction_date.strftime('%Y-%m-%d %H:%M:%S') if pd.notna(
                        transaction_date) else None,
                    'msisdn': row['MSISDN'],
                    'transaction_type': row.get('Type', None),
                    'amount': float(amount_value) if pd.notna(amount_value) else None,
                    'amount_status': row['amount_status'],
                    'first_operation_date': first_op_date.strftime('%Y-%m-%d %H:%M:%S') if pd.notna(
                        first_op_date) else None,
                    # 'within_7_days_status': row['followup_status_within_7_days'],
                    'unique_trans_status': row['client_uniqueness'],
                    'within_7_days_status': row['client_ok_nok']
                })
            except Exception as e:
                logger.warning(f"Data transformation error for row: {e}")
                continue

        logger.info(f"✅ Successfully transformed {len(transformed)} rows")
        return transformed

    except Exception as e:
        logger.error(f"❌ Error in transform_excel_data: {e}")
        raise

def process_moov_money_client_data(client_sheet_path: str, date_to_process: str,
                                   bucket_name: str = "data-dormant-files"):
    logger.info(f"📦 Fetching file from MinIO path: {client_sheet_path}")
    table_to_insert_data = "moov_money_data"
    engine = get_db_engine()
    try:
        minio_service = get_minio_service(bucket_name)
        client_cols_to_read = ['Date', 'MSISDN', 'Type', 'AMOUNT']
        excel_df = minio_service.read_excel(
            object_name=client_sheet_path,
            sheet_name='DATASYSMM',
            usecols = client_cols_to_read
        )

        if excel_df.empty:
            logger.warning("⚠️ Empty DataFrame loaded from Excel file")
            return

        excel_df = excel_df.dropna(how="all")
        logger.info(f"✅ File '{client_sheet_path}' fetched successfully. Rows: {len(excel_df)}")

        # Process the DataFrame
        db_data = transform_excel_data(excel_df, date_to_process)
        df_data = pd.DataFrame(db_data)
        if not db_data:
            logger.warning("⚠️ No data to process after transformation")
            return
        insert_dormant_data(table_to_insert_data, df_data, engine, logger)

    except Exception as e:
        logger.error(f"❌ Fatal error during processing: {e}")
        raise
