import re
from openpyxl import load_workbook
from io import BytesIO

def calculate_formula(formula_str, sheet_name, file_bytes):
    wb = load_workbook(filename=BytesIO(file_bytes), data_only=True)
    sheet = wb[sheet_name]

    if not formula_str:
        return 0

    formula_str = formula_str.strip().lstrip('=')

    # Handle SUM
    sum_match = re.match(r"SUM\(['\"]?([A-Z]+\d+):([A-Z]+\d+)['\"]?\)", formula_str, re.IGNORECASE)
    if sum_match:
        start_cell, end_cell = sum_match.groups()
        cell_range = sheet[start_cell:end_cell]
        return sum(cell[0].value or 0 for cell in cell_range)

    # Handle single cell reference, possibly with a "-"
    cell_match = re.match(r"(-?)([A-Z]+\d+)", formula_str)
    if cell_match:
        sign, cell = cell_match.groups()
        cell_value = sheet[cell].value or 0
        return -cell_value if sign == '-' else cell_value

    raise ValueError(f"Unsupported formula: {formula_str}")
