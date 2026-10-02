import re
from asteval import Interpreter

def find_tbg_key_in_table(conn, tbg_key: str):
    db_table_config = {
        "financial_type_id": "financial_types",
        "financial_metric_id": "financial_metric",
        "financial_submetric_id": "financial_submetric",
        "collapse_type_id": "collapse_types",
        "collapse_category_id": "collapse_categories",
        "collapse_subcategory_id": "collapse_subcategories"
    }

    realize_table_config = {
        'section' : 'cashflow_sections',
        'category' : 'cashflow_categories',
        'subcategory' : 'cashflow_subcategories'
    }
    with conn.cursor() as cur:
        for col_name, table in db_table_config.items():
            query = f"SELECT id FROM {table} WHERE tbg_key = %(tbg_key)s LIMIT 1"
            cur.execute(query, {"tbg_key": tbg_key})
            result = cur.fetchone()
            if result:
                return col_name, table, result[0]
    with conn.cursor() as cur:
        for col_name, table in realize_table_config.items():
            query = f"SELECT id FROM {table} where tbg_key = %(tbg_key)s LIMIT 1"
            cur.execute(query, {"tbg_key" : tbg_key})
            result = cur.fetchone()
            if result:
                return col_name, table, result[0]
    return None

def get_tbg_report_mapping(conn, report_type_id):
    with conn.cursor() as curr:
        query = "SELECT * FROM tbg_formulas WHERE report_type_id = %(report_type_id)s AND formula_type = 'FORMULA' ORDER BY id"
        curr.execute(query, {"report_type_id" : str(report_type_id)})
        result = curr.fetchall()
        if result:
            return result
    return None

def expand_sum_ranges(formula: str) -> str:

    pattern = re.compile(r'SUM\(([A-Za-z]+)(\d+)\s*:\s*([A-Za-z]+)(\d+)\)')

    def replacer(match):
        prefix1, start_str, prefix2, end_str = match.groups()
        if prefix1 != prefix2:
            raise ValueError(f"Mismatched prefixes in SUM range: {prefix1} and {prefix2}")
        start, end = int(start_str), int(end_str)
        if start > end:
            start, end = end, start
        terms = [f"{prefix1}{i}" for i in range(start, end + 1)]
        return f"({' + '.join(terms)})"

    processed_formula = formula
    while pattern.search(processed_formula):
        processed_formula = pattern.sub(replacer, processed_formula)
    return processed_formula

def get_variables_from_formula(formula: str) -> list:

    pattern = re.compile(r'[A-Za-z]+[0-9]+')
    variables = set(pattern.findall(formula))
    return sorted(list(variables))

def extract_keys_from_record(record: tuple):
    formula_str = record[7]
    if not formula_str or not isinstance(formula_str, str):
        return []
    try:
        expanded_formula = expand_sum_ranges(formula_str)
        extracted_keys = get_variables_from_formula(expanded_formula)
        return extracted_keys

    except Exception as e:
        return []

def get_value_from_db(conn, tbg_key_id, table_name, col_name, version_id, date = None ):
    table_to_fetch_data = "financial_metrics_data"
    if table_name.startswith("collapse"):
        type_mapping = {
            "collapse_subcategory_id" : "subcategory",
            "collapse_category_id" : "category",
            "collapse_type_id" : "type"
        }
        table_to_fetch_data = "collapse_monthly_data"
        query = f"SELECT real_value from {table_to_fetch_data} where entity_type = '{type_mapping[col_name]}' AND version_id = %(version_id)s AND entity_id = %(tbg_key_id)s"
        curr = conn.cursor()

        curr.execute(query, {'version_id' : version_id, 'tbg_key_id' : tbg_key_id})
        result = curr.fetchone()
        if result:
            return result[0]
        else:
            return None
    if table_name.startswith('cashflow'):
        year = date.split('-')[0]
        month = date.split('-')[1]
        table_to_fetch_data = 'cashflow_data'
        month_mapping = {
            '01': 'jan',
            '02': 'feb',
            '03': 'mar',
            '04': 'apr',
            '05': 'may',
            '06': 'jun',
            '07': 'jul',
            '08': 'aug',
            '09': 'sep',
            '10': 'oct',
            '11': 'nov',
            '12': 'dec'
        }
        query = f"""
            SELECT {month_mapping[month]}
            FROM {table_to_fetch_data}
            WHERE entity_type = %s
              AND version_id = %s
              AND entity_id = %s
              AND year = %s
        """
        curr = conn.cursor()
        curr.execute(
            query,
            (col_name, version_id, tbg_key_id, year)
        )
        result = curr.fetchone()
        return result[0]
    query = f"SELECT real_value from {table_to_fetch_data} where {col_name} = %(tbg_key_id)s AND version_id = %(version_id)s"
    curr = conn.cursor()
    curr.execute(query, {'version_id' : version_id, 'tbg_key_id' : tbg_key_id})
    # print(query)
    result = curr.fetchone()
    if result:
        return result[0]
    else:
        return None

def update_value_in_db(conn, tbg_key_id, table_name, col_name, version_id, final_value):
    allowed_columns = [
        "financial_type_id", "financial_metric_id", "financial_submetric_id",
        "collapse_type_id", "collapse_category_id", "collapse_subcategory_id"
    ]
    if col_name not in allowed_columns:
        raise ValueError(f"Invalid column name specified: {col_name}")

    try:
        with conn.cursor() as curr:
            if table_name.startswith("collapse"):
                table_to_update = "collapse_monthly_data"
                type_mapping = {
                    "collapse_subcategory_id": "subcategory",
                    "collapse_category_id": "category",
                    "collapse_type_id": "type"
                }
                entity_type_value = type_mapping.get(col_name)
                if not entity_type_value:
                    raise ValueError(f"Could not map collapse column: {col_name}")

                query = f"""
                    UPDATE {table_to_update}
                    SET real_value = %(final_value)s
                    WHERE entity_type = %(entity_type)s
                      AND version_id = %(version_id)s
                      AND entity_id = %(tbg_key_id)s
                """
                params = {
                    'final_value': final_value,
                    'entity_type': entity_type_value,
                    'version_id': version_id,
                    'tbg_key_id': tbg_key_id
                }
                curr.execute(query, params)

            else:
                table_to_update = "financial_metrics_data"
                query = f"""
                    UPDATE {table_to_update}
                    SET real_value = %(final_value)s
                    WHERE {col_name} = %(tbg_key_id)s
                      AND version_id = %(version_id)s
                """
                params = {
                    'final_value': final_value,
                    'version_id': version_id,
                    'tbg_key_id': tbg_key_id
                }
                curr.execute(query, params)
            conn.commit()
            return curr.rowcount

    except Exception as e:
        conn.rollback()
        print(f"Database update failed. Error: {e}")
        return 0

def tokenize_formula(formula: str) -> list:
    token_pattern = re.compile(r'([A-Za-z]+[0-9]+|\-?\d+\.?\d*|[+\-*/()])')
    return token_pattern.findall(formula)

def substitute_tokens(tokens: list, db_values: dict) -> str:
    substituted_list = []
    for token in tokens:
        substituted_list.append(str(db_values.get(token, token)))

    return ' '.join(substituted_list)

def evaluate_expression(expression_string: str):
    aeval = Interpreter()
    try:
        return aeval.eval(expression_string)
    except Exception as e:
        print(f"Could not evaluate expression. Error: {e}")
        return None
