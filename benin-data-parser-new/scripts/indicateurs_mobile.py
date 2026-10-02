import parse_benin_data

sheet_name = 'Indicateurs Mobile'

# Row to financial_types DB table ID mapping
# Key -> row number in excel
# Value -> financial_type ID
financial_type_row_mapping = {
    7: 50,
    11: 51,
    15: 52,
    19: 53,
    27: 54
}

# Row to financial_metric DB table ID mapping
# Key -> row number in excel
# Value -> financial_metric ID
financial_metric_row_mapping = {
    8: 145,
    9: 146,

    12: 147,
    13: 148,

    16: 149,
    17: 150,

    20: 151,
    23: 152,

    28: 153,
    31: 154
}

# Row to financial_submetric DB table ID mapping
# Key -> row number in excel
# Value -> financial_submetric ID
financial_submetric_row_mapping = {
    21: 93,
    22: 94,

    24: 95,
    25: 96,

    29: 97,
    30: 98,

    32: 99,
    33: 100
}

required_rows = list(financial_type_row_mapping.keys()) + list(financial_metric_row_mapping.keys()) + list(financial_submetric_row_mapping.keys())

parse_benin_data.generate_data(sheet_name,
                               "indicateurs_mobile",
                               required_rows,
                               financial_type_row_mapping,
                               financial_metric_row_mapping,
                               financial_submetric_row_mapping)
