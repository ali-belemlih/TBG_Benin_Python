import pandas as pd

FILE_MONTH_MAPPING = {
    1: 'Janvier', 2: 'Février', 3: 'Mars', 4: 'Avril',
    5: 'Mai', 6: 'Juin', 7: 'Juillet', 8: 'Août',
    9: 'Septembre', 10: 'Octobre', 11: 'Novembre', 12: 'Décembre'
}

def safe_number(val):
    try:
        if pd.isna(val):
            return 0
        # Clean string: remove spaces, commas, etc.
        val = str(val).replace(",", "").replace(" ", "").strip()
        if val in ["", "-", "NaN"]:
            return 0
        num = float(val)
        # Cap to PostgreSQL BIGINT max
        if abs(num) > 9223372036854775807:
            print(f"⚠️ Value too large for BIGINT: {val}. Capping to max.")
            return 9223372036854775807
        return int(num)
    except Exception as e:
        print(f"⚠️ Invalid number: {val}. Error: {e}")
        return 0

def safe_date(val):
    if pd.isna(val) or str(val).strip().upper() in ["", "NAT", "NONE"]:
        return None
    try:
        return pd.to_datetime(val).to_pydatetime()
    except:
        return None
