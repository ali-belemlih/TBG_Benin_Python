REEL_DATA_MAPPING = {
    "R30": {
        "type": "financial_submetric",
        "id": 83,
        "formula": {
            "data": "D30",
            "source": {
                "D30":{
                    "table_name": "financial_cumulative_data",
                    "column_name": "financial_submetric_id",
                    "value": 83
                }
            }
        }
    },
    "R33": {
        "type": "financial_submetric",
        "id": 84,
        "formula": {
            "data": "D33",
            "source": {
                "D33":{
                    "table_name": "financial_cumulative_data",
                    "column_name": "financial_submetric_id",
                    "value": 84
                }
            }
        }
    },
    "R35": {
        "type": "financial_submetric",
        "id": 86,
        "formula": {
            "data": "D35",
            "source": {
                "D35":{
                    "table_name": "financial_cumulative_data",
                    "column_name": "financial_submetric_id",
                    "value": 86
                }
            }
        }
    },
    "R41": {
        "type": "financial_submetric",
        "id": 88,
        "formula": {
            "data": "D41",
            "source": {
                "D41":{
                    "table_name": "financial_cumulative_data",
                    "column_name": "financial_submetric_id",
                    "value": 88
                }
            }
        }
    },
    "R42": {
        "type": "financial_submetric",
        "id": 89,
        "formula": {
            "data": "D42",
            "source": {
                "D42":{
                    "table_name": "financial_cumulative_data",
                    "column_name": "financial_submetric_id",
                    "value": 89
                }
            }
        }
    },
    "R45": {
        "type": "financial_submetric",
        "id": 91,
        "formula": {
            "data": "D45+1",
            "source": {
                "D45":{
                    "table_name": "financial_cumulative_data",
                    "column_name": "financial_submetric_id",
                    "value": 91
                }
            }
        }
    },
    "R20": {
        "type": "financial_submetric",
        "id": 78,
        "formula": {
            "data": "R35",
            "source": {
                "R35": {
                    "table_name": "financial_metrics_data",
                    "column_name": "financial_submetric_id",
                    "value": 86
                }
            }
        }
    },
    "R15": {
        "type": "financial_metric",
        "id": 138,
        "formula": {
            "data": "R29+R40",
            "source": {
                "R29": {
                    "table_name": "financial_cumulative_data",
                    "column_name": "financial_metric_id",
                    "value": 141
                },
                "R40": {
                    "table_name": "financial_cumulative_data",
                    "column_name": "financial_metric_id",
                    "value": 143
                }
            }
        }
    },
    "R16": {
        "type": "financial_submetric",
        "id": 74,
        "formula": {
            "data": "SUM(R30,R41)",
            "source": {
                "R30": {
                    "table_name": "financial_metrics_data",
                    "column_name": "financial_submetric_id",
                    "value": 83
                },
                "R41": {
                    "table_name": "financial_metrics_data",
                    "column_name": "financial_submetric_id",
                    "value": 88
                }
            }
        }
    },
    "R17": {
        "type": "financial_submetric",
        "id": 75,
        "formula": {
            "data": "SUM(R33,R42)",
            "source": {
                "R33": {
                    "table_name": "financial_metrics_data",
                    "column_name": "financial_submetric_id",
                    "value": 84
                },
                "R42": {
                    "table_name": "financial_metrics_data",
                    "column_name": "financial_submetric_id",
                    "value": 89
                }
            }
        }
    },
    "R21": {
        "type": "financial_submetric",
        "id": 80,
        "formula": {
            "data": "SUM(R33,R42)",
            "source": {
                "R33": {
                    "table_name": "financial_metrics_data",
                    "column_name": "financial_submetric_id",
                    "value": 84
                },
                "R42": {
                    "table_name": "financial_metrics_data",
                    "column_name": "financial_submetric_id",
                    "value": 89
                }
            }
        }
    },
    "R19": {
        "type": "financial_submetric",
        "id": 77,
        "formula": {
            "data": "R45",
            "source": {
                "R45": {
                    "table_name": "financial_metrics_data",
                    "column_name": "financial_submetric_id",
                    "value": 91
                }
            }
        }
    },
    "R36": {
        "type": "financial_metric",
        "id": 142,
        "formula": {
            "data": "R29+R35",
            "source": {
                "R29": {
                    "table_name": "financial_metrics_data",
                    "column_name": "financial_metric_id",
                    "value": 141
                },
                "R35": {
                    "table_name": "financial_metrics_data",
                    "column_name": "financial_submetric_id",
                    "value": 86
                }
            }
        }
    },
    "R37": {
        "type": "financial_submetric",
        "id": 87,
        "formula": {
            "data": "(R29+R36)/2",
            "source": {
                "R29": {
                    "table_name": "financial_metrics_data",
                    "column_name": "financial_metric_id",
                    "value": 141
                },
                "R36": {
                    "table_name": "financial_metrics_data",
                    "column_name": "financial_metric_id",
                    "value": 142
                }
            }
        }
    },
    "R34": {
        "type": "financial_submetric",
        "id": 85,
        "formula": {
            "data": "(((-R33/R37)/month)*12)",
            "source": {
                "R33": {
                    "table_name": "financial_metrics_data",
                    "column_name": "financial_submetric_id",
                    "value": 84
                },
                "R37": {
                    "table_name": "financial_metrics_data",
                    "column_name": "financial_submetric_id",
                    "value": 87
                }
            }
        }
    },
    "R22": {
        "type": "financial_submetric",
        "id": 80,
        "formula": {
            "data": "R34",
            "source": {
                "R34": {
                    "table_name": "financial_metrics_data",
                    "column_name": "financial_submetric_id",
                    "value": 85
                }
            }
        }
    },
    "R46": {
        "type": "financial_metric",
        "id": 144,
        "formula": {
            "data": "R40+R45",
            "source": {
                "R40": {
                    "table_name": "financial_metrics_data",
                    "column_name": "financial_metric_id",
                    "value": 143
                },
                "R45": {
                    "table_name": "financial_metrics_data",
                    "column_name": "financial_submetric_id",
                    "value": 91
                }
            }
        }
    },
    "R47": {
        "type": "financial_submetric",
        "id": 92,
        "formula": {
            "data": "(R40+R46)/2",
            "source": {
                "R40": {
                    "table_name": "financial_metrics_data",
                    "column_name": "financial_metric_id",
                    "value": 143
                },
                "R46": {
                    "table_name": "financial_metrics_data",
                    "column_name": "financial_metric_id",
                    "value": 144
                }
            }
        }
    },
    "R44": {
        "type": "financial_submetric",
        "id": 90,
        "formula": {
            "data": "(((-R42/R47) /month) * 12)",
            "source": {
                "R42": {
                    "table_name": "financial_metrics_data",
                    "column_name": "financial_submetric_id",
                    "value": 89
                },
                "R47": {
                    "table_name": "financial_metrics_data",
                    "column_name": "financial_submetric_id",
                    "value": 92
                }
            }
        }
    },
    "R18": {
        "type": "financial_submetric",
        "id": 76,
        "formula": {
            "data": "R44",
            "source": {
                "R44": {
                    "table_name": "financial_metrics_data",
                    "column_name": "financial_submetric_id",
                    "value": 90
                }
            }
        }
    },
    "R7": {
        "type": "financial_type",
        "id": 47,
        "formula": {
            "data": "R36+R46",
            "source": {
                "R36": {
                    "table_name": "financial_metrics_data",
                    "column_name": "financial_metric_id",
                    "value": 142
                },
                "R46": {
                    "table_name": "financial_metrics_data",
                    "column_name": "financial_metric_id",
                    "value": 144
                }
            }
        }
    },
    "R23": {
        "type": "financial_metric",
        "id": 139,
        "formula": {
            "data": "SUM(R36,R46)",
            "source": {
                "R36": {
                    "table_name": "financial_metrics_data",
                    "column_name": "financial_metric_id",
                    "value": 142
                },
                "R46": {
                    "table_name": "financial_metrics_data",
                    "column_name": "financial_metric_id",
                    "value": 144
                }
            }
        }
    },
    "R25": {
        "type": "financial_metric",
        "id": 140,
        "formula": {
            "data": "SUM(R36,R46)",
            "source": {
                "R36": {
                    "table_name": "financial_metrics_data",
                    "column_name": "financial_metric_id",
                    "value": 142
                },
                "R46": {
                    "table_name": "financial_metrics_data",
                    "column_name": "financial_metric_id",
                    "value": 144
                }
            }
        }
    },
    "R24": {
        "type": "financial_submetric",
        "id": 81,
        "formula": {
            "data": "SUM(R15,R23)/2",
            "source": {
                "R15": {
                    "table_name": "financial_metrics_data",
                    "column_name": "financial_metric_id",
                    "value": 138
                },
                "R23": {
                    "table_name": "financial_metrics_data",
                    "column_name": "financial_metric_id",
                    "value": 139
                }
            }
        }
    },
    "R26": {
        "type": "financial_submetric",
        "id": 82,
        "formula": {
            "data": "R24",
            "source": {
                "R24": {
                    "table_name": "financial_metrics_data",
                    "column_name": "financial_submetric_id",
                    "value": 81
                }
            }
        }
    }
}

