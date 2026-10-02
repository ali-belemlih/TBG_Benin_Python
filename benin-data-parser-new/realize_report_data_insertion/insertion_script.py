import argparse
import pandas as pd
import psycopg2
from psycopg2.extras import execute_values

# ── Config ────────────────────────────────────────────────────────────────────

EXCEL_PATH = "benin-data-parser-new/realize_report_data_insertion/input_data/TBG Moov_Africa_Bénin DEC 2025 DF FINALE SL.xlsx"

SHEET_NAME = "Réalisé de trésorerie"
CSV_OUTPUT_DIR = "output_csv"  # directory to save CSV files

DB_CONFIG = {
    "host":     "10.16.27.53",
    "port":     5432,
    "dbname":   "digiwise_db",
    "user":     "archive",
    "password": "@rchivE1234",
}

# ── Column Mapping (0-indexed) ────────────────────────────────────────────────

COLUMN_MAPPING = {
    "last_year_total":    3,   # col D
    "current_year_total": 4,   # col E
    "jan": 5,                  # col F
    "feb": 6,                  # col G
    "mar": 7,                  # col H
    "apr": 8,                  # col I
    "may": 9,                  # col J
    "jun": 10,                 # col K
    "jul": 11,                 # col L
    "aug": 12,                 # col M
    "sep": 13,                 # col N
    "oct": 14,                 # col O
    "nov": 15,                 # col P
    "dec": 16,                 # col Q
}

MONTH_ORDER = ["jan", "feb", "mar", "apr", "may", "jun",
               "jul", "aug", "sep", "oct", "nov", "dec"]

# ── Row Mapping ───────────────────────────────────────────────────────────────

from mappings.mapping import MAPPING

# ── Argument Parsing ──────────────────────────────────────────────────────────

def parse_args():
    parser = argparse.ArgumentParser(
        description="Sync cashflow data from Excel into PostgreSQL up to a given month."
    )
    parser.add_argument("--version-id", type=int, required=True,
                        help="version_id to sync data for")
    parser.add_argument("--year",       type=int, required=True,
                        help="year for the data (e.g. 2025)")
    parser.add_argument("--month",      type=str, required=True,
                        choices=MONTH_ORDER,
                        help="month to sync up to e.g. 'jan', 'feb', ..., 'dec'")
    return parser.parse_args()

# ── Active Months ─────────────────────────────────────────────────────────────

def get_active_months(up_to_month: str) -> list:
    idx = MONTH_ORDER.index(up_to_month)
    return MONTH_ORDER[:idx + 1]

# ── Excel Reading ─────────────────────────────────────────────────────────────

def read_excel() -> pd.DataFrame:
    df = pd.read_excel(
        EXCEL_PATH,
        sheet_name=SHEET_NAME,
        header=None,
        index_col=None,
        engine='openpyxl'
    )
    return df

# ── Row Extraction ────────────────────────────────────────────────────────────

def get_row(df: pd.DataFrame, row_number: int) -> pd.Series:
    pandas_index = row_number - 1
    if pandas_index < 0 or pandas_index >= len(df):
        raise IndexError(
            f"row_number={row_number} maps to pandas index {pandas_index}, "
            f"out of bounds (df has {len(df)} rows)."
        )
    return df.iloc[pandas_index]

# ── Value Extraction ──────────────────────────────────────────────────────────

def get_val(excel_row: pd.Series, col_index: int):
    try:
        val = excel_row.iloc[col_index]
        return None if pd.isna(val) else float(val)
    except (ValueError, TypeError):
        return None

# ── Build DB Rows ─────────────────────────────────────────────────────────────

def build_rows(df: pd.DataFrame, version_id: int, year: int, active_months: list) -> list:
    rows = []
    for label, meta in MAPPING.items():
        entity_id   = meta["entity_id"]
        entity_type = meta["entity_type"]
        row_number  = meta["row_number"]

        try:
            excel_row = get_row(df, row_number)
        except IndexError as e:
            print(f"  ⚠ Skipping '{label}': {e}")
            continue

        monthly = {}
        for month in MONTH_ORDER:
            if month in active_months:
                monthly[month] = get_val(excel_row, COLUMN_MAPPING[month])
            else:
                monthly[month] = None

        rows.append((
            entity_id,
            entity_type,
            year,
            get_val(excel_row, COLUMN_MAPPING["last_year_total"]),
            get_val(excel_row, COLUMN_MAPPING["current_year_total"]),
            monthly["jan"], monthly["feb"], monthly["mar"],
            monthly["apr"], monthly["may"], monthly["jun"],
            monthly["jul"], monthly["aug"], monthly["sep"],
            monthly["oct"], monthly["nov"], monthly["dec"],
            version_id,
        ))

        print(
            f"  ✓ '{label}' "
            f"(entity_id={entity_id}, entity_type='{entity_type}', row={row_number}) "
            f"— months: {', '.join(active_months)}"
        )

    return rows

# ── Rows to DataFrame ─────────────────────────────────────────────────────────

