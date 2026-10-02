opex_conso_mapping = {
    "L40": [{
        "type": "financial_type",
        "id": 7,
        "formula": {
            "data": "SUM(L41:L55)",
            "source": {
                "L41": {
                    "table_name" : "collapse_monthly_data",
                    "entity_type": "type",
                    "entity_id": 30
                },
                "L55": {
                    "table_name" : "collapse_monthly_data",
                    "entity_type": "type",
                    "entity_id": 44
                },
            }
        },
        "is_adjustible": True
    }],
    "L58": [{
        "type": "financial_metric",
        "id": 28,
        "formula": {
            "data": "SUM(L59:L78)",
            "source": {
                "L59": {
                    "table_name" : "collapse_monthly_data",
                    "entity_type": "type",
                    "entity_id": 45
                },
                "L78": {
                    "table_name" : "collapse_monthly_data",
                    "entity_type": "type",
                    "entity_id": 64
                },
            }
        },
        "is_adjustible": True
    }],
    "L79": [{
        "type": "financial_metric",
        "id": 29,
        "formula": {
            "data": "SUM(L80:L96)",
            "source": {
                "L80": {
                    "table_name" : "collapse_monthly_data",
                    "entity_type": "type",
                    "entity_id": 65
                },
                "L96": {
                    "table_name" : "collapse_monthly_data",
                    "entity_type": "type",
                    "entity_id": 81
                },
            }
        },
        "is_adjustible": True
    }],
    "L97": [{
        "type": "financial_metric",
        "id": 30,
        "formula": {
            "data": "L98",
            "source": {
                "L98": {
                    "table_name" : "collapse_monthly_data",
                    "entity_type": "type",
                    "entity_id": 82
                }
            }
        },
        "is_adjustible": True
    }],
    "L100": [{
        "type": "financial_metric",
        "id": 31,
        "formula": {
            "data": "SUM(L101:L105)",
            "source": {
                "L101": {
                    "table_name" : "collapse_monthly_data",
                    "entity_type": "type",
                    "entity_id": 83
                },
                "L105": {
                    "table_name" : "collapse_monthly_data",
                    "entity_type": "type",
                    "entity_id": 87
                }
            }
        },
        "is_adjustible": True
    }],
    "L106": [{
        "type": "financial_metric",
        "id": 32,
        "formula": {
            "data": "SUM(L107:L110)",
            "source": {
                "L107": {
                    "table_name" : "collapse_monthly_data",
                    "entity_type": "type",
                    "entity_id": 88
                },
                "L110": {
                    "table_name" : "collapse_monthly_data",
                    "entity_type": "type",
                    "entity_id": 91
                }
            }
        },
        "is_adjustible": True
    }],
    "L57": [{
        "type": "financial_type",
        "id": 8,
        "formula": {
            "data": "L58+L79+L97+L100+L106",
            "source": {

            }
        },
        "is_adjustible": True
    }],
    "L114": [{
        "type": "financial_metric",
        "id": 33,
        "formula": {
            "data": "SUM(L115:L136)",
            "source": {
                "L115": {
                    "table_name" : "collapse_monthly_data",
                    "entity_type": "type",
                    "entity_id": 92
                },
                "L136": {
                    "table_name" : "collapse_monthly_data",
                    "entity_type": "type",
                    "entity_id": 113
                }
            }
        },
        "is_adjustible": True
    }],
    "L137": [{
        "type": "financial_metric",
        "id": 34,
        "formula": {
            "data": "L138+L139",
            "source": {
                "L138": {
                    "table_name" : "collapse_monthly_data",
                    "entity_type": "type",
                    "entity_id": 114
                },
                "L139": {
                    "table_name" : "collapse_monthly_data",
                    "entity_type": "type",
                    "entity_id": 115
                }
            }
        },
        "is_adjustible": True
    }],
    "L140": [{
        "type": "financial_metric",
        "id": 35,
        "formula": {
            "data": "SUM(L141:L150)",
            "source": {
                "L141": {
                    "table_name" : "collapse_monthly_data",
                    "entity_type": "type",
                    "entity_id": 116
                },
                "L150": {
                    "table_name" : "collapse_monthly_data",
                    "entity_type": "type",
                    "entity_id": 125
                }
            }
        },
        "is_adjustible": True
    }],
    "L151": [{
        "type": "financial_metric",
        "id": 36,
        "formula": {
            "data": "SUM(L152:L160)",
            "source": {
                "L152": {
                    "table_name" : "collapse_monthly_data",
                    "entity_type": "type",
                    "entity_id": 126
                },
                "L160": {
                    "table_name" : "collapse_monthly_data",
                    "entity_type": "type",
                    "entity_id": 134
                }
            }
        },
        "is_adjustible": True
    }],
    "L161": [{
        "type": "financial_metric",
        "id": 37,
        "formula": {
            "data": "L162+L163",
            "source": {
                "L162": {
                    "table_name" : "collapse_monthly_data",
                    "entity_type": "type",
                    "entity_id": 135
                },
                "L163": {
                    "table_name" : "collapse_monthly_data",
                    "entity_type": "type",
                    "entity_id": 136
                }
            }
        },
        "is_adjustible": True
    }],
    "L113": [{
        "type": "financial_type",
        "id": 9,
        "formula": {
            "data": "L114+L137+L140+L151+L161",
            "source": {}
        },
        "is_adjustible": True
    }],
    "L168": [{
        "type": "financial_metric",
        "id": 38,
        "formula": {
            "data": "L169+L170",
            "source": {
                "L169": {
                    "table_name" : "collapse_monthly_data",
                    "entity_type": "type",
                    "entity_id": 138
                },
                "L170": {
                    "table_name" : "collapse_monthly_data",
                    "entity_type": "type",
                    "entity_id": 139
                }
            }
        },
        "is_adjustible": True
    }],
    "L173": [{
        "type": "financial_metric",
        "id": 40,
        "formula": {
            "data": "SUM(L174:L181)",
            "source": {
                "L174": {
                    "table_name" : "collapse_monthly_data",
                    "entity_type": "type",
                    "entity_id": 141
                },
                "L181": {
                    "table_name" : "collapse_monthly_data",
                    "entity_type": "type",
                    "entity_id": 148
                }
            }
        },
        "is_adjustible": True
    }],
    "L167": [{
        "type": "financial_type",
        "id": 10,
        "formula": {
            "data": "L168+L173", #Add L171
            "source": {}
        },
        "is_adjustible": True
    }],
    "L185": [{
        "type": "financial_metric",
        "id": 41,
        "formula": {
            "data": "L190+L191+L192+L193+L195+L196+L197+L187+L188",
            "source": {
                "L190": {
                    "table_name" : "collapse_monthly_data",
                    "entity_type": "type",
                    "entity_id": 152
                },
                "L191": {
                    "table_name" : "collapse_monthly_data",
                    "entity_type": "type",
                    "entity_id": 153
                },
                "L192": {
                    "table_name" : "collapse_monthly_data",
                    "entity_type": "type",
                    "entity_id": 154
                },
                "L193": {
                    "table_name" : "collapse_monthly_data",
                    "entity_type": "type",
                    "entity_id": 155
                },
                "L195": {
                    "table_name" : "collapse_monthly_data",
                    "entity_type": "type",
                    "entity_id": 157
                },
                "L196": {
                    "table_name" : "collapse_monthly_data",
                    "entity_type": "type",
                    "entity_id": 158
                },
                "L197": {
                    "table_name" : "collapse_monthly_data",
                    "entity_type": "type",
                    "entity_id": 159
                },
                "L187": {
                    "table_name" : "collapse_monthly_data",
                    "entity_type": "type",
                    "entity_id": 149
                },
                "L188": {
                    "table_name" : "collapse_monthly_data",
                    "entity_type": "type",
                    "entity_id": 150
                }
            }
        },
        "is_adjustible": True
    }],
    "L186": [{
        "type": "financial_metric",
        "id": 42,
        "formula": {
            "data": "L189+L194",
            "source": {
                "L189": {
                    "table_name" : "collapse_monthly_data",
                    "entity_type": "type",
                    "entity_id": 151
                },
                "L194": {
                    "table_name" : "collapse_monthly_data",
                    "entity_type": "type",
                    "entity_id": 156
                }
            }
        },
        "is_adjustible": True
    }],
    "L184": [{
        "type": "financial_type",
        "id": 11,
        "formula": {
            "data": "L186+L185+L198+L199",
            "source": {
                "L198": {
                    "table_name" : "financial_metrics_data",
                    "column_name": "financial_metric_id",
                    "value": 43
                },
                "L199": {
                    "table_name" : "financial_metrics_data",
                    "column_name": "financial_metric_id",
                    "value": 44
                }
            }
        },
        "is_adjustible": True
    }],
    "L11":[{
        "type": "type",
        "id": 2,
        "formula": {
            "data": "L11 - 25.842129",
            "source": {
                "L11": {
                    "table_name" : "collapse_monthly_data",
                    "entity_type": "type",
                    "entity_id": 2
                }
            }
        },
        "is_adjustible": False
    }],
    "L9": [
        {
            "type": "financial_type",
            "id": 6,
            "formula": {
                "data": "SUM(L10:L38)",
                "source": {
                    "L10": {
                        "table_name" : "collapse_monthly_data",
                        "entity_type": "type",
                        "entity_id": 1
                    },
                    "L38": {
                        "table_name" : "collapse_monthly_data",
                        "entity_type": "type",
                        "entity_id": 29
                    }
                }
            },
            "is_adjustible": True
        },
        {
            "type": "financial_type",
            "id": 6,
            "formula": {
                "data": "L9 - L15 - 25.842129",
                "source": {
                    "L15":{
                        "table_name" : "collapse_monthly_data",
                        "entity_type": "type",
                        "entity_id": 6
                    }
                }
            },
            "is_adjustible": False
        }
    ],
    "L15":[{
        "type" : "type",
        "id" : 6,
        "formula" : {
            "data" : "0"
        },
        "is_adjustible": False
    }],
    "L7": [{
        "type": "financial_type",
        "id": 5,
        "formula": {
            "data": "SUM(L9,L40,L57,L113,L167,L184,L201)",
            "source": {
                "L201":{
                    "table_name" : "financial_metrics_data",
                    "column_name": "financial_type_id",
                    "value": 12
                }
            }
        },
        "is_adjustible": True
    }],
    "L101":[{
        "type": "type",
        "id": 83,
        "formula": {
            "data": "L102",
            "source": {
                "L102":{
                    "table_name" : "collapse_monthly_data",
                    "entity_type": "type",
                    "entity_id": 84
                }
            }
        },
        "is_adjustible": False
    }]
}
