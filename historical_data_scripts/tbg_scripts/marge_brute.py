import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

import common
sheet_name = 'MB'

# Mapping based on the Marge Brute sheet structure
# Key -> Excel Row Number | Value -> tbg_key string

financial_type_row_mapping = {
    6: "MB1",    # Total Revenu
    33: "MB2",   # Coûts des ventes
    35: "MB3",   # Marge Brute
    38: "MB4"    # Marge Brute hors transit
}

financial_metric_row_mapping = {
    9: "MB5",    # International
    12: "MB6",   # Telecel
    16: "MB7",   # Orange
    19: "MB8",   # Reversement SVA
    20: "MB9",   # Interconnexion SMS
    21: "MB10",  # Roaming out
    23: "MB11",  # Coûts des terminaux et cartes
    28: "MB12",  # Commissions
    36: "MB13",  # En % du CA (Marge Brute)
    39: "MB14"   # En % du CA (Marge Brute hors transit)
}

financial_submetric_row_mapping = {
    7: "MB15",   # Trafic (mn)
    8: "MB16",   # Coût unitaire
    10: "MB17",  # Trafic (International)
    11: "MB18",  # Coût unitaire (International)
    13: "MB19",  # Trafic (Telecel)
    14: "MB20",  # Coût unitaire (Telecel)
    24: "MB21",  # Dont coût des cartes de recharge vendues
    25: "MB22",  # Dont coût des SIM
    26: "MB23",  # Dont coût des terminaux*
    27: "MB24",  # Dont provisions sur stocks
    30: "MB25",  # Dont commissions up-front
    31: "MB26"   # Dont avoirs de performance
}
required_rows = list(financial_type_row_mapping.keys()) + list(financial_metric_row_mapping.keys()) + list(financial_submetric_row_mapping.keys())

common.generate_data(sheet_name,
                               "marge_mobile",
                               required_rows,
                               financial_type_row_mapping,
                               financial_metric_row_mapping,
                               financial_submetric_row_mapping)