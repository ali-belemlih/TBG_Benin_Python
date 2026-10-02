import psycopg2
from datetime import datetime
from helpers.db_utils import (
    get_db_connection, get_version_id_by_name,
    upsert_financial_data, upsert_collapse_financial_data
)
from helpers.parse_arg import parse_arguments
from .fetch_account_balance import fetch_account_balance_value
from .update_monthly_delta import update_monthly_delta
from .sage_accounts_list import entries

def update_real_value(
    acc_0, cpy_0, version_id, month=None, year=None, entity_type=None,
    entity_id=None, financial_metric_id=None, financial_submetric_id=None,
    date=None, is_negative=None, fetch_in_negative=None
):
    raw_value = fetch_account_balance_value(acc_0=acc_0, cpy_0=cpy_0, month=month, year=year)
    if raw_value is None:
        print(f"No value fetched for acc_0={acc_0}, cpy_0={cpy_0}")
        return

    fetched_value = (raw_value / 1_000_000)
    # Apply consistent sign logic ONCE
    if fetch_in_negative:
        fetched_value *= -1
    if is_negative:
        fetched_value *= -1  # Apply both flags at fetch stage

    print(f"Value for {acc_0}: {fetched_value}")
    conn = get_db_connection()
    with conn.cursor() as cur:
        if entity_id:
            cur.execute("""
                SELECT real_value FROM collapse_monthly_data
                WHERE entity_type = %s AND entity_id = %s AND version_id = %s;
            """, (entity_type, entity_id, version_id))
            current_value = (cur.fetchone() or [0])[0] or 0
            new_value = current_value + fetched_value
            upsert_collapse_financial_data(
                cur, "collapse_monthly_data",
                entity_id=entity_id,
                entity_type=entity_type,
                date_value=date,
                real_value=new_value,
                version_id=version_id
            )
            print(f"[collapse_monthly_data] {entity_id}: {current_value} + {fetched_value} = {new_value}")
        else:
            if financial_metric_id:
                cur.execute("""
                    SELECT real_value FROM financial_metrics_data
                    WHERE financial_metric_id = %s AND version_id = %s;
                """, (financial_metric_id, version_id))
            elif financial_submetric_id:
                cur.execute("""
                    SELECT real_value FROM financial_metrics_data
                    WHERE financial_submetric_id = %s AND version_id = %s;
                """, (financial_submetric_id, version_id))
            else:
                print("❌ Neither financial_metric_id nor financial_submetric_id provided. Skipping.")
                return

            current_value = (cur.fetchone() or [0])[0] or 0
            new_value = current_value + fetched_value

            upsert_financial_data(
                cur, "financial_metrics_data",
                type_id=None,
                metric_id=financial_metric_id,
                submetric_id=financial_submetric_id,
                date_value=date,
                real_value=new_value,
                version_id=version_id
            )
            print(f"[financial_metrics_data] metric={financial_metric_id}, submetric={financial_submetric_id}: {current_value} + {fetched_value} = {new_value}")
    conn.commit()
    conn.close()


if __name__ == "__main__":
    args = parse_arguments()
    month = args.month_year[:2]
    year = args.month_year[2:]
    version_id = get_version_id_by_name(args.version_id)
    date = datetime(int(year), int(month), 1)

    for entry in entries:
        update_real_value(
            acc_0=entry["acc_0"],
            cpy_0=entry["cpy_0"],
            version_id=version_id,
            month=month,
            year=year,
            date=date,
            entity_type=entry.get("entity_type"),
            entity_id=entry.get("entity_id"),
            financial_metric_id=entry.get("financial_metric_id"),
            financial_submetric_id=entry.get("financial_submetric_id"),
            is_negative=entry.get("is_negative"),
            fetch_in_negative=entry.get("fetch_in_negative")
        )
