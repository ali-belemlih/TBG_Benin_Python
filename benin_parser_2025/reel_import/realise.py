import sys
import os
import pandas as pd
from io import BytesIO
from datetime import datetime
from .mapping.realise_mapping import (
    categories, subcategories, sections, months,
    month_column_mapping, dette_nette_mappings
)

from contextlib import closing
from helpers.db_utils import get_db_connection, upsert_cashflow_month_data, get_version_id_by_name
from services.minio_factory import get_minio_service
from tbg_formula.formula_evaluator import evaluate_tbg_formula
from tbg_formula.db_helper import get_tbg_report_mapping, find_tbg_key_in_table


def get_entity(idx):
    if categories.get(idx):
        return categories[idx], 'category'
    if sections.get(idx):
        return sections[idx], 'section'
    if subcategories.get(idx):
        return subcategories[idx], 'subcategory'
    return '', ''

def clean_and_scale_millions(value):
    try:
        if pd.isna(value):
            return 0.0
        value = str(value).replace(",", "").replace(" ", "").strip()
        if value in ["", "-", "NaN"]:
            return 0.0
        return float(value) / 1_000_000
    except Exception as e:
        print(f"⚠️ Could not convert value '{value}': {e}")
        return 0.0

def col_letter_to_index(letter):
    return ord(letter.upper()) - ord('A')

def parse_number_with_commas(value):
    """Convert number strings like '51,36,29,764' to float 513629764.0"""
    try:
        return float(str(value).replace(',', '').replace(' ', ''))
    except:
        return 0.0

def insert_data_from_dette_nette(date, dn_file_bytes, version_id):
    year = date.year
    month_index = date.month
    month_name_fr = list(month_column_mapping.keys())[month_index - 1]
    month_col_letter = month_column_mapping[month_name_fr]
    month_col_index = col_letter_to_index(month_col_letter)
    print(f"Year: {year}, month_index: {month_index}, month_name_fr: {month_name_fr}, month_col_letter: {month_col_letter}, month_col_index: {month_col_index}")
    df = pd.read_excel(BytesIO(dn_file_bytes), header=None, engine="openpyxl")

    # Strip text in column C to allow reliable match
    df.iloc[:, 2] = df.iloc[:, 2].astype(str).str.strip().str.upper()

    conn = get_db_connection()
    cur = conn.cursor()

    for item in dette_nette_mappings:
        metric_name = item['metric_name'].upper()
        matched = df[df.iloc[:, 2] == metric_name]

        if matched.empty:
            print(f"[WARN] Metric '{metric_name}' not found.")
            continue

        row = matched.iloc[0]
        current_year_total = row.iloc[4]
        value = row.iloc[month_col_index]
        print(f"Current Year Total: {current_year_total}, Value: {value}")

        try:
            upsert_cashflow_month_data(
                cur,
                entity_id=item['id'],
                entity_type=item['type'],
                year=year,
                month=months[month_index],
                value=float(value) if pd.notnull(value) else None,
                version_id=version_id,
                current_year_total=float(current_year_total) if pd.notnull(current_year_total) else None
            )
            print(f"[INFO] Inserted: {metric_name} - {month_name_fr} - {value}")
        except Exception as e:
            print(f"[ERROR] Failed for {metric_name}: {e}")

    conn.commit()
    cur.close()
    conn.close()

