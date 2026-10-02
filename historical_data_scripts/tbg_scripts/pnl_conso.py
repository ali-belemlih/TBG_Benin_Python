import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

import common

sheet_name = 'P&L'

# Mapping based on the P&L (Profit & Loss) sheet structure
# Key -> Excel Row Number | Value -> tbg_key string

financial_type_row_mapping = {
    5: "PL1",     # Chiffre d'affaires
    35: "PL2"     # RESULTAT NET
}

financial_metric_row_mapping = {
    6: "PL3",     # Mobile
    8: "PL4",     # Coût des ventes
    11: "PL5",    # Marge Brute
    14: "PL6",    # Coûts opérationnels
    17: "PL7",    # EBITDA
    25: "PL8",    # EBITA
    28: "PL9",    # Résultat financier
    31: "PL10",   # RESULTAT avant IS
    37: "PL11"    # % CA (under RESULTAT NET)
}

financial_submetric_row_mapping = {
    9: "PL12",    # Mobile (under Coût des ventes)
    12: "PL13",   # % CA (Marge Brute)
    15: "PL14",   # % CA (Coûts opérationnels)
    18: "PL15",   # % CA (EBITDA)
    20: "PL16",   # Amortissements et déprec. Courant
    21: "PL17",   # Dotations (Amo. et Pv NC)
    22: "PL18",   # Autres non courant
    23: "PL19",   # +/- value de cession d'immob.
    26: "PL20",   # % CA (EBITA)
    29: "PL21",   # dont intérêt sur SHL
    32: "PL22",   # IS
    33: "PL23"    # ID
}
required_rows = list(financial_type_row_mapping.keys()) + list(financial_metric_row_mapping.keys())+ list(financial_submetric_row_mapping.keys())

common.generate_data(sheet_name,
                     "profit_and_loss_consolidate",
                     required_rows,
                     financial_type_row_mapping,
                     financial_metric_row_mapping,
                     financial_submetric_row_mapping, )
