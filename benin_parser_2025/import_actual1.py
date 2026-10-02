import sys
import subprocess

def main():
    if len(sys.argv) != 6:
        print("Usage: python -m bbenin_parser_2025.actu1_import.import_actual1 <MMYYYY> <version_id> <actual_type> <actual_file>")
        sys.exit(1)

    month_year = sys.argv[1]
    version_name = sys.argv[2]
    actual_type = sys.argv[3]
    actual_file = sys.argv[4]
    opex_actual_file = sys.argv[5]

    print(f"Running import for Month-Year: {month_year}, Version ID: {version_name}")

    scripts = [
        "benin_parser_2025.actu1_import.ca_mobile",
        "benin_parser_2025.actu1_import.capex_conso",
        "benin_parser_2025.actu1_import.cash_conso",
        "benin_parser_2025.actu1_import.indicateurs_mobile",
        "benin_parser_2025.actu1_import.marge_brute",
        "benin_parser_2025.actu1_import.opex_conso",
        "benin_parser_2025.actu1_import.parc_mobile",
        "benin_parser_2025.actu1_import.pnl_conso",
        "benin_parser_2025.actu1_import.trafic_mobile",
    ]

    for script in scripts:
        print(f"\nRunning {script}...")

        if script.endswith("opex_conso"):
            file_to_use = opex_actual_file
        else:
            file_to_use = actual_file

        subprocess.run(
            ["python3", "-m", script, month_year, version_name, actual_type, file_to_use],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            universal_newlines=True
        )

if __name__ == "__main__":
    main()