def process_bouclage_data(date, bouclage_file_bytes, version_id):
    year = date.year
    month_index = date.month

    month_name = months[month_index]

    # Read Excel sheet
    df = pd.read_excel(BytesIO(bouclage_file_bytes), sheet_name='SYNTHESE', header=None, engine="openpyxl")

    # ---------- 1. Sum RECETTES rows (6–9 → index 5 to 8), column E (index 4) ----------
    print("[DEBUG] --- RECETTES ROWS ---")
    recettes_values = df.iloc[5:9, 4].apply(parse_number_with_commas)
    for idx, val in enumerate(recettes_values, start=6):
        print(f"Row {idx + 1}: {val}")
    recettes_total = recettes_values.sum()/1_000_000
    print(f"[DEBUG] Total RECETTES SUM (row 6–9 col E): {recettes_total}")

    # ---------- 2. Subtract cell L19 - L55 ----------
    def get_cell_value(col_letter, row_number):
        """Convert cell reference to DataFrame value"""
        col_idx = ord(col_letter.upper()) - ord('A')
        row_idx = row_number - 1
        if row_idx < len(df) and col_idx < df.shape[1]:
            return parse_number_with_commas(df.iloc[row_idx, col_idx])
        return 0.0

    l19 = get_cell_value('E', 19)
    l55 = get_cell_value('E', 55)
    diff_value = (l19 - l55)/1_000_000
    l55_millions = l55 / 1_000_000

    print(f"[DEBUG] L19 value: {l19}")
    print(f"[DEBUG] L55 value: {l55}")
    print(f"[DEBUG] L19 - L55 = {diff_value}")
    print(f"[DEBUG] L55 (in millions) = {l55_millions}")

    conn = get_db_connection()
    cur = conn.cursor()

    try:
        # Insert RECETTES total
        upsert_cashflow_month_data(
            cur,
            entity_id=4,
            entity_type='category',
            year=year,
            month=month_name,
            value=float(recettes_total),
            version_id=version_id,
            current_year_total=None
        )
        print(f"[INFO] Inserted RECETTES: {month_name.upper()} {year} => {recettes_total}")

        # Insert L19 - L55 difference
        upsert_cashflow_month_data(
            cur,
            entity_id=8,
            entity_type='subcategory',
            year=year,
            month=month_name,
            value=diff_value,
            version_id=version_id,
            current_year_total=None
        )
        print(f"[INFO] Inserted L19 - L55 (subcategory 8): {month_name.upper()} {year} => {diff_value}")

         # Insert L55 value directly
        upsert_cashflow_month_data(
            cur,
            entity_id=9,
            entity_type='category',
            year=year,
            month=month_name,
            value=float(l55_millions),
            version_id=version_id,
            current_year_total=None
        )
        print(f"[INFO] Inserted L55 (category 9): {month_name.upper()} {year} => {l55_millions}")


    except Exception as e:
        print(f"[ERROR] Insert failed: {e}")

    conn.commit()
    cur.close()
    conn.close()

def process_realise_tbg_formulas(month_year, date, version_id, report_type_id, is_adjustible_only=False):
    if len(month_year) != 6:
        raise ValueError(f"Invalid month_year format: {month_year}. Expected MMYYYY")
    month_num = int(month_year[:2])
    year = int(month_year[2:])
    if month_num not in months:
        raise ValueError(f"Invalid month number: {month_num}")

    results = []
    computed_cache = {}
    target_month_name = months[month_num]

    with closing(get_db_connection()) as conn:
        fetched_mapping = get_tbg_report_mapping(conn, report_type_id)
        if not fetched_mapping:
            print("❌ No record found for the passed report type.")
            return pd.DataFrame()

        for record in fetched_mapping:
            (
                formula_id,
                tbg_key,
                report_type_id,
                formula_type,
                account_details,
                include_sage,
                formula,
                is_adjustable,
                created_at,
                updated_at,
                sequence,
            ) = record

            if is_adjustible_only and not is_adjustable:
                continue

            base_record_found = find_tbg_key_in_table(conn, tbg_key)
            if not base_record_found:
                print(f"⚠ Base TBG key '{tbg_key}' not found. Skipping...")
                continue

            base_col_name, base_table, base_tbg_key_id = base_record_found

            value = evaluate_tbg_formula(
                conn,
                tbg_key,
                formula,
                version_id,
                computed_cache,
                date=date
            )

            # computed_cache[tbg_key] = value  # Save result for later formulas

            results.append({
                "label": tbg_key,
                "entity_type": base_col_name,
                "entity_id": base_tbg_key_id,
                "year": year,
                target_month_name: value,
                "version_id": version_id
            })

    realise_df = pd.DataFrame(results)
    output_csv_path = f'benin_parser_2025/reel_import/realise_tbg_formulas_{date}.csv'
    # realise_df.to_csv(output_csv_path, index=False)
    print(f"✅ CSV file for {date} generated successfully at: {output_csv_path}")
    return realise_df

