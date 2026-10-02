import parse_benin_data

sheet_name = 'Cash conso'

# Row to financial_types DB table ID mapping
# Key -> row number in excel
# Value -> financial_type ID
financial_type_row_mapping = {
    7: 13,
    22: 14,
    35: 15,
    39: 16
}

# Row to financial_metric DB table ID mapping
# Key -> row number in excel
# Value -> financial_metric ID
financial_metric_row_mapping = {
    9: 45,
    11: 46,
    13: 47,
    15: 48,
    17: 49,
    18: 50,
    19: 51,
    20: 52,
    30: 53,
    32: 54,
    33: 55,
    37: 56,
    38: 57
}

# Row to financial_submetric DB table ID mapping
# Key -> row number in excel
# Value -> financial_submetric ID
financial_submetric_row_mapping = {
   24: 1,
   26: 2,
   28: 3
}

required_rows = list(financial_type_row_mapping.keys()) + list(financial_metric_row_mapping.keys()) + list(financial_submetric_row_mapping.keys())

parse_benin_data.generate_data(sheet_name,
                               "cash_consolidate",
                               required_rows,
                               financial_type_row_mapping,
                               financial_metric_row_mapping,
                               financial_submetric_row_mapping)
