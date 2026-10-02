import logging
from helpers.db_utils import (
    upsert_financial_data,
    upsert_collapse_financial_data
)

logger = logging.getLogger(__name__)


def resolve_and_upsert(cur, tbg_key, value, version_id, date):
    """
    Resolves tbg_key across collapse and financial tables
    and performs the appropriate upsert.
    """

    # 1️⃣ collapse_types
    cur.execute("SELECT id FROM collapse_types WHERE tbg_key = %s;", (tbg_key,))
    row = cur.fetchone()
    if row:
        upsert_collapse_financial_data(
            cur,
            "collapse_monthly_data",
            entity_id=row[0],
            entity_type="type",
            date_value=date,
            real_value=value,
            version_id=version_id
        )
        return

    # 2️⃣ collapse_categories
    cur.execute("SELECT id FROM collapse_categories WHERE tbg_key = %s;", (tbg_key,))
    row = cur.fetchone()
    if row:
        upsert_collapse_financial_data(
            cur,
            "collapse_monthly_data",
            entity_id=row[0],
            entity_type="category",
            date_value=date,
            real_value=value,
            version_id=version_id
        )
        return

    # 3️⃣ collapse_subcategories
    cur.execute("SELECT id FROM collapse_subcategories WHERE tbg_key = %s;", (tbg_key,))
    row = cur.fetchone()
    if row:
        upsert_collapse_financial_data(
            cur,
            "collapse_monthly_data",
            entity_id=row[0],
            entity_type="subcategory",
            date_value=date,
            real_value=value,
            version_id=version_id
        )
        return

    # 4️⃣ financial_types
    cur.execute("SELECT id FROM financial_types WHERE tbg_key = %s;", (tbg_key,))
    row = cur.fetchone()
    if row:
        upsert_financial_data(
            cur,
            "financial_metrics_data",
            type_id=row[0],
            metric_id=None,
            submetric_id=None,
            date_value=date,
            real_value=value,
            version_id=version_id
        )
        return

    # 5️⃣ financial_metrics
    cur.execute("SELECT id FROM financial_metric WHERE tbg_key = %s;", (tbg_key,))
    row = cur.fetchone()
    if row:
        upsert_financial_data(
            cur,
            "financial_metrics_data",
            type_id=None,
            metric_id=row[0],
            submetric_id=None,
            date_value=date,
            real_value=value,
            version_id=version_id
        )
        return

    # 6️⃣ financial_submetrics
    cur.execute("SELECT id FROM financial_submetric WHERE tbg_key = %s;", (tbg_key,))
    row = cur.fetchone()
    if row:
        upsert_financial_data(
            cur,
            "financial_metrics_data",
            type_id=None,
            metric_id=None,
            submetric_id=row[0],
            date_value=date,
            real_value=value,
            version_id=version_id
        )
        return

    # ❌ Not found
    logger.error(f"TBG key '{tbg_key}' not found in any target table.")
    raise ValueError(f"TBG key '{tbg_key}' not found in any target table.")
