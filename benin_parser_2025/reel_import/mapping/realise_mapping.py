sections = {
    10 : 1, # (A) TOTAL DES ENCAISSEMENTS
    30 : 3, # (B) TOTAL DES DECAISSEMENTS
    31 : 4, # DECAISSEMENTS CUMULES
    32 : 5, # ( C  ) FLUX MENSUEL GENERE PAR EXPLOITATION= CFFO
    33: 6, # FLUX CUMULE
    38 : 7, # ( D) FLUX MENSUEL GENERE PAR  HORS EXPLOITATION
    39 : 8, # FLUX CUMULE
    49 : 9, # ( E ) FLUX MENSUEL
    50 : 10, #         DECAISSEMENTS CUMULES
    52 : 11, # FLUX NET MENSUEL (C+D+E)
    54 : 12 # FLUX NET CUMULE (C+D+E)
}

categories = {
    3: 1,    # REETTES D'EXPLOITATION
    4: 2,    # REETTES INTERCO INTERNATIONALES
    5: 3,    # REETTES INTERCO NATIONALES
    6: 4,    # REETTES CONVENTIONS
    12: 5,    # DECAISSEMENTS D'EXPLOITATION
    22: 6,    # DEPENSES D'INVESTISSEMENTS
    34: 7,    # AUTRES
    40: 8,   # OPERATION DE FINANCEMENT
}

subcategories = {
    # DECAISSEMENTS D'EXPLOITATION (category_id 5)
    13: 1,    # INTERCOS NATIONALES
    14: 2,    # INTERCOS INTERNATIONALES
    15: 3,    # AUTRES ACHATS
    16: 4,    # IMPOTS & TAXES
    17: 5,    # TV.A (matches TAXES in designations)
    18: 6,    # CHARGES DE PERSONNEL
    20: 7,    # REGIES
    19: 8,    # AUTRES CHARGES MOOVMONEY

    # DEPENSES D'INVESTISSEMENTS (category_id 6)
    23: 9,    # LICENCES, FONDS DE COMMERCE & BREVETS MARQUES DROITS ET VALEURS
    24: 10,  # TERRAINS, AMENAGEMENTS ET CONSTRUCTIONS
    25: 11,  # INSTAL. TECHN., MATERIEL & OUTILLAGE
    26: 12,  # MATERIEL DE TRANSPORT
    27: 14,  # MATERIEL ET MOBILIER DE BUREAU
    28: 13,  # AUTRES IMMOBILISATIONS
    29: 15,  # AVANCES ET ACOMPTES/IMMOB

    # AUTRES (category_id 7)
    35: 16,  # I.S
    36: 17,  # DIVIDENDES

    # OPERATION DE FINANCEMENT (category_id 8)
    41: 20,  # CHARGES D'INTERETS
    42: 21,  # REMBOURSEMENT D'EMPRUNTS
    43: 22,  # REMBOURSEMENT CREDITS SPOT
    44: 23,  # NOUVEAU EMPRUNTS A LMT
    45: 24,  # NOUVEAU CREDITS SPOT
    46: 25,  # AUTRES (AUG K, PARTICIPATION, PRETS...)
    47: 26   # PRODUITS FINANCIERS
}

