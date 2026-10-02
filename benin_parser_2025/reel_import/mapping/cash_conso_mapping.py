cash_conso_mapping = {
    "R7": {
        "type": "financial_type",
        "id": 13,
        "formula": {
            "data": "CJ31",
            "source": {
                "CJ31": {
                    "table_name": "financial_metrics_data",
                    "column_name": "financial_metric_id",
                    "value": 83
                },
            }
        },
        "is_adjustible": True
    },
    "R9": {
        "type": "financial_metric",
        "id": 45,
        "formula": {
            "data": "CJ184",
            "source": {
                "CJ184": {
                    "table_name": "financial_metrics_data",
                    "column_name": "financial_type_id",
                    "value": 11
                }
            }
        },
        "is_adjustible": True
    },
    "R15": {
        "type": "financial_metric",
        "id": 48,
        "formula": {
            "data": "-1*AD7",
            "source": {
                "AD7": {
                    "table_name": "financial_metrics_data",
                    "column_name": "financial_type_id",
                    "value": 1
                }
            }
        },
        "is_adjustible": True
    },
    "R22": {
        "type": "financial_type",
        "id": 14,
        "formula": {
            "data": "(R7+R9+R15)+(R11/1_000_000)",
            "source": {
                "R11": {
                    "table_name": "financial_metrics_data",
                    "column_name": "financial_metric_id",
                    "value": 46
                }
            }
        },
        "is_adjustible": True
    },
    "R24": {
        "type": "financial_submetric",
        "id": 1,
        "formula": {
            "data": "Q48 * -1",
            "source": {
                "Q48": {
                    "table_name": "cashflow_data",
                    "entity_type": "subcategory",
                    "entity_id": "20"
                }
            }
        },
        "is_adjustible": True
    },
    "R26": {
        "type": "financial_submetric",
        "id": 2,
        "formula": {
            "data": "CJ51",
            "source": {
                "CJ51": {
                    "table_name": "financial_metrics_data",
                    "column_name": "financial_submetric_id",
                    "value": 21
                }
            }
        },
        "is_adjustible": True
    },
    "R30": {
        "type": "financial_metric",
        "id": 53,
        "formula": {
            "data": "R24+R26"
        },
        "is_adjustible": True
    },
    "R32": {
        "type": "financial_metric",
        "id": 54,
        "formula": {
            "data": "-J23",
            "source": {
                "J23": {
                    "table_name": "cashflow_data",
                    "entity_type": "category",
                    "entity_id": "6"
                }
            }
        },
        "is_adjustible": True
    },
    "R35": {
        "type": "financial_type",
        "id": 15,
        "formula": {
            "data": "(R22+R30+R32)+(R33/1_000_000)",
            "source": {
                "R33": {
                    "table_name": "financial_metrics_data",
                    "column_name": "financial_metric_id",
                    "value": 55
                }
            }
        },
        "is_adjustible": True
    },
    "R37": {
        "type": "financial_metric",
        "id": 56,
        "formula": {
            "data": "-1*Q77",
            "source": {
                "Q77": {
                    "table_name": "cashflow_data",
                    "entity_type": "section",
                    "entity_id": "14"
                }
            }
        },
        "is_adjustible": True
    },
    "R38": {    
        "type": "financial_metric",
        "id": 57,
        "formula": {
            "data": "Q70",
            "source": {
                "Q70": {
                    "table_name": "cashflow_data",
                    "entity_type": "section",
                    "entity_id": "13"
                }
            }
        },
        "is_adjustible": True
    },
    "R39": {
        "type": "financial_type",
        "id": 16,
        "formula": {
            "data": "R37+R38"
        },
        "is_adjustible": True
    }
}
