financial_type_pnl_conso_cumul_mapping = {
    21: {
        "type": "financial_submetric",
        "id": 14,
        "formula": {
            "data": "CR20/CR7",
            "source": {
                "CR20" : {
                    "table_name": "financial_cumulative_data",
                    "column_name": "financial_metric_id",
                    "value": 81
                },
                "CR7" : {
                    "table_name": "financial_cumulative_data",
                    "column_name": "financial_type_id",
                    "value": 29
                }
            }
        }
    },
    32: {
        "type": "financial_submetric",
        "id": 18,
        "formula": {
            "data": "CR31/CR7",
            "source": {
                "CR31" : {
                    "table_name": "financial_cumulative_data",
                    "column_name": "financial_metric_id",
                    "value": 83
                },
                "CR7" : {
                    "table_name": "financial_cumulative_data",
                    "column_name": "financial_type_id",
                    "value": 29
                }
            }
        }
    },
    42: {
        "type": "financial_submetric",
        "id": 20,
        "formula": {
            "data": "CR41/CR7",
            "source": {
                "CR41" : {
                    "table_name": "financial_cumulative_data",
                    "column_name": "financial_metric_id",
                    "value": 85
                },
                "CR7" : {
                    "table_name": "financial_cumulative_data",
                    "column_name": "financial_type_id",
                    "value": 29
                }
            }
        }
    },
    56: {
        "type": "financial_metric",
        "id": 88,
        "formula": {
            "data": "CR54/CR7",
            "source": {
                "CR54" : {
                    "table_name": "financial_cumulative_data",
                    "column_name": "financial_type_id",
                    "value": 30
                },
                "CR7" : {
                    "table_name": "financial_cumulative_data",
                    "column_name": "financial_type_id",
                    "value": 29
                }
            }
        }
    },   
}


pnl_actual_cumul_mapping = {
    21: {
        "type": "financial_submetric",
        "id": 14,
        "formula": {
            "data": "CR20/CR7",
            "source": {
                "CR20" : {
                    "table_name": "financial_cumulative_data",
                    "column_name": "financial_metric_id",
                    "value": 81
                },
                "CR7" : {
                    "table_name": "financial_cumulative_data",
                    "column_name": "financial_type_id",
                    "value": 29
                }
            }
        }
    },
    56: {
        "type": "financial_metric",
        "id": 88,
        "formula": {
            "data": "CR54/CR7",
            "source": {
                "CR54" : {
                    "table_name": "financial_cumulative_data",
                    "column_name": "financial_type_id",
                    "value": 30
                },
                "CR7" : {
                    "table_name": "financial_cumulative_data",
                    "column_name": "financial_type_id",
                    "value": 29
                }
            }
        }
    },   
}