LAST_YEAR_REEL_MAPPING = {
    "R30": {
        "type": "financial_submetric",
        "id": 83,
        "formula": {
            "data": "G30",
            "source": {
                "G30":{
                    "table_name": "financial_cumulative_data",
                    "column_name": "financial_submetric_id",
                    "value": 83
                }
            }
        }
    },
    "R33": {
        "type": "financial_submetric",
        "id": 84,
        "formula": {
            "data": "G33",
            "source": {
                "G33":{
                    "table_name": "financial_cumulative_data",
                    "column_name": "financial_submetric_id",
                    "value": 84
                }
            }
        }
    },
    "R35": {
        "type": "financial_submetric",
        "id": 86,
        "formula": {
            "data": "G35",
            "source": {
                "G35":{
                    "table_name": "financial_cumulative_data",
                    "column_name": "financial_submetric_id",
                    "value": 86
                }
            }
        }
    },
    "R41": {
        "type": "financial_submetric",
        "id": 88,
        "formula": {
            "data": "G41",
            "source": {
                "G41":{
                    "table_name": "financial_cumulative_data",
                    "column_name": "financial_submetric_id",
                    "value": 88
                }
            }
        }
    },
    "R42": {
        "type": "financial_submetric",
        "id": 89,
        "formula": {
            "data": "G42",
            "source": {
                "G42":{
                    "table_name": "financial_cumulative_data",
                    "column_name": "financial_submetric_id",
                    "value": 89
                }
            }
        }
    },
    "R45": {
        "type": "financial_submetric",
        "id": 91,
        "formula": {
            "data": "G45",
            "source": {
                "G45":{
                    "table_name": "financial_cumulative_data",
                    "column_name": "financial_submetric_id",
                    "value": 91
                }
            }
        }
    },
    "R20": {
        "type": "financial_submetric",
        "id": 78,
        "formula": {
            "data": "R35",
            "source": {
                "R35": {
                    "table_name": "financial_metrics_data",
                    "column_name": "financial_submetric_id",
                    "value": 86
                }
            }
        }
    },
    "R15": {
        "type": "financial_metric",
        "id": 138,
        "formula": {
            "data": "R29+R40",
            "source": {
                "R29": {
                    "table_name": "financial_cumulative_data",
                    "column_name": "financial_metric_id",
                    "value": 141
                },
                "R40": {
                    "table_name": "financial_cumulative_data",
                    "column_name": "financial_metric_id",
                    "value": 143
                }
            }
        }
    },
    "R16": {
        "type": "financial_submetric",
        "id": 74,
        "formula": {
            "data": "SUM(R30,R41)",
            "source": {
                "R30": {
                    "table_name": "financial_metrics_data",
                    "column_name": "financial_submetric_id",
                    "value": 83
                },
                "R41": {
                    "table_name": "financial_metrics_data",
                    "column_name": "financial_submetric_id",
                    "value": 88
                }
            }
        }
    },
    "R17": {
        "type": "financial_submetric",
        "id": 75,
        "formula": {
            "data": "SUM(R33,R42)",
            "source": {
                "R33": {
                    "table_name": "financial_metrics_data",
                    "column_name": "financial_submetric_id",
                    "value": 84
                },
                "R42": {
                    "table_name": "financial_metrics_data",
                    "column_name": "financial_submetric_id",
                    "value": 89
                }
            }
        }
    },
    "R21": {
        "type": "financial_submetric",
        "id": 79,
        "formula": {
            "data": "SUM(R33,R42)",
            "source": {
                "R33": {
                    "table_name": "financial_metrics_data",
                    "column_name": "financial_submetric_id",
                    "value": 84
                },
                "R42": {
                    "table_name": "financial_metrics_data",
                    "column_name": "financial_submetric_id",
                    "value": 89
                }
            }
        }
    },
    "R19": {
        "type": "financial_submetric",
        "id": 77,
        "formula": {
            "data": "R45",
            "source": {
                "R45": {
                    "table_name": "financial_metrics_data",
                    "column_name": "financial_submetric_id",
                    "value": 91
                }
            }
        }
    },
    "R36": {
        "type": "financial_metric",
        "id": 142,
        "formula": {
            "data": "R29+R35",
            "source": {
                "R29": {
                    "table_name": "financial_metrics_data",
                    "column_name": "financial_metric_id",
                    "value": 141
                },
                "R35": {
                    "table_name": "financial_metrics_data",
                    "column_name": "financial_submetric_id",
                    "value": 86
                }
            }
        }
    },
    "R37": {
        "type": "financial_submetric",
        "id": 87,
        "formula": {
            "data": "(R29+R36)/2",
            "source": {
                "R29": {
                    "table_name": "financial_metrics_data",
                    "column_name": "financial_metric_id",
                    "value": 141
                },
                "R36": {
                    "table_name": "financial_metrics_data",
                    "column_name": "financial_metric_id",
                    "value": 142
                }
            }
        }
    },
    "R34": {
        "type": "financial_submetric",
        "id": 85,
        "formula": {
            "data": "(((-R33/R37)/month)*12)",
            "source": {
                "R33": {
                    "table_name": "financial_cumulative_data",
                    "column_name": "financial_submetric_id",
                    "value": 84
                },
                "R37": {
                    "table_name": "financial_cumulative_data",
                    "column_name": "financial_submetric_id",
                    "value": 87
                }
            }
        }
    },
    "R22": {
        "type": "financial_submetric",
        "id": 80,
        "formula": {
            "data": "R34",
            "source": {
                "R34": {
                    "table_name": "financial_metrics_data",
                    "column_name": "financial_submetric_id",
                    "value": 85
                }
            }
        }
    },
    "R46": {
        "type": "financial_metric",
        "id": 144,
        "formula": {
            "data": "R40+R45",
            "source": {
                "R40": {
                    "table_name": "financial_metrics_data",
                    "column_name": "financial_metric_id",
                    "value": 143
                },
                "R45": {
                    "table_name": "financial_metrics_data",
                    "column_name": "financial_submetric_id",
                    "value": 91
                }
            }
        }
    },
    "R47": {
        "type": "financial_submetric",
        "id": 92,
        "formula": {
            "data": "(R40+R46)/2",
            "source": {
                "R40": {
                    "table_name": "financial_metrics_data",
                    "column_name": "financial_metric_id",
                    "value": 143
                },
                "R46": {
                    "table_name": "financial_metrics_data",
                    "column_name": "financial_metric_id",
                    "value": 144
                }
            }
        }
    },
    "R44": {
        "type": "financial_submetric",
        "id": 90,
        "formula": {
            "data": "(((-R42/R47)/month) * 12)",
            "source": {
                "R42": {
                    "table_name": "financial_cumulative_data",
                    "column_name": "financial_submetric_id",
                    "value": 89
                },
                "R47": {
                    "table_name": "financial_cumulative_data",
                    "column_name": "financial_submetric_id",
                    "value": 92
                }
            }
        }
    },
    "R18": {
        "type": "financial_submetric",
        "id": 76,
        "formula": {
            "data": "R44",
            "source": {
                "R44": {
                    "table_name": "financial_metrics_data",
                    "column_name": "financial_submetric_id",
                    "value": 90
                }
            }
        }
    },
    "R7": {
        "type": "financial_type",
        "id": 47,
        "formula": {
            "data": "R36+R46",
            "source": {
                "R36": {
                    "table_name": "financial_cumulative_data",
                    "column_name": "financial_metric_id",
                    "value": 142
                },
                "R46": {
                    "table_name": "financial_cumulative_data",
                    "column_name": "financial_metric_id",
                    "value": 144
                }
            }
        }
    },
    "R23": {
        "type": "financial_metric",
        "id": 139,
        "formula": {
            "data": "SUM(R36,R46)",
            "source": {
                "R36": {
                    "table_name": "financial_metrics_data",
                    "column_name": "financial_metric_id",
                    "value": 142
                },
                "R46": {
                    "table_name": "financial_metrics_data",
                    "column_name": "financial_metric_id",
                    "value": 144
                }
            }
        }
    },
    "R25": {
        "type": "financial_metric",
        "id": 140,
        "formula": {
            "data": "SUM(R36,R46)",
            "source": {
                "R36": {
                    "table_name": "financial_metrics_data",
                    "column_name": "financial_metric_id",
                    "value": 142
                },
                "R46": {
                    "table_name": "financial_metrics_data",
                    "column_name": "financial_metric_id",
                    "value": 144
                }
            }
        }
    },
    "R24": {
        "type": "financial_submetric",
        "id": 81,
        "formula": {
            "data": "SUM(R15,R23)/2",
            "source": {
                "R15": {
                    "table_name": "financial_metrics_data",
                    "column_name": "financial_metric_id",
                    "value": 138
                },
                "R23": {
                    "table_name": "financial_metrics_data",
                    "column_name": "financial_metric_id",
                    "value": 139
                }
            }
        }
    },
    "R26": {
        "type": "financial_submetric",
        "id": 82,
        "formula": {
            "data": "R24",
            "source": {
                "R24": {
                    "table_name": "financial_metrics_data",
                    "column_name": "financial_submetric_id",
                    "value": 81
                }
            }
        }
    }
}

