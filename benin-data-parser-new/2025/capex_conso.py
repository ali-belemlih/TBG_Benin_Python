import parse_benin_data

sheet_name = 'Capex Consolidés'

# Row to financial_types DB table ID mapping
# Key -> row number in excel
# Value -> financial_type ID
financial_type_row_mapping = {
    7: 1,
    10: 2,
    23: 3,
    28: 4
}

# Row to financial_metric DB table ID mapping
# Key -> row number in excel
# Value -> financial_metric ID
financial_metric_row_mapping = {
    11: 1,
    12: 2,
    13: 3,
    14: 4,
    15: 5,
    16: 6,
    17: 7,
    18: 8,
    19: 9,
    20: 10,
    21: 11,
    24: 12,
    25: 13,
    26: 14,
    29: 15,
    30: 16,
    31: 17,
    32: 18,
    33: 19,
    34: 20,
    35: 21,
    36: 22,
    37: 23,
    38: 24,
    39: 25,
    40: 26,
    41: 27
}

required_rows = list(financial_type_row_mapping.keys()) + list(financial_metric_row_mapping.keys())

parse_benin_data.generate_data(sheet_name, "capex_consolidate_2025", required_rows, financial_type_row_mapping, financial_metric_row_mapping)
