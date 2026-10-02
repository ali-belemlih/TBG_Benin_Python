import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

import common
sheet_name = 'Indicateurs'

# Mapping based on the Indicateurs Mobile sheet structure
# Key -> Excel Row Number | Value -> tbg_key string

financial_type_row_mapping = {
    7: "IM1",    # ARPU Global
    11: "IM2",   # ARPU Prépayé
    15: "IM3",   # ARPU Postpayé
    19: "IM4",   # Usage / client / mois
    27: "IM5"    # Prix mn
}

financial_metric_row_mapping = {
    # ARPU Global
    8: "IM6",    # ARPU Sortant
    9: "IM7",    # ARPU Entrant

    # ARPU Prépayé
    12: "IM8",   # ARPU Sortant
    13: "IM9",   # ARPU Entrant

    # ARPU Postpayé
    16: "IM10",  # ARPU Sortant
    17: "IM11",  # ARPU Entrant

    # Usage / client / mois
    20: "IM12",  # Usage Sortant
    23: "IM13",  # Usage Entrant

    # Prix mn
    28: "IM14",  # Prix mn Sortant
    31: "IM15"   # Prix mn Entrant
}

financial_submetric_row_mapping = {
    # Usage Sortant
    21: "IM16",  # Prépayé
    22: "IM17",  # Postpayé

    # Usage Entrant
    24: "IM18",  # Prépayé
    25: "IM19",  # Postpayé

    # Prix mn Sortant
    29: "IM20",  # Prépayé
    30: "IM21"   # Postpayé
}
required_rows = list(financial_type_row_mapping.keys()) + list(financial_metric_row_mapping.keys()) + list(financial_submetric_row_mapping.keys())

common.generate_data(sheet_name,
                               "indicateurs_mobile",
                               required_rows,
                               financial_type_row_mapping,
                               financial_metric_row_mapping,
                               financial_submetric_row_mapping)