BUDGET_MAPPING = {
    "R30": {
        "type": "financial_submetric",
        "id": 83,
        "formula": {
            "data": "E30",
            "source": {
                "E30":{
                    "table_name": "financial_cumulative_data",
                    "column_name": "financial_submetric_id",
                    "value": 83
                }
            }
        }
    },
    "R33": {
        "type": "financial_submetric",
        "id": 84,
        "formula": {
            "data": "E33",
            "source": {
                "E33":{
                    "table_name": "financial_cumulative_data",
                    "column_name": "financial_submetric_id",
                    "value": 84
                }
            }
        }
    },
    "R35": {
        "type": "financial_submetric",
        "id": 86,
        "formula": {
            "data": "E35",
            "source": {
                "E35":{
                    "table_name": "financial_cumulative_data",
                    "column_name": "financial_submetric_id",
                    "value": 86
                }
            }
        }
    },
    "R41": {
        "type": "financial_submetric",
        "id": 88,
        "formula": {
            "data": "E41",
            "source": {
                "E41":{
                    "table_name": "financial_cumulative_data",
                    "column_name": "financial_submetric_id",
                    "value": 88
                }
            }
        }
    },
    "R42": {
        "type": "financial_submetric",
        "id": 89,
        "formula": {
            "data": "E42",
            "source": {
                "E42":{
                    "table_name": "financial_cumulative_data",
                    "column_name": "financial_submetric_id",
                    "value": 89
                }
            }
        }
    },
    "R45": {
        "type": "financial_submetric",
        "id": 91,
        "formula": {
            "data": "E45",
            "source": {
                "E45":{
                    "table_name": "financial_cumulative_data",
                    "column_name": "financial_submetric_id",
                    "value": 91
                }
            }
        }
    },
    "R20": {
        "type": "financial_submetric",
        "id": 78,
        "formula": {
            "data": "R35",
            "source": {
                "R35": {
                    "table_name": "financial_metrics_data",
                    "column_name": "financial_submetric_id",
                    "value": 86
                }
            }
        }
    },
    "R15": {
        "type": "financial_metric",
        "id": 138,
        "formula": {
            "data": "R29+R40",
            "source": {
                "R29": {
                    "table_name": "financial_cumulative_data",
                    "column_name": "financial_metric_id",
                    "value": 141
                },
                "R40": {
                    "table_name": "financial_cumulative_data",
                    "column_name": "financial_metric_id",
                    "value": 143
                }
            }
        }
    },
    "R16": {
        "type": "financial_submetric",
        "id": 74,
        "formula": {
            "data": "SUM(R30,R41)",
            "source": {
                "R30": {
                    "table_name": "financial_metrics_data",
                    "column_name": "financial_submetric_id",
                    "value": 83
                },
                "R41": {
                    "table_name": "financial_metrics_data",
                    "column_name": "financial_submetric_id",
                    "value": 88
                }
            }
        }
    },
    "R17": {
        "type": "financial_submetric",
        "id": 75,
        "formula": {
            "data": "SUM(R33,R42)",
            "source": {
                "R33": {
                    "table_name": "financial_metrics_data",
                    "column_name": "financial_submetric_id",
                    "value": 84
                },
                "R42": {
                    "table_name": "financial_metrics_data",
                    "column_name": "financial_submetric_id",
                    "value": 89
                }
            }
        }
    },
    "R21": {
        "type": "financial_submetric",
        "id": 79,
        "formula": {
            "data": "SUM(R33,R42)",
            "source": {
                "R33": {
                    "table_name": "financial_metrics_data",
                    "column_name": "financial_submetric_id",
                    "value": 84
                },
                "R42": {
                    "table_name": "financial_metrics_data",
                    "column_name": "financial_submetric_id",
                    "value": 89
                }
            }
        }
    },
    "R19": {
        "type": "financial_submetric",
        "id": 77,
        "formula": {
            "data": "R45",
            "source": {
                "R45": {
                    "table_name": "financial_metrics_data",
                    "column_name": "financial_submetric_id",
                    "value": 91
                }
            }
        }
    },
    "R36": {
        "type": "financial_metric",
        "id": 142,
        "formula": {
            "data": "R29+R35",
            "source": {
                "R29": {
                    "table_name": "financial_metrics_data",
                    "column_name": "financial_metric_id",
                    "value": 141
                },
                "R35": {
                    "table_name": "financial_metrics_data",
                    "column_name": "financial_submetric_id",
                    "value": 86
                }
            }
        }
    },
    "R37": {
        "type": "financial_submetric",
        "id": 87,
        "formula": {
            "data": "(R29+R36)/2",
            "source": {
                "R29": {
                    "table_name": "financial_metrics_data",
                    "column_name": "financial_metric_id",
                    "value": 141
                },
                "R36": {
                    "table_name": "financial_metrics_data",
                    "column_name": "financial_metric_id",
                    "value": 142
                }
            }
        }
    },
    "R34": {
        "type": "financial_submetric",
        "id": 85,
        "formula": {
            "data": "(((-R33/R37)/month)*12)",
            "source": {
                "R33": {
                    "table_name": "financial_metrics_data",
                    "column_name": "financial_submetric_id",
                    "value": 84
                },
                "R37": {
                    "table_name": "financial_metrics_data",
                    "column_name": "financial_submetric_id",
                    "value": 87
                }
            }
        }
    },
    "R22": {
        "type": "financial_submetric",
        "id": 80,
        "formula": {
            "data": "R34",
            "source": {
                "R34": {
                    "table_name": "financial_metrics_data",
                    "column_name": "financial_submetric_id",
                    "value": 85
                }
            }
        }
    },
    "R46": {
        "type": "financial_metric",
        "id": 144,
        "formula": {
            "data": "R40+R45",
            "source": {
                "R40": {
                    "table_name": "financial_metrics_data",
                    "column_name": "financial_metric_id",
                    "value": 143
                },
                "R45": {
                    "table_name": "financial_metrics_data",
                    "column_name": "financial_submetric_id",
                    "value": 91
                }
            }
        }
    },
    "R47": {
        "type": "financial_submetric",
        "id": 92,
        "formula": {
            "data": "(R40+R46)/2",
            "source": {
                "R40": {
                    "table_name": "financial_metrics_data",
                    "column_name": "financial_metric_id",
                    "value": 143
                },
                "R46": {
                    "table_name": "financial_metrics_data",
                    "column_name": "financial_metric_id",
                    "value": 144
                }
            }
        }
    },
    "R44": {
        "type": "financial_submetric",
        "id": 90,
        "formula": {
            "data": "(((-R42/R47)/month) * 12)",
            "source": {
                "R42": {
                    "table_name": "financial_metrics_data",
                    "column_name": "financial_submetric_id",
                    "value": 89
                },
                "R47": {
                    "table_name": "financial_metrics_data",
                    "column_name": "financial_submetric_id",
                    "value": 92
                }
            }
        }
    },
    "R18": {
        "type": "financial_submetric",
        "id": 76,
        "formula": {
            "data": "R44",
            "source": {
                "R44": {
                    "table_name": "financial_metrics_data",
                    "column_name": "financial_submetric_id",
                    "value": 90
                }
            }
        }
    },
    "R7": {
        "type": "financial_type",
        "id": 47,
        "formula": {
            "data": "R36+R46",
            "source": {
                "R36": {
                    "table_name": "financial_cumulative_data",
                    "column_name": "financial_metric_id",
                    "value": 142
                },
                "R46": {
                    "table_name": "financial_cumulative_data",
                    "column_name": "financial_metric_id",
                    "value": 144
                }
            }
        }
    },
    "R23": {
        "type": "financial_metric",
        "id": 139,
        "formula": {
            "data": "SUM(R36,R46)",
            "source": {
                "R36": {
                    "table_name": "financial_metrics_data",
                    "column_name": "financial_metric_id",
                    "value": 142
                },
                "R46": {
                    "table_name": "financial_metrics_data",
                    "column_name": "financial_metric_id",
                    "value": 144
                }
            }
        }
    },
    "R25": {
        "type": "financial_metric",
        "id": 140,
        "formula": {
            "data": "SUM(R36,R46)",
            "source": {
                "R36": {
                    "table_name": "financial_metrics_data",
                    "column_name": "financial_metric_id",
                    "value": 142
                },
                "R46": {
                    "table_name": "financial_metrics_data",
                    "column_name": "financial_metric_id",
                    "value": 144
                }
            }
        }
    },
    "R24": {
        "type": "financial_submetric",
        "id": 81,
        "formula": {
            "data": "SUM(R15,R23)/2",
            "source": {
                "R15": {
                    "table_name": "financial_cumulative_data",
                    "column_name": "financial_metric_id",
                    "value": 138
                },
                "R23": {
                    "table_name": "financial_cumulative_data",
                    "column_name": "financial_metric_id",
                    "value": 139
                }
            }
        }
    },
    "R26": {
        "type": "financial_submetric",
        "id": 82,
        "formula": {
            "data": "R24",
            "source": {
                "R24": {
                    "table_name": "financial_metrics_data",
                    "column_name": "financial_submetric_id",
                    "value": 81
                }
            }
        }
    }
}

