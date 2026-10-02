import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

import common
sheet_name = 'Parc '

# Mapping based on the Parc d'abonnés sheet structure
# Key -> Excel Row Number | Value -> tbg_key string

financial_type_row_mapping = {
    7: "PARC1",    # Parc Total Mobile Actif
    17: "PARC2",   # Parc Prépayé Actif
    23: "PARC3",   # Parc prépayé actif fin de période
    29: "PARC4",   # Parc Postpayé (section header)
    35: "PARC5"    # Parc Postpayé (fin section)
}

financial_metric_row_mapping = {
    # Parc Total Mobile Actif
    8: "PARC6",    # Activations totales
    9: "PARC7",    # Flux d'inactivité
    10: "PARC8",   # Accroissement net
    11: "PARC9",   # % churn annualisé
    12: "PARC10",  # Parc Actif Moyen

    # Parc Prépayé Actif
    18: "PARC11",  # Parc prépayé actif début Période

    # Parc prépayé actif fin de période
    24: "PARC12",  # Parc Actif Moyen
    25: "PARC13",  # Parc actif localisé
    26: "PARC14",  # Parc internet
    27: "PARC15",  # Parc actif Mobile Money

    # Parc Postpayé
    30: "PARC16",  # Parc début Période
    36: "PARC17"   # Parc Moyen Postpayé
}

financial_submetric_row_mapping = {
    # Under Parc Total Mobile Actif
    13: "PARC18",  # Parc actif localisé
    14: "PARC19",  # Parc internet

    # Under Parc prépayé actif début Période
    19: "PARC20",  # Activations totales
    20: "PARC21",  # Flux d'inactivité
    21: "PARC22",  # Accroissement net
    22: "PARC23",  # % churn annualisé

    # Under Parc Postpayé
    31: "PARC24",  # Activations totales
    32: "PARC25",  # Résiliations totales
    33: "PARC26",  # % résiliation annualisé
    34: "PARC27"   # Ventes nettes
}
required_rows = list(financial_type_row_mapping.keys()) + list(financial_metric_row_mapping.keys()) + list(financial_submetric_row_mapping.keys())

common.generate_data(sheet_name,
                               "parc_mobile",
                               required_rows,
                               financial_type_row_mapping,
                               financial_metric_row_mapping,
                               financial_submetric_row_mapping)
