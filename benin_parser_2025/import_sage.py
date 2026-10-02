import sys
import subprocess

def main():
    if len(sys.argv) != 4:
        print("Usage: python -m benin_parser_2025.import_sage <MMYYYY> <version_id> <sage_version>")
        sys.exit(1)

    month_year = sys.argv[1]
    version_id = sys.argv[2]
    sage_version = sys.argv[3]

    print(f"Running import for Month-Year: {month_year}, Version ID: {version_id}, Sage Version: {sage_version}")

    scripts = [
        "benin_parser_2025.sage_import.real_import_from_sage",
        "benin_parser_2025.sage_import.real_import_from_sage_for_collapse",
        "benin_parser_2025.sage_import.process_account_formulas"
    ]

    for script in scripts:
        print(f"\nRunning {script}...")
        subprocess.run(["python3", "-m", script, month_year, version_id, sage_version], check=True)

if __name__ == "__main__":
    main()
