import sys
import subprocess

def main():
    if len(sys.argv) != 11:
        print("Usage: python import_reel.py <MMYYYY> <version_id> "
              "<pnl_file> <ca_mobile_file> <marge_file> <traffic_file> "
              "<mobile_money_file> <data_mobile_file> <parc_file> <realise_file>")
        sys.exit(1)

    month_year = sys.argv[1]
    version_id = sys.argv[2]

    script_file_map = {
        "benin-parser-2025/reel_import/pnl_import.py": sys.argv[3],
        "benin-parser-2025/reel_import/ca_mobile.py": sys.argv[4],
        "benin-parser-2025/reel_import/marge_brute_mobile.py": sys.argv[5],
        "benin-parser-2025/reel_import/traffic_mobile.py": sys.argv[6],
        "benin-parser-2025/reel_import/mobile_money.py": sys.argv[7],
        "benin-parser-2025/reel_import/data_mobile.py": sys.argv[8],
        "benin-parser-2025/reel_import/parc_mobile.py": sys.argv[9],
        "benin-parser-2025/reel_import/realise.py": sys.argv[10],
    }

    scripts_without_file = [
        "benin-parser-2025/reel_import/indicateurs_mobile.py",
        "benin-parser-2025/reel_import/cash_conso.py"
    ]

    # Run scripts with file argument
    for script, file in script_file_map.items():
        print(f"\n🚀 Running {script} with file: {file}...")
        subprocess.run(["python3", script, month_year, version_id, file], check=True)

    # Run scripts without file argument
    for script in scripts_without_file:
        print(f"\n🚀 Running {script} (no file)...")
        subprocess.run(["python3", script, month_year, version_id], check=True)

if __name__ == "__main__":
    main()
