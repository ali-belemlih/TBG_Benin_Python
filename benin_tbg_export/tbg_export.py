import os
import subprocess
from helpers.tbg_export.parse_arg import parse_arguments
from services.minio_uploader import upload_excel_report
from helpers.db_utils import get_version_id_by_name, get_month_year_by_version_name

def main():
    args = parse_arguments()
    version_name = args.version_name

    if not version_name:
        print("❌ version_name argument is required.")
        return

    version_id = get_version_id_by_name(version_name)
    month_year = get_month_year_by_version_name(version_name)

    print(f"Running for version_id: {version_id}")
    scripts = [
        'excel_data_export',
        'rh_excel_data_report',
        'impact_excel_data_report',
        'details_projects_capex',
        'realize_de_treasure',
        'collapsible_opex_consolidate',
        'collapsible_ca_mobile',
        'cumul_report_export'
    ]

    for script in scripts:
        module_path = f"benin_tbg_export.{script}"
        print(f"\n--- Running script: {script}.py with month_year={month_year} and version_id={version_id} ---")
        try:
            result = subprocess.run(
                ["python3", "-m", module_path, str(month_year), str(version_id)],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True
            )
            print(f"✅ Successfully ran {script}.py\n{result.stdout}")
        except subprocess.CalledProcessError as e:
            print(f"❌ Error running {script}.py:\n{e.stderr}")
            # continue  # Use this to skip failed scripts
            return  # Use this to stop on first failure

    output_file = os.path.join('benin_tbg_export', 'outputs', f"tbg_report_{month_year}.xlsx")

    if os.path.exists(output_file):
        upload_excel_report(output_file, month_year, version_name)
    else:
        print(f"\n❌ Error: Output file not found at {output_file}")

if __name__ == "__main__":
    main()
