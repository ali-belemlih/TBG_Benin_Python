import parse_benin_data

sheet_name = 'CA Mobile'

# Row to financial_types DB table ID mapping
# Key -> row number in excel
# Value -> financial_type ID
financial_type_row_mapping = {
    8: 17,
    12: 18,
    14: 19,
    16: 20,
    149: 21,
    171: 22,
    177: 23,
    179: 24
}

# Row to financial_metric DB table ID mapping
# Key -> row number in excel
# Value -> financial_metric ID
financial_metric_row_mapping = {
    17: 58,
    53: 59,
    143: 60,
    144: 61,
    145: 62,
    165: 63,
    178: 64,
    180: 65,
    181: 66,
    182: 67
}

# Row to financial_submetric DB table ID mapping
# Key -> row number in excel
# Value -> financial_submetric ID
financial_submetric_row_mapping = {
    54: 4,
    58: 5
}

required_rows = list(financial_type_row_mapping.keys()) + list(financial_metric_row_mapping.keys()) + list(financial_submetric_row_mapping.keys())

parse_benin_data.generate_data(sheet_name,
                               "ca_mobile_2025",
                               required_rows,
                               financial_type_row_mapping,
                               financial_metric_row_mapping,
                               financial_submetric_row_mapping)

# 17	CA Global
# 18	CA services Mobile
# 19	CA récurrent
# 20	CA sortant
# 	58	Prépayé (yc commissions)
# 	59	Postpayé
# 		4 Redevance d'abonnement
# 		5 Trafic sortant
# 	60	Mobile Money
# 	61	Liaisons Spécialisées
# 	62	Internet Mobile (PrP+PoP)

# 21	CA entrant
# 	63	International

# 22	Colocalisation

# 23	Roaming in
# 	64	Dont Roaming National

# 24	CA Non récurrent
# 	65	Terminaux
# 	66	Clé Internet Mobile
# 	67	Autres
