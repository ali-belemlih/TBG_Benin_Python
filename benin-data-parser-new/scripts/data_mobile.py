import parse_benin_data

sheet_name = 'Data Mobile'

# Row to financial_types DB table ID mapping
# Key -> row number in excel
# Value -> financial_type ID
financial_type_row_mapping = {
    7: 41,
    12: 42,
    17: 43,
    22: 44,
    27: 45,
    32: 46
}

# Row to financial_metric DB table ID mapping
# Key -> row number in excel
# Value -> financial_metric ID
financial_metric_row_mapping = {
    8: 120,
    9: 121,
    10: 122,

    13: 123,
    14: 124,
    15: 125,

    18: 126,
    19: 127,
    20: 128,

    23: 129,
    24: 130,
    25: 131,

    28: 132,
    29: 133,
    30: 134,

    33: 135,
    34: 136,
    35: 137
}

required_rows = list(financial_type_row_mapping.keys()) + list(financial_metric_row_mapping.keys())

parse_benin_data.generate_data(sheet_name, "data_mobile", required_rows, financial_type_row_mapping, financial_metric_row_mapping)
