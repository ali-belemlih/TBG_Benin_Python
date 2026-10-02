pnl_import_mapping = {
    'L10': {
        "table_name" : "financial_submetric",
        "id" : 11,
        "formula": {
            "data": "AD8",
            "source": {
                "AD8": {
                    "table_name": "financial_metrics_data",
                    "column_name": "financial_type_id",
                    "value": 17
                }
            }
        },
        "is_adjustible": True
    },
    'L9': {
        "table_name" : "financial_metric",
        "id" : 79,
        "formula": {
            "data": "L10"
        },
        "is_adjustible": True

    },
    'L7': {
        "table_name" : "financial_type",
        "id" : 29,
        "formula": {
            "data": "L9"
        },
        "is_adjustible": True
    },
    'L18':{
        "table_name" : "financial_submetric",
        "id" : 13,
        "formula": {
            "data": "AD58",
            "source": {
                "AD58": {
                    "table_name": "financial_metrics_data",
                    "column_name": "financial_type_id",
                    "value": 26
                }
            }
        },
        "is_adjustible": True
    },
    'L17':{
        "table_name" : "financial_submetric",
        "id" : 12,
        "formula": {
            "data": "L18"
        },
        "is_adjustible": True
    },
    'L15':{
        "table_name" : "financial_metric",
        "id": 80,
        "formula": {
            "data": "L17"
        },
        "is_adjustible": True
    },
    'L20': {
        "table_name" : "financial_metric",
        "id" : 81,
        "formula": {
            "data": "L7+L15"
        },
        "is_adjustible": True
    },
    'L21': {
        "table_name" : "financial_submetric",
        "id" : 14,
        "formula": {
            "data": "(L20/L7)*100"
        },
        "is_adjustible": True
    },
    'L23': {
        "table_name" : "financial_submetric",
        "id" : 15,
        "formula": {
            "data": "L9+L17"
        },
        "is_adjustible": True
    },
    'L29': {
        "table_name" : "financial_submetric",
        "id" : 17,
        "formula": {
            "data": "-AD7",
            "source": {
                "AD7": {
                    "table_name": "financial_metrics_data",
                    "column_name": "financial_type_id",
                    "value": 5
                }
            }
        },
        "is_adjustible": True
    },
    'L28': {
        "table_name" : "financial_submetric",
        "id" : 16,
        "formula": {
            "data": "L29"
        },
        "is_adjustible": True
    },
    'L25': {
        "table_name" : "financial_metric",
        "id" : 82,
        "formula": {
            "data": "L28"
        },
        "is_adjustible": True
    },
    'L31': {
        "table_name" : "financial_metric",
        "id" : 83,
        "formula": {
        "data": "L20+L25"
        },
        "is_adjustible": True
    },
    'L32': {
        "table_name" : "financial_submetric",
        "id" : 18,
        "formula": {
            "data": "(L31/L7)*100"
            },
        "is_adjustible": True
        },
    'L34': {
        "table_name" : "financial_submetric",
        "id" : 19,
        "formula": {
            "data": "L23+L28"
        },
        "is_adjustible": True
    },
    'L41': {
        "table_name" : "financial_metric",
        "id" : 85,
        "formula": {
            "data": "L31+L36",
            "source": {
                "L36": {
                    "table_name": "financial_metrics_data",
                    "column_name": "financial_metric_id",
                    "value": 84
                }
            }
        },
        "is_adjustible": True
    },
    'L42': {
        "table_name" : "financial_submetric",
        "id" : 20,
        "formula": {
            "data": "(L41/L7)*100"
        },
        "is_adjustible": True
    },
    'L50': {
        "table_name" : "financial_metric",
        "id" : 87,
        "formula": {
            "data": "L41+L47",
            "source": {
                "L47": {
                    "table_name": "financial_metrics_data",
                    "column_name": "financial_metric_id",
                    "value": 86
                }
            }
        },
        "is_adjustible": True
    },
    'L51': {
        "table_name" : "financial_submetric",
        "id" : 21,
        "formula": {
            "data": "-0.01 * L7",
        },
        "is_adjustible": False
    },
    'L54': {
        "table_name" : "financial_type",
        "id" : 30,
        "formula": {
            "data": "L50+L51+L52",
            "source": {
                "L52": {
                    "table_name": "financial_metrics_data",
                    "column_name": "financial_submetric_id",
                    "value": 22
                },
                "L51": {
                    "table_name": "financial_metrics_data",
                    "column_name": "financial_submetric_id",
                    "value": 21
                }
            }
        },
        "is_adjustible": True
    },
    'L56': {
        "table_name" : "financial_metric",
        "id" : 88,
        "formula": {
            "data": "(L54/L7)*100"
        },
        "is_adjustible": True
    }
}

# Map months to columns in Excel
month_column_map = {
    1: "B", 2: "C", 3: "D", 4: "E", 5: "F", 6: "G",
    7: "H", 8: "I", 9: "J", 10: "K", 11: "L", 12: "M"
}

impact_ifrs_column_map = {
    1: "C", 2: "D", 3: "E", 4: "F", 5: "G", 6: "H",
    7: "I", 8: "J", 9: "K", 10: "L", 11: "M", 12: "N"
}

FILE_MONTH_MAPPING = {
    '01': 'JAN', '02': 'FEV', '03': 'MAR', '04': 'APR',
    '05': 'MAY', '06': 'JUN', '07': 'JUL', '08': 'AUG',
    '09': 'SEP', '10': 'OCT', '11': 'NOV', '12': 'DEC'
}
