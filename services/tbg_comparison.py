import openpyxl
from openpyxl.styles import PatternFill
from openpyxl.comments import Comment
import os
import json

# Base dir is the folder where tbg_comparison.py is located
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# === File paths ===
folder = "/home/akashdixitks45/Downloads"
file_master = os.path.join(folder, "TBG Moov_Africa_Bénin AVR 2026 DF SL.xlsx")
file_gen    = os.path.join(folder,"TBG_20260413_144103.xlsx")
output_file = os.path.join(folder, "compared_tbg_april.xlsx")
config_file = os.path.join(BASE_DIR, "configs", "comparsion_configs.json")

# === Load configs ===
with open(config_file, "r", encoding="utf-8") as f:
    sheets_to_compare = json.load(f)

# === Fill colors ===
yellow_fill = PatternFill(start_color="FFFF00", end_color="FFFF00", fill_type="solid")
orange_fill = PatternFill(start_color="FFA500", end_color="FFA500", fill_type="solid")
red_fill    = PatternFill(start_color="FF0000", end_color="FF0000", fill_type="solid")

# === Helpers ===
def col_letter_to_index(col):
    return openpyxl.utils.column_index_from_string(col)

def normalize_value(val):
    """Normalize numeric values for comparison. Treats None, empty string, and '-' as None."""
    if val is None or val == "" or str(val).strip() == "-":  # ← treat dash as None
        return None
    try:
        return round(float(str(val).replace(",", "")), 4)
    except ValueError:
        return str(val).strip()

# === Load workbooks ===
wb_master = openpyxl.load_workbook(file_master, data_only=True, keep_links=False)
wb_gen    = openpyxl.load_workbook(file_gen, data_only=True)

# === Summary results ===
summary_results = []

# === Compare for each sheet ===
for sheet in sheets_to_compare:
    sheet_name = sheet["name"]
    print(f"🔎 Comparing sheet: {sheet_name}")

    ws_master = wb_master[sheet_name]
    ws_gen    = wb_gen[sheet_name]

    start_row = sheet["start_row"]
    start_col = col_letter_to_index(sheet["start_col"])
    end_col   = col_letter_to_index(sheet["end_col"])

    total_cells, matched_cells, unmatched_cells = 0, 0, 0

    for row in range(start_row, ws_master.max_row + 1):
        for col in range(start_col, end_col + 1):
            val_master = ws_master.cell(row=row, column=col).value
            val_gen    = ws_gen.cell(row=row, column=col).value

            norm_master = normalize_value(val_master)
            norm_gen    = normalize_value(val_gen)

            # Skip if both are None/0 (includes '-' now)
            if (norm_master in (None, 0)) and (norm_gen in (None, 0)):
                continue

            total_cells += 1

            if norm_master == norm_gen:
                matched_cells += 1
                continue

            # ← One is None/dash and the other is None/dash — count as matched, don't highlight
            if (norm_master is None and norm_gen in (None, 0)) or \
               (norm_gen is None and norm_master in (None, 0)):
                matched_cells += 1
                continue

            unmatched_cells += 1

            # Coloring mismatches
            cell = ws_gen.cell(row=row, column=col)
            diff = None

            if isinstance(norm_master, (int, float)) and isinstance(norm_gen, (int, float)):
                diff = round(norm_gen - norm_master, 4)
                if int(norm_master) == int(norm_gen) and norm_master != norm_gen:
                    cell.fill = yellow_fill
                elif 0.1 < abs(diff) < 0.9:
                    cell.fill = orange_fill
                else:
                    cell.fill = red_fill
            else:
                cell.fill = red_fill

            # Add comment with values
            comment_text = (
                f"Generated file value: {val_gen}\n"
                f"Master file value: {val_master}\n"
                f"Difference: {diff if diff is not None else 'N/A'}"
            )
            cell.comment = Comment(comment_text, "Comparator")

    # === Save summary for this sheet ===
    if total_cells > 0:
        matched_pct   = (matched_cells / total_cells) * 100
        unmatched_pct = (unmatched_cells / total_cells) * 100
        print(f"📊 {sheet_name}: {matched_pct:.2f}% matched, {unmatched_pct:.2f}% unmatched "
              f"({matched_cells} matched, {unmatched_cells} unmatched out of {total_cells})")
        summary_results.append([
            sheet_name, total_cells, matched_cells, unmatched_cells,
            f"{matched_pct:.2f}%", f"{unmatched_pct:.2f}%"
        ])
    else:
        print(f"⚠️ {sheet_name}: No comparable cells found.")
        summary_results.append([sheet_name, 0, 0, 0, "0.00%", "0.00%"])

# === Add summary sheet ===
ws_summary = wb_gen.create_sheet("Comparison_Summary")
ws_summary.append(["Sheet Name", "Total Cells", "Matched", "Unmatched", "% Matched", "% Unmatched"])
for row in summary_results:
    ws_summary.append(row)

# === Save compared file ===
wb_gen.save(output_file)
print(f"✅ Comparison completed. Output saved as {output_file}")