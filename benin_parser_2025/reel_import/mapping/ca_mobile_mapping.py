ca_mobile_mapping = {
    'L20': {
        "type": "subcategory",
        "id": 1,
        "formula": {
            "data": 'L20+L22',
            "source": {
                "L20": {
                    "table_name": "collapse_monthly_data",
                    "entity_type": "subcategory",
                    "entity_id": 1
                },
                "L22": {
                    "table_name": "collapse_monthly_data",
                    "entity_type": "subcategory",
                    "entity_id": 3
                }
            }
        },
        "is_adjustible": True
    },
    'L28': {
        "type": "category",
        "id": 2,
        "formula": {
            "data": 'SUM(L20:L27) + L22',
            "source": {
                "L20": {
                    "table_name": "collapse_monthly_data",
                    "entity_type": "subcategory",
                    "entity_id": 1
                },
                "L27": {
                    "table_name": "collapse_monthly_data",
                    "entity_type": "subcategory",
                    "entity_id": 8
                },
                "L22": {
                    "table_name": "collapse_monthly_data",
                    "entity_type": "subcategory",
                    "entity_id": 3
                }
            }
        },
        "is_adjustible": True
    },
    'L22': {
        "type": "subcategory",
        "id": 3,
        "formula": {
            "data": "0"
        },
        "is_adjustible": False
    },
    'L36': {
        "type": "category",
        "id": 3,
        "formula": {
            "data": 'SUM(L30:L35)',
            "source": {
                "L30": {
                    "table_name": "collapse_monthly_data",
                    "entity_type": "subcategory",
                    "entity_id": 9
                },
                "L35": {
                    "table_name": "collapse_monthly_data",
                    "entity_type": "subcategory",
                    "entity_id": 14
                }
            }
        },
        "is_adjustible": True
    },
    "L45":{
        "type": "subcategory",
        "id": 20,
        "formula": {
            "data": 'L45-L41',
            "source": {
                "L45": {
                    "table_name": "collapse_monthly_data",
                    "entity_type": "subcategory",
                    "entity_id": 20
                },
                "L41": {
                    "table_name": "collapse_monthly_data",
                    "entity_type": "subcategory",
                    "entity_id": 16
                }
            }
        },
        "is_adjustible": False
    },
    'L47': {
        "type": "category",
        "id": 5,
        "formula": {
            "data": 'L40+L41+L45',
            "source": {
                "L40": {
                    "table_name": "collapse_monthly_data",
                    "entity_type": "subcategory",
                    "entity_id": 15
                },
                "L41": {
                    "table_name": "collapse_monthly_data",
                    "entity_type": "subcategory",
                    "entity_id": 16
                },
                "L45": {
                    "table_name": "collapse_monthly_data",
                    "entity_type": "subcategory",
                    "entity_id": 20
                },
            }
        },
        "is_adjustible": True
    },
    'L17': {
        "type": "financial_metric",
        "id": 58,
        "formula": {
            "data": 'L19+L28+L36+L47',
            "source": {
                "L19": {
                    "table_name": "collapse_monthly_data",
                    "entity_type": "category",
                    "entity_id": 1
                },
                'L28': {
                    "table_name": "collapse_monthly_data",
                    "entity_type": "category",
                    "entity_id": 2
                },
                'L36': {
                    "table_name": "collapse_monthly_data",
                    "entity_type": "category",
                    "entity_id": 3
                },
                'L47': {
                    "table_name": "collapse_monthly_data",
                    "entity_type": "category",
                    "entity_id": 5
                }
            }
        },
        "is_adjustible": True
    },
    'L18': {
        "type": "type",
        "id": 160,
        "formula": {
            "data": 'L19+L28+L36+L47',
            "source": {
                "L19": {
                    "table_name": "collapse_monthly_data",
                    "entity_type": "category",
                    "entity_id": 1
                },
                'L28': {
                    "table_name": "collapse_monthly_data",
                    "entity_type": "category",
                    "entity_id": 2
                },
                'L36': {
                    "table_name": "collapse_monthly_data",
                    "entity_type": "category",
                    "entity_id": 3
                },
                'L47': {
                    "table_name": "collapse_monthly_data",
                    "entity_type": "category",
                    "entity_id": 5
                }
            }
        },
        "is_adjustible": True
    },
    "L54": {
        "type": "financial_submetric",
        "id": 4,
        "formula": {
            "data": "SUM(L55:L57)",
            "source": {
                "L55": {
                    "table_name": "collapse_monthly_data",
                    "entity_type": "type",
                    "entity_id": 161
                },
                "L57": {
                    "table_name": "collapse_monthly_data",
                    "entity_type": "type",
                    "entity_id": 163
                }
            }
        },
        "is_adjustible": True
    },
    "L68": {
        "type": "category",
        "id": 6,
        "formula": {
            "data": "SUM(L60:L67)",
            "source": {
                "L60": {
                    "table_name": "collapse_monthly_data",
                    "entity_type": "subcategory",
                    "entity_id": 22
                },
                "L67": {
                    "table_name": "collapse_monthly_data",
                    "entity_type": "subcategory",
                    "entity_id": 29
                }
            }
        },
        "is_adjustible": True
    },
    "L71":{
        "type" : "subcategory",
        "id" : 31,
        "formula" : {
            "data" : "0"
        },
        "is_adjustible": False
    },
    "L72":{
        "type" : "subcategory",
        "id" : 32,
        "formula" : {
            "data" : "0"
        },
        "is_adjustible": False
    },
    "L73":{
        "type" : "subcategory",
        "id" : 33,
        "formula" : {
            "data" : "0"
        },
        "is_adjustible": False
    },
    "L74":{
        "type" : "subcategory",
        "id" : 34,
        "formula" : {
            "data" : "0"
        },
        "is_adjustible": False
    },
    "L75":{
        "type" : "subcategory",
        "id" : 35,
        "formula" : {
            "data" : "0"
        },
        "is_adjustible": False
    },
    "L76": {
        "type": "category",
        "id": 7,
        "formula": {
            "data": "L70",
            "source": {
                "L70": {
                    "table_name": "collapse_monthly_data",
                    "entity_type": "subcategory",
                    "entity_id": 30
                }
            }
        },
        "is_adjustible": False
    },
    "L59": {
        "type": "type",
        "id": 164,
        "formula": {
            "data": "L68+L76+L82",
            "source": {
                "L68": {
                    "table_name": "collapse_monthly_data",
                    "entity_type": "category",
                    "entity_id": 6
                },
                "L76": {
                    "table_name": "collapse_monthly_data",
                    "entity_type": "category",
                    "entity_id": 7
                },
                "L82": {
                    "table_name": "collapse_monthly_data",
                    "entity_type": "category",
                    "entity_id": 9
                }
            }
        },
        "is_adjustible": True
    },
    'L93': {
        'type': 'category',
        'id': 10,
        "formula": {
            "data": "SUM(L85:L92)",
            "source": {
                'L85': {
                    "table_name": "collapse_monthly_data",
                    "entity_type": "subcategory",
                    "entity_id": 39
                },
                'L92': {
                    "table_name": "collapse_monthly_data",
                    "entity_type": "subcategory",
                    "entity_id": 46
                }
            }
        },
        "is_adjustible": True
    },
     "L96":{
        "type" : "subcategory",
        "id" : 48,
        "formula" : {
            "data" : "0"
        },
        "is_adjustible": False
    },
    "L97":{
        "type" : "subcategory",
        "id" : 49,
        "formula" : {
            "data" : "0"
        },
        "is_adjustible": False
    },
    "L98":{
        "type" : "subcategory",
        "id" : 50,
        "formula" : {
            "data" : "0"
        },
        "is_adjustible": False
    },
    "L99":{
        "type" : "subcategory",
        "id" : 51,
        "formula" : {
            "data" : "0"
        },
        "is_adjustible": False
    },
    "L100":{
        "type" : "subcategory",
        "id" : 52,
        "formula" : {
            "data" : "0"
        },
        "is_adjustible": False
    },
    'L101':{
        'type': 'category',
        'id': 11,
        "formula": {
            "data": "L95",
            "source": {
                'L95': {
                    "table_name": "collapse_monthly_data",
                    "entity_type": "subcategory",
                    "entity_id": 47
                }
            }
        },
        "is_adjustible": True
    },
    'L107': {
        'type': 'category',
        'id': 13,
        "formula": {
            "data": "SUM(L104:L106)",
            "source": {
                "L104": {
                    "table_name": "collapse_monthly_data",
                    "entity_type": 'subcategory',
                    "entity_id": 53
                },
                "L106": {
                    "table_name": "collapse_monthly_data",
                    "entity_type": 'subcategory',
                    "entity_id": 55
                },
            }
        },
        "is_adjustible": True
    },
    "L84": {
        "type" : "type",
        "id" : 165,
        "formula" : {
            "data" : "L93+L101+L107",
            "source" : {
                "L93" : {
                    "table_name" : "collapse_monthly_data",
                    "entity_type" : "category",
                    "entity_id" : 10
                },
                "L101" : {
                    "table_name" : "collapse_monthly_data",
                    "entity_type" : "category",
                    "entity_id" : 11
                },
                "L107" : {
                    "table_name" : "collapse_monthly_data",
                    "entity_type" : "category",
                    "entity_id" : 13
                }
            }
        },
        "is_adjustible": True
    },
    'L118': {
        'type': 'category',
        'id': 14,
        "formula": {
            "data": "SUM(L110:L117)",
            "source": {
                'L110': {
                    "table_name": "collapse_monthly_data",
                    "entity_type": 'subcategory',
                    "entity_id": 56
                },
                'L117': {
                    "table_name": "collapse_monthly_data",
                    "entity_type": 'subcategory',
                    "entity_id": 63
                }
            },
        },
        "is_adjustible": True
    },
    'L126': {
        'type': 'category',
        'id': 15,
        "formula": {
            "data": "SUM(L120:L125)",
            "source": {
                'L120': {
                    "table_name": "collapse_monthly_data",
                    "entity_type": 'subcategory',
                    "entity_id": 64
                },
                'L125': {
                    "table_name": "collapse_monthly_data",
                    "entity_type": 'subcategory',
                    "entity_id": 69
                }
            }
        },
        "is_adjustible": True
    },
    'L137': {
        'type': 'category',
        'id': 17,
        "formula": {
            "data": "SUM(L129:L133)",
            "source": {
                'L129': {
                    "table_name": "collapse_monthly_data",
                    "entity_type": 'subcategory',
                    "entity_id": 70
                },
                'L133': {
                    "table_name": "collapse_monthly_data",
                    "entity_type": 'subcategory',
                    "entity_id": 74
                }
            }
        },
        "is_adjustible": True
    },
    'L109': {
        'type': 'type',
        'id': 166,
        "formula": {
            "data": "L118+L126+L137",
            "source": {
                'L118': {
                    "table_name": "collapse_monthly_data",
                    "entity_type": 'category',
                    "entity_id": 14
                },
                'L126': {
                    "table_name": "collapse_monthly_data",
                    "entity_type": 'category',
                    "entity_id": 15
                },
                'L137': {
                    "table_name": "collapse_monthly_data",
                    "entity_type": 'category',
                    "entity_id": 16
                },
            }
        },
        "is_adjustible": True
    },
    "L58": {
        "type": "financial_submetric",
        "id": 5,
        "formula": {
            "data": "L59+L84+L109",
            "source": {
                "L59": {
                    "table_name": "collapse_monthly_data",
                    "entity_type": "type",
                    "entity_id": 163
                },
                "L84": {
                    "table_name": "collapse_monthly_data",
                    "entity_type": "type",
                    "entity_id": 165
                },
                "L109": {
                    "table_name": "collapse_monthly_data",
                    "entity_type": "type",
                    "entity_id": 166
                }
            }
        },
        "is_adjustible": True
    },
    "L52": {
        "type": "category",
        "id": 25,
        "formula": {
            "data": "L38",
            "source": {
                "L38": {
                    "table_name": "collapse_monthly_data",
                    "entity_type": "category",
                    "entity_id": 4
                }
            }
        },
        "is_adjustible": True
    },
    'L142': {
        'type': 'category',
        'id': 21,
        "formula": {
            "data": "L128+L103+L78",
            "source": {
                'L128': {
                    "table_name": "collapse_monthly_data",
                    "entity_type": 'category',
                    "entity_id": 16
                },
                'L103': {
                    "table_name": "collapse_monthly_data",
                    "entity_type": 'category',
                    "entity_id": 12
                },
                'L78': {
                    "table_name": "collapse_monthly_data",
                    "entity_type": 'category',
                    "entity_id": 8
                }
            }
        },
        "is_adjustible": True
    },
    "L145": {
        "type": "financial_metric",
        "id": 62,
        "formula": {
            "data": "L142+L52",
            "source": {
                "L142": {
                    "table_name": "collapse_monthly_data",
                    "entity_type": "subcategory",
                    "entity_id": 21
                },
                "L52": {
                    "table_name": "collapse_monthly_data",
                    "entity_type": "category",
                    "entity_id": "25"
                }
            }
        },
        "is_adjustible": True
    },
    "L165": {
        "type": "financial_metric",
        "id": 63,
        "formula": {
            "data": "SUM(L166:L169)",
            "source": {
                "L166": {
                    "table_name": "collapse_monthly_data",
                    "entity_type": "type",
                    "entity_id": 169
                },
                "L169": {
                    "table_name": "collapse_monthly_data",
                    "entity_type": "type",
                    "entity_id": 172
                }
            }
        },
        "is_adjustible": True
    },
    "L179": {
        "type": "financial_type",
        "id": 24,
        "formula": {
            "data": "L180+L181",
            "source": {
                "L180": {
                    "table_name": "financial_metrics_data",
                    "column_name": "financial_metric_id",
                    "value": 65
                },
                "L181": {
                    "table_name": "financial_metrics_data",
                    "column_name": "financial_metric_id",
                    "value": 66
                }
            }
        },
        "is_adjustible": True
    },
    "L53": {
        "type": "financial_metric",
        "id": 59,
        "formula": {
            "data": "L54+L58",
            "source": {
                "L54": {
                    "table_name": "financial_metrics_data",
                    "column_name": "financial_metric_id",
                    "value": 4
                },
                "L58": {
                    "table_name": "financial_metrics_data",
                    "column_name": "financial_metric_id",
                    "value": 5
                }
            }
        },
        "is_adjustible": True
    },
    "L144":{
        "type": "financial_metric",
        "id": 61,
        "formula": {
            "data": 'L144-L171',
            "source": {
                "L144": {
                    "table_name": "financial_metrics_data",
                    "column_name": "financial_metric_id",
                    "value": 61
                },
                "L171": {
                    "table_name": "financial_metrics_data",
                    "column_name": "financial_type_id",
                    "value": 22
                }
            }
        },
        "is_adjustible": False
    },
    'L16': {
        "type": "financial_type",
        "id": 20,
        "formula": {
            "data": 'L17+L53+L143+L144+L145',
            "source": {
                'L17': {
                    "table_name": "financial_metrics_data",
                    "column_name": "financial_metric_id",
                    "value": 58,
                },
                "L53": {
                    "table_name": "financial_metrics_data",
                    "column_name": "financial_metric_id",
                    "value": 59,
                },
                "L143": {
                    "table_name": "financial_metrics_data",
                    "column_name": "financial_metric_id",
                    "value": 60
                },
                "L144": {
                    "table_name": "financial_metrics_data",
                    "column_name": "financial_metric_id",
                    "value": 61
                },
                "L145": {
                    "table_name": "financial_metrics_data",
                    "column_name": "financial_metric_id",
                    "value": 62
                },
            }
        },
        "is_adjustible": True
    },
    'L149': {
        'type': 'financial_type',
        'id': 21,
        "formula": {
            "data": "SUM(L166:L169)",
            "source": {
                "L166": {
                    "table_name": "collapse_monthly_data",
                    "entity_type": "type",
                    "entity_id": 169
                },
                "L169": {
                    "table_name": "collapse_monthly_data",
                    "entity_type": "type",
                    "entity_id": 172
                }
            }
        },
        "is_adjustible": True
    },
    'L14': {
        "type": "financial_type",
        "id": 19,
        "formula": {
            "data": 'L16+L149+L171',
            "source": {
                'L16': {
                    'table_name': "financial_metrics_data",
                    "column_name": "financial_type_id",
                    "value": 20
                },
                "L149": {
                    "table_name": "financial_metrics_data",
                    "column_name": "financial_type_id",
                    "value": 21
                },
                "L171": {
                    "table_name": "financial_metrics_data",
                    "column_name": "financial_type_id",
                    "value": 22
                }
            }
        },
        "is_adjustible": True
    },
    'L12': {
        "type": "financial_type",
        "id": 18,
        "formula": {
            "data": 'L14+L177',
            "source": {
                'L14': {
                    "table_name": "financial_metrics_data",
                    "column_name": "financial_type_id",
                    "value": 19
                },
                "L177": {
                    "table_name": "financial_metrics_data",
                    "column_name": "financial_type_id",
                    "value": 23
                }
            }
        },
        "is_adjustible": True
    },
    'L8': {
        "type": "financial_type",
        "id": 17,
        "formula": {
            "data": 'L12+L179',
            "source": {
                'L12': {
                    "table_name": "financial_metrics_data",
                    "column_name": 'financial_type_id',
                    "value": 18
                },
                "L179": {
                    "table_name": "financial_metrics_data",
                    "column_name": "financial_type_id",
                    "value": 24
                }
            }
        },
        "is_adjustible": True
    },
    "L134":{
        "type" : "subcategory",
        "id" : 75,
        "formula" : {
            "data" : "0"
        },
        "is_adjustible": False
    },
    "L135":{
        "type" : "subcategory",
        "id" : 76,
        "formula" : {
            "data" : "0"
        },
        "is_adjustible": False
    },
    "L136":{
        "type" : "subcategory",
        "id" : 77,
        "formula" : {
            "data" : "0"
        },
        "is_adjustible": False
    },
    "L42":{
        "type" : "subcategory",
        "id" : 17,
        "formula" : {
            "data" : "0"
        },
        "is_adjustible": False
    },
    "L43":{
        "type" : "subcategory",
        "id" : 18,
        "formula" : {
            "data" : "0"
        },
        "is_adjustible": False
    },
    "L44":{
        "type" : "subcategory",
        "id" : 19,
        "formula" : {
            "data" : "0"
        },
        "is_adjustible": False
    },
    "L46":{
        "type" : "subcategory",
        "id" : 21,
        "formula" : {
            "data" : "0"
        },
        "is_adjustible": False
    },
}

