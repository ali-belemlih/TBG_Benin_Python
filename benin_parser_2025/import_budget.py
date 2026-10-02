import sys
import subprocess

def main():
    if len(sys.argv) != 5:
        print("Usage: python import_budget.py <MMYYYY> <version_id> <file1 or ''> <file2 or ''>")
        sys.exit(1)

    month_year = sys.argv[1]
    version_id = sys.argv[2]
    file1 = sys.argv[3].strip() or None
    file2 = sys.argv[4].strip() or None

    print(f"📅 Running import for Month-Year: {month_year}, Version ID: {version_id}")

    script_groups = [
        {
            "scripts": [
                "benin_parser_2025.budget_import.budget",
                "benin_parser_2025.budget_import.collapse_ca_mobile"
            ],
            "file_name": file1
        },
        {
            "scripts": [
                "benin_parser_2025.budget_import.opex_budget",
                "benin_parser_2025.budget_import.collapse_opex_conso"
            ],
            "file_name": file2
        },
        {
            "scripts": [
                "benin_parser_2025.budget_import.parc_mobile_budget"
            ],
            "file_name": "ALWAYS"
        }
    ]

    ran_any = False

    for group in script_groups:
        if group["file_name"] == "ALWAYS":
            # always run parc_mobile_budget
            for script in group["scripts"]:
                print(f"\n🚀 Running {script} (always runs)...")
                subprocess.run(["python3", "-m", script, month_year, version_id], check=True)
            ran_any = True

        elif group["file_name"]:  # only run if non-empty
            for script in group["scripts"]:
                print(f"\n🚀 Running {script} with file: {group['file_name']}...")
                subprocess.run(["python3", "-m", script, month_year, version_id, group["file_name"]], check=True)
            ran_any = True

    if not ran_any:
        print("❌ No files provided. Nothing to run.")
        sys.exit(1)


if __name__ == "__main__":
    main()
