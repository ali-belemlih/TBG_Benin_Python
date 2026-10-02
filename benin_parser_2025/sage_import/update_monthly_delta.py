from datetime import datetime
from .fetch_account_balance import fetch_account_balance_value
from helpers.db_utils import get_db_connection, upsert_financial_data

def update_monthly_delta(
    acc_0, cpy_0,
    version_id,
    metric_id,
    month,     # current month: '06'
    year,      # e.g., '2025'
    date,      # datetime object (e.g., June 1st)
    submetric_id=None,
    is_negative=False
):
    current_month = int(month)
    previous_month = current_month - 1
    if previous_month <= 0:
        print(f"Invalid month: {month} for delta computation")
        return

    prev_month_str = f"{previous_month:02}"
    print(f"Month: {month}, Previous Month: {prev_month_str}")
    # Fetch balance values
    current_value = fetch_account_balance_value(acc_0=acc_0, cpy_0=cpy_0, month=month) or 0
    previous_value = fetch_account_balance_value(acc_0=acc_0, cpy_0=cpy_0, month=prev_month_str) or 0
    delta = (current_value - previous_value) / 1_000_000
    print(f"For Account number: {acc_0} current_value: {current_value} previous_value: {previous_value} delta: {delta}")
    if is_negative:
        delta *= -1

    conn = get_db_connection()
    with conn.cursor() as cur:
        cur.execute("""
            SELECT real_value FROM financial_metrics_data
            WHERE financial_metric_id = %s AND version_id = %s;
        """, (metric_id, version_id))
        row = cur.fetchone()
        existing_value = row[0] if row and row[0] is not None else 0.0

        new_value = existing_value + delta

        upsert_financial_data(
            cur=cur,
            table_name="financial_metrics_data",
            type_id=None,
            metric_id=metric_id,
            submetric_id=submetric_id,
            date_value=date,
            real_value=new_value,
            version_id=version_id
        )

        print(f"[financial_metrics_data][metric_id={metric_id}] {acc_0}/{cpy_0}: {existing_value} + ({current_value} - {previous_value}) = {new_value}")

    conn.commit()
    conn.close()
