import psycopg2  # or use any other DB connector you're using, like SQLAlchemy
import helpers.db_utils as db_utils

# Original dictionary
financial_submetric_row_mapping = {
    42: 47,
    43: 48,
    44: 49,
    45: 50,
    46: 51,
    47: 52,
    48: 53,
    49: 54,
    50: 55,
    52: 56,
    53: 57,
    54: 58,
    55: 59,
    56: 60,
    57: 61,
    58: 62,
    59: 63,
    60: 64,
    62: 65,
    63: 66,
    64: 67,
    65: 68,
    66: 69,
    67: 70,
    68: 71,
    69: 72,
    70: 73
}

# Establish database connection (replace placeholders)
conn = db_utils.get_db_connection()
cur = conn.cursor()

# Extract unique submetric IDs
ids = tuple(set(financial_submetric_row_mapping.values()))

print(ids)

# Query to get tbg_keys for given IDs
query = f"""
    SELECT id, tbg_key
    FROM financial_submetric
    WHERE id IN {ids}
"""
cur.execute(query)
results = cur.fetchall()

# Create a lookup dictionary from id to tbg_key
id_to_tbg_key = {id_: tbg_key for id_, tbg_key in results}

# Replace IDs in the original mapping
final_mapping = {
    key: id_to_tbg_key.get(value)
    for key, value in financial_submetric_row_mapping.items()
}

# Clean up
cur.close()
conn.close()

# Now final_mapping has tbg_keys as values
print(final_mapping)
