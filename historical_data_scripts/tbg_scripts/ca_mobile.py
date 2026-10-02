import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

import common

sheet_name = 'CA'

# Mapping based on the ca_mobile structure
# Key -> Excel Row Number | Value -> tbg_key string
financial_type_row_mapping = {
    7: "CA1",    # CA Global
    9: "CA2",    # CA services Mobile
    11: "CA3",   # CA récurrent
    13: "CA4",   # CA sortant
    26: "CA5",   # CA entrant
    33: "CA6",   # Colocation
    38: "CA7",   # Roaming in
    40: "CA8"    # CA équipement
}

financial_metric_row_mapping = {
    # Under CA sortant
    14: "CA9",   # Prépayé (yc commissions)
    21: "CA10",  # Postpayé

    # Under CA entrant
    27: "CA11",  # Prépayé
    28: "CA12",  # Postpayé
    29: "CA13",  # Telecel
    30: "CA14",  # Orange
    32: "CA15",  # International

    # Under CA équipement
    41: "CA16",  # Vente de SIM
    42: "CA17",  # Terminaux
    43: "CA18"   # Accessoire
}

financial_submetric_row_mapping = {
    # Under Prépayé (yc commissions)
    15: "CA19",  # dont voix
    16: "CA20",  # CA Internet 2G/3G
    17: "CA21",  # dont BLR
    18: "CA22",  # dont MIHD
    19: "CA23",  # dont sms
    20: "CA24",  # CA Mobile money

    # Under Postpayé (sortant)
    22: "CA25",  # dont voix +sms
    23: "CA26"   # dont data 3G
}

required_rows = list(financial_type_row_mapping.keys()) + list(financial_metric_row_mapping.keys()) + list(financial_submetric_row_mapping.keys())

common.generate_data(sheet_name,
                               "ca_mobile",
                               required_rows,
                               financial_type_row_mapping,
                               financial_metric_row_mapping,
                               financial_submetric_row_mapping)
