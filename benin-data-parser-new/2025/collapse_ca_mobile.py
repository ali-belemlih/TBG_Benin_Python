import callapse_parse_benin_data as parse_benin_data

sheet_name = 'CA Mobile'

# Row to financial_types DB table ID mapping
# Key -> row number in excel
# Value -> financial_type ID

collapse_types_row_mapping = {

    18:160,

    55:161,
    56:162,
    57:163,

    59:164,
    84:165,
    109:166,

    146:167,
    147:168,


    166:169,
    167:170,
    168:171,
    169:172,


}


collapse_categories_row_mapping = {

    19:1,
    28:2,
    36:3,
    38:4,
    47:5,

    68:6,
    76:7,
    78:8,
    82:9,

    93:10,
    101:11,
    103:12,
    107:13,

    118:14,
    126:15,
    128:16,
    137:17,
    139:18,
    140:19,
    141:20,
    142:21,


}

collapse_subcategories_row_mapping = {

    20: 1,
    21: 2,
    22: 3,
    23: 4,
    24: 5,
    25: 6,
    26: 7,
    27: 8,

    30: 9,
    31: 10,
    32: 11,
    33: 12,
    34: 13,
    35: 14,

    40: 15,
    41: 16,
    42: 17,
    43: 18,
    44: 19,
    45: 20,
    46: 21,


    60: 22,
    61: 23,
    62: 24,
    63: 25,
    64: 26,
    65: 27,
    66: 28,
    67: 29,


    70: 30,
    71: 31,
    72: 32,
    73: 33,
    74: 34,
    75: 35,


    79: 36,
    80: 37,
    81: 38,

    85: 39,
    86: 40,
    87: 41,
    88: 42,
    89: 43,
    90: 44,
    91: 45,
    92: 46,

    95: 47,
    96: 48,
    97: 49,
    98: 50,
    99: 51,
    100: 52,


    104: 53,
    105: 54,
    106: 55,

    110: 56,
    111: 57,
    112: 58,
    113: 59,
    114: 60,
    115: 61,
    116: 62,
    117: 63,


    120: 64,
    121: 65,
    122: 66,
    123: 67,
    124: 68,
    125: 69,

    129: 70,
    130: 71,
    131: 72,
    132: 73,
    133: 74,
    134: 75,
    135: 76,
    136: 77


}



required_rows = list(collapse_types_row_mapping.keys()) + list(collapse_categories_row_mapping.keys()) + list(collapse_subcategories_row_mapping.keys())

parse_benin_data.generate_data(
    sheet_name,
    "collapse_ca_mobile_2025",
    required_rows,
    collapse_types_row_mapping,
    collapse_category_row_mapping=collapse_categories_row_mapping,
    collapse_subcategory_row_mapping=collapse_subcategories_row_mapping,
)
