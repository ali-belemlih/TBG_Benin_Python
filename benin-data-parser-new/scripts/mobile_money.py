import parse_benin_data

sheet_name = 'Mobile Money'

# Row to financial_types DB table ID mapping
# Key -> row number in excel
# Value -> financial_type ID
financial_type_row_mapping = {
    7: 33,
    9: 34,
    11: 35,
    13: 36,
    15: 37,
    28: 38,
    42: 39,
    74: 40
}

# Row to financial_metric DB table ID mapping
# Key -> row number in excel
# Value -> financial_metric ID
financial_metric_row_mapping = {
    16: 93,
    17: 94,
    18: 95,
    19: 96,
    20: 97,
    21: 98,
    22: 99,
    23: 100,
    24: 101,
    25: 102,
    26: 103,

    29: 104,
    30: 105,
    31: 106,
    32: 107,
    33: 108,
    34: 109,
    35: 110,
    36: 111,
    37: 112,
    38: 113,
    39: 114,
    40: 115,

    43: 116,
    53: 117,
    63: 118,

    75: 119
}

# Row to financial_submetric DB table ID mapping
# Key -> row number in excel
# Value -> financial_submetric ID
financial_submetric_row_mapping = {
    44: 47,
    45: 48,
    46: 49,
    47: 50,
    48: 51,
    49: 52,
    50: 53,
    51: 54,
    52: 55,

    54: 56,
    55: 57,
    56: 58,
    57: 59,
    58: 60,
    59: 61,
    60: 62,
    61: 63,
    62: 64,

    64: 65,
    65: 66,
    66: 67,
    67: 68,
    68: 69,
    69: 70,
    70: 71,
    71: 72,
    72: 73
}


required_rows = list(financial_type_row_mapping.keys()) + list(financial_metric_row_mapping.keys()) + list(financial_submetric_row_mapping.keys())

parse_benin_data.generate_data(sheet_name,
                               "mobile_money",
                               required_rows,
                               financial_type_row_mapping,
                               financial_metric_row_mapping,
                               financial_submetric_row_mapping)
