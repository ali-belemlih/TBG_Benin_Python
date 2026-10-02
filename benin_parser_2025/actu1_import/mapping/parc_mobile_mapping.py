financial_type_row_mapping = {
    7: 47,
    11: 48,
    20: 49
}

financial_metric_row_mapping = {
    12: 141,
    17: 142,

    21: 143,
    26: 144
}

financial_submetric_row_mapping = {
    13: 83,
    14: 84,
    16: 85,
    15: 86,

    18: 87,

    22: 88,
    23: 89,
    24: 90,
    25: 91,

    27: 92
}


annual_actual_mapping = {
    "R45": {
        "type": "financial_submetric",
        "id": 91,
        "formula": {
            "data": "R41+R42",
            "source": {
                "R41": {
                    "table_name": "financial_annual_data",
                    "column_name": "financial_submetric_id",
                    "value": 88
                },
                "R42": {
                    "table_name": "financial_annual_data",
                    "column_name": "financial_submetric_id",
                    "value": 89
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
                    "table_name": "financial_annual_data",
                    "column_name": "financial_metric_id",
                    "value": 143
                },
                "R45": {
                    "table_name": "financial_annual_data",
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
                    "table_name": "financial_annual_data",
                    "column_name": "financial_metric_id",
                    "value": 143
                },
                "R46": {
                    "table_name": "financial_annual_data",
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
            "data": "(-R42/R47)",
            "source": {
                "R42": {
                    "table_name": "financial_annual_data",
                    "column_name": "financial_submetric_id",
                    "value": 89
                },
                "R47": {
                    "table_name": "financial_annual_data",
                    "column_name": "financial_submetric_id",
                    "value": 92
                }
            }
        }
    },
    'R16': {
        "type": "financial_submetric",
        "id": 74,
        "formula": {
            "data": "R30+R41",
            "source": {
                "R30": {
                    "table_name": "financial_annual_data",
                    "column_name": "financial_submetric_id",
                    "value": 83
                },
                "R41": {
                    "table_name": "financial_annual_data",
                    "column_name": "financial_submetric_id",
                    "value": 88
                }
            }
        }
    },
    'R17': {
        "type": "financial_submetric",
        "id": 75,
        "formula": {
            "data": "R33+R42",
            "source":{
                "R33": {
                    "table_name": "financial_annual_data",
                    "column_name": "financial_submetric_id",
                    "value": 84
                },
                "R42": {
                    "table_name": "financial_annual_data",
                    "column_name": "financial_submetric_id",
                    "value": 89
                }
            }
        }
    },
    'R21': {
        "type": "financial_submetric",
        "id": 79,
        "formula": {
            "data": "R33+R42",
            "source":{
                "R33": {
                    "table_name": "financial_annual_data",
                    "column_name": "financial_submetric_id",
                    "value": 84
                },
                "R42": {
                    "table_name": "financial_annual_data",
                    "column_name": "financial_submetric_id",
                    "value": 89
                }
            }
        }
    },
    'R20': {
        "type": "financial_submetric",
        "id": 78,
        "formula": {
            "data": "R35",
            "source":{
                "R35": {
                    "table_name": "financial_annual_data",
                    "column_name": "financial_submetric_id",
                    "value": 86
                }
            }

        }
    },
    'R19': {
        "type": "financial_submetric",
        "id": 77,
        "formula": {
            "data": "R45",
            "source": {
                "R45": {
                    "table_name": "financial_annual_data",
                    "column_name": "financial_submetric_id",
                    "value": 91
                }
            }
        }
    },
    'R15': {
        "type": "financial_metric",
        "id": 138,
        "formula": {
            "data": "R29+R40",
            "source": {
                "R29": {
                    "table_name": "financial_annual_data",
                    "column_name": "financial_metric_id",
                    "value": 141
                },
                "R40": {
                    "table_name": "financial_annual_data",
                    "column_name": "financial_metric_id",
                    "value": 143
                }
            }
        }
    },
    'R23': {
        "type": "financial_metric",
        "id": 139,
        "formula": {
            "data": "R36+R46",
            "source": {
                "R36": {
                    "table_name": "financial_annual_data",
                    "column_name": "financial_metric_id",
                    "value": 142
                },
                "R46": {
                    "table_name": "financial_annual_data",
                    "column_name": "financial_metric_id",
                    "value": 144
                }
            }
        }
    },
    'R25': {
        "type": "financial_metric",
        "id": 140,
        "formula": {
            "data": "R36+R46",
            "source": {
                "R36": {
                    "table_name": "financial_annual_data",
                    "column_name": "financial_metric_id",
                    "value": 142
                },
                "R46": {
                    "table_name": "financial_annual_data",
                    "column_name": "financial_metric_id",
                    "value": 144
                }
            }
        }
    },
    'R24': {
        "type": "financial_submetric",
        "id": 81,
        "formula": {
            "data": "SUM(R15,R23)/2",
            "source": {
                "R15": {
                    "table_name": "financial_annual_data",
                    "column_name": "financial_metric_id",
                    "value": 138
                },
                "R23": {
                    "table_name": "financial_annual_data",
                    "column_name": "financial_metric_id",
                    "value": 139
                }
            }

        }
    },
    'R26': {
        "type": "financial_submetric",
        "id": 82,
        "formula": {
            "data": "R24",
            "source": {
                "R24": {
                    "table_name": "financial_annual_data",
                    "column_name": 'financial_submetric_id',
                    "value": 81
                }
            }
        }
    },
    'R22': {
        "type": "financial_submetric",
        "id": 80,
        "formula": {
            "data": "R34",
            "source": {
                "R34": {
                    "table_name": "financial_annual_data",
                    "column_name": 'financial_submetric_id',
                    "value": 85
                }
            }
        }
    },
    'R18': {
        "type": "financial_submetric",
        "id": 76,
        "formula": {
            "data": "R44",
            "source": {
                "R44": {
                    "table_name": "financial_annual_data",
                    "column_name": 'financial_submetric_id',
                    "value": 90
                }
            }

        }
    }
}

monthly_actual_mapping = {
    "R45": {
        "type": "financial_submetric",
        "id": 91,
        "formula": {
            "data": "R41+R42",
            "source": {
                "R41": {
                    "table_name": "financial_metrics_data",
                    "column_name": "financial_submetric_id",
                    "value": 88
                },
                "R42": {
                    "table_name": "financial_metrics_data",
                    "column_name": "financial_submetric_id",
                    "value": 89
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
            "data": "((-R42/R47) * 12)",
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
    'R16': {
        "type": "financial_submetric",
        "id": 74,
        "formula": {
            "data": "R30+R41",
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
    'R17': {
        "type": "financial_submetric",
        "id": 75,
        "formula": {
            "data": "R33+R42",
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
    'R21': {
        "type": "financial_submetric",
        "id": 79,
        "formula": {
            "data": "R33+R42",
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
    'R20': {
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
    'R19': {
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
    'R15': {
        "type": "financial_metric",
        "id": 138,
        "formula": {
            "data": "R29+R40",
            "source": {
                "R29": {
                    "table_name": "financial_metrics_data",
                    "column_name": "financial_metric_id",
                    "value": 141
                },
                "R40": {
                    "table_name": "financial_metrics_data",
                    "column_name": "financial_metric_id",
                    "value": 143
                }
            }
        }
    },
    'R23': {
        "type": "financial_metric",
        "id": 139,
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
    'R25': {
        "type": "financial_metric",
        "id": 140,
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
    'R24': {
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
    'R26': {
        "type": "financial_submetric",
        "id": 82,
        "formula": {
            "data": "R24",
            "source": {
                "R24": {
                    "table_name": "financial_metrics_data",
                    "column_name": 'financial_submetric_id',
                    "value": 81
                }
            }
        }
    },
    'R22': {
        "type": "financial_submetric",
        "id": 80,
        "formula": {
            "data": "R34",
            "source": {
                "R34": {
                    "table_name": "financial_metrics_data",
                    "column_name": 'financial_submetric_id',
                    "value": 85
                }
            }
        }
    },
    'R18': {
        "type": "financial_submetric",
        "id": 76,
        "formula": {
            "data": "R44",
            "source": {
                "R44": {
                    "table_name": "financial_metrics_data",
                    "column_name": 'financial_submetric_id',
                    "value": 90
                }
            }

        }
    }
}

