import numpy as np
import pandas as pd

from helpers.db_utils import get_db_engine
from helpers.dormant_utils.db_utils import insert_dormant_data
from helpers.logger_utils import get_logger
from services.minio_factory import get_minio_service

# ─── Set Up logger ────────────────────────────────────────────
logger = get_logger(__name__, log_filename="data_voix.log", clear_log=True)

def calculate_first_date(df):
    df = df.copy()
    df.loc[:, 'DATE'] = pd.to_datetime(df['DATE'])
    first_dates = df.groupby('Abonne')['DATE'].min()
    return df['Abonne'].map(first_dates)

def calculate_follow_up_status(df):
    df = df.copy()
    df.loc[:, 'DATE'] = pd.to_datetime(df['DATE'])
    df.loc[:, 'first_transaction_date'] = pd.to_datetime(df['first_transaction_date'])

    df.loc[:, 'txn_count'] = df.groupby(['Abonne', 'DATE']).cumcount() + 1

    def get_status(row):
        if row['DATE'] == row['first_transaction_date'] and row['txn_count'] == 1:
            return True
        elif row['DATE'] > row['first_transaction_date'] + pd.Timedelta(days=7):
            return True
        else:
            return False

    return df.apply(get_status, axis=1)

def filter_dates(df, date_to_process):
    df = df.copy()
    df.loc[:, 'DATE'] = pd.to_datetime(df['DATE'])
    date_to_process = pd.to_datetime(date_to_process).date()
    return df[df['DATE'].dt.date >= date_to_process].copy()

def process_data_voix(df, date_to_process):
    df = filter_dates(df, date_to_process)

    logger.info(f"🧾 Processing {len(df)} rows from 'DATAVOIX' sheet...")

    df.loc[:, 'first_transaction_date'] = calculate_first_date(df)
    df.loc[:, 'amount_check_status'] = np.where(df['Montant'] >= 200, True, False)
    df.loc[:, 'followup_status_within_7_days'] = calculate_follow_up_status(df)

    df = df.rename(columns={
        'DATE': 'date',
        'Abonne': 'subscriber_number',
        'PDV': 'point_of_sale',
        'Montant': 'amount'
    })

    df['unique_transaction_status'] = df.duplicated(subset=['date', 'subscriber_number'], keep=False)
    df['unique_transaction_status'] = df['unique_transaction_status'].apply(lambda x: False if x else True)

    df['Date'] = pd.to_datetime(df['date'])
    df['first_transaction_date'] = pd.to_datetime(df['first_transaction_date'])
    df["amount"] = pd.to_numeric(df["amount"], errors="coerce")

    df['client_ok_nok'] = df.apply(
        lambda row: True if (
                row['date'] == row['first_transaction_date'] and row['unique_transaction_status'] == True)
        else (True if (row['date'] > row['first_transaction_date'] + pd.Timedelta(days=30)) else False),
        axis=1
    )



    result_df = df[[
        'date', 'subscriber_number', 'point_of_sale', 'amount', 'amount_check_status',
        'first_transaction_date', 'unique_transaction_status', 'client_ok_nok'
    ]]

    return result_df


def process_data_voix_client_data(client_sheet_path, date_to_process, bucket_name):
    logger.info(f" Fetching file from MinIO path: {client_sheet_path} for date {date_to_process}")
    table_to_insert_data = "data_voix_data"
    minio_service = get_minio_service(bucket_name)
    engine = get_db_engine()
    try:
        client_cols_to_read = ['DATE', 'Abonne', 'PDV', 'Montant']
        excel_df = minio_service.read_excel(object_name=client_sheet_path, sheet_name='DATASYSVOIX',
                                            usecols=client_cols_to_read)

        logger.info(f"✅ File '{client_sheet_path}' fetched successfully.")
        df_voix = process_data_voix(excel_df, date_to_process)
        df_voix.rename(columns={'client_ok_nok': 'followup_status_within_7_days'}, inplace=True)

        print("processed data voix dataframe successfully")

        print("AMOUNT OK count:", (df_voix['amount_check_status'] == True).sum())
        print("AMOUNT NOK count:", (df_voix['amount_check_status'] == False).sum())


        print("unique count:", (df_voix['unique_transaction_status'] == True).sum())
        print("duplicate count:", (df_voix['unique_transaction_status'] == False).sum())

        print("OK count:", (df_voix['followup_status_within_7_days'] == True).sum())
        print("NOK count:", (df_voix['followup_status_within_7_days'] == False).sum())
        insert_dormant_data(table_to_insert_data, df_voix, engine, logger)
        logger.info(" Data ingestion pipeline completed.")
    except Exception as e:
        logger.exception("❌ Fatal error during processing:")
        raise