ca_mobile_sheet_mapping = {
    'L20': {
        "table_name": 'collapse_monthly_data',
        "entity_id": 1,
        "entity_type": "subcategory",
        "sheet": "CA Consumer",
        "formula": {
            "data": "SUM(D29:D34)",
        }
    },
    'L21': {
        "table_name": 'collapse_monthly_data',
        "entity_id": 2,
        "entity_type": "subcategory",
        "sheet": "CA Consumer",
        "formula": {
            "data": "-D29"
        }
    },
    'L25': {
        "table_name": 'collapse_monthly_data',
        "entity_id": 6,
        "entity_type": "subcategory",
        "sheet": "CA Consumer",
        "formula": {
            "data": "-D33"
        }
    },
    'L26': {
        "table_name": 'collapse_monthly_data',
        "entity_id": 7,
        "entity_type": "subcategory",
        "sheet": "CA Consumer",
        "formula": {
            "data": "-D34"
        }
    },
    'L41': {
        "table_name": 'collapse_monthly_data',
        "entity_id": 16,
        "entity_type": "subcategory",
        "sheet": "Crédits secours",
        "formula": {
            "data": "D4"
        }
    },
    'L110': {
        "table_name": 'collapse_monthly_data',
        "entity_id": 56,
        "entity_type": "subcategory",
        "sheet": "CA Business",
        "formula": {
            "data": 'SUM(D29:D34)'
        }
    },
    'L111': {
        "table_name": 'collapse_monthly_data',
        "entity_id": 57,
        "entity_type": "subcategory",
        "sheet": "CA Business",
        "formula": {
            "data": "-D29"
        }
    },
    'L115': {
        "table_name": 'collapse_monthly_data',
        "entity_id": 61,
        "entity_type": "subcategory",
        "sheet": "CA Business",
        "formula": {
            "data": "-D33"
        }
    },
    'L116': {
        "table_name": 'collapse_monthly_data',
        "entity_id": 62,
        "entity_type": "subcategory",
        "sheet": "CA Business",
        "formula": {
            "data": "-D34"
        }
    },
    'L171': {
        "table_name": 'financial_metrics_data',
        "column_name": "financial_type_id",
        "value": 22,
        "sheet": "COLOCALISATION",
        "formula": {
            "data": "H19"
        }
    }
}