def get_default_cashflow_data(conn, target_month_num, year):
    default_data = {}

    for month_num in range(1, target_month_num):
        month_name = months[month_num]

        with conn.cursor() as cur:
            # Fetch default version for this month/year
            cur.execute("""
                SELECT id FROM public.tbg_version
                WHERE is_default = true AND is_active = true
                AND month = %s AND year = %s
                ORDER BY created_at DESC
                LIMIT 1;
            """, (month_num, year))
            row = cur.fetchone()
            if not row:
                print(f"⚠️ No default version found for {month_name} {year}")
                continue

            default_version_id = row[0]
            print(f'Default Version for {month_name}: {default_version_id}')
            # Fetch cashflow data for that version/month
            cur.execute(f"""
                SELECT entity_id, entity_type, year, {month_name}
                FROM public.cashflow_data
                WHERE version_id = %s
            """, (default_version_id,))
            for entity_id, entity_type, data_year, value in cur.fetchall():
                key = (entity_id, entity_type)
                if key not in default_data:
                    default_data[key] = {'entity_id': entity_id, 'entity_type': entity_type, 'year': data_year}
                default_data[key][month_name] = value

    return list(default_data.values())

def process_realise_data(month_year, file_bytes, version, default_data):
    try:
        df = pd.read_excel(BytesIO(file_bytes), sheet_name='SYNTHESE', header=None, engine="openpyxl")

        if len(month_year) != 6:
            raise ValueError(f"Invalid month_year format: {month_year}. Expected MMYYYY")

        month_num = int(month_year[:2])
        year = int(month_year[2:])

        if month_num not in months:
            raise ValueError(f"Invalid month number: {month_num}")

        results_dict = {}

        # Step 1: Add default data from Jan to (target month - 1)
        for row in default_data:
            key = (row['entity_id'], row['entity_type'], row['year'])
            if key not in results_dict:
                results_dict[key] = {
                    'entity_id': row['entity_id'],
                    'entity_type': row['entity_type'],
                    'year': row['year'],
                    'version_id': version
                }
            for m in range(1, month_num):
                month_name = months[m]
                if month_name in row:
                    results_dict[key][month_name] = row[month_name]

        # Step 2: Add current month from uploaded file
        target_month_name = months[month_num]
        for idx, row in df.iterrows():
            row_number = idx + 1
            if row_number >= 3 and pd.notna(row[1]) and len(row) > 4:
                value = clean_and_scale_millions(row[4])
                if isinstance(value, (int, float)):
                    entity_id, entity_type = get_entity(row_number)
                    if entity_id != '':
                        key = (entity_id, entity_type, year)
                        if key not in results_dict:
                            results_dict[key] = {
                                'entity_id': entity_id,
                                'entity_type': entity_type,
                                'year': year,
                                'version_id': version
                            }
                        results_dict[key][target_month_name] = value

        # Convert dict to DataFrame
        # return pd.DataFrame(results_dict.values())

        realise_df = pd.DataFrame(results_dict.values())
        month_columns = [months[m] for m in range(1, int(month_year[:2]) + 1)]

        realise_df["current_year_total"] = realise_df[month_columns].fillna(0).sum(axis=1)
        output_csv_path = f'benin_parser_2025/reel_import/realise_mapping_{month_year}.csv'
        realise_df.to_csv(output_csv_path, index=False)
        print(f"✅ CSV file for {month_year} generated successfully at: {output_csv_path}")
        return realise_df

    except Exception as e:
        print(f"Error processing file: {str(e)}")
        raise

def insert_cashflow_data_to_db(df, month_year):
    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        year = int(month_year[2:])
        month_num = int(month_year[:2])

        rows_affected = 0

        for _, row in df.iterrows():
            entity_id = row['entity_id']
            entity_type = row['entity_type']
            version_id = row['version_id']
            current_year_total = row.get('current_year_total')

            for m in range(1, month_num + 1):
                month_name = months[m]
                value = row.get(month_name)

                # Insert only if value is present (including 0), skip if None
                if value is not None:
                    if pd.notna(value):
                        value = float(value)
                    else:
                        value = None

                    upsert_cashflow_month_data(
                        cur,
                        entity_id=entity_id,
                        entity_type=entity_type,
                        year=year,
                        month=month_name,
                        value=value,
                        version_id=version_id,
                        current_year_total=current_year_total
                    )
                    rows_affected += cur.rowcount

        print(f"Committing {rows_affected} changes to database...")
        conn.commit()
        print(f"✅ Successfully committed {rows_affected} records for Jan–{months[month_num]} {year}")

    except Exception as e:
        print(f"Error inserting data to database: {str(e)}")
        if conn:
            conn.rollback()
        raise
    finally:
        if conn:
            cur.close()
            conn.close()

