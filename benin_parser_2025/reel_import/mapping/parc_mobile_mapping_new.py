
REEL_DATA_MAPPING = [
    {
        "R7": {
        "formula": "=CR36+CR46",
        "type": "financial_type",
        "id": 47
        },
        "R15": {
        "formula": "=+CR29+CR40",
        "type": "financial_metric",
        "id": 138
        },
        "R16": {
        "formula": "=SUM(CR30,CR41)",
        "type": "financial_submetric",
        "id": 74
        },
        "R17": {
        "formula": "=SUM(CR33,CR42)",
        "type": "financial_submetric",
        "id": 75
        },
        "R18": {
        "formula": "=+CR44",
        "type": "financial_submetric",
        "id": 76
        },
        "R19": {
        "formula": "=+CR45",
        "type": "financial_submetric",
        "id": 77
        },
        "R20": {
        "formula": "=+CR35",
        "type": "financial_submetric",
        "id": 78
        },
        "R21": {
        "formula": "=SUM(CR33,CR42)",
        "type": "financial_submetric",
        "id": 79
        },
        "R22": {
        "formula": "=+CR34",
        "type": "financial_submetric",
        "id": 80
        },
        "R23": {
        "formula": "=SUM(CR36,CR46)",
        "type": "financial_metric",
        "id": 139
        },
        "R24": {
        "formula": "=SUM(CR15,CR23)/2",
        "type": "financial_submetric",
        "id": 81
        },
        "R25": {
        "formula": "=SUM(CR36,CR46)",
        "type": "financial_metric",
        "id": 140
        },
        "R26": {
        "formula": "=+CR24",
        "type": "financial_submetric",
        "id": 82
        },
        "R29": {
        "type": "financial_metric",
        "id": 141,
        "formula": {
            "data": "D29",
            "source": {
                "table_name": "financial_metrics_data",
                "column_name": "financial_metric_id"
                "value": 141

            }
        }
        },
        "R30": {
        "formula": "=+SUMIF($D$5:$CQ$5,CR$5,$D30:$CQ30)",
        "type": "financial_submetric",
        "id": 83
        },
        "R33": {
        "formula": "=+SUMIF($D$5:$CQ$5,CR$5,$D33:$CQ33)",
        "type": "financial_submetric",
        "id": 84
        },
        "R34": {
        "formula": "=(((-CR33/CR37))/COUNTIFS($D$5:$CP$5,CR5,$D$7:$CP$7,\">0\"))*12",
        "type": "financial_submetric",
        "id": 85
        },
        "R35": {
        "formula": "=+SUMIF($D$5:$CQ$5,CR$5,$D35:$CQ35)",
        "type": "financial_submetric",
        "id": 86
        },
        "R36": {
        "formula": "=+CR29+CR35",
        "type": "financial_metric",
        "id": 142
        },
        "R37": {
        "formula": "=(CR29+CR36)/2",
        "type": "financial_submetric",
        "id": 87
        },
        "R40": {
        "formula": "=D40",
        "type": "financial_metric",
        "id": 143
        },
        "R41": {
        "formula": "=+SUMIF($D$5:$CQ$5,CR$5,$D41:$CQ41)",
        "type": "financial_submetric",
        "id": 88
        },
        "R42": {
        "formula": "=+SUMIF($D$5:$CQ$5,CR$5,$D42:$CQ42)",
        "type": "financial_submetric",
        "id": 89
        },
        "R44": {
        "formula": "=(((-CR42/CR47))/COUNTIFS($D$5:$CP$5,CR5,$D$7:$CP$7,\">0\"))*12",
        "type": "financial_submetric",
        "id": 90
        },
        "R45": {
        "formula": "=+SUMIF($D$5:$CQ$5,CR$5,$D45:$CQ45)",
        "type": "financial_submetric",
        "id": 91
        },
        "R46": {
        "formula": "=CR40+CR45",
        "type": "financial_metric",
        "id": 144
        },
        "R47": {
        "formula": "=(CR40+CR46)/2",
        "type": "financial_submetric",
        "id": 92
        }
    }
]



