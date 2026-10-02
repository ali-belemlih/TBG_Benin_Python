monthly_budget_mapping = {
    "R15": {
        "type": "financial_metric",
        "id": 138,
        "formula": {
            "data": "K29+K40",
            "source": {
                "K29": {
                    "table_name": "financial_metrics_data",
                    "column_name": "financial_metric_id",
                    "value": 141
                },
                "K40": {
                    "table_name": "financial_metrics_data",
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
            "data": "SUM(K30,K41)",
            "source": {
                "K30": {
                    "table_name": "financial_metrics_data",
                    "column_name": "financial_submetric_id",
                    "value": 83
                },
                "K41": {
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
            "data": "SUM(K33,K42)",
            "source": {
                "K33": {
                    "table_name": "financial_metrics_data",
                    "column_name": "financial_submetric_id",
                    "value": 84
                },
                "K42": {
                    "table_name": "financial_metrics_data",
                    "column_name": "financial_submetric_id",
                    "value": 89
                }
            }
        }
    },
    "R18": {
        "type": "financial_submetric",
        "id": 76,
        "formula": {
            "data": "K44",
            "source": {
                "K44": {
                    "table_name": "financial_metrics_data",
                    "column_name": "financial_submetric_id",
                    "value": 90
                }
            }
        }
    },
    "R19": {
        "type": "financial_submetric",
        "id": 77,
        "formula": {
            "data": "K45",
            "source": {
                "K45": {
                    "table_name": "financial_metrics_data",
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
            "data": "K35",
            "source": {
                "K35": {
                    "table_name": "financial_metrics_data",
                    "column_name": "financial_submetric_id",
                    "value": 86
                }
            }
        }
    },
    "R21": {
        "type": "financial_submetric",
        "id": 79,
        "formula": {
            "data": "SUM(K33,K42)",
            "source": {
                "K33": {
                    "table_name": "financial_metrics_data",
                    "column_name": "financial_submetric_id",
                    "value": 84
                },
                "K42": {
                    "table_name": "financial_metrics_data",
                    "column_name": "financial_submetric_id",
                    "value": 89
                }
            }
        }
    },
    "R22": {
        "type": "financial_submetric",
        "id": 80,
        "formula": {
            "data": "K34",
            "source": {
                "K34": {
                    "table_name": "financial_metrics_data",
                    "column_name": "financial_submetric_id",
                    "value": 85
                }
            }
        }
    },
    "R23": {
        "type": "financial_metric",
        "id": 139,
        "formula": {
            "data": "SUM(K36,K46)",
            "source": {
                "K36": {
                    "table_name": "financial_metrics_data",
                    "column_name": "financial_metric_id",
                    "value": 142
                },
                "K46": {
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
            "data": "(R15+R23)/2",
            "source": {
                "R15": {
                    "table_name": "financial_metrics_data",
                    "column_name": "financial_submetric_id",
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
    "R25": {
        "type": "financial_metric",
        "id": 140,
        "formula": {
            "data": "SUM(K36,K46)",
            "source": {
                "K36": {
                    "table_name": "financial_metrics_data",
                    "column_name": "financial_metric_id",
                    "value": 142
                },
                "K46": {
                    "table_name": "financial_metrics_data",
                    "column_name": "financial_metric_id",
                    "value": 144
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





annual_budget_mapping = {
    "R15": {
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
    "R16": {
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
    "R17": {
        "type": "financial_submetric",
        "id": 75,
        "formula": {
            "data": "R33+R42",
            "source": {
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
    "R18": {
        "type": "financial_submetric",
        "id": 76,
        "formula": {
            "data": "R44",
            "source": {
                "R44": {
                    "table_name": "financial_annual_data",
                    "column_name": "financial_submetric_id",
                    "value": 90
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
                    "table_name": "financial_annual_data",
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
                    "table_name": "financial_annual_data",
                    "column_name": "financial_submetric_id",
                    "value": 86
                }
            }
        }
    },
    "R21": {
        "type": "financial_submetric",
        "id": 79,
        "formula": {
            "data": "R33+R42",
            "source": {
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
    "R22": {
        "type": "financial_submetric",
        "id": 80,
        "formula": {
            "data": "R34",
            "source": {
                "R34": {
                    "table_name": "financial_annual_data",
                    "column_name": "financial_submetric_id",
                    "value": 85
                }
            }
        }
    },
    "R23": {
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
    "R24": {
        "type": "financial_submetric",
        "id": 81,
        "formula": {
            "data": "(R15+R23)/2",
            "source": {
                "R15": {
                    "table_name": "financial_annual_data",
                    "column_name": "financial_submetric_id",
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
    "R25": {
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
    "R26": {
        "type": "financial_submetric",
        "id": 82,
        "formula": {
            "data": "R24",
            "source": {
                "R24": {
                    "table_name": "financial_annual_data",
                    "column_name": "financial_submetric_id",
                    "value": 81
                }
            }
        }
    }
}
