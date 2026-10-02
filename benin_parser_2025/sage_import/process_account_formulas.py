from typing import Any, Optional
import logging
from datetime import datetime

from helpers.db_utils import (
    get_db_connection,
    get_version_id_by_name,
    upsert_financial_data,
    upsert_collapse_financial_data
)
from helpers.parse_arg import parse_arguments
from .target_resolver import resolve_and_upsert
from .fetch_account_balance import fetch_account_balance_value

MILLION = 1_000_000

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

def resolve_tbg_key(cur, tbg_key: str) -> Optional[dict]:
    # --- Check Collapse Tables ---
    collapse_checks = [
        ("collapse_categories", "category"),
        ("collapse_subcategories", "subcategory"),
        ("collapse_types", "type"),
    ]
    for table, entity_type in collapse_checks:
        cur.execute(f"""
            SELECT id FROM {table}
            WHERE tbg_key = %s;
        """, (tbg_key,))
        row = cur.fetchone()
        if row:
            logger.info(f"tbg_key='{tbg_key}' resolved to collapse table='{table}', entity_type='{entity_type}', id={row[0]}")
            return {
                "source": "collapse_monthly_data",
                "entity_type": entity_type,
                "record_id": row[0]
            }

    # --- Check Financial Tables ---
    financial_checks = [
        ("financial_types", "financial_type_id"),
        ("financial_metric", "financial_metric_id"),
        ("financial_submetric", "financial_submetric_id"),
    ]
    for table, id_column in financial_checks:
        cur.execute(f"""
            SELECT id FROM {table}
            WHERE tbg_key = %s;
        """, (tbg_key,))
        row = cur.fetchone()
        if row:
            logger.info(f"tbg_key='{tbg_key}' resolved to financial table='{table}', id_column='{id_column}', id={row[0]}")
            return {
                "source": "financial_metrics_data",
                "id_column": id_column,
                "record_id": row[0]
            }

    logger.warning(f"tbg_key='{tbg_key}' not found in any collapse or financial table.")
    return None

def process_account_formulas(month_year: str, version_id: int):
    month = month_year[:2]
    year = month_year[2:]
    date = datetime(int(year), int(month), 1)

    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            logger.info("Fetching ACCOUNT formulas...")
            cur.execute("""
                SELECT id, tbg_key, account_details
                FROM tbg_formulas
                WHERE formula_type = 'ACCOUNT';
            """)
            formulas = cur.fetchall()
            logger.info(f"{len(formulas)} formulas found.")

            for formula_id, tbg_key, account_details in formulas:
                if not account_details:
                    logger.warning(f"Formula {formula_id} has no account_details.")
                    continue

                # Resolve tbg_key once per formula
                resolved = resolve_tbg_key(cur, tbg_key)
                if not resolved:
                    logger.warning(f"Formula {formula_id}: tbg_key='{tbg_key}' could not be resolved. Skipping.")
                    continue

                seen_accounts = set()

                for acc in account_details:
                    acc_no = acc.get("no")
                    cpy = acc.get("type")
                    is_negative = acc.get("is_negative", False)
                    fetch_in_negative = acc.get("fetch_in_negative", False)

                    if not acc_no or not cpy:
                        logger.warning(f"Invalid account entry in formula {formula_id}: {acc}")
                        continue

                    key = (acc_no, cpy)
                    if key in seen_accounts:
                        logger.warning(f"Duplicate account {key} in formula {formula_id}")
                        continue
                    seen_accounts.add(key)

                    # Step 1: Fetch raw value from SAGE
                    raw_value = fetch_account_balance_value(
                        acc_0=acc_no,
                        cpy_0=cpy,
                        month=month,
                        year=year
                    )
                    if raw_value is None:
                        logger.warning(f"No SAGE value for acc={acc_no}, cpy={cpy}")
                        continue

                    # Step 2: Apply sign logic
                    fetched_value = raw_value / MILLION
                    if fetch_in_negative:
                        fetched_value *= -1
                    if is_negative:
                        fetched_value *= -1

                    # Step 3: Fetch existing value, accumulate, upsert
                    if resolved["source"] == "collapse_monthly_data":
                        entity_type = resolved["entity_type"]
                        entity_id = resolved["record_id"]

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
                        logger.info(
                            f"[collapse_monthly_data] formula={formula_id}, tbg_key={tbg_key}, "
                            f"entity_type={entity_type}, entity_id={entity_id}: "
                            f"{current_value} + {fetched_value} = {new_value}"
                        )

                    elif resolved["source"] == "financial_metrics_data":
                        id_column = resolved["id_column"]
                        record_id = resolved["record_id"]

                        cur.execute(f"""
                            SELECT real_value FROM financial_metrics_data
                            WHERE {id_column} = %s AND version_id = %s;
                        """, (record_id, version_id))
                        current_value = (cur.fetchone() or [0])[0] or 0
                        new_value = current_value + fetched_value

                        upsert_financial_data(
                            cur, "financial_metrics_data",
                            type_id=record_id if id_column == "financial_type_id" else None,
                            metric_id=record_id if id_column == "financial_metric_id" else None,
                            submetric_id=record_id if id_column == "financial_submetric_id" else None,
                            date_value=date,
                            real_value=new_value,
                            version_id=version_id
                        )
                        logger.info(
                            f"[financial_metrics_data] formula={formula_id}, tbg_key={tbg_key}, "
                            f"{id_column}={record_id}: "
                            f"{current_value} + {fetched_value} = {new_value}"
                        )

        conn.commit()
        logger.info("Processing completed successfully.")
    except Exception:
        conn.rollback()
        logger.exception("Error occurred. Transaction rolled back.")
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    args = parse_arguments()

    month_year = args.month_year
    version_name = args.version_id

    version_id = get_version_id_by_name(version_name)

    process_account_formulas(
        month_year=month_year,
        version_id=version_id
    )
