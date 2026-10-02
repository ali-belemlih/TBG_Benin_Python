import psycopg2
from datetime import datetime

def get_collapse_monthly_data(conn):
    """Fetch Collapse Monthly data sorted by date."""
    query = """
    SELECT entity_id, entity_type, date,
           real_value, budget_value, last_year_real_value,
           actual1_value, actual2_value, actual3_value
    FROM public.collapse_monthly_data
    ORDER BY entity_type, entity_id, date
    """
    with conn.cursor() as cur:
        cur.execute(query)
        return cur.fetchall()

def insert_cumulative_data(conn, cumulative_data):
    """Insert records into collapse_cumul_data table."""
    query = """
    INSERT INTO public.collapse_cumul_data (
        entity_id, entity_type, date,
        real_value, budget_value, last_year_real_value,
        actual1_value, actual2_value, actual3_value
    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    with conn.cursor() as cur:
        cur.executemany(query, cumulative_data)
        conn.commit()

def generate_cumulative_data(conn):
    data = get_collapse_monthly_data(conn)
    cumulative_dict = {}
    cumulative_data = []
    
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
        
        # Compute cumulative values
        cumulative_dict[key]["real_value"] += real_value
        cumulative_dict[key]["budget_value"] += budget_value
        cumulative_dict[key]["last_year_real_value"] += last_year_real_value
        
        # Extract month from date (stored as YYYY-MM-DD)
        if isinstance(date, datetime):
            date_obj = date
        else:
            date_obj = datetime.strptime(str(date), "%Y-%m-%d")
        
        month_name = date_obj.strftime("%b").lower()  # Converts '2025-04-01' -> 'apr'
        month = date_obj.month
        
        # Store monthly real_value
        cumulative_dict[key][month_name] += real_value

        jan_mar_reel = cumulative_dict[key]["jan"] + cumulative_dict[key]["feb"] + cumulative_dict[key]["mar"]
        jan_may_reel = cumulative_dict[key]["apr"] + cumulative_dict[key]["may"] + jan_mar_reel
        jan_aug_reel = cumulative_dict[key]["jun"] + cumulative_dict[key]["jul"] + cumulative_dict[key]["aug"] + jan_may_reel

        if month == 4: # April
            cumulative_dict[key]["actual1_value"] += actual1_value
            actual1_value = cumulative_dict[key]["actual1_value"] + jan_mar_reel

        elif month == 5: # May
            cumulative_dict[key]["actual1_value"] += actual1_value
            actual1_value = cumulative_dict[key]["actual1_value"] + jan_mar_reel

        elif month == 6: # June
            cumulative_dict[key]["actual2_value"] += actual2_value
            actual1_value = actual1_value + cumulative_dict[key]["actual1_value"] + jan_mar_reel

        elif month == 7: # July
            cumulative_dict[key]["actual2_value"] += actual2_value
            actual2_value = cumulative_dict[key]["actual2_value"] + jan_may_reel

        elif month == 8: # August
            cumulative_dict[key]["actual2_value"] += actual2_value
            actual2_value = cumulative_dict[key]["actual2_value"] + jan_may_reel

        elif month == 9: # September
            cumulative_dict[key]["actual3_value"] += actual3_value
            actual2_value = actual2_value + cumulative_dict[key]["actual2_value"] + jan_may_reel

        elif month == 10: # October
            cumulative_dict[key]["actual3_value"] += actual3_value
            actual3_value = cumulative_dict[key]["actual3_value"] + jan_aug_reel

        elif month == 11: # November
            cumulative_dict[key]["actual3_value"] += actual3_value
            actual3_value = cumulative_dict[key]["actual3_value"] + jan_aug_reel

        elif month == 12: # December
            cumulative_dict[key]["actual3_value"] += actual3_value
            actual3_value = cumulative_dict[key]["actual3_value"] + jan_aug_reel

        if month <= 3:
            actual1_value, actual2_value, actual3_value = None, None, None
        elif month in [4, 5, 6]:  # Q2 (April - June)
            actual2_value, actual3_value = None, None
        elif month in [7, 8, 9]:  # Q3 (July - Sep)
            actual1_value, actual3_value = None, None
        elif month in [10, 11, 12]:  # Q4 (Oct - Dec)
            actual1_value, actual2_value = None, None

        cumulative_data.append(
            (entity_id, entity_type, date,
             cumulative_dict[key]["real_value"], cumulative_dict[key]["budget_value"],
             cumulative_dict[key]["last_year_real_value"], actual1_value, actual2_value, actual3_value)
        )

    insert_cumulative_data(conn, cumulative_data)

def establish_connection():
    """Establish database connection."""
    return psycopg2.connect(
        dbname="digiwise_db_apr16",
        user="digiwise_rw",
        password="digiwise_rw",
        host="13.234.6.83"
    )

# Example usage
if __name__ == "__main__":
    conn = establish_connection()
    generate_cumulative_data(conn)
    conn.close()
