# TODO: Create a new column unique_id in DB table financial_types, financial_metrics, financial_submetrics
# and populate it with the following formula:
# unique_id = name in downcase, replace spaces with underscores, remove special characters, remove trailing and leading spaces
# In case of conflict, add the ID or random number to the unique_id
# This will allow us to quickly identify the correct financial type, metric, and submetric for a given row
# in the excel file.
# Use unique_id to map instead of DB IDs

# Row to financial_types DB table ID mapping
# Key -> row number in excel
# Value -> financial_type ID
financial_type_row_mapping = {
    5: 29,
    52: 30
}

# Row to financial_metric DB table ID mapping
# Key -> row number in excel
# Value -> financial_metric ID
financial_metric_row_mapping = {
    7: 79,
    13: 80,
    18: 81,
    23: 82,
    29: 83,
    34: 84,
    39: 85,
    45: 86,
    48: 87,
    54: 88
}

# Row to financial_submetric DB table ID mapping
# Key -> row number in excel
# Value -> financial_submetric ID
financial_submetric_row_mapping = {
    8: 11,
    15: 12,
    16: 13,
    19: 14,
    21: 15,
    26: 16,
    27: 17,
    30: 18,
    32: 19,
    40: 20,
    49: 21,
    50: 22
}
