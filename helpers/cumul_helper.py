from calendar import monthrange
from datetime import datetime

from calendar import monthrange

def get_financial_metrics_data(conn, month_year, version_id):
    """
    Fetch financial_metrics_data for all months up to the given month_year,
    using default versions for previous months and the given version_id for the target month.
    Excludes financial data under categories 'Mobile Money' and 'Data Mobile'.
    Handles both cases where financial_submetric_id may be NULL or not.
    """
    target_month = int(month_year[:2])
    target_year = int(month_year[2:])

    version_map = {}

    with conn.cursor() as cur:
        # 1️⃣ Get default versions for earlier months
        cur.execute("""
            SELECT month, year, id
            FROM tbg_version
            WHERE is_default = TRUE AND year = %s AND month < %s
        """, (target_year, target_month))

        for month, year, default_version_id in cur.fetchall():
            version_map[(year, month)] = default_version_id

        # 2️⃣ Add current month with provided version_id
        version_map[(target_year, target_month)] = version_id

        # 3️⃣ Build date/version conditions dynamically
        conditions = []
        params = []
        for (year, month), ver_id in version_map.items():
            start_date = f"{year}-{month:02d}-01"
            end_day = monthrange(year, month)[1]
            end_date = f"{year}-{month:02d}-{end_day}"
            conditions.append("(fmd.date >= %s AND fmd.date <= %s AND fmd.version_id = %s)")
            params.extend([start_date, end_date, ver_id])

        # 4️⃣ Query with LEFT JOINs to traverse category hierarchy safely
        query = f"""
            SELECT fmd.financial_type_id,
                fmd.financial_metric_id,
                fmd.financial_submetric_id,
                fmd.date,
                fmd.real_value,
                fmd.budget_value,
                fmd.last_year_real_value,
                fmd.actual1_value,
                fmd.actual2_value,
                fmd.actual3_value
            FROM public.financial_metrics_data fmd
            LEFT JOIN public.financial_submetric fsm ON fmd.financial_submetric_id = fsm.id
            LEFT JOIN public.financial_metric fm 
                ON COALESCE(fmd.financial_metric_id, fsm.financial_metric_id) = fm.id
            LEFT JOIN public.financial_types ft 
                ON COALESCE(fm.financial_type_id, fmd.financial_type_id) = ft.id
            LEFT JOIN public.financial_categories fc 
                ON ft.financial_category_id = fc.id
            WHERE {" OR ".join(conditions)}
            AND (fc.name IS NULL OR fc.name NOT IN ('Mobile Money', 'Data Mobile'))
            ORDER BY fmd.financial_type_id, fmd.financial_metric_id, fmd.financial_submetric_id, fmd.date
        """


        cur.execute(query, params)
        return cur.fetchall()

def get_collapse_monthly_data(conn, month_year, version_id):
    target_month = int(month_year[:2])
    target_year = int(month_year[2:])

    version_map = {}

    with conn.cursor() as cur:
        # Get default versions for months < target month
        cur.execute("""
            SELECT month, year, id
            FROM tbg_version
            WHERE is_default = TRUE AND year = %s AND month < %s
        """, (target_year, target_month))

        for month, year, default_version_id in cur.fetchall():
            version_map[(year, month)] = default_version_id

        # Add target month with provided version_id
        version_map[(target_year, target_month)] = version_id

        # Prepare WHERE conditions
        conditions = []
        params = []
        for (year, month), ver_id in version_map.items():
            start_date = f"{year}-{month:02d}-01"
            end_day = monthrange(year, month)[1]
            end_date = f"{year}-{month:02d}-{end_day}"
            conditions.append("(date >= %s AND date <= %s AND version_id = %s)")
            params.extend([start_date, end_date, ver_id])

        query = f"""
            SELECT entity_id, entity_type, date,
                   real_value, budget_value, last_year_real_value,
                   actual1_value, actual2_value, actual3_value
            FROM public.collapse_monthly_data
            WHERE {" OR ".join(conditions)}
            ORDER BY entity_type, entity_id, date
        """

        cur.execute(query, params)
        return cur.fetchall()
