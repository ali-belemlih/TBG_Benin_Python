from helpers.db_utils import get_db_connection


def main():

    conn = None

    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # -------------------------------------------------
        # Step 1: Fetch non-default versions
        # -------------------------------------------------
        cur.execute("""
            SELECT id, version_name
            FROM public.tbg_version
            WHERE is_default = false
            ORDER BY version_name;
        """)

        versions = cur.fetchall()

        if not versions:
            print("No non-default versions found.")
            return

        print("\nAvailable versions:\n")
        for v in versions:
            print(f"- {v[1]}")

        # -------------------------------------------------
        # Step 2: Ask user for version name
        # -------------------------------------------------
        version_name = input("\nEnter the VERSION NAME to delete: ").strip()

        cur.execute("""
            SELECT id
            FROM public.tbg_version
            WHERE version_name = %s
            AND is_default = false;
        """, (version_name,))

        row = cur.fetchone()

        if not row:
            print(f"❌ Version '{version_name}' not found or it is a default version.")
            return

        version_id = row[0]

        print(f"\n⚠️ You are about to delete version '{version_name}' (ID: {version_id}) and all related data.")
        confirm = input("Are you sure you want to continue? (y/n): ").strip().lower()

        if confirm not in ["y", "yes"]:
            print("❌ Operation cancelled.")
            return

        # -------------------------------------------------
        # Step 3: Delete related data
        # -------------------------------------------------
        queries = [
            "DELETE FROM public.financial_metrics_data WHERE version_id = %s;",
            "DELETE FROM public.financial_cumulative_data WHERE version_id = %s;",
            "DELETE FROM public.financial_annual_data WHERE version_id = %s;",
            "DELETE FROM public.collapse_monthly_data WHERE version_id = %s;",
            "DELETE FROM public.collapse_cumul_data WHERE version_id = %s;",
            "DELETE FROM public.collapse_annual_data WHERE version_id = %s;",
            "DELETE FROM public.tbg_report_request WHERE tbg_version_id = %s;",
            "DELETE FROM public.tbg_version WHERE id = %s;",
        ]

        for q in queries:
            print(f"Executing: {q.strip().splitlines()[0]}")
            cur.execute(q, (version_id,))

        conn.commit()
        print(f"\n✅ Version '{version_name}' deleted successfully.")

        cur.close()

    except Exception as e:
        print(f"❌ Error: {e}")
        if conn:
            conn.rollback()

    finally:
        if conn:
            conn.close()


if __name__ == "__main__":
    main()