BUDGET_MAPPING = [
    {
        "R7": {
        "formula": "=CS36+CS46",
        "type": "financial_type",
        "id": 47
        },
        "R15": {
        "formula": "=CS29+CS40",
        "type": "financial_metric",
        "id": 138
        },
        "R16": {
        "formula": "=SUM(CS30,CS41)",
        "type": "financial_submetric",
        "id": 74
        },
        "R17": {
        "formula": "=SUM(CS33,CS42)",
        "type": "financial_submetric",
        "id": 75
        },
        "R18": {
        "formula": "=CS44",
        "type": "financial_submetric",
        "id": 76
        },
        "R19": {
        "formula": "=CS45",
        "type": "financial_submetric",
        "id": 77
        },
        "R20": {
        "formula": "=CS35",
        "type": "financial_submetric",
        "id": 78
        },
        "R21": {
        "formula": "=SUM(CS33,CS42)",
        "type": "financial_submetric",
        "id": 79
        },
        "R22": {
        "formula": "=CS34",
        "type": "financial_submetric",
        "id": 80
        },
        "R23": {
        "formula": "=SUM(CS36,CS46)",
        "type": "financial_metric",
        "id": 139
        },
        "R24": {
        "formula": "=SUM(CS15,CS23)/2",
        "type": "financial_submetric",
        "id": 81
        },
        "R25": {
        "formula": "=SUM(CS36,CS46)",
        "type": "financial_metric",
        "id": 140
        },
        "R26": {
        "formula": "=CS24",
        "type": "financial_submetric",
        "id": 82
        },
        "R29": {
        "formula": "=E29",
        "type": "financial_metric",
        "id": 141
        },
        "R30": {
        "formula": "=SUMIF($D$5:$CQ$5,CS$5,$D30:$CQ30)",
        "type": "financial_submetric",
        "id": 83
        },
        "R33": {
        "formula": "=SUMIF($D$5:$CQ$5,CS$5,$D33:$CQ33)",
        "type": "financial_submetric",
        "id": 84
        },
        "R34": {
        "formula": "=(((-CS33/CS37))/COUNTIFS($D$5:$CP$5,CR5,$D$7:$CP$7,\">0\"))*12",
        "type": "financial_submetric",
        "id": 85
        },
        "R35": {
        "formula": "=SUMIF($D$5:$CQ$5,CS$5,$D35:$CQ35)",
        "type": "financial_submetric",
        "id": 86
        },
        "R36": {
        "formula": "=CS29+CS35",
        "type": "financial_metric",
        "id": 142
        },
        "R37": {
        "formula": "=(CS29+CS36)/2",
        "type": "financial_submetric",
        "id": 87
        },
        "R40": {
        "formula": "=E40",
        "type": "financial_metric",
        "id": 143
        },
        "R41": {
        "formula": "=SUMIF($D$5:$CQ$5,CS$5,$D41:$CQ41)",
        "type": "financial_submetric",
        "id": 88
        },
        "R42": {
        "formula": "=SUMIF($D$5:$CQ$5,CS$5,$D42:$CQ42)",
        "type": "financial_submetric",
        "id": 89
        },
        "R44": {
        "formula": "=(((-CS42/CS47))/COUNTIFS($D$5:$CP$5,CR5,$D$7:$CP$7,\">0\"))*12",
        "type": "financial_submetric",
        "id": 90
        },
        "R45": {
        "formula": "=SUMIF($D$5:$CQ$5,CS$5,$D45:$CQ45)",
        "type": "financial_submetric",
        "id": 91
        },
        "R46": {
        "formula": "=CS40+CS45",
        "type": "financial_metric",
        "id": 144
        },
        "R47": {
        "formula": "=(CS40+CS46)/2",
        "type": "financial_submetric",
        "id": 92
        }
    }
]

