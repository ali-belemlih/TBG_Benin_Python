import argparse
import sys
from datetime import datetime
def get_script_name():
    return sys.modules['__main__'].__spec__.name.split('.')[-1].lower()

def parse_arguments():
    script_name = get_script_name()

    parser = argparse.ArgumentParser(description='Process data based on month-year.')
    parser.add_argument('month_year', type=str, help='Month and Year in MMYYYY format (e.g., 032025)')
    parser.add_argument('version_id', type=str, help='Version to process (e.g., TBG_20250401_124714)')
    sage_script = {'real_import_from_sage', 'real_import_from_sage_for_collapse'}

    if script_name in sage_script:
        parser.add_argument('sage_version', type=str, help='Sage Version ')

    two_arg_script = {'real_import_from_sage', 'real_import_from_sage_for_collapse',
                     'indicateurs_mobile', 'indicateurs_cumul','collapse_cum_data_import', 'cum_data_import',
                     'deduction_script_opex_consolidate', 'tbg_export', 'excel_data_export', 'rh_excel_data_report',
                     'impact_excel_data_report', 'details_projects_capex', 'realize_de_treasure', 'collapsible_opex_consolidate',
                     'collapsible_ca_mobile', 'cumul_report_export', 'data_mobile_cumul', 'parc_mobile_cumul', 'parc_mobile_budget',
                     'capex_conso', 'update_account_balance', 'mobile_money_cumul',
                      'marge_mobile_cumul',
                      'cash_conso_cumul',
                      'pnl_conso_cumul_percent_fields',
                      'data_mobile_cumul_actual1',
                      'opex_cumul_import',
                      'opex_actu1_cumul_import',
                      'opex_collapsible_cumul_actual1_import',
                      'opex_collapsible_cumul_import',
                      'process_account_formulas'
                     }

    if script_name not in two_arg_script:
        parser.add_argument('file_name', type=str, help='Excel file (e.g., file1.xlsx,file2.xlsx)')
    else:
        parser.add_argument('file_name', nargs='?', default=None)

    return parser.parse_args()

def parse_date_from_args():
    script_name = get_script_name()

    parser = argparse.ArgumentParser(description='Process data based on a specific date.')
    parser.add_argument('date', type=str, help='Date in YYYY-MM-DD format (e.g., 2024-01-01)')

    args = parser.parse_args()

    # Validate and attach parsed date
    try:
        args.date_obj = datetime.strptime(args.date, '%Y-%m-%d')
    except ValueError:
        parser.error("Invalid date format. Please use YYYY-MM-DD (e.g., 2024-01-01).")

    print(f"{script_name}")
    return args

def parse_dormant_arguments():
    script_name = get_script_name()

    parser = argparse.ArgumentParser(description='Process data based on month-year.')
    parser.add_argument('id', type=str, help='id of the table')
    parser.add_argument('bucket_name', type=str, help='bucket name')

    args = parser.parse_args()
    print(f"{script_name}")

    return args
