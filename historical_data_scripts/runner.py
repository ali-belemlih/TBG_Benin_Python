import subprocess

scripts = [
    "data_mobile",
    "pnl_conso",
    "opex_conso",
    "ca_mobile",
    "capex_conso",
    "cash_conso",
    "indicateurs",
    "marge_brute",
    "parc_mobile",
    "trafic_mobile",
]

# Convert the base path to a module path (dots instead of slashes)
base_module = "historical_data_scripts.tbg_scripts"

def main():
    for script in scripts:
        # Full module path e.g., historical_data_scripts.tbg_scripts.data_mobile
        module_path = f"{base_module}.{script}"
        
        print(f"\n🚀 Running module: {module_path} ...")
        
        # Execute using the -m flag
        result = subprocess.run(["python3", "-m", module_path])
        
        if result.returncode != 0:
            print(f"❌ {script} failed with code {result.returncode}")
            # Optional: Decide if you want to stop the whole process or continue
            break 
        else:
            print(f"✅ Finished {script}")

if __name__ == "__main__":
    main()