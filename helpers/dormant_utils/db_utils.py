from sqlalchemy import text

def insert_dormant_data(table_to_insert_data,df,engine, logger):

    logger.info(f"⏳ Attempting to insert {len(df)} rows into '{table_to_insert_data}' table...")

    try:
        df.to_sql(
            name=table_to_insert_data,
            con=engine,
            if_exists='append',
            index=False,
            method = 'multi'
        )
        logger.info(f"✅ Successfully inserted {len(df)} rows into '{table_to_insert_data}' table.")

    except Exception as e:
        logger.error(f"❌ Failed to insert data into '{table_to_insert_data}' table: {e}")
        raise
def update_old_reactivation_records_db(engine,):
    update_query = """
    UPDATE moov_money_reactivation_data
    SET matching_status = dm.any_true
    FROM (
        SELECT msisdn, BOOL_OR(within_7_days_status) AS any_true
        FROM moov_money_data
        WHERE amount_status = TRUE 
        AND unique_trans_status = TRUE 
        AND within_7_days_status = TRUE
        GROUP BY moov_money_data.msisdn 
    ) dm
    WHERE moov_money_reactivation_data.subscriber_number = dm.msisdn;
    """

    # Execute the query
    with engine.connect() as conn:
        conn.execute(text(update_query))
        print("Update operation completed successfully.")


def update_matching_status_for_voix_auto_rechargement(engine):
    update_query = """
    UPDATE data_voix_auto_rechargement_data
    SET matching_status = dm.any_true
    FROM (
        SELECT subscriber_number, BOOL_OR(followup_status_within_7_days) AS any_true
        FROM data_voix_data
        WHERE amount_check_status = TRUE
        AND unique_transaction_status = TRUE
        AND followup_status_within_7_days = TRUE
        GROUP BY data_voix_data.subscriber_number
    ) dm
    WHERE data_voix_auto_rechargement_data.subscriber_number = dm.subscriber_number;
    """
    with engine.connect() as conn:
        conn.execute(text(update_query))
        print("Update operation completed successfully for data_voix_auto_rechargement_data.")
