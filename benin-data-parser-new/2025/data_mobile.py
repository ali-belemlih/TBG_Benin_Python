import parse_benin_data

sheet_name = 'Data Mobile'

# Row to financial_types DB table ID mapping
# Key -> row number in excel
# Value -> financial_type ID
financial_type_row_mapping = {
    6: 41,
    11: 42,
    16: 43,
    21: 44,
    26: 45,
    31: 46
}

# Row to financial_metric DB table ID mapping
# Key -> row number in excel
# Value -> financial_metric ID
financial_metric_row_mapping = {
    7: 120,
    8: 121,
    9: 122,

    12: 123,
    13: 124,
    14: 125,

    17: 126,
    18: 127,
    19: 128,

    22: 129,
    23: 130,
    24: 131,

    27: 132,
    28: 133,
    29: 134,

    32: 135,
    33: 136,
    34: 137
}

required_rows = list(financial_type_row_mapping.keys()) + list(financial_metric_row_mapping.keys())

parse_benin_data.generate_data(sheet_name, "data_mobile2_2025", required_rows, financial_type_row_mapping, financial_metric_row_mapping)
