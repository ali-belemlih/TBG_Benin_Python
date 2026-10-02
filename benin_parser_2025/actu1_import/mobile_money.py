from .mapping.mobile_money_mapping import (
    financial_type_row_mapping,
    financial_metric_row_mapping,
    financial_submetric_row_mapping
)
from helpers.actual_helper import parse_arguments
from benin_parser_2025.actu1_import.main_driver import run, load_sheet_config

args = parse_arguments()
config = load_sheet_config("mobile_money")

mappings = {
    "financial_type_row_mapping": financial_type_row_mapping,
    "financial_metric_row_mapping": financial_metric_row_mapping,
    "financial_submetric_row_mapping": financial_submetric_row_mapping
}

# Monthly
run(
    sheet_name=config["sheet_name"],
    mappings=mappings,
    mode="monthly",
    args=args,
    output_prefix="mobile_money",
    db_table_name=config["monthly"]["table"],
    custom_month_column_map=config["monthly"]["column_map"],
    category_fallback=config["category_fallback"],
    start_row_offset=config["start_row_offset"]
)
