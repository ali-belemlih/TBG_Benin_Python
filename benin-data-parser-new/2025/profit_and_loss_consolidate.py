import parse_benin_data

sheet_name = 'P&L conso'

# Row to financial_types DB table ID mapping
# Key -> row number in excel
# Value -> financial_type ID
financial_type_row_mapping = {
    7: 29,
    54: 30
}

# Row to financial_metric DB table ID mapping
# Key -> row number in excel
# Value -> financial_metric ID
financial_metric_row_mapping = {
    9: 79,
    15: 80,
    20: 81,
    25: 82,
    31: 83,
    36: 84,
    41: 85,
    47: 86,
    50: 87,
    56: 88
}

# Row to financial_submetric DB table ID mapping
# Key -> row number in excel
# Value -> financial_submetric ID
financial_submetric_row_mapping = {
    10: 11,
    17: 12,
    18: 13,
    21: 14,
    23: 15,
    28: 16,
    29: 17,
    32: 18,
    34: 19,
    42: 20,
    51: 21,
    52: 22
}

required_rows = list(financial_type_row_mapping.keys()) + list(financial_metric_row_mapping.keys()) + list(financial_submetric_row_mapping.keys())

parse_benin_data.generate_data(sheet_name,
                               "profit_and_loss_consolidate_mai_2025",
                               required_rows,
                               financial_type_row_mapping,
                               financial_metric_row_mapping,
                               financial_submetric_row_mapping)

# 29	Chiffre d'affaires
# 	79	Mobile
# 		11 Intercompagnie Mobile

# 	80	Coût des ventes
# 		12	Mobile
# 		13	Intercompagnie Mobile

# 	81	Marge Brute
# 		14	% CA
# 		15	Mobile

# 	82	Coûts opérationnels
# 		16	Mobile
# 		17	Intercompagnie Mobile

# 	83	EBITDA
# 		18	% CA
# 		19	Mobile

# 	84	Amortissements et déprec. Courant

# 	85	EBITA
# 		20	% CA

# 	86	Résultat financier

# 	87	RESULTAT avant IS
# 		21	IS
# 		22	ID

# 30	RESULTAT NET
# 	88	% CA

