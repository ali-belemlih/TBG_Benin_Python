import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

import common

sheet_name = 'Cash'

# Mapping based on the Flux Financiers (Cash Flow) sheet structure
# Key -> Excel Row Number | Value -> tbg_key string

financial_type_row_mapping = {
    7: "CASH1",    # EBITDA
    19: "CASH2",   # CFFO
    32: "CASH3",   # Net cash flow
    36: "CASH4"    # Trésorerie nette fin de période
}

financial_metric_row_mapping = {
    # Under EBITDA
    9: "CASH5",    # Neutralisation de la var. de provisions incluses dans l'Ebitda (-)
    10: "CASH6",   # Autre résultat non courant
    11: "CASH7",   # Variation de BFR opérationnel (+/-)
    13: "CASH8",   # Dividendes reçus des participations non consolidées (+)
    15: "CASH9",   # Cession d'immobilisations
    16: "CASH10",  # Investissements nets (Capex brutes - cession d'immo.) (-)
    17: "CASH11",  # Plan de restructuration

    # Under CFFO
    21: "CASH12",  # Résultat financier hors dividendes des stés non consolidées (+/-)
    23: "CASH13",  # Impôts payés (-)
    25: "CASH14",  # Dividendes payés (-)
    27: "CASH15",  # Cash flow used for financing and taxes
    29: "CASH16",  # Cash flow used for investment (+/-)
    30: "CASH17",  # Autres éléments non cash

    # Under Net cash flow
    34: "CASH18",  # Dettes brutes (-)
    35: "CASH19"   # Trésorerie brute (+)
}

financial_submetric_row_mapping = {}
required_rows = list(financial_type_row_mapping.keys()) + list(financial_metric_row_mapping.keys())

common.generate_data(sheet_name,
                               "cash_consolidate",
                               required_rows,
                               financial_type_row_mapping,
                               financial_metric_row_mapping)
