from sqlalchemy.sql import true


marge_mobile_mapping = {
    "L8": {
        "type": "financial_metric",
        "id": 68,
        "formula": {
            "data": "AD11 + AD20",
            "source": {
                "AD11": {
                    "table_name": "financial_metrics_data",
                    "column_name": "financial_submetric_id",
                    "value": 24
                },
                "AD20": {
                    "table_name": "financial_metrics_data",
                    "column_name": "financial_submetric_id",
                    "value": 31
                }
            }
        },
        "is_adjustible": True
    },
    "L7": {
        "type": "financial_type",
        "id": 25,
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
    "L9": {
        "type": "financial_metric",
        "id": 69,
        "formula": {
            "data": "L10/L8",
            "source": {
                "L10": {
                    "table_name": "financial_metrics_data",
                    "column_name": "financial_metric_id",
                    "value": 70
                    },
                "L8": {
                    "table_name": "financial_metrics_data",
                    "column_name": "financial_metric_id",
                    "value": 68
                }
            }
        },
        "is_adjustible": True
    },
    "L41": {
        "type": "financial_metric",
        "id": 74,
        "formula": {
            "data": "L42/L40",
            "source": {
                "L42": {
                    "table_name": "financial_metrics_data",
                    "column_name": "financial_metric_id",
                    "value": 75
                },
                "L40": {
                    "table_name": "financial_metrics_data",
                    "column_name": "financial_metric_id",
                    "value": 73
                }
            }
        },
        "is_adjustible": True
    },
    "L45": {
        "type": "financial_metric",
        "id": 77,
        "formula": {
            "data": "SUM(L49,L51)",
            "source": {
                "L49": {
                    "table_name": "financial_metrics_data",
                    "column_name": "financial_submetric_id",
                    "value": 6
                },
                "L51": {
                    "table_name": "financial_metrics_data",
                    "column_name": "financial_submetric_id",
                    "value": 7
                },
        }
        },
        "is_adjustible": True
    },
    "L52": {
        "type": "financial_metric",
        "id": 78,
        "formula":{
            "data": "L53+L54+L56",
            "source": {
                "L53": {
                    "table_name": "financial_metrics_data",
                    "column_name": "financial_submetric_id",
                    "value": 8
                },
                "L54": {
                    "table_name": "financial_metrics_data",
                    "column_name": "financial_submetric_id",
                    "value": 9
                },
                "L56": {
                    "table_name": "financial_metrics_data",
                    "column_name": "financial_submetric_id",
                    "value": 10
                }
            }
        },
        "is_adjustible": True
    },
    "L58": {
        "type": "financial_type",
        "id": 26,
        "formula": {
            "data": "L10+L38+L42+L43+L45+L52+L39",
            "source": {
                "L10": {
                    "table_name": "financial_metrics_data",
                    "column_name": "financial_metric_id",
                    "value": 70
                },
                "L38": {
                    "table_name": "financial_metrics_data",
                    "column_name": "financial_metric_id",
                    "value": 71
                },
                "L42": {
                    "table_name": "financial_metrics_data",
                    "column_name": "financial_metric_id",
                    "value": 75
                },
                "L43": {
                    "table_name": "financial_metrics_data",
                    "column_name": "financial_metric_id",
                    "value": 76
                },
                "L45": {
                    "table_name": "financial_metrics_data",
                    "column_name": "financial_metric_id",
                    "value": 77
                },
                "L52": {
                    "table_name": "financial_metrics_data",
                    "column_name": "financial_metric_id",
                    "value": 78
                },
                "L39": {
                    "table_name": "financial_metrics_data",
                    "column_name": "financial_metric_id",
                    "value": 72
                }
            }
        },
        "is_adjustible": True
    },
    "L60": {
        "type": "financial_type",
        "id": 27,
        "formula": {
            "data": "L7+L58",
            "source": {
                "L7": {
                    "table_name": "financial_metrics_data",
                    "column_name": "financial_type_id",
                    "value": 25
                },
                "L58": {
                    "table_name": "financial_metrics_data",
                    "column_name": "financial_type_id",
                    "value": 26,
                }
            }
        },
        "is_adjustible": True
    },
    "L61": {
        "type": "financial_type",
        "id": 28,
        "formula": {
            "data": "(L60/L7)*100",
            "source": {
                "L60": {
                    "table_name": "financial_metrics_data",
                    "column_name": "financial_type_id",
                    "value": 27,
                },
                "L7": {
                    "table_name": "financial_metrics_data",
                    "column_name": "financial_type_id",
                    "value": 25
                },
            }
        },
        "is_adjustible": True
    },
}

extraction_mapping = {
    'L38': {
        "id": 71,
        "type": "financial_metric",
        "formula": {
            "data": "-B14"
        },
    },
    'L42': {
        "id": 75,
        "type": "financial_metric",
        "formula": {
            "data": "-B13"
        },
    },
    'L53': {
        "id": 8,
        "type": "financial_submetric",
        "formula": {
            "data": "-B2"
        },
    },
    'L54': {
        "id": 9,
        "type": "financial_submetric",
        "formula": {
            "data": "-B4"
        },
    }
}
