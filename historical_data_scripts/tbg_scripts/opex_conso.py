import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

import common
sheet_name = 'Opex'

# Mapping based on the Opex (Operational Expenses) sheet structure
# Key -> Excel Row Number | Value -> tbg_key string

financial_type_row_mapping = {
    7: "OPEX1",    # Total Opex
    9: "OPEX2",    # Personnel
    14: "OPEX3",   # Communication
    16: "OPEX4",   # Exploitation & maintenance
    23: "OPEX5",   # Frais généraux
    30: "OPEX6",   # Impôts, taxes et redevances
    37: "OPEX7",   # Provision clients, R&C & NC
    43: "OPEX8"    # Ecart de change sur exploitation
}

financial_metric_row_mapping = {
    # Personnel
    10: "OPEX9",   # Traitement & salaires et autres
    11: "OPEX10",  # Assurance maladie

    # Exploitation & maintenance
    17: "OPEX11",  # Achat d'énergie - Bâtiment - Gardiennage
    18: "OPEX12",  # Lignes et réseaux (entretien & achats)
    20: "OPEX13",  # Matériel de transport (Entretien et locat°)
    21: "OPEX14",  # Maintenance informatique

    # Frais généraux
    24: "OPEX15",  # Frais d'achats d'études, honoraires
    25: "OPEX16",  # Management fees
    26: "OPEX17",  # Transport, déplacement, mission
    27: "OPEX18",  # Frais postaux, bancaires et assurances
    28: "OPEX19",  # Achats de mat. et fournitures consom.

    # Impôts, taxes et redevances
    31: "OPEX20",  # Redevances régulateur
    32: "OPEX21",  # Autres impôts et taxes

    # Provision clients, R&C & NC
    38: "OPEX22",  # Prov. Créances clients
    39: "OPEX23",  # Prov. R&C
    40: "OPEX24"   # PIDR
}

financial_submetric_row_mapping = {
    # Under Impôts, taxes et redevances
    33: "OPEX25",  # Dont Taxe sur l'entrant international
    35: "OPEX26",  # Dont Autres impôts

    # Under Provision clients
    41: "OPEX27"   # Autres provisions (Stock)
}
required_rows = list(financial_type_row_mapping.keys()) + list(financial_metric_row_mapping.keys()) + list(financial_submetric_row_mapping.keys())

common.generate_data(sheet_name, "opex_consolidate", required_rows, financial_type_row_mapping, financial_metric_row_mapping, financial_submetric_row_mapping)