ACTUAL1_MAPPING = {
    "R30": {
        "type": "financial_submetric",
        "id": 83,
        "formula": {
            "data": "E30",
            "source": {
                "E30":{
                    "table_name": "financial_cumulative_data",
                    "column_name": "financial_submetric_id",
                    "value": 83
                }
            }
        }
    },
    "R33": {
        "type": "financial_submetric",
        "id": 84,
        "formula": {
            "data": "E33",
            "source": {
                "E33":{
                    "table_name": "financial_cumulative_data",
                    "column_name": "financial_submetric_id",
                    "value": 84
                }
            }
        }
    },
    "R35": {
        "type": "financial_submetric",
        "id": 86,
        "formula": {
            "data": "R30+R33",
            "source": {
                "E35":{
                    "table_name": "financial_cumulative_data",
                    "column_name": "financial_submetric_id",
                    "value": 86
                }
            }
        }
    },
    "R41": {
        "type": "financial_submetric",
        "id": 88,
        "formula": {
            "data": "E41",
            "source": {
                "E41":{
                    "table_name": "financial_cumulative_data",
                    "column_name": "financial_submetric_id",
                    "value": 88
                }
            }
        }
    },
    "R42": {
        "type": "financial_submetric",
        "id": 89,
        "formula": {
            "data": "E42",
            "source": {
                "E42":{
                    "table_name": "financial_cumulative_data",
                    "column_name": "financial_submetric_id",
                    "value": 89
                }
            }
        }
    },
    "R45": {
        "type": "financial_submetric",
        "id": 91,
        "formula": {
            "data": "E45",
            "source": {
                "E45":{
                    "table_name": "financial_cumulative_data",
                    "column_name": "financial_submetric_id",
                    "value": 91
                }
            }
        }
    },
    "R20": {
        "type": "financial_submetric",
        "id": 78,
        "formula": {
            "data": "R35",
            "source": {
                "R35": {
                    "table_name": "financial_metrics_data",
                    "column_name": "financial_submetric_id",
                    "value": 86
                }
            }
        }
    },
    "R15": {
        "type": "financial_metric",
        "id": 138,
        "formula": {
            "data": "R29+R40",
            "source": {
                "R29": {
                    "table_name": "financial_cumulative_data",
                    "column_name": "financial_metric_id",
                    "value": 141
                },
                "R40": {
                    "table_name": "financial_cumulative_data",
                    "column_name": "financial_metric_id",
                    "value": 143
                }
            }
        }
    },
    "R16": {
        "type": "financial_submetric",
        "id": 74,
        "formula": {
            "data": "SUM(R30,R41)",
            "source": {
                "R30": {
                    "table_name": "financial_metrics_data",
                    "column_name": "financial_submetric_id",
                    "value": 83
                },
                "R41": {
                    "table_name": "financial_metrics_data",
                    "column_name": "financial_submetric_id",
                    "value": 88
                }
            }
        }
    },
    "R17": {
        "type": "financial_submetric",
        "id": 75,
        "formula": {
            "data": "SUM(R33,R42)",
            "source": {
                "R33": {
                    "table_name": "financial_metrics_data",
                    "column_name": "financial_submetric_id",
                    "value": 84
                },
                "R42": {
                    "table_name": "financial_metrics_data",
                    "column_name": "financial_submetric_id",
                    "value": 89
                }
            }
        }
    },
    "R21": {
        "type": "financial_submetric",
        "id": 79,
        "formula": {
            "data": "SUM(R33,R42)",
            "source": {
                "R33": {
                    "table_name": "financial_metrics_data",
                    "column_name": "financial_submetric_id",
                    "value": 84
                },
                "R42": {
                    "table_name": "financial_metrics_data",
                    "column_name": "financial_submetric_id",
                    "value": 89
                }
            }
        }
    },
    "R19": {
        "type": "financial_submetric",
        "id": 77,
        "formula": {
            "data": "R45",
            "source": {
                "R45": {
                    "table_name": "financial_metrics_data",
                    "column_name": "financial_submetric_id",
                    "value": 91
                }
            }
        }
    },
    "R36": {
        "type": "financial_metric",
        "id": 142,
        "formula": {
            "data": "R29+R35",
            "source": {
                "R29": {
                    "table_name": "financial_metrics_data",
                    "column_name": "financial_metric_id",
                    "value": 141
                },
                "R35": {
                    "table_name": "financial_metrics_data",
                    "column_name": "financial_submetric_id",
                    "value": 86
                }
            }
        }
    },
    "R37": {
        "type": "financial_submetric",
        "id": 87,
        "formula": {
            "data": "(R29+R36)/2",
            "source": {
                "R29": {
                    "table_name": "financial_metrics_data",
                    "column_name": "financial_metric_id",
                    "value": 141
                },
                "R36": {
                    "table_name": "financial_metrics_data",
                    "column_name": "financial_metric_id",
                    "value": 142
                }
            }
        }
    },
    "R34": {
        "type": "financial_submetric",
        "id": 85,
        "formula": {
            "data": "(((-R33/R37)/month)*12)",
            "source": {
                "R33": {
                    "table_name": "financial_metrics_data",
                    "column_name": "financial_submetric_id",
                    "value": 84
                },
                "R37": {
                    "table_name": "financial_metrics_data",
                    "column_name": "financial_submetric_id",
                    "value": 87
                }
            }
        }
    },
    "R22": {
        "type": "financial_submetric",
        "id": 80,
        "formula": {
            "data": "R34",
            "source": {
                "R34": {
                    "table_name": "financial_metrics_data",
                    "column_name": "financial_submetric_id",
                    "value": 85
                }
            }
        }
    },
    "R46": {
        "type": "financial_metric",
        "id": 144,
        "formula": {
            "data": "R40+R45",
            "source": {
                "R40": {
                    "table_name": "financial_metrics_data",
                    "column_name": "financial_metric_id",
                    "value": 143
                },
                "R45": {
                    "table_name": "financial_metrics_data",
                    "column_name": "financial_submetric_id",
                    "value": 91
                }
            }
        }
    },
    "R47": {
        "type": "financial_submetric",
        "id": 92,
        "formula": {
            "data": "(R40+R46)/2",
            "source": {
                "R40": {
                    "table_name": "financial_metrics_data",
                    "column_name": "financial_metric_id",
                    "value": 143
                },
                "R46": {
                    "table_name": "financial_metrics_data",
                    "column_name": "financial_metric_id",
                    "value": 144
                }
            }
        }
    },
    "R44": {
        "type": "financial_submetric",
        "id": 90,
        "formula": {
            "data": "(((-R42/R47)/month) * 12)",
            "source": {
                "R42": {
                    "table_name": "financial_metrics_data",
                    "column_name": "financial_submetric_id",
                    "value": 89
                },
                "R47": {
                    "table_name": "financial_metrics_data",
                    "column_name": "financial_submetric_id",
                    "value": 92
                }
            }
        }
    },
    "R18": {
        "type": "financial_submetric",
        "id": 76,
        "formula": {
            "data": "R44",
            "source": {
                "R44": {
                    "table_name": "financial_metrics_data",
                    "column_name": "financial_submetric_id",
                    "value": 90
                }
            }
        }
    },
    "R7": {
        "type": "financial_type",
        "id": 47,
        "formula": {
            "data": "R36+R46",
            "source": {
                "R36": {
                    "table_name": "financial_cumulative_data",
                    "column_name": "financial_metric_id",
                    "value": 142
                },
                "R46": {
                    "table_name": "financial_cumulative_data",
                    "column_name": "financial_metric_id",
                    "value": 144
                }
            }
        }
    },
    "R23": {
        "type": "financial_metric",
        "id": 139,
        "formula": {
            "data": "SUM(R36,R46)",
            "source": {
                "R36": {
                    "table_name": "financial_metrics_data",
                    "column_name": "financial_metric_id",
                    "value": 142
                },
                "R46": {
                    "table_name": "financial_metrics_data",
                    "column_name": "financial_metric_id",
                    "value": 144
                }
            }
        }
    },
    "R25": {
        "type": "financial_metric",
        "id": 140,
        "formula": {
            "data": "SUM(R36,R46)",
            "source": {
                "R36": {
                    "table_name": "financial_metrics_data",
                    "column_name": "financial_metric_id",
                    "value": 142
                },
                "R46": {
                    "table_name": "financial_metrics_data",
                    "column_name": "financial_metric_id",
                    "value": 144
                }
            }
        }
    },
    "R24": {
        "type": "financial_submetric",
        "id": 81,
        "formula": {
            "data": "SUM(R15,R23)/2",
            "source": {
                "R15": {
                    "table_name": "financial_cumulative_data",
                    "column_name": "financial_metric_id",
                    "value": 138
                },
                "R23": {
                    "table_name": "financial_cumulative_data",
                    "column_name": "financial_metric_id",
                    "value": 139
                }
            }
        }
    },
    "R26": {
        "type": "financial_submetric",
        "id": 82,
        "formula": {
            "data": "R24",
            "source": {
                "R24": {
                    "table_name": "financial_metrics_data",
                    "column_name": "financial_submetric_id",
                    "value": 81
                }
            }
        }
    }
}