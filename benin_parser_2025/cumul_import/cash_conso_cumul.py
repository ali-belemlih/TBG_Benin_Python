from helpers.db_utils import get_db_connection, get_version_id_by_name
from helpers.parse_arg import parse_arguments


def process_r38_r39(label, conn, cur, date, version_id):
    label_to_fetch = label
    query = f"""
    SELECT 
        {label_to_fetch}
    FROM financial_metrics_data fmd
    WHERE fmd.financial_metric_id = %s
    AND fmd.date = %s
    AND version_id = %s
    """
    metric_ids = [56,57]

    try:
        for metric_id in metric_ids:
            cur.execute(query, (metric_id,date,version_id))
            result = cur.fetchone()

            if result:
                value = result[0]
                print(f"Fetched {label_to_fetch} for ID {metric_id}: {value}")
            else:
                print(f"No data found for financial_metric_id {metric_id} and label {label}")

            if result:
                update_query = f"""
                UPDATE financial_cumulative_data
                SET 
                    {label} = %s
                WHERE date = %s
                AND financial_metric_id = %s
                """
                cur.execute(update_query, (value, date, metric_id))
                print(f"Updated {label} for ID {metric_id} with value {value} for date {date}.")
        conn.commit()

    except Exception as e:
        print(f"❌ Error processing {label}: {str(e)}")
        conn.rollback()

    print(f"✅ Updated {label} successfully in financial_cumulative_data for date {date}.")

def process_r_40(label, conn, cur, date, version_id):
    label_to_fetch = label
    query = f"""
    SELECT 
        {label_to_fetch}
    FROM financial_metrics_data fmd
    WHERE fmd.financial_type_id = %s
    AND fmd.date = %s
    AND version_id = %s
    """
    financial_type_id = [16]

    try:
        for type_id in financial_type_id:
            cur.execute(query, (type_id,date,version_id))
            result = cur.fetchone()

            if result:
                value = result[0]
                print(f"Fetched {label_to_fetch} for ID {type_id}: {value}")
            else:
                print(f"No data found for financial_metric_id {type_id} and label {label}")

            if result:
                update_query = f"""
                UPDATE financial_cumulative_data
                SET 
                    {label} = %s
                WHERE date = %s
                AND financial_type_id = %s
                """
                cur.execute(update_query, (value, date, type_id))
                print(f"Updated {label} for ID {type_id} with value {value} for date {date}.")
        conn.commit()

    except Exception as e:
        print(f"❌ Error processing {label}: {str(e)}")
        conn.rollback()

if __name__ == "__main__":
    args = parse_arguments()
    month_year = args.month_year
    month = int(month_year[:2])
    year = month_year[2:]
    date = f"{year}-{month:02d}-01"

    version_id = get_version_id_by_name(args.version_id)

    # Base labels
    mapping_sets = [
        "real_value",
        "budget_value",
        "last_year_real_value",
    ]

    # Dynamically include actuals based on month
    if 4 <= month <= 6:
        mapping_sets.append("actual1_value")
    elif 7 <= month <= 8:
        mapping_sets.append("actual2_value")
    elif month == 9:
        mapping_sets.extend(["actual2_value", "actual3_value"])
    elif 10 <= month <= 12:
        mapping_sets.append("actual3_value")

    all_results = []
    for label in mapping_sets:
        try:
            computed_cache = {}
            conn = get_db_connection()
            cur = conn.cursor()
            
            print(f"\nProcessing {label}...")

            process_r38_r39(label, conn, cur, date, version_id)
            process_r_40(label, conn, cur, date, version_id)

        except Exception as e:
            print(f"❌ Error processing {label}: {e}")
        finally:
            cur.close()
            conn.close()

    print("✅ All mappings processed.")

