import sys
import subprocess

def main():
    if len(sys.argv) not in (3, 5):
        print("Usage: python -m benin_parser_2025.import_sage <MMYYYY> <version_id> [<mobile_money_file> <data_mobile_file>]")
        sys.exit(1)

    month_year = sys.argv[1]
    version_id = sys.argv[2]
    mobile_money_file = sys.argv[3] if len(sys.argv) == 5 else None
    data_mobile_file = sys.argv[4] if len(sys.argv) == 5 else None

    print(f"Running import for Month-Year: {month_year}, Version ID: {version_id}")
    print(f"Using Mobile Money file: {mobile_money_file}")
    print(f"Using Data Mobile file: {data_mobile_file}")

    scripts = [
        "benin_parser_2025.cumul_import.cum_data_import",
        "benin_parser_2025.cumul_import.collapse_cum_data_import",
        "benin_parser_2025.cumul_import.data_mobile_cumul",
        "benin_parser_2025.cumul_import.mobile_money_cumul",
        "benin_parser_2025.cumul_import.parc_mobile_cumul",
        "benin_parser_2025.cumul_import.indicateurs_cumul",
        "benin_parser_2025.cumul_import.marge_mobile_cumul",
        "benin_parser_2025.cumul_import.pnl_conso_cumul_percent_fields",
        "benin_parser_2025.cumul_import.cash_conso_cumul",
    ]

    for script in scripts:
        print(f"\nRunning {script}...")

        # handle mobile money and data mobile differently
        if mobile_money_file and "mobile_money_cumul" in script:
            subprocess.run(
                ["python3", "-m", script, month_year, version_id, mobile_money_file],
                check=True
            )
        elif data_mobile_file and "data_mobile_cumul" in script:
            subprocess.run(
                ["python3", "-m", script, month_year, version_id, data_mobile_file],
                check=True
            )
        else:
            subprocess.run(
                ["python3", "-m", script, month_year, version_id],
                check=True
            )

    print("\n✅ All cumulative imports completed successfully!")


if __name__ == "__main__":
    main()
