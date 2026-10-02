import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

import common

sheet_name = 'Trafic'

# Mapping based on the Trafic sheet structure
# Key -> Excel Row Number | Value -> tbg_key string

financial_type_row_mapping = {
    6: "TM1",     # Total Trafic
    32: "TM2"     # Trafic entrant
}

financial_metric_row_mapping = {
    8: "TM3",     # Trafic sortant
    35: "TM4",    # Dont Prépayé (entrant)
    36: "TM5",    # Dont Postpayé (entrant)
    37: "TM6",    # Telecel
    38: "TM7",    # Orange
    40: "TM8"     # International
}

financial_submetric_row_mapping = {
    9: "TM9",     # Dont Prépayé (sortant)
    10: "TM10",   # Dont Postpayé (sortant)
    11: "TM11",   # vers On net
    12: "TM12",   # vers Off net local
    13: "TM13"    # vers International
}
required_rows = list(financial_type_row_mapping.keys()) + list(financial_metric_row_mapping.keys()) + list(
    financial_submetric_row_mapping.keys())

common.generate_data(sheet_name,
                     "traffic_mobile",
                     required_rows,
                     financial_type_row_mapping,
                     financial_metric_row_mapping,
                     financial_submetric_row_mapping)