def copy_section_values(version_id):
    conn = get_db_connection()
    cur = conn.cursor()

    copy_pairs = [
        (5, 6),
        (9, 10)
    ]

    try:
        for source_id, target_id in copy_pairs:
            # Step 1: Get jan value from source section
            cur.execute("""
                SELECT jan FROM public.cashflow_data
                WHERE entity_type = 'section'
                  AND entity_id = %s
                  AND version_id = %s
            """, (source_id, version_id))

            result = cur.fetchone()
            if not result:
                print(f"⚠️ No data found for section {source_id}, version {version_id}")
                continue

            jan_value = result[0]

            # Step 2: Update target section with the same jan value
            cur.execute("""
                UPDATE public.cashflow_data
                SET jan = %s,
                    current_year_total = %s
                WHERE entity_type = 'section'
                  AND entity_id = %s
                  AND version_id = %s
            """, (jan_value, jan_value, target_id, version_id))

            print(f"✅ Copied jan value ({jan_value}) from section {source_id} → section {target_id} for version {version_id}")

        conn.commit()
    except Exception as e:
        conn.rollback()
        print(f"❌ Failed to copy section values: {e}")
        raise
    finally:
        cur.close()
        conn.close()

def update_current_year_total(version_id, year, month_num):
    conn = get_db_connection()
    cur = conn.cursor()

    try:
        month_columns = [months[m] for m in range(1, month_num + 1)]

        # Build SQL sum dynamically
        sum_expr = " + ".join([
            f"COALESCE({col}, 0) + COALESCE(adjusted_{col}, 0)"
            for col in month_columns
        ])
        query = f"""
            UPDATE public.cashflow_data
            SET current_year_total = {sum_expr}
            WHERE version_id = %s
              AND year = %s;
        """

        print(f"[INFO] Updating current_year_total using: {sum_expr}")

        cur.execute(query, (version_id, year))
        affected = cur.rowcount

        conn.commit()
        print(f"✅ Updated current_year_total for {affected} rows")

    except Exception as e:
        conn.rollback()
        print(f"❌ Failed to update current_year_total: {e}")
        raise
    finally:
        cur.close()
        conn.close()

def update_special_entities_current_year_total(conn, version_id, year, month_num):
    """
    For specific entity_type/entity_id combos, set current_year_total
    to just the current month's value instead of cumulative sum.
    """
    target_month_col = months[int(month_num)]  # e.g. 'apr', 'may'

    special_entities = [
        ('section', 6),
        ('section', 13),
        ('section', 14),
        ('category', 12),
        ('category', 13),
        ('category', 15),
        ('category', 17),
    ]

    cur = conn.cursor()
    try:
        for entity_type, entity_id in special_entities:
            query = f"""
                UPDATE public.cashflow_data
                SET current_year_total = COALESCE({target_month_col}, 0) + COALESCE(adjusted_{target_month_col}, 0)
                WHERE version_id = %s
                AND year = %s
                AND entity_type = %s
                AND entity_id = %s;
            """
            cur.execute(query, (version_id, year, entity_type, entity_id))
            affected = cur.rowcount
            print(f"✅ [{entity_type} | id={entity_id}] current_year_total = {target_month_col}, rows affected: {affected}")

        conn.commit()
    except Exception as e:
        conn.rollback()
        print(f"❌ Failed to update special entities current_year_total: {e}")
        raise
    finally:
        cur.close()

