import parse_benin_data

sheet_name = 'Mobile Money'

# Row to financial_types DB table ID mapping
# Key -> row number in excel
# Value -> financial_type ID
financial_type_row_mapping = {
    6: 33,
    8: 34,
    10: 35,
    12: 36,
    14: 37,
    27: 38,
    41: 39,
    73: 40
}

# Row to financial_metric DB table ID mapping
# Key -> row number in excel
# Value -> financial_metric ID
financial_metric_row_mapping = {
    15: 93,
    16: 94,
    17: 95,
    18: 96,
    19: 97,
    20: 98,
    21: 99,
    22: 100,
    23: 101,
    24: 102,
    25: 103,

    28: 104,
    29: 105,
    30: 106,
    31: 107,
    32: 108,
    33: 109,
    34: 110,
    35: 111,
    36: 112,
    37: 113,
    38: 114,
    39: 115,

    42: 116,
    52: 117,
    62: 118,

    74: 119
}

# Row to financial_submetric DB table ID mapping
# Key -> row number in excel
# Value -> financial_submetric ID
financial_submetric_row_mapping = {
    43: 47,
    44: 48,
    45: 49,
    46: 50,
    47: 51,
    48: 52,
    49: 53,
    50: 54,
    51: 55,

    53: 56,
    54: 57,
    55: 58,
    56: 59,
    57: 60,
    58: 61,
    59: 62,
    60: 63,
    61: 64,

    63: 65,
    64: 66,
    65: 67,
    66: 68,
    67: 69,
    68: 70,
    69: 71,
    70: 72,
    71: 73
}


required_rows = list(financial_type_row_mapping.keys()) + list(financial_metric_row_mapping.keys()) + list(financial_submetric_row_mapping.keys())

parse_benin_data.generate_data(sheet_name,
                               "mobile_money_2025",
                               required_rows,
                               financial_type_row_mapping,
                               financial_metric_row_mapping,
                               financial_submetric_row_mapping)
