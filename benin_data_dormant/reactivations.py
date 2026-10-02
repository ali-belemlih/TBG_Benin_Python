import pandas as pd

from helpers.db_utils import get_db_engine, get_db_connection
from helpers.dormant_utils.db_utils import insert_dormant_data, update_old_reactivation_records_db
from helpers.logger_utils import get_logger
from services.minio_factory import get_minio_service

logger = get_logger(__name__, log_filename="reactivations.log", clear_log=True)

def extract_excel_data(file_path, sheet_name):
    logger.info(f" Loading Excel sheet '{sheet_name}' from {file_path}...")
    df = pd.read_excel(file_path, sheet_name=sheet_name)
    logger.info(f" Successfully extracted {len(df)} rows from Excel.")
    return df

def fetch_active_subscribers_since(subscriber_numbers, date_to_process):

    if not subscriber_numbers:
        return pd.DataFrame(columns=["subscriber_number", "recent_transaction_exists"])

    placeholders = ','.join(['%s'] * len(subscriber_numbers))
    query = f"""
        SELECT  DISTINCT msisdn AS subscriber_number
        FROM moov_money_data
        WHERE msisdn IN ({placeholders})
        AND amount_status = TRUE
        AND unique_trans_status = TRUE
        AND within_7_days_status = TRUE
    """

    conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute(query, tuple(subscriber_numbers))
        results = cursor.fetchall()

    return pd.DataFrame(
        {"subscriber_number": [row[0] for row in results], "recent_transaction_exists": True}
    )


def transform_reactivation_data(df, date_to_process):
    logger.info(" Transforming reactivation data...")
    column_mapping = {
        "DATE DE RAPPORT": "report_date",
        "DEPARTEMENT": "department",
        "COMMUNE": "commune",
        "QUARTIER": "district",
        "NUMERO DE L'ABONNE": "subscriber_number",
        "NOM ET PRENOM DU BA": "agent_name",
        "NUMERO LOGIN DU BA": "agent_number",
        "MONTANT CASH-IN/CASHOUT": "transaction_amount",
    }
    df.rename(columns=column_mapping, inplace=True)

    df["subscriber_number"] = df["subscriber_number"].astype(str)
    df['subscriber_number'] = df['subscriber_number'].str.replace('.0', '', regex=False)
    df["report_date"] = pd.to_datetime(df["report_date"], errors="coerce")
    df["transaction_amount"] = pd.to_numeric(df["transaction_amount"], errors="coerce")
    df["district"] = df["district"].fillna("UNKNOWN")

    print(f"================== Number of Records During Transformation in partner sheet : {len(df)} ===================")

    subscriber_numbers = df["subscriber_number"].unique().tolist()
    activity_df = fetch_active_subscribers_since(subscriber_numbers, date_to_process)
    print(f"================== Number of Active Subscribers Since {date_to_process} : {len(activity_df)} ===================")

    merged_df = df.merge(activity_df, on="subscriber_number", how="left")
    merged_df["recent_transaction_exists"] = merged_df["recent_transaction_exists"].fillna(False)

    logger.info("✅ Data transformation complete.")
    return merged_df

def filter_dates(df, date_to_process):
    date_to_process = pd.to_datetime(date_to_process).date()
    return df[df['DATE DE RAPPORT'].dt.date >= date_to_process]

def process_moov_money_partner_data(partner_file_path, date_to_process, bucket_name):
    try:
        minio_service = get_minio_service(bucket_name)
        engine = get_db_engine()

        partner_cols_to_read = [
            'DATE DE RAPPORT',
            'DEPARTEMENT',
            'COMMUNE',
            'QUARTIER',
            'NUMERO DE L\'ABONNE',
            'NOM ET PRENOM DU BA',
            'NUMERO LOGIN DU BA',
            'MONTANT CASH-IN/CASHOUT'
        ]
        excel_df = minio_service.read_excel(object_name=partner_file_path, sheet_name='REACTIVATIONS_COMPTE MOOV MONEY',
                                            usecols=partner_cols_to_read)
        table_to_insert_data = "moov_money_reactivation_data"
        print(f"================== Number of Records Fetched from partner sheet : {len(excel_df)} ===================")
        date_filtered_df = filter_dates(excel_df, date_to_process)
        print(f"================== Number of Records After Data Filtering in partner sheet : {len(date_filtered_df)} ===================")
        transformed_df = transform_reactivation_data(date_filtered_df, date_to_process)
        print(f"================== Number of Records After Data Transformation in partner sheet : {len(transformed_df)} ===================")
        transformed_df.rename(columns = {'recent_transaction_exists' : 'matching_status'}, inplace = True)
        insert_dormant_data(table_to_insert_data, transformed_df, engine, logger)
        update_old_reactivation_records_db(engine)
        logger.info(" Reactivation data processing completed successfully.")
    except Exception as e:
        logger.exception("Fatal error during reactivation data processing:")
        raise
