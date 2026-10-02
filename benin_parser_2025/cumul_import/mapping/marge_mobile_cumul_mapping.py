cumul_mobile_money_reel_mapping = {
    9 : {
        "type" : "financial_metric",
        "id" : 69,
        "formula" : {
            "data" : "(CR10/CR8)",
            "source" : {
                "CR10" : {
                    "table_name": "financial_cumulative_data",
                    "column_name": "financial_metric_id",
                    "value": 70
                },
                "CR8" : {
                    "table_name": "financial_cumulative_data",
                    "column_name": "financial_metric_id",
                    "value": 68
                }
            }
        }
    },
    41 : {
        "type" : "financial_metric",
        "id" : 74,
        "formula" : {
            "data" : "(CR42/CR40)",
            "source" : {
                "CR40" : {
                    "table_name": "financial_cumulative_data",
                    "column_name": "financial_metric_id",
                    "value": 73
                },
                "CR42" : {
                    "table_name": "financial_cumulative_data",
                    "column_name": "financial_metric_id",
                    "value": 75
                }
            }
        }
    },
    64 : {
        "type" : "financial_type",
        "id" : 28,
        "formula" : {
                    "data" : "(CR60/CR7)",
                    "source" : {
                        "CR60" : {
                            "table_name": "financial_cumulative_data",
                            "column_name": "financial_type_id",
                            "value": 27
                        },
                        "CR7" : {
                            "table_name": "financial_cumulative_data",
                            "column_name": "financial_type_id",
                            "value": 25
                        }
                    }
                }
    }
}