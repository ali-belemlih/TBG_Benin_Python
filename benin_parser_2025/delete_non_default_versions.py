from helpers.db_utils import get_db_connection

def main():
    queries = [
        """
        DELETE FROM public.financial_metrics_data
        WHERE version_id IN (
          SELECT id FROM public.tbg_version WHERE is_default = false
        );
        """,
        """
        DELETE FROM public.financial_cumulative_data
        WHERE version_id IN (
          SELECT id FROM public.tbg_version WHERE is_default = false
        );
        """,
        """
        DELETE FROM public.financial_annual_data
        WHERE version_id IN (
          SELECT id FROM public.tbg_version WHERE is_default = false
        );
        """,
        """
        DELETE FROM public.collapse_monthly_data
        WHERE version_id IN (
          SELECT id FROM public.tbg_version WHERE is_default = false
        );
        """,
        """
        DELETE FROM public.collapse_cumul_data
        WHERE version_id IN (
          SELECT id FROM public.tbg_version WHERE is_default = false
        );
        """,
        """
        DELETE FROM public.collapse_annual_data
        WHERE version_id IN (
          SELECT id FROM public.tbg_version WHERE is_default = false
        );
        """,
        """
        DELETE FROM public.tbg_version
        WHERE is_default = false;
        """,
        """
        DELETE FROM public.tbg_report_request
        WHERE tbg_version_id IS NULL;
        """,
    ]

    print("⚠️ WARNING: This will permanently delete ALL non-default versions and related data.")
    confirm = input("Are you sure you want to continue? (y/n): ").strip().lower()

    if confirm not in ["y", "yes"]:
        print("❌ Operation cancelled.")
        return

    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        for q in queries:
            print(f"Executing: {q.strip().splitlines()[0]} ...")
            cur.execute(q)
        conn.commit()
        cur.close()
        print("✅ Non-default versions deleted successfully.")
    except Exception as e:
        print(f"❌ Error: {e}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()


if __name__ == "__main__":
    main()