def update_last_year_total(year):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        # Step 1: Fetch the default version for December of last year
        last_year = year - 1
        cur.execute("""
            SELECT id 
            FROM public.tbg_version
            WHERE year = %s
              AND month = 12
              AND is_default = true
              AND is_active = true
            LIMIT 1;
        """, (last_year,))
        
        row = cur.fetchone()
        if not row:
            print(f"❌ No default December version found for year {last_year}")
            return
        
        default_version_id = row[0]
        print(f"[INFO] Found default December version for {last_year}: version_id = {default_version_id}")

        # Step 2: Update last_year_total for the current year rows
        # using current_year_total from the default December version of last year
        query = """
            UPDATE public.cashflow_data curr
            SET last_year_total = COALESCE(prev.current_year_total, 0)
            FROM public.cashflow_data prev
            WHERE curr.entity_id = prev.entity_id
              AND curr.entity_type = prev.entity_type
              AND curr.year = %s
              AND prev.version_id = %s;
        """
        print(f"[INFO] Updating last_year_total for year {year} using version_id {default_version_id}")
        cur.execute(query, (year, default_version_id))
        affected = cur.rowcount
        conn.commit()
        print(f"✅ Updated last_year_total for {affected} rows")

    except Exception as e:
        conn.rollback()
        print(f"❌ Failed to update last_year_total: {e}")
        raise
    finally:
        cur.close()
        conn.close()

def main():
    if len(sys.argv) < 5:
        print("Usage: script.py <month_year MMYYYY> <version_name> <bouclage_filename or ''> <dette_nette_filename or ''>")
        sys.exit(1)

    month_year = sys.argv[1]
    if len(month_year) != 6 or not month_year.isdigit():
        raise ValueError("month_year must be in MMYYYY format, e.g., '062025'")

    target_month = month_year[:2]
    target_year = month_year[2:]

    version_id = get_version_id_by_name(sys.argv[2])
    bouclage = sys.argv[3].strip()
    dette_nette = sys.argv[4].strip()
    date = datetime(int(target_year), int(target_month), 1)

    minio_service = get_minio_service()
    conn = None

    try:
        conn = get_db_connection()

        default_data = get_default_cashflow_data(conn, int(target_month), int(target_year))

        # --- Bouclage ---
        bouclage_file_bytes = None
        if bouclage:
            bouclage_path = f"{target_year}/{target_year}{target_month}/{bouclage}"
            print(f"📥 Fetching Bouclage from: {bouclage_path}")
            bouclage_file_bytes = minio_service.get_file_bytes(object_name=bouclage_path)

            print("⚙️ Processing realisé data...")
            result_df = process_realise_data(month_year, bouclage_file_bytes, version_id, default_data)
            insert_cashflow_data_to_db(result_df, month_year)

            print("⚙️ Processing bouclage data...")
            process_bouclage_data(date, bouclage_file_bytes, version_id)
        else:
            print("ℹ️ No Bouclage file provided. Skipping bouclage-related processing...")

        # --- Dette Nette ---
        if dette_nette:
            dette_nette_path = f"{target_year}/{target_year}{target_month}/{dette_nette}"
            print(f"📥 Fetching Dette Nette from: {dette_nette_path}")
            dette_nette_file_bytes = minio_service.get_file_bytes(object_name=dette_nette_path)

            print("⚙️ Processing dette nette data...")
            insert_data_from_dette_nette(date, dette_nette_file_bytes, version_id)
        else:
            print("ℹ️ No Dette Nette file provided. Skipping dette nette-related processing...")

        # --- Always run ---
        print("⚙️ Processing TBG formulas...")
        realise_df = process_realise_tbg_formulas(month_year, date, version_id, 1000)
        insert_cashflow_data_to_db(realise_df, month_year)

        # --- Copy section values (January only) ---
        if int(target_month) == 1:
            print("⚙️ Copying January section values (5→6, 9→10)...")
            copy_section_values(version_id)
        else:
            print("ℹ️ Not January, skipping section copy...")
        
        # --- update the current year total ---
        print("⚙️ Updating current_year_total for all rows...")
        update_current_year_total(version_id, int(target_year), int(target_month))

        print("⚙️ Updating current_year_total for specific entities...")
        update_special_entities_current_year_total(conn, version_id, target_year, target_month)

        # --- Final Step ---
        print("⚙️ Updating last_year_total for all rows...")
        update_last_year_total(int(target_year))

        print("✅ All processing completed successfully.")

    except Exception as e:
        print(f"❌ Error: {str(e)}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    main()
