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
    parser.add_argument('actual_type', type=str, help='Actual Type to process (e.g., actual1)')
    parser.add_argument('file_name', nargs='?', default=None)

    return parser.parse_args()