tbg_formulas = {
    'L11': {
        "type": "section",
        "id": 1,
        "formula": {
            "data": 'SUM(J6:J10)',
            "source": {
                "J6": {
                    "table_name": "cashflow_data",
                    "entity_type": "category",
                    "entity_id": 1
                },
                "J10": {
                    "table_name": "cashflow_data",
                    "entity_type": "category",
                    "entity_id": 4
                }
            }
        },
        "is_adjustible": True
    },
    'L12': {
        "type": "section",
        "id": 2,
        "formula": {
            "data": 'L11',
            "source": {}
        },
        "is_adjustible": True
    },
    'L14': {
        "type": "category",
        "id": 5,
        "formula": {
            "data": 'SUM(J15:J22)',
            "source": {
                "J15": {
                    "table_name": "cashflow_data",
                    "entity_type": "subcategory",
                    "entity_id": 1
                },
                "J22": {
                    "table_name": "cashflow_data",
                    "entity_type": "subcategory",
                    "entity_id": 8
                }
            }
        },
        "is_adjustible": True
    },
    'L23': {
        "type": "category",
        "id": 6,
        "formula": {
            "data": 'SUM(J24:J30)',
            "source": {
                "J24": {
                    "table_name": "cashflow_data",
                    "entity_type": "subcategory",
                    "entity_id": 9
                },
                "J30": {
                    "table_name": "cashflow_data",
                    "entity_type": "subcategory",
                    "entity_id": 15
                }
            }
        },
        "is_adjustible": True
    },
    'L32': {
        "type": "section",
        "id": 3,
        "formula": {
            "data": 'L23 + L14',
            "source": {}
        },
        "is_adjustible": True
    },
    'L33': {
        "type": "section",
        "id": 4,
        "formula": {
            "data": 'L32',
            "source": {}
        },
        "is_adjustible": True
    },
    'L35': {
        "type": "section",
        "id": 5,
        "formula": {
            "data": 'L11-L32-L34',
            "source": {
                "L34": {
                    "table_name": "cashflow_data",
                    "entity_type": "category",
                    "entity_id": 9
                }
            }
        },
        "is_adjustible": True
    },
    'L36': {
        "type": "section",
        "id": 6,
        "formula": {
            "data": 'L35+L36',
            "source": {
                "L36": {
                    "table_name": "cashflow_data",
                    "entity_type": "section",
                    "entity_id": 6,
                    "month": 'previous_month'
                }
            }
        },
        "is_adjustible": True
    },
    'L39': {
        "type": "category",
        "id": 7,
        "formula": {
            "data": 'L40+L41',
            "source": {
                "L40": {
                    "table_name": "cashflow_data",
                    "entity_type": "subcategory",
                    "entity_id": 16,
                },
                "L41": {
                    "table_name": "cashflow_data",
                    "entity_type": "subcategory",
                    "entity_id": 17,
                }
            }
        },
        "is_adjustible": True
    },
    'L44': {
        "type": "section",
        "id": 7,
        "formula": {
            "data": 'L39',
            "source": {}
        },
        "is_adjustible": True
    },
    'L45': {
        "type": "section",
        "id": 8,
        "formula": {
            "data": 'L44',
            "source": {}
        },
        "is_adjustible": True
    },
    'L47': {
        "type": "category",
        "id": 8,
        "formula": {
            "data": '-L48-L49-L50+L51+L52+L53+L54',
            "source": {
                "L48": {
                    "table_name": "cashflow_data",
                    "entity_type": "subcategory",
                    "entity_id": 20,
                },
                "L49": {
                    "table_name": "cashflow_data",
                    "entity_type": "subcategory",
                    "entity_id": 21,
                },
                "L50": {
                    "table_name": "cashflow_data",
                    "entity_type": "subcategory",
                    "entity_id": 22,
                },
                "L51": {
                    "table_name": "cashflow_data",
                    "entity_type": "subcategory",
                    "entity_id": 23,
                },
                "L52": {
                    "table_name": "cashflow_data",
                    "entity_type": "subcategory",
                    "entity_id": 24,
                },
                "L53": {
                    "table_name": "cashflow_data",
                    "entity_type": "subcategory",
                    "entity_id": 25,
                },
                "L54": {
                    "table_name": "cashflow_data",
                    "entity_type": "subcategory",
                    "entity_id": 26,
                },
            }
        },
        "is_adjustible": True
    },
    'L57': {
        "type": "section",
        "id": 9,
        "formula": {
            "data": 'L47',
            "source": {}
        },
        "is_adjustible": True
    },
    'L58': {
        "type": "section",
        "id": 10,
        "formula": {
            "data": 'L57+L58',
            "source": {
                "L58": {
                    "table_name": "cashflow_data",
                    "entity_type": "section",
                    "entity_id": 10,
                    "month": 'previous_month'
                },
            }
        },
        "is_adjustible": True
    },
    'L61': {
        "type": "section",
        "id": 11,
        "formula": {
            "data": 'L35+L57+L44',
            "source": {},
            },
            "is_adjustible": True
        },
    'L62': {
        "type": "section",
        "id": 12,
        "formula": {
            "data": 'L61',
            "source": {},
            },
            "is_adjustible": True
        },
    'L69': {
        "type": "category",
        "id": 12,
        "formula": {
            "data": 'L61+L69',
            "source": {
                "L69": {
                    "table_name": "cashflow_data",
                    "entity_type": "category",
                    "entity_id": 12,
                    "month": 'previous_month'
                },
            }
        },
        "is_adjustible": True
    },
    'L70': {
        "type": "section",
        "id": 13,
        "formula": {
            "data": 'L67+L68+L69',
            "source": {
                "L67": {
                    "table_name": "cashflow_data",
                    "entity_type": "category",
                    "entity_id": 10,
                },
                "L68": {
                    "table_name": "cashflow_data",
                    "entity_type": "category",
                    "entity_id": 11,
                },
                "L69": {
                    "table_name": "cashflow_data",
                    "entity_type": "category",
                    "entity_id": 12,
                },

            },
        },
        "is_adjustible": True
    },
    'L77': {
        "type": "section",
        "id": 14,
        "formula": {
            "data": 'SUM(L72:L76)',
            "source": {
                "L72": {
                    "table_name": "cashflow_data",
                    "entity_type": "category",
                    "entity_id": 13,
                },
                "L76": {
                    "table_name": "cashflow_data",
                    "entity_type": "category",
                    "entity_id": 17,
                },
            },
        },
        "is_adjustible": True
    },
}

months = {1:'jan', 2:'feb', 3:'mar', 4:'apr',
           5:'may', 6:'jun', 7:'jul', 8:'aug',
           9:'sep', 10:'oct', 11:'nov', 12:'dec'
}

dette_nette_mappings = [
    {'metric_name': "CHARGES D'INTERETS", 'type': 'subcategory', 'id': 20},
    {'metric_name': "REMBOURSEMENT D'EMPRUNTS", 'type': 'subcategory', 'id': 21},
    {'metric_name': "NOUVEAU EMPRUNTS A LMT", 'type': 'subcategory', 'id': 23},
    {'metric_name': "EMPRUNTS BANCAIRES", 'type': 'category', 'id': 13},
    {'metric_name': "CREDIT SPOT", 'type': 'category', 'id': 15},
    {'metric_name': "INTERETS COURUS NON ECHUS", 'type': 'category', 'id': 17},
]

month_column_mapping = {
    'JANVIER': 'F',
    'FEVRIER': 'G',
    'MARS': 'H',
    'AVRIL': 'I',
    'MAI': 'J',
    'JUIN': 'K',
    'JUILLET': 'L',
    'AOÛT': 'M',
    'SEPTEMBRE': 'N',
    'OCTOBRE': 'O',
    'NOVEMBRE': 'P',
    'DECEMBRE': 'Q',
}
