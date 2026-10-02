capex_coso_mapping = {
    "L23": {
        "type": "financial_type",
        "id": 3,
        "formula": {
            "data": "SUM(L24:L26)",
            "source": {
                "L24": {
                    "table_name": "financial_metrics_data",
                    "column_name": "financial_metric_id",
                    "value": 12
                },
                "L26": {
                    "table_name": "financial_metrics_data",
                    "column_name": "financial_metric_id",
                    "value": 14
                }
            }
        }
    },
    "L28": {
        "type": "financial_type",
        "id": 4,
        "formula": {
            "data": "SUM(L29:L41)",
            "source": {
                "L29": {
                    "table_name": "financial_metrics_data",
                    "column_name": "financial_metric_id",
                    "value": 15
                },
                "L41": {
                    "table_name": "financial_metrics_data",
                    "column_name": "financial_metric_id",
                    "value": 27
                }
            }
        }
    },
    "L12":{
        "type": "financial_metric",
        "id": 2,
        "formula": {
            "data": "L12 + 25.842129",
            "source": {
                "L12": {
                    "table_name": "financial_metrics_data",
                    "column_name": "financial_metric_id",
                    "value": 2
                }
            }
        }
    },
    "L11": {
        "type": "financial_metric",
        "id": 1,
        "formula": {
            "data": "L11+L14",
            "source": {
                "L11": {
                    "table_name": "financial_metrics_data",
                    "column_name": "financial_metric_id",
                    "value": 1
                },
                "L14": {
                    "table_name": "financial_metrics_data",
                    "column_name": "financial_metric_id",
                    "value": 4
                }
            }
        }
    },
    "L14": {
        "type": "financial_metric",
        "id": 4,
        "formula": {
            "data": "0",
            "source": {}
        }
    },
    "L10": {
        "type": "financial_type",
        "id": 2,
        "formula": {
            "data": "SUM(L11:L21) + L12",
            "source": {
                "L11": {
                    "table_name": "financial_metrics_data",
                    "column_name": "financial_metric_id",
                    "value": 1
                },
                "L21": {
                    "table_name": "financial_metrics_data",
                    "column_name": "financial_metric_id",
                    "value": 11
                }
            }
        }
    },
    "L7": {
        "type": "financial_type",
        "id": 1,
        "formula": {
            "data": 'L10+L23+L28',
            "source": {}
        }
    },
}
