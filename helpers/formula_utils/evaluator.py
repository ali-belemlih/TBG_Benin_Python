import re
from datetime import datetime
from ..db_utils import get_real_or_budget_value, get_default_version_id

def evaluate_formula(cur, formula, date, label, version_id=None, cache=None,
                     row5=None, row7=None, cr5_target=None, month=None):
    if cache is None:
        cache = {}

    if version_id is None:
        date = datetime.strptime(date, "%Y-%m-%d").date()
        version_id = get_default_version_id(date.month, date.year)

    expr = formula.get("data", "")
    source = formula.get("source", {})

    # --- Step 1: Handle SUM ---
    expr = _handle_sum(expr, cache, source, cur, date, label, version_id)

    # --- Step 2: Replace Excel-style references (e.g., CR16, CR6) ---
    columns = re.findall(r'\b[A-Z]+[0-9]+\b', expr)
    expr = _replace_column_references(expr, columns, cache, source, cur, date, label, version_id)

    # --- Step 3: Handle COUNTIFS ---
    expr = _handle_countifs(expr, row5, row7, cr5_target)

    # --- Step 4: Handle "…/month" logic ---
    if "/month" in expr:
        # Strip out the "/month" part
        expr = expr.replace("/month", "")
        base_value = _safe_eval(expr)

        if month is not None and month != 0:
            return base_value / month
        return base_value  # if no month, just return the base result

    # --- Default case: evaluate normally ---
    return _safe_eval(expr)


def _resolve_column_value(column, cache, source, cur, date, label, version_id):
    if column in cache:
        return cache[column]
    elif column in source:
        source_info = source[column]
        value = get_real_or_budget_value(cur, source_info, date, label, version_id)
        cache[column] = value
        return value
    return 0.0


def _replace_column_references(expr, columns, cache, source, cur, date, label, version_id):
    for column in columns:
        value = _resolve_column_value(column, cache, source, cur, date, label, version_id)
        expr = expr.replace(column, str(value))
    return expr


def _handle_sum(expr, cache, source, cur, date, label, version_id):
    def sum_replacer(match):
        args = match.group(1).strip()
        if ":" in args and "," not in args:
            try:
                start_cell, end_cell = args.split(":")
            except ValueError:
                print(f"⚠️ Invalid range format: {args}")
                return "0.0"

            if not source or start_cell not in source or end_cell not in source:
                print(f"⚠️ Missing source for range: {start_cell}:{end_cell}")
                return "0.0"
            start_info = source[start_cell]
            end_info = source[end_cell]

            if start_info["table_name"] != end_info["table_name"]:
                print("⚠️ Mismatched table in SUM range")
                return "0.0"

            table_name = start_info["table_name"]
            values = []
            # Handle column_name-based ranges
            if "column_name" in start_info and "value" in start_info:
                if start_info["column_name"] != end_info["column_name"]:
                    print("⚠️ Mismatched column_name in SUM range")
                    return "0.0"

                column_name = start_info["column_name"]
                start_val = start_info["value"]
                end_val = end_info["value"]

                for v in range(start_val, end_val + 1):
                    cache_key = f"{table_name}:{column_name}:{v}"
                    if cache_key in cache:
                        result = cache[cache_key]
                    else:
                        result = get_real_or_budget_value(cur, {
                            "table_name": table_name,
                            "column_name": column_name,
                            "value": v
                        }, date, label, version_id)
                        cache[cache_key] = result
                    values.append(result or 0.0)

            # Handle entity_type/entity_id-based ranges
            elif "entity_type" in start_info and "entity_id" in start_info:
                if start_info["entity_type"] != end_info["entity_type"]:
                    print("⚠️ Mismatched entity_type in SUM range")
                    return "0.0"
                entity_type = start_info["entity_type"]
                start_id = start_info["entity_id"]
                end_id = end_info["entity_id"]
                for v in range(start_id, end_id + 1):
                    cache_key = f"{table_name}:{entity_type}:{v}"
                    if cache_key in cache:
                        result = cache[cache_key]
                    else:
                        result = get_real_or_budget_value(cur, {
                            "table_name": table_name,
                            "entity_type": entity_type,
                            "entity_id": v
                        }, date, label, version_id)
                        cache[cache_key] = result
                    values.append(result or 0.0)

            else:
                print("⚠️ Unrecognized SUM range structure")
                return "0.0"

            print(f"🔍 SUM({args}) => {values}")
            return f"sum({values})"

        # Else: standard comma-separated sum
        return f"sum([{args}])"

    return re.sub(r'SUM\(([^()]+)\)', sum_replacer, expr)

def _handle_countifs(expr, row5, row7, cr5_target):
    def countifs_replacer(match):
        if row5 is None or row7 is None or cr5_target is None:
            return "1"
        return str(sum(1 for r5, r7_val in zip(row5, row7) if r5 == cr5_target and r7_val > 0))

    return re.sub(r'COUNTIFS\(([^)]+)\)', countifs_replacer, expr)


def _safe_eval(expr):
    expr = expr.replace('^', '**')
    try:
        result = eval(expr, {"__builtins__": None}, {"sum": sum})
        if result == float('inf') or result == float('-inf'):
            return 0.0
        return result
    except ZeroDivisionError:
        print(f"Division by zero in expression: {expr}")
        return 0.0
    except Exception as e:
        print(f"Error evaluating: {expr} -> {e}")
        return 0.0
