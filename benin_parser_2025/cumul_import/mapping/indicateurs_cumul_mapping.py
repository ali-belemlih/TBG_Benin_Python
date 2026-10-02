cumul_reel_mapping = {
    'L7': {
        "type": "financial_type",
        "id": 50,
        "formula": {
            "data": " ((((CR16 + CR149) / (CR37 + CR47)) * 1000000) /month)",
            "source": {
                "CR16": {
                    "table_name": "financial_cumulative_data",
                    "column_name": "financial_type_id",
                    "value": 20
                },
                "CR149": {
                    "table_name": "financial_cumulative_data",
                    "column_name": "financial_type_id",
                    "value": 21
                },
                "CR37": {
                    "table_name": "financial_cumulative_data",
                    "column_name": "financial_submetric_id",
                    "value": 87
                },
                "CR47": {
                    "table_name": "financial_cumulative_data",
                    "column_name": "financial_submetric_id",
                    "value": 92
                }
            }
        }
    },
    'L8': {
        "type": "financial_metric",
        "id": 145,
        "formula": {
            "data": "(((CR16/(CR37+CR47)) * 1000000 )/month)",
            "source": {
                "CR16": {
                    "table_name": "financial_cumulative_data",
                    "column_name": "financial_type_id",
                    "value": 20
                },
                "CR37": {
                    "table_name": "financial_cumulative_data",
                    "column_name": "financial_submetric_id",
                    "value": 87
                },
                "CR47": {
                    "table_name": "financial_cumulative_data",
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
            "data": "(((CR149 / (CR37 + CR47)) * 1000000)/month)",
            "source": {
                "CR149": {
                    "table_name": "financial_cumulative_data",
                    "column_name": "financial_type_id",
                    "value": 21
                },
                "CR37": {
                    "table_name": "financial_cumulative_data",
                    "column_name": "financial_submetric_id",
                    "value": 87
                },
                "CR47": {
                    "table_name": "financial_cumulative_data",
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
            "data": "(CR18+CR38)/(CR37/1000000)/month",
            "source": {
                "CR18": {
                    "table_name": "collapse_cumul_data",
                    "entity_type": "type",
                    "entity_id": 160,
                },
                "CR38": {
                    "table_name": "collapse_cumul_data",
                    "entity_type": "category",
                    "entity_id": 4
                },
                "CR37": {
                    "table_name": "financial_cumulative_data",
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
            "data": "SUM(CR151,CR156,CR161,CR166)/(CR37/1000000)/month",
            "source": {
                "CR151": {
                    # NOT PRESENT IN DB
                    "table_name": "collapse_cumul_data",
                    "entity_type": "type",
                    "entity_id": -1,
                },
                "CR156": {
                    # NOT PRESENT IN DB
                    "table_name": "collapse_cumul_data",
                    "entity_type": "type",
                    "entity_id": -1,
                },
                "CR161": {
                    # NOT PRESENT IN DB
                    "table_name": "collapse_cumul_data",
                    "entity_type": "type",
                    "entity_id": -1
                },
                "CR166": {
                    "table_name": "collapse_cumul_data",
                    "entity_type": "type",
                    "entity_id": 169,
                },
                "CR37": {
                    "table_name": "financial_cumulative_data",
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
            "source": {
                "CR12": {
                    "table_name": "financial_cumulative_data",
                    "column_name": "financial_metric_id",
                    "value": 147,
                },
                "CR13": {
                    "table_name": "financial_cumulative_data",
                    "column_name": "financial_metric_id",
                    "value": 148,
                }
            }
        }
    },
    'L16': {
        "type": "financial_metric",
        "id": 149,
        "formula": {
            "data": "SUM(L53,L78,L103,L128)/(L47/1000000)/month",
            "source": {
                "L53": {
                    "table_name": "financial_cumulative_data",
                    "column_name": "financial_metric_id",
                    "value": 59,
                },
                "L78": {
                    "table_name": "collapse_cumul_data",
                    "entity_type": "category",
                    "entity_id": 8
                },
                "L103": {
                    "table_name": "collapse_cumul_data",
                    "entity_type": "category",
                    "entity_id": 12
                },
                "L128": {
                    "table_name": "collapse_cumul_data",
                    "entity_type": "category",
                    "entity_id": 16
                },
                "L47": {
                    "table_name": "financial_cumulative_data",
                    "column_name": "financial_submetric_id",
                    "value": 92,
                },
            }
        }
    },
    'L17': {
        "type": "financial_metric",
        "id": 150,
        "formula": {
            "data": "(L152+L153+L154+L157+L158+L159+L162+L163+L164+L167+L168+L169)*1000000/L47",
            "source": {
                "L152": {
                    # HIDDEN RECORD
                    "table_name": "",
                    "column_name": "",
                    "value": -1,
                },
                "L153": {
                    # HIDDEN RECORD
                    "table_name": "",
                    "column_name": "",
                    "value": -1,
                },
                "L154": {
                    # HIDDEN RECORD
                    "table_name": "",
                    "column_name": "",
                    "value": -1,
                },
                "L157": {
                    # HIDDEN RECORD
                    "table_name": "",
                    "column_name": "",
                    "value": -1,
                },
                "L158": {
                    # HIDDEN RECORD
                    "table_name": "",
                    "column_name": "",
                    "value": -1,
                },
                "L159": {
                    # HIDDEN RECORD
                    "table_name": "",
                    "column_name": "",
                    "value": -1,
                },
                "L162": {
                    # NOT PRESENT IN DB
                    "table_name": "",
                    "column_name": "",
                    "value": -1
                },
                "L163": {
                    # NOT PRESENT IN DB
                    "column_name": "",
                    "value": -1
                },
                "L164": {
                    # NOT PRESENT IN DB
                    "table_name": "",
                    "column_name": "",
                    "value": -1
                },
                "L167": {
                    "table_name": "collapse_cumul_data",
                    "entity_type": "type",
                    "entity_id": 170
                },
                "L168": {
                    "table_name": "collapse_cumul_data",
                    "entity_type": "type",
                    "entity_id": 171,
                },
                "L169": {
                    "table_name": "collapse_cumul_data",
                    "entity_type": "type",
                    "entity_id": 172
                },
                "L47": {
                    "table_name": "financial_cumulative_data",
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
            "source": {
                "L16": {
                    "table_name": "financial_cumulative_data",
                    "column_name": "financial_metric_id",
                    "value": 149,
                },
                "L17": {
                    "table_name": "financial_cumulative_data",
                    "column_name": "financial_metric_id",
                    "value": 150,
                }
            }
        }
    },
    'L19': {
        "type": "financial_type",
        "id": 53,
        "formula": {
            "data": "(CR7+CR55)/(SUM(CR37,CR47)/1000000)/month",
            "source": {
                "CR7": {
                    "table_name": "financial_cumulative_data",
                    "column_name": "financial_type_id",
                    "value": 31
                },
                "CR55": {
                    "table_name": "financial_cumulative_data",
                    "column_name": "financial_type_id",
                    "value": 32
                },
                "CR37": {
                    "table_name": "financial_cumulative_data",
                    "column_name": "financial_submetric_id",
                    "value": 87
                },
                "CR47": {
                    "table_name": "financial_cumulative_data",
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
            "data": "CR7/(SUM(CR37,CR47)/1000000)/month",
            "source": {
                "CR7": {
                    "table_name": "financial_cumulative_data",
                    "column_name": "financial_type_id",
                    "value": 31
                },
                "CR37": {
                    "table_name": "financial_cumulative_data",
                    "column_name": "financial_submetric_id",
                    "value": 87
                },
                "CR47": {
                    "table_name": "financial_cumulative_data",
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
            "data": "CR9/(CR37/1000000)/month",
            "source": {
                "CR9": {
                    "table_name": "financial_cumulative_data",
                    "column_name": "financial_metric_id",
                    "value": 89
                },
                "CR37": {
                    "table_name": "financial_cumulative_data",
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
            "data": "(((L18 / CR47) * 1000000)/month)",
            "source": {
                "L18": {
                    "table_name": "financial_cumulative_data",
                    "column_name": "financial_metric_id",
                    "value": 90
                },
                "CR47": {
                    "table_name": "financial_cumulative_data",
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
            "data": "(CR55/(SUM(CR37,CR47)/1000000))/month",
            "source": {
                "CR55": {
                    "table_name": "financial_cumulative_data",
                    "column_name": "financial_type_id",
                    "value": 32
                },
                "CR37": {
                    "table_name": "financial_cumulative_data",
                    "column_name": "financial_submetric_id",
                    "value": 87
                },
                "CR47": {
                    "table_name": "financial_cumulative_data",
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
            "data": "(CR57/(CR37/1000000))/month",
            "source": {
                "CR57": {
                    "table_name": "financial_cumulative_data",
                    "column_name": "financial_metric_id",
                    "value": 91
                },
                "CR37": {
                    "table_name": "financial_cumulative_data",
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
            "data": "(CR64/(CR47/1000000))/month",
            "source": {
                "CR64": {
                    "table_name": "financial_cumulative_data",
                    "column_name": "financial_metric_id",
                    "value": 92
                },
                "CR47": {
                    "table_name": "financial_cumulative_data",
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
            "data": "SUM(CR28,CR68,CR93,CR118,CR149)/(CR7+CR55)",
            "source": {
                "CR28": {
                    "table_name": "collapse_cumul_data",
                    "entity_type": "category",
                    "entity_id": 2
                },
                "CR68": {
                    "table_name": "collapse_cumul_data",
                    "entity_type": "category",
                    "entity_id": 6
                },
                "CR93": {
                    "table_name": "collapse_cumul_data",
                    "entity_type": "category",
                    "entity_id": 10
                },
                "CR118": {
                    "table_name": "collapse_cumul_data",
                    "entity_type": "category",
                    "entity_id": 14
                },
                "CR149": {
                    "table_name": "financial_cumulative_data",
                    "column_name": "financial_type_id",
                    "value": 21
                },
                "CR7": {
                    "table_name": "financial_cumulative_data",
                    "column_name": "financial_type_id",
                    "value": 31
                },
                "CR55": {
                    "table_name": "financial_cumulative_data",
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
            "data": "SUM(CR28,CR68,CR93,CR118)/CR7",
            "source": {
                "CR28": {
                    "table_name": "collapse_cumul_data",
                    "entity_type": "category",
                    "entity_id": 2
                },
                "CR68": {
                    "table_name": "collapse_cumul_data",
                    "entity_type": "category",
                    "entity_id": 6
                },
                "CR93": {
                    "table_name": "collapse_cumul_data",
                    "entity_type": "category",
                    "entity_id": 10
                },
                "CR118": {
                    "table_name": "collapse_cumul_data",
                    "entity_type": "category",
                    "entity_id": 14
                },
                "CR7": {
                    "table_name": "financial_cumulative_data",
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
            "data": "SUM(CR28)/CR9",
            "source": {
                "CR28": {
                    "table_name": "collapse_cumul_data",
                    "entity_type": "category",
                    "entity_id": 2
                },
                "CR9": {
                    "table_name": "financial_cumulative_data",
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
            "data": "SUM(L68,L93,L118)/L18",
            "source": {
                "L68": {
                    "table_name": "collapse_cumul_data",
                    "entity_type": "category",
                    "entity_id": 6
                },
                "L93": {
                    "table_name": "collapse_cumul_data",
                    "entity_type": "category",
                    "entity_id": 10
                },
                "L118": {
                    "table_name": "collapse_cumul_data",
                    "entity_type": "category",
                    "entity_id": 14
                },
                "L18": {
                    "table_name": "financial_cumulative_data",
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
            "data": "SUM(CR149)/CR55",
            "source": {
                "CR149": {
                    "table_name": "financial_cumulative_data",
                    "column_name": "financial_type_id",
                    "value": 21
                },
                "CR55": {
                    "table_name": "financial_cumulative_data",
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
            "data": "SUM(CR151,CR156,CR161,CR166)/CR57",
            "source": {
                "CR151": {
                    # HIDDEN RECORD
                    "column_name": "",
                    "value": -1,
                },
                "CR156": {
                    # HIDDEN RECORD
                    "column_name": "",
                    "value": -1,
                },
                "CR161": {
                    # NOT PRESENT IN DB
                    "column_name": "",
                    "value": -1
                },
                "CR166": {
                    "table_name": "collapse_cumul_data",
                    "entity_type": "type",
                    "entity_id": 169,
                },
                "CR57": {
                    "table_name": "financial_cumulative_data",
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
            "data": "SUM(CR167,CR168,CR169)/CR64",
            "source": {
                "CR167": {
                    "table_name": "collapse_cumul_data",
                    "entity_type": "type",
                    "entity_id": 170
                },
                "CR168": {
                    "table_name": "collapse_cumul_data",
                    "entity_type": "type",
                    "entity_id": 171
                },
                "CR169": {
                    "table_name": "collapse_cumul_data",
                    "entity_type": "type",
                    "entity_id": 172
                },
                "CR64": {
                    "table_name": "financial_cumulative_data",
                    "column_name": "financial_metric_id",
                    "value": 92
                },
            }
        }
    }
}

cumul_budget_mapping = {
    'L7': {
        "type": "financial_type",
        "id": 50,
        "formula": {
            "data": " ((((CR16 + CR149) / (CR37 + CR47)) * 1000000) /month)",
            "source": {
                "CR16": {
                    "table_name": "financial_cumulative_data",
                    "column_name": "financial_type_id",
                    "value": 20
                },
                "CR149": {
                    "table_name": "financial_cumulative_data",
                    "column_name": "financial_type_id",
                    "value": 21
                },
                "CR37": {
                    "table_name": "financial_cumulative_data",
                    "column_name": "financial_submetric_id",
                    "value": 87
                },
                "CR47": {
                    "table_name": "financial_cumulative_data",
                    "column_name": "financial_submetric_id",
                    "value": 92
                }
            }
        }
    },
    'L8': {
        "type": "financial_metric",
        "id": 145,
        "formula": {
            "data": "(((CR16/(CR37+CR47)) * 1000000 )/month)",
            "source": {
                "CR16": {
                    "table_name": "financial_cumulative_data",
                    "column_name": "financial_type_id",
                    "value": 20
                },
                "CR37": {
                    "table_name": "financial_cumulative_data",
                    "column_name": "financial_submetric_id",
                    "value": 87
                },
                "CR47": {
                    "table_name": "financial_cumulative_data",
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
            "data": "(((CR149 / (CR37 + CR47)) * 1000000)/month)",
            "source": {
                "CR149": {
                    "table_name": "financial_cumulative_data",
                    "column_name": "financial_type_id",
                    "value": 21
                },
                "CR37": {
                    "table_name": "financial_cumulative_data",
                    "column_name": "financial_submetric_id",
                    "value": 87
                },
                "CR47": {
                    "table_name": "financial_cumulative_data",
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
            "data": "(CR18+CR38)/(CR37/1000000)/month",
            "source": {
                "CR18": {
                    "table_name": "collapse_cumul_data",
                    "entity_type": "type",
                    "entity_id": 160,
                },
                "CR38": {
                    "table_name": "collapse_cumul_data",
                    "entity_type": "category",
                    "entity_id": 4
                },
                "CR37": {
                    "table_name": "financial_cumulative_data",
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
            "data": "SUM(CR151,CR156,CR161,CR166)/(CR37/1000000)/month",
            "source": {
                "CR151": {
                    # NOT PRESENT IN DB
                    "table_name": "collapse_cumul_data",
                    "entity_type": "type",
                    "entity_id": -1,
                },
                "CR156": {
                    # NOT PRESENT IN DB
                    "table_name": "collapse_cumul_data",
                    "entity_type": "type",
                    "entity_id": -1,
                },
                "CR161": {
                    # NOT PRESENT IN DB
                    "table_name": "collapse_cumul_data",
                    "entity_type": "type",
                    "entity_id": -1
                },
                "CR166": {
                    "table_name": "collapse_cumul_data",
                    "entity_type": "type",
                    "entity_id": 169,
                },
                "CR37": {
                    "table_name": "financial_cumulative_data",
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
            "source": {
                "CR12": {
                    "table_name": "financial_cumulative_data",
                    "column_name": "financial_metric_id",
                    "value": 147,
                },
                "CR13": {
                    "table_name": "financial_cumulative_data",
                    "column_name": "financial_metric_id",
                    "value": 148,
                }
            }
        }
    },
    'L16': {
        "type": "financial_metric",
        "id": 149,
        "formula": {
            "data": "SUM(L53,L78,L103,L128)/(L47/1000000)/month",
            "source": {
                "L53": {
                    "table_name": "financial_cumulative_data",
                    "column_name": "financial_metric_id",
                    "value": 59,
                },
                "L78": {
                    "table_name": "collapse_cumul_data",
                    "entity_type": "category",
                    "entity_id": 8
                },
                "L103": {
                    "table_name": "collapse_cumul_data",
                    "entity_type": "category",
                    "entity_id": 12
                },
                "L128": {
                    "table_name": "collapse_cumul_data",
                    "entity_type": "category",
                    "entity_id": 16
                },
                "L47": {
                    "table_name": "financial_cumulative_data",
                    "column_name": "financial_submetric_id",
                    "value": 92,
                },
            }
        }
    },
    'L17': {
        "type": "financial_metric",
        "id": 150,
        "formula": {
            "data": "(L152+L153+L154+L157+L158+L159+L162+L163+L164+L167+L168+L169)*1000000/L47",
            "source": {
                "L152": {
                    # HIDDEN RECORD
                    "table_name": "",
                    "column_name": "",
                    "value": -1,
                },
                "L153": {
                    # HIDDEN RECORD
                    "table_name": "",
                    "column_name": "",
                    "value": -1,
                },
                "L154": {
                    # HIDDEN RECORD
                    "table_name": "",
                    "column_name": "",
                    "value": -1,
                },
                "L157": {
                    # HIDDEN RECORD
                    "table_name": "",
                    "column_name": "",
                    "value": -1,
                },
                "L158": {
                    # HIDDEN RECORD
                    "table_name": "",
                    "column_name": "",
                    "value": -1,
                },
                "L159": {
                    # HIDDEN RECORD
                    "table_name": "",
                    "column_name": "",
                    "value": -1,
                },
                "L162": {
                    # NOT PRESENT IN DB
                    "table_name": "",
                    "column_name": "",
                    "value": -1
                },
                "L163": {
                    # NOT PRESENT IN DB
                    "column_name": "",
                    "value": -1
                },
                "L164": {
                    # NOT PRESENT IN DB
                    "table_name": "",
                    "column_name": "",
                    "value": -1
                },
                "L167": {
                    "table_name": "collapse_cumul_data",
                    "entity_type": "type",
                    "entity_id": 170
                },
                "L168": {
                    "table_name": "collapse_cumul_data",
                    "entity_type": "type",
                    "entity_id": 171,
                },
                "L169": {
                    "table_name": "collapse_cumul_data",
                    "entity_type": "type",
                    "entity_id": 172
                },
                "L47": {
                    "table_name": "financial_cumulative_data",
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
            "source": {
                "L16": {
                    "table_name": "financial_cumulative_data",
                    "column_name": "financial_metric_id",
                    "value": 149,
                },
                "L17": {
                    "table_name": "financial_cumulative_data",
                    "column_name": "financial_metric_id",
                    "value": 150,
                }
            }
        }
    },
    'L19': {
        "type": "financial_type",
        "id": 53,
        "formula": {
            "data": "(CR7+CR55)/(SUM(CR37,CR47)/1000000)/month",
            "source": {
                "CR7": {
                    "table_name": "financial_cumulative_data",
                    "column_name": "financial_type_id",
                    "value": 31
                },
                "CR55": {
                    "table_name": "financial_cumulative_data",
                    "column_name": "financial_type_id",
                    "value": 32
                },
                "CR37": {
                    "table_name": "financial_cumulative_data",
                    "column_name": "financial_submetric_id",
                    "value": 87
                },
                "CR47": {
                    "table_name": "financial_cumulative_data",
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
            "data": "CR7/(SUM(CR37,CR47)/1000000)/month",
            "source": {
                "CR7": {
                    "table_name": "financial_cumulative_data",
                    "column_name": "financial_type_id",
                    "value": 31
                },
                "CR37": {
                    "table_name": "financial_cumulative_data",
                    "column_name": "financial_submetric_id",
                    "value": 87
                },
                "CR47": {
                    "table_name": "financial_cumulative_data",
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
            "data": "CR9/(CR37/1000000)/month",
            "source": {
                "CR9": {
                    "table_name": "financial_cumulative_data",
                    "column_name": "financial_metric_id",
                    "value": 89
                },
                "CR37": {
                    "table_name": "financial_cumulative_data",
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
            "data": "(((L18 / CR47) * 1000000)/month)",
            "source": {
                "L18": {
                    "table_name": "financial_cumulative_data",
                    "column_name": "financial_metric_id",
                    "value": 90
                },
                "CR47": {
                    "table_name": "financial_cumulative_data",
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
            "data": "(CR55/(SUM(CR37,CR47)/1000000))/month",
            "source": {
                "CR55": {
                    "table_name": "financial_cumulative_data",
                    "column_name": "financial_type_id",
                    "value": 32
                },
                "CR37": {
                    "table_name": "financial_cumulative_data",
                    "column_name": "financial_submetric_id",
                    "value": 87
                },
                "CR47": {
                    "table_name": "financial_cumulative_data",
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
            "data": "(CR57/(CR37/1000000))/month",
            "source": {
                "CR57": {
                    "table_name": "financial_cumulative_data",
                    "column_name": "financial_metric_id",
                    "value": 91
                },
                "CR37": {
                    "table_name": "financial_cumulative_data",
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
            "data": "(CR64/(CR47/1000000))/month",
            "source": {
                "CR64": {
                    "table_name": "financial_cumulative_data",
                    "column_name": "financial_metric_id",
                    "value": 92
                },
                "CR47": {
                    "table_name": "financial_cumulative_data",
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
            "data": "SUM(CR28,CR68,CR93,CR118,CR149)/(CR7+CR55)",
            "source": {
                "CR28": {
                    "table_name": "collapse_cumul_data",
                    "entity_type": "category",
                    "entity_id": 2
                },
                "CR68": {
                    "table_name": "collapse_cumul_data",
                    "entity_type": "category",
                    "entity_id": 6
                },
                "CR93": {
                    "table_name": "collapse_cumul_data",
                    "entity_type": "category",
                    "entity_id": 10
                },
                "CR118": {
                    "table_name": "collapse_cumul_data",
                    "entity_type": "category",
                    "entity_id": 14
                },
                "CR149": {
                    "table_name": "financial_cumulative_data",
                    "column_name": "financial_type_id",
                    "value": 21
                },
                "CR7": {
                    "table_name": "financial_cumulative_data",
                    "column_name": "financial_type_id",
                    "value": 31
                },
                "CR55": {
                    "table_name": "financial_cumulative_data",
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
            "data": "SUM(CR28,CR68,CR93,CR118)/CR7",
            "source": {
                "CR28": {
                    "table_name": "collapse_cumul_data",
                    "entity_type": "category",
                    "entity_id": 2
                },
                "CR68": {
                    "table_name": "collapse_cumul_data",
                    "entity_type": "category",
                    "entity_id": 6
                },
                "CR93": {
                    "table_name": "collapse_cumul_data",
                    "entity_type": "category",
                    "entity_id": 10
                },
                "CR118": {
                    "table_name": "collapse_cumul_data",
                    "entity_type": "category",
                    "entity_id": 14
                },
                "CR7": {
                    "table_name": "financial_cumulative_data",
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
            "data": "SUM(CR28)/CR9",
            "source": {
                "CR28": {
                    "table_name": "collapse_cumul_data",
                    "entity_type": "category",
                    "entity_id": 2
                },
                "CR9": {
                    "table_name": "financial_cumulative_data",
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
            "data": "SUM(L68,L93,L118)/L18",
            "source": {
                "L68": {
                    "table_name": "collapse_cumul_data",
                    "entity_type": "category",
                    "entity_id": 6
                },
                "L93": {
                    "table_name": "collapse_cumul_data",
                    "entity_type": "category",
                    "entity_id": 10
                },
                "L118": {
                    "table_name": "collapse_cumul_data",
                    "entity_type": "category",
                    "entity_id": 14
                },
                "L18": {
                    "table_name": "financial_cumulative_data",
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
            "data": "SUM(CR149)/CR55",
            "source": {
                "CR149": {
                    "table_name": "financial_cumulative_data",
                    "column_name": "financial_type_id",
                    "value": 21
                },
                "CR55": {
                    "table_name": "financial_cumulative_data",
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
            "data": "SUM(CR151,CR156,CR161,CR166)/CR57",
            "source": {
                "CR151": {
                    # HIDDEN RECORD
                    "column_name": "",
                    "value": -1,
                },
                "CR156": {
                    # HIDDEN RECORD
                    "column_name": "",
                    "value": -1,
                },
                "CR161": {
                    # NOT PRESENT IN DB
                    "column_name": "",
                    "value": -1
                },
                "CR166": {
                    "table_name": "collapse_cumul_data",
                    "entity_type": "type",
                    "entity_id": 169,
                },
                "CR57": {
                    "table_name": "financial_cumulative_data",
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
            "data": "SUM(CR167,CR168)/CR64",
            "source": {
                "CR167": {
                    "table_name": "collapse_cumul_data",
                    "entity_type": "type",
                    "entity_id": 170
                },
                "CR168": {
                    "table_name": "collapse_cumul_data",
                    "entity_type": "type",
                    "entity_id": 171
                },
                "CR64": {
                    "table_name": "financial_cumulative_data",
                    "column_name": "financial_metric_id",
                    "value": 92
                },
            }
        }
    }
}

actual1_mapping = {
    'L7': {
        "type": "financial_type",
        "id": 50,
        "formula": {
            "data": " ((((CR16 + CR149) / (CR37 + CR47)) * 1000000) /month)",
            "source": {
                "CR16": {
                    "table_name": "financial_cumulative_data",
                    "column_name": "financial_type_id",
                    "value": 20
                },
                "CR149": {
                    "table_name": "financial_cumulative_data",
                    "column_name": "financial_type_id",
                    "value": 21
                },
                "CR37": {
                    "table_name": "financial_cumulative_data",
                    "column_name": "financial_submetric_id",
                    "value": 87
                },
                "CR47": {
                    "table_name": "financial_cumulative_data",
                    "column_name": "financial_submetric_id",
                    "value": 92
                }
            }
        }
    },
    'L8': {
        "type": "financial_metric",
        "id": 145,
        "formula": {
            "data": "(((CR16/(CR37+CR47)) * 1000000 )/month)",
            "source": {
                "CR16": {
                    "table_name": "financial_cumulative_data",
                    "column_name": "financial_type_id",
                    "value": 20
                },
                "CR37": {
                    "table_name": "financial_cumulative_data",
                    "column_name": "financial_submetric_id",
                    "value": 87
                },
                "CR47": {
                    "table_name": "financial_cumulative_data",
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
            "data": "(((CR149 / (CR37 + CR47)) * 1000000)/month)",
            "source": {
                "CR149": {
                    "table_name": "financial_cumulative_data",
                    "column_name": "financial_type_id",
                    "value": 21
                },
                "CR37": {
                    "table_name": "financial_cumulative_data",
                    "column_name": "financial_submetric_id",
                    "value": 87
                },
                "CR47": {
                    "table_name": "financial_cumulative_data",
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
            "data": "(CR18+CR38)/(CR37/1000000)/month",
            "source": {
                "CR18": {
                    "table_name": "collapse_cumul_data",
                    "entity_type": "type",
                    "entity_id": 160,
                },
                "CR38": {
                    "table_name": "collapse_cumul_data",
                    "entity_type": "category",
                    "entity_id": 4
                },
                "CR37": {
                    "table_name": "financial_cumulative_data",
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
            "data": "SUM(CR151,CR156,CR161,CR166)/(CR37/1000000)/month",
            "source": {
                "CR151": {
                    # NOT PRESENT IN DB
                    "table_name": "collapse_cumul_data",
                    "entity_type": "type",
                    "entity_id": -1,
                },
                "CR156": {
                    # NOT PRESENT IN DB
                    "table_name": "collapse_cumul_data",
                    "entity_type": "type",
                    "entity_id": -1,
                },
                "CR161": {
                    # NOT PRESENT IN DB
                    "table_name": "collapse_cumul_data",
                    "entity_type": "type",
                    "entity_id": -1
                },
                "CR166": {
                    "table_name": "collapse_cumul_data",
                    "entity_type": "type",
                    "entity_id": 169,
                },
                "CR37": {
                    "table_name": "financial_cumulative_data",
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
            "source": {
                "L12": {
                    "table_name": "financial_cumulative_data",
                    "column_name": "financial_metric_id",
                    "value": 147,
                },
                "L13": {
                    "table_name": "financial_cumulative_data",
                    "column_name": "financial_metric_id",
                    "value": 148,
                }
            }
        }
    },
    'L16': {
        "type": "financial_metric",
        "id": 149,
        "formula": {
            "data": "SUM(L53,L78,L103,L128)/(L47/1000000)/month",
            "source": {
                "L53": {
                    "table_name": "financial_cumulative_data",
                    "column_name": "financial_metric_id",
                    "value": 59,
                },
                "L78": {
                    "table_name": "collapse_cumul_data",
                    "entity_type": "category",
                    "entity_id": 8
                },
                "L103": {
                    "table_name": "collapse_cumul_data",
                    "entity_type": "category",
                    "entity_id": 12
                },
                "L128": {
                    "table_name": "collapse_cumul_data",
                    "entity_type": "category",
                    "entity_id": 16
                },
                "L47": {
                    "table_name": "financial_cumulative_data",
                    "column_name": "financial_submetric_id",
                    "value": 92,
                },
            }
        }
    },
    'L17': {
        "type": "financial_metric",
        "id": 150,
        "formula": {
            "data": "(L152+L153+L154+L157+L158+L159+L162+L163+L164+L167+L168+L169)*1000000/L47",
            "source": {
                "L152": {
                    # HIDDEN RECORD
                    "table_name": "",
                    "column_name": "",
                    "value": -1,
                },
                "L153": {
                    # HIDDEN RECORD
                    "table_name": "",
                    "column_name": "",
                    "value": -1,
                },
                "L154": {
                    # HIDDEN RECORD
                    "table_name": "",
                    "column_name": "",
                    "value": -1,
                },
                "L157": {
                    # HIDDEN RECORD
                    "table_name": "",
                    "column_name": "",
                    "value": -1,
                },
                "L158": {
                    # HIDDEN RECORD
                    "table_name": "",
                    "column_name": "",
                    "value": -1,
                },
                "L159": {
                    # HIDDEN RECORD
                    "table_name": "",
                    "column_name": "",
                    "value": -1,
                },
                "L162": {
                    # NOT PRESENT IN DB
                    "table_name": "",
                    "column_name": "",
                    "value": -1
                },
                "L163": {
                    # NOT PRESENT IN DB
                    "column_name": "",
                    "value": -1
                },
                "L164": {
                    # NOT PRESENT IN DB
                    "table_name": "",
                    "column_name": "",
                    "value": -1
                },
                "L167": {
                    "table_name": "collapse_cumul_data",
                    "entity_type": "type",
                    "entity_id": 170
                },
                "L168": {
                    "table_name": "collapse_cumul_data",
                    "entity_type": "type",
                    "entity_id": 171,
                },
                "L169": {
                    "table_name": "collapse_cumul_data",
                    "entity_type": "type",
                    "entity_id": 172
                },
                "L47": {
                    "table_name": "financial_cumulative_data",
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
            "source": {
                "L16": {
                    "table_name": "financial_cumulative_data",
                    "column_name": "financial_metric_id",
                    "value": 149,
                },
                "L17": {
                    "table_name": "financial_cumulative_data",
                    "column_name": "financial_metric_id",
                    "value": 150,
                }
            }
        }
    },
    'L19': {
        "type": "financial_type",
        "id": 53,
        "formula": {
            "data": "(CR7+CR55)/(SUM(CR37,CR47)/1000000)/month",
            "source": {
                "CR7": {
                    "table_name": "financial_cumulative_data",
                    "column_name": "financial_type_id",
                    "value": 31
                },
                "CR55": {
                    "table_name": "financial_cumulative_data",
                    "column_name": "financial_type_id",
                    "value": 32
                },
                "CR37": {
                    "table_name": "financial_cumulative_data",
                    "column_name": "financial_submetric_id",
                    "value": 87
                },
                "CR47": {
                    "table_name": "financial_cumulative_data",
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
            "data": "CR7/(SUM(CR37,CR47)/1000000)/month",
            "source": {
                "CR7": {
                    "table_name": "financial_cumulative_data",
                    "column_name": "financial_type_id",
                    "value": 31
                },
                "CR37": {
                    "table_name": "financial_cumulative_data",
                    "column_name": "financial_submetric_id",
                    "value": 87
                },
                "CR47": {
                    "table_name": "financial_cumulative_data",
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
            "data": "CR9/(CR37/1000000)/month",
            "source": {
                "CR9": {
                    "table_name": "financial_cumulative_data",
                    "column_name": "financial_metric_id",
                    "value": 89
                },
                "CR37": {
                    "table_name": "financial_cumulative_data",
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
            "data": "(((L18 / CR47) * 1000000)/month)",
            "source": {
                "L18": {
                    "table_name": "financial_cumulative_data",
                    "column_name": "financial_metric_id",
                    "value": 90
                },
                "CR47": {
                    "table_name": "financial_cumulative_data",
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
            "data": "(CR55/(SUM(CR37,CR47)/1000000))/month",
            "source": {
                "CR55": {
                    "table_name": "financial_cumulative_data",
                    "column_name": "financial_type_id",
                    "value": 32
                },
                "CR37": {
                    "table_name": "financial_cumulative_data",
                    "column_name": "financial_submetric_id",
                    "value": 87
                },
                "CR47": {
                    "table_name": "financial_cumulative_data",
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
            "data": "(CR57/(CR37/1000000))/month",
            "source": {
                "CR57": {
                    "table_name": "financial_cumulative_data",
                    "column_name": "financial_metric_id",
                    "value": 91
                },
                "CR37": {
                    "table_name": "financial_cumulative_data",
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
            "data": "(CR64/(CR47/1000000))/month",
            "source": {
                "CR64": {
                    "table_name": "financial_cumulative_data",
                    "column_name": "financial_metric_id",
                    "value": 92
                },
                "CR47": {
                    "table_name": "financial_cumulative_data",
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
            "data": "SUM(CR28,CR68,CR93,CR118,CR149)/(CR7+CR55)",
            "source": {
                "CR28": {
                    "table_name": "collapse_cumul_data",
                    "entity_type": "category",
                    "entity_id": 2
                },
                "CR68": {
                    "table_name": "collapse_cumul_data",
                    "entity_type": "category",
                    "entity_id": 6
                },
                "CR93": {
                    "table_name": "collapse_cumul_data",
                    "entity_type": "category",
                    "entity_id": 10
                },
                "CR118": {
                    "table_name": "collapse_cumul_data",
                    "entity_type": "category",
                    "entity_id": 14
                },
                "CR149": {
                    "table_name": "financial_cumulative_data",
                    "column_name": "financial_type_id",
                    "value": 21
                },
                "CR7": {
                    "table_name": "financial_cumulative_data",
                    "column_name": "financial_type_id",
                    "value": 31
                },
                "CR55": {
                    "table_name": "financial_cumulative_data",
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
            "data": "SUM(CR28,CR68,CR93,CR118)/CR7",
            "source": {
                "CR28": {
                    "table_name": "collapse_cumul_data",
                    "entity_type": "category",
                    "entity_id": 2
                },
                "CR68": {
                    "table_name": "collapse_cumul_data",
                    "entity_type": "category",
                    "entity_id": 6
                },
                "CR93": {
                    "table_name": "collapse_cumul_data",
                    "entity_type": "category",
                    "entity_id": 10
                },
                "CR118": {
                    "table_name": "collapse_cumul_data",
                    "entity_type": "category",
                    "entity_id": 14
                },
                "CR7": {
                    "table_name": "financial_cumulative_data",
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
            "data": "SUM(CR28)/CR9",
            "source": {
                "CR28": {
                    "table_name": "collapse_cumul_data",
                    "entity_type": "category",
                    "entity_id": 2
                },
                "CR9": {
                    "table_name": "financial_cumulative_data",
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
            "data": "SUM(L68,L93,L118)/L18",
            "source": {
                "L68": {
                    "table_name": "collapse_cumul_data",
                    "entity_type": "category",
                    "entity_id": 6
                },
                "L93": {
                    "table_name": "collapse_cumul_data",
                    "entity_type": "category",
                    "entity_id": 10
                },
                "L118": {
                    "table_name": "collapse_cumul_data",
                    "entity_type": "category",
                    "entity_id": 14
                },
                "L18": {
                    "table_name": "financial_cumulative_data",
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
            "data": "SUM(CR149)/CR55",
            "source": {
                "CR149": {
                    "table_name": "financial_cumulative_data",
                    "column_name": "financial_type_id",
                    "value": 21
                },
                "CR55": {
                    "table_name": "financial_cumulative_data",
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
            "data": "SUM(CR151,CR156,CR161,CR166)/CR57",
            "source": {
                "CR151": {
                    # HIDDEN RECORD
                    "column_name": "",
                    "value": -1,
                },
                "CR156": {
                    # HIDDEN RECORD
                    "column_name": "",
                    "value": -1,
                },
                "CR161": {
                    # NOT PRESENT IN DB
                    "column_name": "",
                    "value": -1
                },
                "CR166": {
                    "table_name": "collapse_cumul_data",
                    "entity_type": "type",
                    "entity_id": 169,
                },
                "CR57": {
                    "table_name": "financial_cumulative_data",
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
            "data": "SUM(CR167,CR168)/CR64",
            "source": {
                "CR167": {
                    "table_name": "collapse_cumul_data",
                    "entity_type": "type",
                    "entity_id": 170
                },
                "CR168": {
                    "table_name": "collapse_cumul_data",
                    "entity_type": "type",
                    "entity_id": 171
                },
                "CR64": {
                    "table_name": "financial_cumulative_data",
                    "column_name": "financial_metric_id",
                    "value": 92
                },
            }
        }
    }}

cumul_last_year_real_mapping = {
    'L7': {
        "type": "financial_type",
        "id": 50,
        "formula": {
            "data": " ((((CR16 + CR149) / (CR37 + CR47)) * 1000000) /month)",
            "source": {
                "CR16": {
                    "table_name": "financial_cumulative_data",
                    "column_name": "financial_type_id",
                    "value": 20
                },
                "CR149": {
                    "table_name": "financial_cumulative_data",
                    "column_name": "financial_type_id",
                    "value": 21
                },
                "CR37": {
                    "table_name": "financial_cumulative_data",
                    "column_name": "financial_submetric_id",
                    "value": 87
                },
                "CR47": {
                    "table_name": "financial_cumulative_data",
                    "column_name": "financial_submetric_id",
                    "value": 92
                }
            }
        }
    },
    'L8': {
        "type": "financial_metric",
        "id": 145,
        "formula": {
            "data": "(((CR16/(CR37+CR47)) * 1000000 )/month)",
            "source": {
                "CR16": {
                    "table_name": "financial_cumulative_data",
                    "column_name": "financial_type_id",
                    "value": 20
                },
                "CR37": {
                    "table_name": "financial_cumulative_data",
                    "column_name": "financial_submetric_id",
                    "value": 87
                },
                "CR47": {
                    "table_name": "financial_cumulative_data",
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
            "data": "(((CR149 / (CR37 + CR47)) * 1000000)/month)",
            "source": {
                "CR149": {
                    "table_name": "financial_cumulative_data",
                    "column_name": "financial_type_id",
                    "value": 21
                },
                "CR37": {
                    "table_name": "financial_cumulative_data",
                    "column_name": "financial_submetric_id",
                    "value": 87
                },
                "CR47": {
                    "table_name": "financial_cumulative_data",
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
            "data": "(CR18+CR38)/(CR37/1000000)/month",
            "source": {
                "CR18": {
                    "table_name": "collapse_cumul_data",
                    "entity_type": "type",
                    "entity_id": 160,
                },
                "CR38": {
                    "table_name": "collapse_cumul_data",
                    "entity_type": "category",
                    "entity_id": 4
                },
                "CR37": {
                    "table_name": "financial_cumulative_data",
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
            "data": "SUM(CR151,CR156,CR161,CR166)/(CR37/1000000)/month",
            "source": {
                "CR151": {
                    # NOT PRESENT IN DB
                    "table_name": "collapse_cumul_data",
                    "entity_type": "type",
                    "entity_id": -1,
                },
                "CR156": {
                    # NOT PRESENT IN DB
                    "table_name": "collapse_cumul_data",
                    "entity_type": "type",
                    "entity_id": -1,
                },
                "CR161": {
                    # NOT PRESENT IN DB
                    "table_name": "collapse_cumul_data",
                    "entity_type": "type",
                    "entity_id": -1
                },
                "CR166": {
                    "table_name": "collapse_cumul_data",
                    "entity_type": "type",
                    "entity_id": 169,
                },
                "CR37": {
                    "table_name": "financial_cumulative_data",
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
            "source": {
                "L12": {
                    "table_name": "financial_cumulative_data",
                    "column_name": "financial_metric_id",
                    "value": 147,
                },
                "L13": {
                    "table_name": "financial_cumulative_data",
                    "column_name": "financial_metric_id",
                    "value": 148,
                }
            }
        }
    },
    'L16': {
        "type": "financial_metric",
        "id": 149,
        "formula": {
            "data": "SUM(L53,L78,L103,L128)/(L47/1000000)/month",
            "source": {
                "L53": {
                    "table_name": "financial_cumulative_data",
                    "column_name": "financial_metric_id",
                    "value": 59,
                },
                "L78": {
                    "table_name": "collapse_cumul_data",
                    "entity_type": "category",
                    "entity_id": 8
                },
                "L103": {
                    "table_name": "collapse_cumul_data",
                    "entity_type": "category",
                    "entity_id": 12
                },
                "L128": {
                    "table_name": "collapse_cumul_data",
                    "entity_type": "category",
                    "entity_id": 16
                },
                "L47": {
                    "table_name": "financial_cumulative_data",
                    "column_name": "financial_submetric_id",
                    "value": 92,
                },
            }
        }
    },
    'L17': {
        "type": "financial_metric",
        "id": 150,
        "formula": {
            "data": "(L152+L153+L154+L157+L158+L159+L162+L163+L164+L167+L168+L169)*1000000/L47",
            "source": {
                "L152": {
                    # HIDDEN RECORD
                    "table_name": "",
                    "column_name": "",
                    "value": -1,
                },
                "L153": {
                    # HIDDEN RECORD
                    "table_name": "",
                    "column_name": "",
                    "value": -1,
                },
                "L154": {
                    # HIDDEN RECORD
                    "table_name": "",
                    "column_name": "",
                    "value": -1,
                },
                "L157": {
                    # HIDDEN RECORD
                    "table_name": "",
                    "column_name": "",
                    "value": -1,
                },
                "L158": {
                    # HIDDEN RECORD
                    "table_name": "",
                    "column_name": "",
                    "value": -1,
                },
                "L159": {
                    # HIDDEN RECORD
                    "table_name": "",
                    "column_name": "",
                    "value": -1,
                },
                "L162": {
                    # NOT PRESENT IN DB
                    "table_name": "",
                    "column_name": "",
                    "value": -1
                },
                "L163": {
                    # NOT PRESENT IN DB
                    "column_name": "",
                    "value": -1
                },
                "L164": {
                    # NOT PRESENT IN DB
                    "table_name": "",
                    "column_name": "",
                    "value": -1
                },
                "L167": {
                    "table_name": "collapse_cumul_data",
                    "entity_type": "type",
                    "entity_id": 170
                },
                "L168": {
                    "table_name": "collapse_cumul_data",
                    "entity_type": "type",
                    "entity_id": 171,
                },
                "L169": {
                    "table_name": "collapse_cumul_data",
                    "entity_type": "type",
                    "entity_id": 172
                },
                "L47": {
                    "table_name": "financial_cumulative_data",
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
            "source": {
                "L16": {
                    "table_name": "financial_cumulative_data",
                    "column_name": "financial_metric_id",
                    "value": 149,
                },
                "L17": {
                    "table_name": "financial_cumulative_data",
                    "column_name": "financial_metric_id",
                    "value": 150,
                }
            }
        }
    },
    'L19': {
        "type": "financial_type",
        "id": 53,
        "formula": {
            "data": "(CR7+CR55)/(SUM(CR37,CR47)/1000000)/month",
            "source": {
                "CR7": {
                    "table_name": "financial_cumulative_data",
                    "column_name": "financial_type_id",
                    "value": 31
                },
                "CR55": {
                    "table_name": "financial_cumulative_data",
                    "column_name": "financial_type_id",
                    "value": 32
                },
                "CR37": {
                    "table_name": "financial_cumulative_data",
                    "column_name": "financial_submetric_id",
                    "value": 87
                },
                "CR47": {
                    "table_name": "financial_cumulative_data",
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
            "data": "CR7/(SUM(CR37,CR47)/1000000)/month",
            "source": {
                "CR7": {
                    "table_name": "financial_cumulative_data",
                    "column_name": "financial_type_id",
                    "value": 31
                },
                "CR37": {
                    "table_name": "financial_cumulative_data",
                    "column_name": "financial_submetric_id",
                    "value": 87
                },
                "CR47": {
                    "table_name": "financial_cumulative_data",
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
            "data": "CR9/(CR37/1000000)/month",
            "source": {
                "CR9": {
                    "table_name": "financial_cumulative_data",
                    "column_name": "financial_metric_id",
                    "value": 89
                },
                "CR37": {
                    "table_name": "financial_cumulative_data",
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
            "data": "(((L18 / CR47) * 1000000)/month)",
            "source": {
                "L18": {
                    "table_name": "financial_cumulative_data",
                    "column_name": "financial_metric_id",
                    "value": 90
                },
                "CR47": {
                    "table_name": "financial_cumulative_data",
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
            "data": "(CR55/(SUM(CR37,CR47)/1000000))/month",
            "source": {
                "CR55": {
                    "table_name": "financial_cumulative_data",
                    "column_name": "financial_type_id",
                    "value": 32
                },
                "CR37": {
                    "table_name": "financial_cumulative_data",
                    "column_name": "financial_submetric_id",
                    "value": 87
                },
                "CR47": {
                    "table_name": "financial_cumulative_data",
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
            "data": "(CR57/(CR37/1000000))/month",
            "source": {
                "CR57": {
                    "table_name": "financial_cumulative_data",
                    "column_name": "financial_metric_id",
                    "value": 91
                },
                "CR37": {
                    "table_name": "financial_cumulative_data",
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
            "data": "(CR64/(CR47/1000000))/month",
            "source": {
                "CR64": {
                    "table_name": "financial_cumulative_data",
                    "column_name": "financial_metric_id",
                    "value": 92
                },
                "CR47": {
                    "table_name": "financial_cumulative_data",
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
            "data": "SUM(CR28,CR68,CR93,CR118,CR149)/(CR7+CR55)",
            "source": {
                "CR28": {
                    "table_name": "collapse_cumul_data",
                    "entity_type": "category",
                    "entity_id": 2
                },
                "CR68": {
                    "table_name": "collapse_cumul_data",
                    "entity_type": "category",
                    "entity_id": 6
                },
                "CR93": {
                    "table_name": "collapse_cumul_data",
                    "entity_type": "category",
                    "entity_id": 10
                },
                "CR118": {
                    "table_name": "collapse_cumul_data",
                    "entity_type": "category",
                    "entity_id": 14
                },
                "CR149": {
                    "table_name": "financial_cumulative_data",
                    "column_name": "financial_type_id",
                    "value": 21
                },
                "CR7": {
                    "table_name": "financial_cumulative_data",
                    "column_name": "financial_type_id",
                    "value": 31
                },
                "CR55": {
                    "table_name": "financial_cumulative_data",
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
            "data": "SUM(CR28,CR68,CR93,CR118)/CR7",
            "source": {
                "CR28": {
                    "table_name": "collapse_cumul_data",
                    "entity_type": "category",
                    "entity_id": 2
                },
                "CR68": {
                    "table_name": "collapse_cumul_data",
                    "entity_type": "category",
                    "entity_id": 6
                },
                "CR93": {
                    "table_name": "collapse_cumul_data",
                    "entity_type": "category",
                    "entity_id": 10
                },
                "CR118": {
                    "table_name": "collapse_cumul_data",
                    "entity_type": "category",
                    "entity_id": 14
                },
                "CR7": {
                    "table_name": "financial_cumulative_data",
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
            "data": "SUM(CR28)/CR9",
            "source": {
                "CR28": {
                    "table_name": "collapse_cumul_data",
                    "entity_type": "category",
                    "entity_id": 2
                },
                "CR9": {
                    "table_name": "financial_cumulative_data",
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
            "data": "SUM(L68,L93,L118)/L18",
            "source": {
                "L68": {
                    "table_name": "collapse_cumul_data",
                    "entity_type": "category",
                    "entity_id": 6
                },
                "L93": {
                    "table_name": "collapse_cumul_data",
                    "entity_type": "category",
                    "entity_id": 10
                },
                "L118": {
                    "table_name": "collapse_cumul_data",
                    "entity_type": "category",
                    "entity_id": 14
                },
                "L18": {
                    "table_name": "financial_cumulative_data",
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
            "data": "SUM(CR149)/CR55",
            "source": {
                "CR149": {
                    "table_name": "financial_cumulative_data",
                    "column_name": "financial_type_id",
                    "value": 21
                },
                "CR55": {
                    "table_name": "financial_cumulative_data",
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
            "data": "SUM(CR151,CR156,CR161,CR166)/CR57",
            "source": {
                "CR151": {
                    # HIDDEN RECORD
                    "column_name": "",
                    "value": -1,
                },
                "CR156": {
                    # HIDDEN RECORD
                    "column_name": "",
                    "value": -1,
                },
                "CR161": {
                    # NOT PRESENT IN DB
                    "column_name": "",
                    "value": -1
                },
                "CR166": {
                    "table_name": "collapse_cumul_data",
                    "entity_type": "type",
                    "entity_id": 169,
                },
                "CR57": {
                    "table_name": "financial_cumulative_data",
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
            "data": "SUM(CR167,CR168,CR169)/CR64",
            "source": {
                "CR167": {
                    "table_name": "collapse_cumul_data",
                    "entity_type": "type",
                    "entity_id": 170
                },
                "CR168": {
                    "table_name": "collapse_cumul_data",
                    "entity_type": "type",
                    "entity_id": 171
                },
                "CR169": {
                    "table_name": "collapse_cumul_data",
                    "entity_type": "type",
                    "entity_id": 172
                },
                "CR64": {
                    "table_name": "financial_cumulative_data",
                    "column_name": "financial_metric_id",
                    "value": 92
                },
            }
        }
    }
}