DB_COLUMNS = [
    "entity_id", "entity_type", "year",
    "last_year_total", "current_year_total",
    "jan", "feb", "mar", "apr", "may", "jun",
    "jul", "aug", "sep", "oct", "nov", "dec",
    "version_id"
]

def rows_to_dataframe(rows: list) -> pd.DataFrame:
    return pd.DataFrame(rows, columns=DB_COLUMNS)

# ── Save to CSV ───────────────────────────────────────────────────────────────

def save_to_csv(rows: list, version_id: int, year: int, month: str):
    import os
    os.makedirs(CSV_OUTPUT_DIR, exist_ok=True)

    csv_path = os.path.join(
        CSV_OUTPUT_DIR,
        f"cashflow_v{version_id}_{year}_{month}.csv"
    )

    df = rows_to_dataframe(rows)
    df.to_csv(csv_path, index=False)
    print(f"\n✓ CSV saved to: {csv_path}")

# ── SQL ───────────────────────────────────────────────────────────────────────

# ── SQL ───────────────────────────────────────────────────────────────────────
UPDATE_SQL = """
    UPDATE cashflow_data AS target
    SET
        last_year_total    = data.last_year_total,
        current_year_total = data.current_year_total,
        jan = data.jan, feb = data.feb, mar = data.mar,
        apr = data.apr, may = data.may, jun = data.jun,
        jul = data.jul, aug = data.aug, sep = data.sep,
        oct = data.oct, nov = data.nov, "dec" = data.dec
    FROM (VALUES %s) AS data (
        entity_id, entity_type, year,
        last_year_total, current_year_total,
        jan, feb, mar, apr, may, jun,
        jul, aug, sep, oct, nov, dec,
        version_id
    )
    WHERE target.entity_id   = data.entity_id
      AND target.entity_type = data.entity_type::varchar
      AND target.year        = data.year
      AND target.version_id  = data.version_id;
"""

INSERT_SQL = """
    INSERT INTO cashflow_data (
        entity_id, entity_type, year,
        last_year_total, current_year_total,
        jan, feb, mar, apr, may, jun,
        jul, aug, sep, oct, nov, "dec",
        version_id
    )
    SELECT
        data.entity_id,
        data.entity_type,
        data.year,
        data.last_year_total,
        data.current_year_total,
        data.jan, data.feb, data.mar,
        data.apr, data.may, data.jun,
        data.jul, data.aug, data.sep,
        data.oct, data.nov, data.dec,
        data.version_id
    FROM (VALUES %s) AS data (
        entity_id, entity_type, year,
        last_year_total, current_year_total,
        jan, feb, mar, apr, may, jun,
        jul, aug, sep, oct, nov, dec,
        version_id
    )
    WHERE NOT EXISTS (
        SELECT 1 FROM cashflow_data AS target
        WHERE target.entity_id   = data.entity_id
          AND target.entity_type = data.entity_type::varchar
          AND target.year        = data.year
          AND target.version_id  = data.version_id
    );
"""

def sync_to_db(rows: list):
    if not rows:
        print("No rows to process.")
        return

    template = """(
        %s::int,
        %s::varchar,
        %s::int,
        %s::float8,
        %s::float8,
        %s::float8, %s::float8, %s::float8,
        %s::float8, %s::float8, %s::float8,
        %s::float8, %s::float8, %s::float8,
        %s::float8, %s::float8, %s::float8,
        %s::int
    )"""

    conn = psycopg2.connect(**DB_CONFIG)
    try:
        with conn:
            with conn.cursor() as cur:
                # Step 1: Update existing rows
                execute_values(cur, UPDATE_SQL, rows, template=template)
                updated = cur.rowcount
                print(f"  → Updated  : {updated} rows")

                # Step 2: Insert new rows
                execute_values(cur, INSERT_SQL, rows, template=template)
                inserted = cur.rowcount
                print(f"  → Inserted : {inserted} rows")

        print(f"\n✓ Synced {len(rows)} rows successfully (inserted or updated).")
    except Exception as e:
        print(f"\n✗ Database error: {e}")
        raise
    finally:
        conn.close()
# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    args = parse_args()
    active_months = get_active_months(args.month)

    print(f"Version ID     : {args.version_id}")
    print(f"Year           : {args.year}")
    print(f"Month          : {args.month.upper()} (populating: {', '.join(active_months)})")
    print(f"Excel          : {EXCEL_PATH} | Sheet: {SHEET_NAME}\n")

    df = read_excel()
    print(f"Loaded {len(df)} rows, {len(df.columns)} columns from Excel.\n")

    print("Processing rows...")
    rows = build_rows(df, version_id=args.version_id, year=args.year, active_months=active_months)

    print(f"\nTotal rows built : {len(rows)}")
    print(f"Active months    : {', '.join(active_months)}\n")

    # Save to CSV
    save_to_csv(rows, version_id=args.version_id, year=args.year, month=args.month)

    # Preview
    print("\nPreview:")

    # Sync to DB
    sync_to_db(rows)

if __name__ == "__main__":
    main()