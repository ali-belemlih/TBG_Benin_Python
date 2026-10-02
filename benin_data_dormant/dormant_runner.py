import traceback
from contextlib import closing

from benin_data_dormant.data_voix import process_data_voix_client_data
from benin_data_dormant.moov_money import process_moov_money_client_data
from benin_data_dormant.reactivations import process_moov_money_partner_data
from benin_data_dormant.rechargement import process_data_voix_partner_data
from helpers.db_utils import get_db_connection
from helpers.dormant_utils.parse_arg import parse_arguments
from helpers.logger_utils import get_logger

# Logging setup
logger = get_logger(__name__, log_filename="dormant_runner.log", clear_log=True)

def safe_process(func, *args, label="processing"):
    try:
        func(*args)
    except Exception as e:
        logger.error(f"⚠️ Error while {label}: {e}")
        logger.debug(traceback.format_exc())
        exit(f"❌ Script failed due to error: {e}")

def fetch_metadata_record(cursor, record_id):
    cursor.execute(f"SELECT * FROM data_dormant_metadata WHERE id = %s", (record_id,))
    row = cursor.fetchone()
    return dict(zip([desc[0] for desc in cursor.description], row)) if row else None

def fetch_upload_file(cursor, file_id):
    cursor.execute(f"SELECT * FROM data_dormant_upload_files WHERE id = %s", (file_id,))
    row = cursor.fetchone()
    return dict(zip([desc[0] for desc in cursor.description], row)) if row else None

def run_dormant_processing():
    args = parse_arguments()
    record_to_check_id = args.id
    bucket_name = args.bucket_name

    with closing(get_db_connection()) as conn:
        try:
            with conn.cursor() as cursor:
                # Step 1: Fetch metadata
                record = fetch_metadata_record(cursor, record_to_check_id)
                if not record:
                    logger.error(f"❌ No metadata found for ID: {record_to_check_id}")
                    return

                logger.info("======== RECORD FOUND =========")
                dormant_file_type = record["dormant_file_type"].lower()
                date_to_process = record["processing_start_date"]
                # Step 2: Fetch client and partner sheet info
                client_data = fetch_upload_file(cursor, record["client_sheet_id"])
                partner_data = fetch_upload_file(cursor, record["partner_sheet_id"])

                client_file_path = client_data["file_path"]
                partner_file_path = partner_data["file_path"]

                logger.info(f"📄 CLIENT FILE PATH: {client_file_path}")
                logger.info(f"📄 PARTNER FILE PATH: {partner_file_path}")

        except Exception as e:
            logger.error(f"❌ Exception during metadata/loading phase: {e}")
            logger.debug(traceback.format_exc())
            exit(f"❌ Script failed due to error: {e}")

    # ========== DORMANT TYPE-SPECIFIC LOGIC ==========
    if dormant_file_type == "data_voix":
        print("Processing for data voix client started")
        safe_process(
            process_data_voix_client_data,
            client_file_path, date_to_process, bucket_name,
            label="processing data_voix client data"
        )
        print("Processing for data voix client completed successfully")
        print("processing for data voix auto rechargement started")
        safe_process(
            process_data_voix_partner_data,
             partner_file_path, date_to_process, bucket_name,
            label="processing data_voix partner data"
        )
        print("processing for data voix auto rechargement completed successfully")

    elif dormant_file_type == "moov_money":
        print("processing for moov money client data started")
        # Call Moov Money script with record.client_sheet_path,  record.partner_sheet_path, date, bucket_name
        safe_process(
            process_moov_money_client_data,
            client_file_path, date_to_process, bucket_name,
            label="processing moov_money client data"
        )
        print("processing for moov money client data completed successfully")
        print("processing for moov money partner data started")
        safe_process(
            process_moov_money_partner_data,
             partner_file_path, date_to_process, bucket_name,
            label="processing moov money partner data"
        )
        print("processing for moov money partner data finished successfully")

    else:
        logger.error(f"❌ Invalid dormant_file_type for record ID {record_to_check_id}: '{dormant_file_type}'")
        # Send error message back to NiFi if needed

if __name__ == "__main__":
    try:
        run_dormant_processing()
    except Exception as e:
        logger.error(f"Fatal Error: {e}")
        logger.debug(traceback.format_exc())
        exit(f"❌ Script failed due to error: {e}")
