indicateurs_mobile_mapping = {
    'L7': {
        "type": "financial_type",
        "id": 50,
        "formula": {
            "data": "SUM(CJ16,CJ149)/(SUM(CJ37,CJ47)/1000000)",
            "source": {
                "CJ16": {
                    "table_name" : "financial_metrics_data",
                    "column_name": "financial_type_id",
                    "value": 20
                },
                "CJ149": {
                    "table_name" : "financial_metrics_data",
                    "column_name": "financial_type_id",
                    "value": 21
                },
                "CJ37": {
                    "table_name" : "financial_metrics_data",
                    "column_name": "financial_submetric_id",
                    "value": 87
                },
                "CJ47": {
                    "table_name" : "financial_metrics_data",
                    "column_name": "financial_submetric_id",
                    "value": 92
                }
            }
        }
    },
    'L8': {
        "type": "financial_metric",
        "id" : 145,
        "formula": {
            "data": "CJ16/(SUM(CJ37,CJ47)/1000000)",
            "source": {
                "CJ16": {
                    "table_name" : "financial_metrics_data",
                    "column_name": "financial_type_id",
                    "value": 20
                },
                "CJ37":{
                    "table_name" : "financial_metrics_data",
                    "column_name": "financial_submetric_id",
                    "value": 87
                },
                "CJ47":{
                    "table_name" : "financial_metrics_data",
                    "column_name": "financial_submetric_id",
                    "value": 92
                },
            }
        }
    },
    'L9': {
        "type": "financial_metric",
        "id": 146,
        "formula": {
            "data": "CJ149/(SUM(CJ37,CJ47)/1000000)",
            "source": {
                "CJ149":{
                    "table_name" : "financial_metrics_data",
                    "column_name": "financial_type_id",
                    "value": 21
                },
                "CJ37":{
                    "table_name" : "financial_metrics_data",
                    "column_name": "financial_submetric_id",
                    "value": 87
                },
                "CJ47":{
                    "table_name" : "financial_metrics_data",
                    "column_name": "financial_submetric_id",
                    "value": 92
                },
            }
        }
    },
    'L12': {
        "type": "financial_metric",
        "id": 147,
        "formula": {
            "data": "(CJ18+CJ38)/(CJ37/1000000)",
            "source": {
                "CJ18": {
                    "table_name" : "collapse_monthly_data",
                    "entity_type": "type",
                    "entity_id": 160,
                },
                "CJ38": {
                    "table_name" : "collapse_monthly_data",
                    "entity_type": "category",
                    "entity_id": 4
                },
                "CJ37": {
                    "table_name" : "financial_metrics_data",
                    "column_name": "financial_submetric_id",
                    "value": 87
                }
            }
        }
    },
    'L13': {
        "type": "financial_metric",
        "id": 148,
        "formula": {
            "data": "CJ166/(CJ37/1000000)",
            "source": {
                "CJ151":{
                    # NOT PRESENT IN DB
                    "table_name" : "",
                    "column_name": "",
                    "value": "",
                },
                "CJ156":{
                    # NOT PRESENT IN DB
                    "table_name" : "",
                    "column_name": "",
                    "value": "",
                },
                "CJ161":{
                    # NOT PRESENT IN DB
                    "table_name" : "",
                    "column_name": "",
                    "value": ''
                },
                "CJ166":{
                   "table_name" : "collapse_monthly_data",
                    "entity_type": "type",
                    "entity_id": 169,
                },
                "CJ37":{
                    "table_name" : "financial_metrics_data",
                    "column_name": "financial_submetric_id",
                    "value": 87
                },
            }
        }
    },
    'L11': {
        "type": "financial_type",
        "id": 51,
        "formula": {
            "data": "L12+L13",
            "source": {}
        }
    },
    'L16': {
        "type": "financial_metric",
        "id": 149,
        "formula": {
            "data": "(CJ53+CJ78+CJ103+CJ128)/(CJ47/1000000)",
            "source": {
                "CJ53":{
                    "table_name" : "financial_metrics_data",
                    "column_name": "financial_metric_id",
                    "value": 59 ,
                },
                "CJ78":{
                    "table_name" : "collapse_monthly_data",
                    "entity_type": "category",
                    "entity_id": 8
                },
                "CJ103":{
                    "table_name" : "collapse_monthly_data",
                    "entity_type": "category",
                    "entity_id": 12
                },
                "CJ128":{
                    "table_name" : "collapse_monthly_data",
                    "entity_type": "category",
                    "entity_id": 16
                },
                "CJ47":{
                    "table_name" : "financial_metrics_data",
                    "column_name": "financial_submetric_id",
                    "id": 92,
                },
            }
        }
    },
    'L17': {
        "type": "financial_metric",
        "id": 150,
        "formula": {
            "data": "((CJ167+CJ168+CJ169)*1000000)/CJ47",
            "source": {
                "CJ152":{
                     # NOT PRESENT IN DB
                     "table_name" : "",
                    "column_name": "",
                    "value": "",
                },
                "CJ153":{
                    # NOT PRESENT IN DB
                     "table_name" : "",
                    "column_name": "",
                    "value": "",
                },
                "CJ154":{
                    # NOT PRESENT IN DB
                     "table_name" : "",
                    "column_name": "",
                    "value": "",
                },
                "CJ157":{
                    # NOT PRESENT IN DB
                     "table_name" : "",
                    "column_name": "",
                    "value": "",
                },
                "CJ158":{
                    # NOT PRESENT IN DB
                    "table_name" : "",
                    "column_name": "",
                    "value": "",
                },
                "CJ159":{
                    # NOT PRESENT IN DB
                    "table_name" : "",
                    "column_name": "",
                    "value": "",
                },
                "CJ162":{
                     # NOT PRESENT IN DB
                     "table_name" : "",
                    "column_name": "",
                    "value": ''
                },
                "CJ163":{
                    # NOT PRESENT IN DB
                    "table_name" : "",
                    "column_name": "",
                    "value": ''
                },
                "CJ164":{
                    # NOT PRESENT IN DB
                    "table_name" : "",
                    "column_name": "",
                    "value": ''
                },
                "CJ167":{
                   "table_name" : "collapse_monthly_data",
                    "entity_type": "type",
                    "entity_id": 170,
                },
                "CJ168":{
                   "table_name" : "collapse_monthly_data",
                   "entity_type": "type",
                   "entity_id": 171,
                },
                "CJ169":{
                    "table_name" : "collapse_monthly_data",
                    "entity_type" : "type",
                    "entity_id": 172,
                },
                "CJ47":{
                    "table_name" : "financial_metrics_data",
                    "column_name": "financial_submetric_id",
                    "value": 92,
                },
            }
        }
    },
    'L15': {
        "type": "financial_type",
        "id": 52,
        "formula": {
            "data": "L16+L17",
            "source": {}
        }
    },
    'L19': {
        "type": "financial_type",
        "id": 53,
        "formula": {
            "data": "(CJ7+CJ55)/(SUM(CJ37,CJ47)/1000000)",
            "source": {
                "CJ7":{
                    "table_name" : "financial_metrics_data",
                    "column_name": "financial_type_id",
                    "value": 31
                },
                "CJ55":{
                    "table_name" : "financial_metrics_data",
                    "column_name": "financial_type_id",
                    "value": 32
                },
                "CJ37":{
                    "table_name" : "financial_metrics_data",
                    "column_name": "financial_submetric_id",
                    "value": 87
                },
                "CJ47":{
                    "table_name" : "financial_metrics_data",
                    "column_name": "financial_submetric_id",
                    "value": 92,
                },
            }
        }
    },
    'L20': {
        "type": "financial_metric",
        "id": 151,
        "formula": {
            "data": "CJ7/(SUM(CJ37,CJ47)/1000000)",
            "source": {
                "CJ7":{
                    "table_name" : "financial_metrics_data",
                    "column_name": "financial_type_id",
                    "value": 31
                },
               "CJ37":{
                   "table_name" : "financial_metrics_data",
                    "column_name": "financial_submetric_id",
                    "value": 87
                },
                "CJ47":{
                    "table_name" : "financial_metrics_data",
                    "column_name": "financial_submetric_id",
                    "value": 92,
                },
            }
        }
    },
    'L21': {
        "type": "financial_submetric",
        "id": 93,
        "formula": {
            "data": "CJ9/(CJ37/1000000)",
            "source": {
                "CJ9":{
                    "table_name" : "financial_metrics_data",
                    "column_name": "financial_metric_id",
                    "value": 89
                },
                "CJ37":{
                    "table_name" : "financial_metrics_data",
                    "column_name": "financial_submetric_id",
                    "value": 87
                },
            }
        }
    },
    'L22': {
        "type": "financial_submetric",
        "id": 94,
        "formula": {
            "data": "R18/(R47/1000000)",
            "source": {
                "R18":{
                    "table_name" : "financial_metrics_data",
                    "column_name": "financial_metric_id",
                    "value": 90
                },
                "R47":{
                    "table_name" : "financial_metrics_data",
                    "column_name": "financial_submetric_id",
                    "value": 92,
                },
            }
        }
    },
    'L23': {
        "type": "financial_metric",
        "id": 152,
        "formula": {
            "data": "CJ55/(SUM(CJ37,CJ47)/1000000)",
            "source": {
                "CJ55":{
                    "table_name" : "financial_metrics_data",
                    "column_name": "financial_type_id",
                    "value": 32
                },
                "CJ37":{
                    "table_name" : "financial_metrics_data",
                    "column_name": "financial_submetric_id",
                    "value": 87
                },
                "CJ47":{
                    "table_name" : "financial_metrics_data",
                    "column_name": "financial_submetric_id",
                    "value": 92,
                },
            }
        }
    },
    'L24': {
        "type": "financial_submetric",
        "id": 95,
        "formula": {
            "data": "CJ57/(CJ37/1000000)",
            "source": {
                "CJ57":{
                    "table_name" : "financial_metrics_data",
                    "column_name": "financial_metric_id",
                    "value": 91
                },
                "CJ37":{
                    "table_name" : "financial_metrics_data",
                    "column_name": "financial_submetric_id",
                    "value": 87
                }
            }
        }
    },
    'L25': {
        "type": "financial_submetric",
        "id": 96,
        "formula": {
            "data": "CJ64/(CJ47/1000000)",
            "source": {
                "CJ64":{
                    "table_name" : "financial_metrics_data",
                    "column_name": "financial_metric_id",
                    "value": 92
                },
                "CJ47":{
                    "table_name" : "financial_metrics_data",
                    "column_name": "financial_submetric_id",
                    "value": 92,
                },
            }
        }
    },
    'L27': {
        "type": "financial_type",
        "id": 54,
        "formula": {
            "data": "(CJ28+CJ68+CJ93+CJ118+CJ149)/(CJ7+CJ55)",
            "source": {
                "CJ28":{
                    "table_name" : "collapse_monthly_data",
                    "entity_type": "category",
                    "entity_id": 2
                },
                "CJ68":{
                    "table_name" : "collapse_monthly_data",
                    "entity_type": "category",
                    "entity_id": 6
                },
                "CJ93":{
                    "table_name" : "collapse_monthly_data",
                    "entity_type": "category",
                    "entity_id": 10
                },
                "CJ118":{
                   "table_name" : "collapse_monthly_data",
                    "entity_type": "category",
                    "entity_id": 14
                },
                "CJ149":{
                    "table_name" : "financial_metrics_data",
                    "column_name": "financial_type_id",
                    "value": 21
                },
                "CJ7":{
                    "table_name" : "financial_metrics_data",
                    "column_name": "financial_type_id",
                    "value": 31
                },
                "CJ55":{
                    "table_name" : "financial_metrics_data",
                    "column_name": "financial_type_id",
                    "value": 32
                },
            }
        }
    },
    'L28': {
        "type": "financial_metric",
        "id": 153,
        "formula": {
            "data": "(CJ28+CJ68+CJ93+CJ118)/CJ7",
            "source": {
                "CJ28":{
                    "table_name" : "collapse_monthly_data",
                    "entity_type": "category",
                    "entity_id": 2
                },
                "CJ68":{
                    "table_name" : "collapse_monthly_data",
                    "entity_type": "category",
                    "entity_id": 6
                },
                "CJ93":{
                    "table_name" : "collapse_monthly_data",
                    "entity_type": "category",
                    "entity_id": 10
                },
                "CJ118":{
                   "table_name" : "collapse_monthly_data",
                    "entity_type": "category",
                    "entity_id": 14
                },
                "CJ7":{
                    "table_name" : "financial_metrics_data",
                    "column_name": "financial_type_id",
                    "value": 31
                }
            }
        }
    },
    'L29': {
        "type": "financial_submetric",
        "id": 97,
        "formula": {
            "data": "CJ28/CJ9",
            "source": {
                "CJ28":{
                    "table_name" : "collapse_monthly_data",
                    "entity_type": "category",
                    "entity_id": 2
                },
                 "CJ9":{
                    "table_name" : "financial_metrics_data",
                    "column_name": "financial_metric_id",
                    "value": 89
                },
            }
        }
    },
    'L30': {
        "type": "financial_submetric",
        "id": 98,
        "formula": {
            "data": "(R68+R93+R118)/R18",
            "source": {
                "R68":{
                    "table_name" : "collapse_monthly_data",
                    "entity_type": "category",
                    "entity_id": 6
                },
                "R93":{
                    "table_name" : "collapse_monthly_data",
                    "entity_type": "category",
                    "entity_id": 10
                },
                "R118":{
                   "table_name" : "collapse_monthly_data",
                    "entity_type": "category",
                    "entity_id": 14
                },
                "R18":{
                    "table_name" : "financial_metrics_data",
                    "column_name": "financial_metric_id",
                    "value": 90
                },

            }
        }
    },
    'L31': {
        "type": "financial_metric",
        "id": 154,
        "formula": {
            "data": "SUM(CJ149)/CJ55",
            "source": {
                "CJ149": {
                    "table_name" : "financial_metrics_data",
                    "column_name": "financial_type_id",
                    "value": 21
                },
                "CJ55":{
                    "table_name" : "financial_metrics_data",
                    "column_name": "financial_type_id",
                    "value": 32
                }
            }
        }
    },
    'L32': {
        "type": "financial_submetric",
        "id": 99,
        "formula": {
            "data": "CJ166/CJ57",
            "source": {
                "CJ151":{
                    # NOT PRESENT IN DB
                    "table_name" : "",
                    "column_name": "",
                    "value": "",
                },
                "CJ156":{
                    # NOT PRESENT IN DB
                    "table_name" : "",
                    "column_name": "",
                    "value": "",
                },
                "CJ161":{
                    # NOT PRESENT IN DB
                    "table_name" : "",
                    "column_name": "",
                    "value": ""
                },
                "CJ166":{
                   "table_name" : "collapse_monthly_data",
                   "entity_type": "type",
                   "entity_id": 169,
                },
                "CJ57":{
                    "table_name" : "financial_metrics_data",
                    "column_name": "financial_metric_id",
                    "value": 91
                }
            }
        }
    },
    'L33': {
        "type": "financial_submetric",
        "id": 100,
        "formula": {
            "data": "(CJ167+CJ168+CJ169)/CJ64",
            "source": {
                "CJ167":{
                    "table_name" : "collapse_monthly_data",
                    "entity_type": "type",
                    "entity_id": 170
                },
                "CJ168":{
                    "table_name" : "collapse_monthly_data",
                    "entity_type": "type",
                    "entity_id": 171
                },
                "CJ169":{
                    "table_name" : "collapse_monthly_data",
                    "entity_type": "type",
                    "entity_id": 172
                },
               "CJ64":{
                    "table_name" : "financial_metrics_data",
                    "column_name": "financial_metric_id",
                    "value": 92
                },
            }
        }
    }
}