_2023_REEL_MAPPING = [
    {
        "R7": {
        "formula": "=CW36+CW46",
        "type": "financial_type",
        "id": 47
        },
        "R15": {
        "formula": "=+CW29+CW40",
        "type": "financial_metric",
        "id": 138
        },
        "R16": {
        "formula": "=SUM(CW30,CW41)",
        "type": "financial_submetric",
        "id": 74
        },
        "R17": {
        "formula": "=SUM(CW33,CW42)",
        "type": "financial_submetric",
        "id": 75
        },
        "R18": {
        "formula": "=+CW44",
        "type": "financial_submetric",
        "id": 76
        },
        "R19": {
        "formula": "=+CW45",
        "type": "financial_submetric",
        "id": 77
        },
        "R20": {
        "formula": "=+CW35",
        "type": "financial_submetric",
        "id": 78
        },
        "R21": {
        "formula": "=SUM(CW33,CW42)",
        "type": "financial_submetric",
        "id": 79
        },
        "R22": {
        "formula": "=+CW34",
        "type": "financial_submetric",
        "id": 80
        },
        "R23": {
        "formula": "=SUM(CW36,CW46)",
        "type": "financial_metric",
        "id": 139
        },
        "R24": {
        "formula": "=SUM(CW15,CW23)/2",
        "type": "financial_submetric",
        "id": 81
        },
        "R25": {
        "formula": "=SUM(CW36,CW46)",
        "type": "financial_metric",
        "id": 140
        },
        "R26": {
        "formula": "=+CW24",
        "type": "financial_submetric",
        "id": 82
        },
        "R29": {
        "formula": "=G29",
        "type": "financial_metric",
        "id": 141
        },
        "R30": {
        "formula": "=+SUMIF($D$5:$CQ$5,CW$5,$D30:$CQ30)",
        "type": "financial_submetric",
        "id": 83
        },
        "R33": {
        "formula": "=+SUMIF($D$5:$CQ$5,CW$5,$D33:$CQ33)",
        "type": "financial_submetric",
        "id": 84
        },
        "R34": {
        "formula": "=(((-CW33/CW37))/COUNTIFS($D$5:$CP$5,CR5,$D$7:$CP$7,\">0\"))*12",
        "type": "financial_submetric",
        "id": 85
        },
        "R35": {
        "formula": "=+SUMIF($D$5:$CQ$5,CW$5,$D35:$CQ35)",
        "type": "financial_submetric",
        "id": 86
        },
        "R36": {
        "formula": "=+CW29+CW35",
        "type": "financial_metric",
        "id": 142
        },
        "R37": {
        "formula": "=(CW29+CW36)/2",
        "type": "financial_submetric",
        "id": 87
        },
        "R40": {
        "formula": "=G40",
        "type": "financial_metric",
        "id": 143
        },
        "R41": {
        "formula": "=+SUMIF($D$5:$CQ$5,CW$5,$D41:$CQ41)",
        "type": "financial_submetric",
        "id": 88
        },
        "R42": {
        "formula": "=+SUMIF($D$5:$CQ$5,CW$5,$D42:$CQ42)",
        "type": "financial_submetric",
        "id": 89
        },
        "R44": {
        "formula": "=(((-CW42/CW47))/COUNTIFS($D$5:$CP$5,CR5,$D$7:$CP$7,\">0\"))*12",
        "type": "financial_submetric",
        "id": 90
        },
        "R45": {
        "formula": "=+SUMIF($D$5:$CQ$5,CW$5,$D45:$CQ45)",
        "type": "financial_submetric",
        "id": 91
        },
        "R46": {
        "formula": "=CW40+CW45",
        "type": "financial_metric",
        "id": 144
        },
        "R47": {
        "formula": "=(CW40+CW46)/2",
        "type": "financial_submetric",
        "id": 92
        }
    }
]
