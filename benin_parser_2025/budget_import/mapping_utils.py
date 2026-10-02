from typing import Optional, Tuple

import pandas as pd

from .mapping.ca_mobile_mapping import (
    financial_type_row_mapping as ca_type_mapping,
    financial_metric_row_mapping as ca_metric_mapping,
    financial_submetric_row_mapping as ca_submetric_mapping
)
from .mapping.capex_conso_mapping import (
    financial_type_row_mapping as capex_type_mapping,
    financial_metric_row_mapping as capex_metric_mapping,
    financial_submetric_row_mapping as capex_submetric_mapping
)
from .mapping.cash_conso_mapping import (
    financial_type_row_mapping as cash_type_mapping,
    financial_metric_row_mapping as cash_metric_mapping,
    financial_submetric_row_mapping as cash_submetric_mapping
)
from .mapping.indicateurs_mobile_mapping import (
    financial_type_row_mapping as indicateurs_type_mapping,
    financial_metric_row_mapping as indicateurs_metric_mapping,
    financial_submetric_row_mapping as indicateurs_submetric_mapping
)
from .mapping.marge_mobile_mapping import (
    financial_type_row_mapping as marge_type_mapping,
    financial_metric_row_mapping as marge_metric_mapping,
    financial_submetric_row_mapping as marge_submetric_mapping
)
from .mapping.opex_conso_mapping import (
    financial_type_row_mapping as opex_type_mapping,
    financial_metric_row_mapping as opex_metric_mapping,
    financial_submetric_row_mapping as opex_submetric_mapping
)
from .mapping.parc_mobile_mapping import (
    financial_type_row_mapping as parc_type_mapping,
    financial_metric_row_mapping as parc_metric_mapping,
    financial_submetric_row_mapping as parc_submetric_mapping
)
# Import all mappings in a more organized way
from .mapping.profit_and_loss_mapping import (
    financial_type_row_mapping as pl_type_mapping,
    financial_metric_row_mapping as pl_metric_mapping,
    financial_submetric_row_mapping as pl_submetric_mapping
)
from .mapping.traffic_mobile_mapping import (
    financial_type_row_mapping as traffic_type_mapping,
    financial_metric_row_mapping as traffic_metric_mapping,
    financial_submetric_row_mapping as traffic_submetric_mapping
)

# Create a mapping dictionary for quick category lookup
CATEGORY_MAPPINGS = {
    "P&L consolidé": (pl_type_mapping, pl_metric_mapping, pl_submetric_mapping),
    "CA Mobile": (ca_type_mapping, ca_metric_mapping, ca_submetric_mapping),
    "Marge brute Mobile": (marge_type_mapping, marge_metric_mapping, marge_submetric_mapping),
    "Trafic Mobile": (traffic_type_mapping, traffic_metric_mapping, traffic_submetric_mapping),
    "Parc Mobile": (parc_type_mapping, parc_metric_mapping, parc_submetric_mapping),
    "Indicateurs Mobile": (indicateurs_type_mapping, indicateurs_metric_mapping, indicateurs_submetric_mapping),
    "Capex Consolidés": (capex_type_mapping, capex_metric_mapping, capex_submetric_mapping),
    "Flux Financiers consolidés": (cash_type_mapping, cash_metric_mapping, cash_submetric_mapping),
    "Opex Consolidés": (opex_type_mapping, opex_metric_mapping, opex_submetric_mapping)
}


def get_financial_hierarchy(row: pd.Series, category: str) -> Tuple[Optional[int], Optional[int], Optional[int]]:
    """
    Get financial type, metric, and submetric IDs based on the row number and category.
    
    Args:
        row: The row from the dataframe
        category: The financial category name
        
    Returns:
        tuple: (type_id, metric_id, submetric_id) where each can be None if not found
    """
    # Get the row number (1-indexed) from the dataframe index
    row_number = row.name + 1  # Convert 0-indexed to 1-indexed

    # Get mappings for the category, defaulting to empty dictionaries if category not found
    type_mapping, metric_mapping, submetric_mapping = CATEGORY_MAPPINGS.get(
        category,
        ({}, {}, {})
    )

    # Get IDs from selected mappings
    return (
        type_mapping.get(row_number),
        metric_mapping.get(row_number),
        submetric_mapping.get(row_number)
    )
