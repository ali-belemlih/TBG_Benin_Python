import parse_benin_data

sheet_name = 'Marge Mobile'

# Row to financial_types DB table ID mapping
# Key -> row number in excel
# Value -> financial_type ID
financial_type_row_mapping = {
    7: 25,
    58: 26,
    60: 27,
    61: 28
}

# Row to financial_metric DB table ID mapping
# Key -> row number in excel
# Value -> financial_metric ID
financial_metric_row_mapping = {
    8: 68,
    9: 69,
    10: 70,
    38: 71,
    39: 72,
    40: 73,
    41: 74,
    42: 75,
    43: 76,
    45: 77,
    52: 78
}

# Row to financial_submetric DB table ID mapping
# Key -> row number in excel
# Value -> financial_submetric ID
financial_submetric_row_mapping = {
    49: 6,
    51: 7,
    53: 8,
    54: 9,
    56: 10
}

required_rows = list(financial_type_row_mapping.keys()) + list(financial_metric_row_mapping.keys()) + list(financial_submetric_row_mapping.keys())

parse_benin_data.generate_data(sheet_name,
                               "marge_mobile_2025",
                               required_rows,
                               financial_type_row_mapping,
                               financial_metric_row_mapping,
                               financial_submetric_row_mapping)


# 25	Total Revenu
# 	68	Trafic (mn)
# 	69	Coût unitaire-Trafic
# 	70	International
# 	71	Reversements SVA
# 	72	Achat de capacité
# 	73	Nbre SMS
# 	74	Coût unitaire-SMS
# 	75	Interconnexion SMS
# 	76	Roaming out
# 	77	Coûts des terminaux et cartes
# 		6	Dont coût des terminaux.
# 		7	Dont provisions sur stocks
# 	78	Commissions
# 		8	Dont commissions up-front
# 		9	Dont avoirs de performance
# 		10	Dont Commissions Flooz
# 
# 26	Coûts des ventes
# 27	Marge Brute
# 28	En % du CA
