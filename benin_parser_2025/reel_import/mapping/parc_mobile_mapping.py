initial_mapping = {
    'PARC24':{
        "table_name": "financial_metrics_data",
        "financial_submetric_id": 83,
        "kpi_key": 'E2'
    },
    'PARC27':{
        "table_name": "financial_metrics_data",
        "financial_submetric_id": 84,
        "kpi_key": 'G2'
    },
    'PARC35':{
        "table_name": "financial_metrics_data",
        "financial_submetric_id": 88,
        "kpi_key": 'E3'
    },
    'PARC36':{
        "table_name": "financial_metrics_data",
        "financial_submetric_id": 89,
        "kpi_key": 'G3'
    }
}
previous_month_mapping = {
    'PARC23':{
        "type_id": 141,
        "column_name" : "financial_metric_id",  
        "value" : 142
    },
    'PARC34':{
        "type_id": 143,
        "column_name" : "financial_metric_id",
        "value" : 144
    },
}

parc_mobile_mapping = {
    'R35':{
        "table_name" : "financial_submetric",
        "id" : 86,
        "formula": {
                "data": "R30+R33",
        }
    },
    'R45':{
        "table_name" : "financial_submetric",
        "id" : 91,
        "formula": {
            "data": "R41+R42",
        }
    },
    'R16':{
        "table_name" : "financial_submetric",
        "id" : 74,
        "formula": {
            "data": "SUM(R30,R41)",
        }
    },
    'R17':{
        "table_name" : "financial_submetric",
        "id" : 75,
        "formula": {
            "data": "SUM(R33,R42)",
        }
    },
    'R21':{
        "table_name" : "financial_submetric",
        "id" : 79,
        "formula": {
            "data": "SUM(R33,R42)",
        }
    },
    'R20':{
        "table_name" : "financial_submetric",
        "id" : 78,
        "formula": {
            "data": "R35",
        }
    },
    'R19':{
        "table_name" : "financial_submetric",
        "id" : 77,
        "formula": {
            "data": "R45",
        }
    },
    'R46':{
        "table_name" : "financial_metric",
        "id" : 144,
        "formula": {
            "data": "R40+R45",
        }
    },
    'R36':{
        "table_name" : "financial_metric",
        "id" : 142,
        "formula": {
            "data": "R29+R35",
        }
    },
    'R15':{
        "table_name" : "financial_metric",
        "id" : 138,
        "formula": {
            "data": "R29+R40",
        }
    },
    'R23':{
        "table_name" : "financial_metric",
        "id" : 139,
        "formula": {
            "data": "SUM(R36,R46)",
        }
    },
    'R25':{
        "table_name" : "financial_metric",
        "id" : 140,
        "formula": {
            "data": "SUM(R36,R46)",
        }
    },
    'R24':{
        "table_name" : "financial_submetric",
        "id" : 81,
        "formula": {
            "data": "SUM(R15,R23)/2",
        }
    },
    'R26':{
        "table_name" : "financial_submetric",
        "id" : 82,
        "formula": {
            "data": "R24",
        }
    },
    'R37':{
        "table_name" : "financial_submetric",
        "id" : 87,
        "formula": {
            "data": "(R29+R36)/2",
        }
    },
    'R34':{
        "table_name" : "financial_submetric",
        "id" : 85,
        "formula": {
            "data": "(R33/R37)*-12",
        }
    },
    'R22':{
        "table_name" : "financial_submetric",
        "id" : 80,
        "formula": {
            "data": "R34",
        }
    },
    'R47':{
        "table_name" : "financial_submetric",
        "id" : 92,
        "formula": {
            "data": "(R40+R46)/2",
        }
        },
    'R44':{
        "table_name" : "financial_submetric",
        "id" : 90,
        "formula": {
            "data": "(R42/R47)*-12",
        }
    },
    'R18':{
        "table_name" : "financial_submetric",
        "id" : 76,
        "formula": {
            "data": "R44",
        }
    },
    'R7':{
        "table_name" : "financial_types",
        "id" : 47,
        "formula": {
            "data": "R36+R46",
        }
    },
}
