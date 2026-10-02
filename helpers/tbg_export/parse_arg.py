import argparse
import sys
from datetime import datetime

def parse_arguments():
    parser = argparse.ArgumentParser(description='Process data based on TBG Version!')
    parser.add_argument('version_name', type=str, help='Version to process (e.g., TBG_20250401_124714)')

    return parser.parse_args()
