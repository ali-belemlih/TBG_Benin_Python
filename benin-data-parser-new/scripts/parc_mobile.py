import parse_benin_data

sheet_name = 'Parc Mobile '

# Row to financial_types DB table ID mapping
# Key -> row number in excel
# Value -> financial_type ID
financial_type_row_mapping = {
    7: 47,
    28: 48,
    39: 49
}

# Row to financial_metric DB table ID mapping
# Key -> row number in excel
# Value -> financial_metric ID
financial_metric_row_mapping = {
    15: 138,
    23: 139,
    25: 140,

    29: 141,
    36: 142,

    40: 143,
    46: 144
}

# Row to financial_submetric DB table ID mapping
# Key -> row number in excel
# Value -> financial_submetric ID
financial_submetric_row_mapping = {
    16: 74,
    17: 75,
    18: 76,
    19: 77,
    20: 78,
    21: 79,
    22: 80,

    24: 81,

    26: 82,

    30: 83,
    33: 84,
    34: 85,
    35: 86,

    37: 87,
    
    41: 88,
    42: 89,
    44: 90,
    45: 91,

    47: 92
}

required_rows = list(financial_type_row_mapping.keys()) + list(financial_metric_row_mapping.keys()) + list(financial_submetric_row_mapping.keys())

parse_benin_data.generate_data(sheet_name,
                               "parc_mobile",
                               required_rows,
                               financial_type_row_mapping,
                               financial_metric_row_mapping,
                               financial_submetric_row_mapping)
