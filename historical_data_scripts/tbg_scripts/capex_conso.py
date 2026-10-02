import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

import common

sheet_name = 'Capex'

# Mapping based on the CAPEX sheet structure
# Key -> Excel Row Number | Value -> tbg_key string

financial_type_row_mapping = {
    7: "CAPEX1",    # Total capex
    10: "CAPEX2",   # Réseau
    32: "CAPEX3",   # Commercial et Marketing
    37: "CAPEX4"    # Administratif et Financier
}

financial_metric_row_mapping = {
    # Réseau
    11: "CAPEX5",   # Modernisation et densification du réseau d'accès (50 sites à Bangui)
    12: "CAPEX6",   # Modernisation du réseau Core CS/PS & Plateformes de services
    13: "CAPEX7",   # Modernisation et extension Radio (130 Sites)
    14: "CAPEX8",   # Modernisation et extension Transmission (yc BB FH de Bangui)
    15: "CAPEX9",   # Mise à niveau et extension réseau VSAT domestique
    16: "CAPEX10",  # Extension du réseau de transmission FH sur Bangui à 4 boucles de 4 Gbps
    17: "CAPEX11",  # Acquisition de groupes électrogènes 15KVA
    18: "CAPEX12",  # Construction des sites (Pylônes yc)
    19: "CAPEX13",  # Outils de planification et de mesures Radio
    20: "CAPEX14",  # Mise à niveau SI Commercial
    21: "CAPEX15",  # Acquisition de Firewall pour POP Internet
    22: "CAPEX16",  # Solution de Gestion du réseau IP
    23: "CAPEX17",  # Equipements informatiques
    24: "CAPEX18",  # Transmission VSAT (complément 15 SRAN)
    25: "CAPEX19",  # Construction 15 sites outdoor (complément 15 SRAN)
    26: "CAPEX20",  # Energie - Redresseur 48V + Batteries Lithium autonomie 12h (80 sites à Bangui)
    27: "CAPEX21",  # Construction de 17 sites à Bangui - Pylônes 40m-15m-150km/h
    28: "CAPEX22",  # Extension du réseau de transmission FH sur Bangui à 4 boucles de 4 Gbps
    29: "CAPEX23",  # Pièces de rechange et outils
    30: "CAPEX24",  # Equipements informatiques
    31: "CAPEX25",  # Licences Régulateur

    # Commercial et Marketing
    33: "CAPEX26",  # Cartes SIM
    34: "CAPEX27",  # Autres Commerciales
    35: "CAPEX28",  # Agences commerciales

    # Administratif et Financier
    38: "CAPEX29"   # Activation charges du personnel
}

financial_submetric_row_mapping = {
    39: "CAPEX30",  # Logistique
    40: "CAPEX31",  # Matériel et outillage industriels
    41: "CAPEX32",  # Matériel informatique
    42: "CAPEX33",  # Matériels et mobiliers
    43: "CAPEX34",  # Climatiseurs
    44: "CAPEX35",  # Autres matériels et mobiliers
    45: "CAPEX36",  # Autres agencements (eau electricité, autres)
    46: "CAPEX37",  # Autres installations
    47: "CAPEX38",  # Terrains et Batiments
    48: "CAPEX39",  # Transport
    49: "CAPEX40",  # Autres (mat. Bureau, bureautique,…)
    50: "CAPEX41",  # Materiel bureautique
    51: "CAPEX42"   # Mobilier de bureau
}
required_rows = list(financial_type_row_mapping.keys()) + list(financial_metric_row_mapping.keys())

common.generate_data(sheet_name, "capex_consolidate", required_rows, financial_type_row_mapping, financial_metric_row_mapping)
