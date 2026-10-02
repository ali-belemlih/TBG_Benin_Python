# file: benin-data-parser-new/2025/run_all.py
import subprocess

scripts = [
    "data_mobile.py",
    "mobile_money.py",
    "profit_and_loss_consolidate.py",
    "opex_conso.py",
    "ca_mobile.py",
    "capex_conso.py",
    "cash_conso.py",
    "collapse_ca_mobile.py",
    "collapse_opex_conso.py",
    "indicateurs_mobile.py",
    "marge_mobile.py",
    "parc_mobile.py",
    "traffic_mobile.py",
]

base_path = "benin-data-parser-new/2025"

def main():
    for script in scripts:
        print(f"\n🚀 Running {script} ...")
        result = subprocess.run(["python3", f"{base_path}/{script}"])
        if result.returncode != 0:
            print(f"❌ {script} failed with code {result.returncode}")
            break
        else:
            print(f"✅ Finished {script}")

if __name__ == "__main__":
    main()
