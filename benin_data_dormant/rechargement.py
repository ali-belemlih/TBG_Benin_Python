import pandas as pd

from helpers.db_utils import get_db_engine, get_db_connection
from helpers.dormant_utils.db_utils import insert_dormant_data, update_matching_status_for_voix_auto_rechargement
from helpers.logger_utils import get_logger
from services.minio_factory import get_minio_service
from sqlalchemy import text
logger = get_logger(__name__, log_filename="reactivations.log", clear_log=True)

def fetch_active_subscribers_since(subscriber_numbers, date_to_process):
    if not subscriber_numbers:
        return pd.DataFrame(columns=["subscriber_number", "recent_transaction_exists"])
    date_to_process = pd.to_datetime(date_to_process).date()
    query = """
        SELECT  subscriber_number AS subscriber_number
        FROM data_voix_data
        WHERE subscriber_number = ANY(%s)
        AND amount_check_status = True
        AND unique_transaction_status = True
        AND followup_status_within_7_days  = True
        AND first_transaction_date >= %s
    """
    conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute(query, (subscriber_numbers, date_to_process))
        results = cursor.fetchall()
    found_msisdns = set(row[0] for row in results)

    return pd.DataFrame([
        {"subscriber_number": msisdn, "recent_transaction_exists": msisdn in found_msisdns}
        for msisdn in subscriber_numbers
    ])

def transform_reactivation_data(df, date_to_process):
    logger.info(" Transforming reactivation data...")
    column_mapping = {
        "DATE DE RAPPORT": "report_date",
        "DEPARTEMENT": "department",
        "COMMUNE": "commune",
        "QUARTIER": "neighborhood",
        "NUMERO DE L'ABONNE": "subscriber_number",
        "NOM ET PRENOM DU BA": "agent_name",
        "NUMERO LOGIN DU BA": "agent_number",
        'MONTANT DEPOT' : "deposit_amount",
        'TYPE D\'ACTIVATION' : "activation_type",
        "MONTANT DE L'ACTIVATION": "activation_amount",
    }
    df.rename(columns=column_mapping, inplace=True)

    df["subscriber_number"] = df["subscriber_number"].astype(str)
    subscriber_numbers = df["subscriber_number"].dropna().unique().tolist()

    query = """
        SELECT subscriber_number, amount
        FROM data_voix_data
        WHERE subscriber_number = ANY(:subs)
    """
    engine = get_db_engine()
    with engine.connect() as conn:
        voix_df = pd.read_sql(text(query), conn, params={"subs": subscriber_numbers})

    amounts_df = voix_df.groupby("subscriber_number", as_index=False)["amount"].sum()
    amounts_df.rename(columns={"amount": "total_amount"}, inplace=True)

    df = df.merge(amounts_df, on="subscriber_number", how="left")

    df["total_amount"] = df["total_amount"].where(pd.notnull(df["total_amount"]), None)

    df["report_date"] = pd.to_datetime(df["report_date"], errors="coerce")
    df["deposit_amount"] = pd.to_numeric(df["deposit_amount"], errors="coerce")
    df["total_amount"] = pd.to_numeric(df["total_amount"], errors="coerce")
    df["activation_amount"] = pd.to_numeric(df["activation_amount"], errors="coerce")
    df["neighborhood"] = df["neighborhood"].fillna("UNKNOWN")

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

def process_data_voix_partner_data(partner_file_path, date_to_process, bucket_name):
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
            'MONTANT DEPOT',
            'TYPE D\'ACTIVATION',
            'MONTANT DE L\'ACTIVATION'
        ]

        excel_df = minio_service.read_excel(object_name=partner_file_path, sheet_name='AUTO RECHARGEMENT_DATA_VOIX',
                                            usecols=partner_cols_to_read)

        table_to_insert_data = "data_voix_auto_rechargement_data"
        print(f"================== Number of Records Fetched from partner sheet : {len(excel_df)} ===================")
        date_filtered_df = filter_dates(excel_df, date_to_process)
        print(f"================== Number of Records After Data Filtering in partner sheet : {len(date_filtered_df)} ===================")
        transformed_df = transform_reactivation_data(date_filtered_df, date_to_process)
        print(f"================== Number of Records After Data Transformation in partner sheet : {len(transformed_df)} ===================")
        transformed_df.rename(columns = {'recent_transaction_exists' : 'matching_status'}, inplace = True)

        print("OK COUNT" , (transformed_df["matching_status"] == True).sum())
        print("NOK COUNT" , (transformed_df["matching_status"] == False).sum())
        insert_dormant_data(table_to_insert_data, transformed_df, engine, logger)
        update_matching_status_for_voix_auto_rechargement(engine)
        logger.info(" Reactivation data processing completed successfully.")
    except Exception as e:
        logger.exception("Fatal error during reactivation data processing:")
        raise

    logger.info("✅ ETL completed successfully.")
    logger.info("=========== Finished Auto Rechargement Data Voix Script ============= ")
