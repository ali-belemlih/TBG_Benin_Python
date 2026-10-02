import pandas as pd
import psycopg2
from datetime import datetime
import logging
from helpers.parse_arg import parse_arguments
from helpers.db_utils import get_db_connection, get_version_id_by_name, upsert_collapse_cumulative_data
from helpers.cumul_helper import get_collapse_monthly_data

def generate_cumulative_data(conn, version_id, month_year):
    data = get_collapse_monthly_data(conn, month_year, version_id)
    cumulative_dict = {}
    cumulative_data = []

    # Parse month_year to get the month number
    target_month = int(month_year[:2])
    target_year = int(month_year[2:])

    for row in data:
        entity_id, entity_type, date, real_value, budget_value, last_year_real_value, actual1_value, actual2_value, actual3_value = row
        key = f"{entity_id}-{entity_type}"

        # Initialize cumulative storage
        if key not in cumulative_dict:
            cumulative_dict[key] = {
                "real_value": 0, "budget_value": 0, "last_year_real_value": 0,
                "jan": 0, "feb": 0, "mar": 0, "apr": 0, "may": 0, "jun": 0,
                "jul": 0, "aug": 0, "sep": 0, "oct": 0, "nov": 0, "dec": 0,
                "actual1_value": 0, "actual2_value": 0, "actual3_value": 0
            }

        # Handle null values by treating them as zero where applicable
        real_value = real_value if real_value is not None else 0
        budget_value = budget_value if budget_value is not None else 0
        last_year_real_value = last_year_real_value if last_year_real_value is not None else 0
        actual1_value = actual1_value if actual1_value is not None else 0
        actual2_value = actual2_value if actual2_value is not None else 0
        actual3_value = actual3_value if actual3_value is not None else 0

        # Compute cumulative values for the specified month
        cumulative_dict[key]["real_value"] += real_value
        cumulative_dict[key]["budget_value"] += budget_value
        cumulative_dict[key]["last_year_real_value"] += last_year_real_value

        # Extract month from date (stored as YYYY-MM-DD)
        if isinstance(date, datetime):
            date_obj = date
        else:
            date_obj = datetime.strptime(str(date), "%Y-%m-%d")

        month = date_obj.month
        year = date_obj.year

        # Store monthly real_value only for the specified month
        month_name = date_obj.strftime("%b").lower()  # Converts '2025-04-01' -> 'apr'
        cumulative_dict[key][month_name] += real_value

        # Calculate cumulative sums for specific periods
        jan_mar_reel = cumulative_dict[key]["jan"] + cumulative_dict[key]["feb"] + cumulative_dict[key]["mar"]
        jan_may_reel = cumulative_dict[key]["apr"] + cumulative_dict[key]["may"] + jan_mar_reel
        jan_aug_reel = cumulative_dict[key]["jun"] + cumulative_dict[key]["jul"] + cumulative_dict[key]["aug"] + jan_may_reel
        # Apply logic based on the specified month
        
        # Initialize cumulative tracking
        if key not in cumulative_dict:
            cumulative_dict[key] = {
                "actual1_value": 0,
                "actual2_value": 0,
                "actual3_value": 0
            }

        # Handle Q2 (Apr–Jun)
        if month in [4, 5]:
            cumulative_dict[key]["actual1_value"] += actual1_value or 0
            actual1_value = cumulative_dict[key]["actual1_value"] + jan_mar_reel

        elif month == 6:  # June
            # Always calculate Actual1
            cumulative_dict[key]["actual1_value"] += actual1_value or 0
            actual1_value = cumulative_dict[key]["actual1_value"] + jan_mar_reel

            # If target_month == 6 → calculate Actual2 as well
            if target_month == 6:
                cumulative_dict[key]["actual2_value"] += actual2_value or 0
                actual2_value = cumulative_dict[key]["actual2_value"] + jan_may_reel

        # Handle Q3 (Jul–Sep)
        elif month in [7, 8]:
            cumulative_dict[key]["actual2_value"] += actual2_value or 0
            actual2_value = cumulative_dict[key]["actual2_value"] + jan_may_reel

        elif month == 9:  # September
            # Always calculate Actual2
            cumulative_dict[key]["actual2_value"] += actual2_value or 0
            actual2_value = cumulative_dict[key]["actual2_value"] + jan_may_reel
            
            cumulative_dict[key]["actual3_value"] += actual3_value or 0
            actual3_value = cumulative_dict[key]["actual3_value"] + jan_aug_reel

        # Handle Q4 (Oct–Dec)
        elif month in [10, 11, 12]:
            cumulative_dict[key]["actual3_value"] += actual3_value or 0
            actual3_value = cumulative_dict[key]["actual3_value"] + jan_aug_reel

        # Handle Q1 (Jan–Mar)
        else:
            actual1_value, actual2_value, actual3_value = None, None, None

        # Disable non-applicable actuals based on quarter
        if month <= 3:
            actual1_value, actual2_value, actual3_value = None, None, None
        elif 4 <= month <= 6:  # Q2 (Apr–Jun)
            actual2_value, actual3_value = (actual2_value if target_month == 6 else None), None
        elif 7 <= month <= 9:  # Q3 (Jul–Sep)
            actual1_value, actual3_value = None, (actual3_value if target_month == 9 else None)
        elif 10 <= month <= 12:  # Q4 (Oct–Dec)
            actual1_value, actual2_value = None, None

        if year == target_year and month == target_month:
            cumulative_data.append(
                (entity_id, entity_type, date,
                 cumulative_dict[key]["real_value"], cumulative_dict[key]["budget_value"],
                 cumulative_dict[key]["last_year_real_value"], actual1_value, actual2_value, actual3_value)
            )
    df = pd.DataFrame(cumulative_data)
    df.columns = [
        "entity_id",
        "entity_type",
        "date",
        "real_value",
        "budget_value",
        "last_year_real_value",
        "actual1_value",
        "actual2_value",
        "actual3_value"
    ]
    # df.to_csv('/home/yuvrajksi199/workspace/digiwise/benin_parser_2025/cumul_import/outputs/collapse_cumulative_data.csv', index = False)

    upsert_collapse_cumulative_data(conn, cumulative_data, version_id)

if __name__ == "__main__":
    args = parse_arguments()
    month_year = args.month_year  # Expected format: MMYYYY (e.g., '012025' for Jan 2025)

    version_id = get_version_id_by_name(args.version_id)
    conn = get_db_connection()
    generate_cumulative_data(conn, version_id, month_year)
