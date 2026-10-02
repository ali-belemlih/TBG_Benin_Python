import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

import common

sheet_name = 'Data Mobile'

# Mapping based on the Data Mobile sheet structure
# Key -> Excel Row Number | Value -> tbg_key string

financial_type_row_mapping = {
    6: "DM1",    # Parc Data Mobile actif (90 jrs)
    11: "DM2",   # Trafic data (en millions de Go)
    16: "DM3",   # Chiffre d'affaires MFCFA
    21: "DM4",   # ARPU
    26: "DM5",   # Usage (en Go/client)
    31: "DM6"    # Prix / Go
}

financial_metric_row_mapping = {
    # Parc Data Mobile actif
    7: "DM7",    # 2G
    8: "DM8",    # 3G
    9: "DM9",    # 4G

    # Trafic data
    12: "DM10",  # 2G
    13: "DM11",  # 3G
    14: "DM12",  # 4G

    # Chiffre d'affaires MFCFA
    17: "DM13",  # 2G
    18: "DM14",  # 3G
    19: "DM15",  # 4G

    # ARPU
    22: "DM16",  # 2G
    23: "DM17",  # 3G
    24: "DM18",  # 4G

    # Usage (en Go/client)
    27: "DM19",  # 2G
    28: "DM20",  # 3G
    29: "DM21",  # 4G

    # Prix / Go
    32: "DM22",  # 2G
    33: "DM23",  # 3G
    34: "DM24"   # 4G
}

financial_submetric_row_mapping = {}
required_rows = list(financial_type_row_mapping.keys()) + list(financial_metric_row_mapping.keys())

common.generate_data(sheet_name, "data_mobile", required_rows, financial_type_row_mapping, financial_metric_row_mapping)
