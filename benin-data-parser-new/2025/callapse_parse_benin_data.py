import pandas as pd
import numpy as np
from openpyxl import load_workbook


def generate_data(sheet_name,
                  output_file_name,
                  required_rows,
                  collapse_type_row_mapping={},
                  collapse_category_row_mapping={},
                  collapse_subcategory_row_mapping={}
                  ):

    # Load the Excel file
    base_path = "benin-data-parser-new/2025"
    file_path = f'{base_path}/TBG Moov_Africa_Bénin DEC 2025 DF FINALE SL - Copy.xlsx'
    wb = load_workbook(file_path, read_only=True, data_only=True, keep_links=False)
    sheet = wb[sheet_name]

    data = sheet.values
    df = pd.DataFrame(data)

    year = 2025

    header_row = 4
    zero_index = 1

    entity_type_mapping = {
        "type":        "type",
        "category":    "category",
        "subcategory": "subcategory"
    }

    required_rows = [x - header_row - zero_index for x in required_rows]

    months_details_hash = {
        # "jan": {"date": f"01-01-{year}", "cols": "D:H"},
        # "feb": {"date": f"02-01-{year}", "cols": "J:N"},
        # "mar": {"date": f"03-01-{year}", "cols": "P:T"},
        # "apr": {"date": f"04-01-{year}", "cols": "V:AB"},
        # "may": {"date": f"05-01-{year}", "cols": "AD:AJ"},
        # "jun": {"date": f"06-01-{year}", "cols": "AL:AS"},
        # "jul": {"date": f"07-01-{year}", "cols": "AU:BA"},
        # "aug": {"date": f"08-01-{year}", "cols": "BC:BI"},
        # "sep": {"date": f"09-01-{year}", "cols": "BK:BR"},
        # "oct": {"date": f"10-01-{year}", "cols": "BT:BZ"},
        # "nov": {"date": f"11-01-{year}", "cols": "CB:CH"},
        # "dec": {"date": f"12-01-{year}", "cols": "CJ:CP"},
        "cumul":  {"date": f"12-01-{year}", "cols": "CR:CX"},
        # "annual": {"date": f"01-01-{year}", "cols": "CZ:DH"}
    }

    dataframes = []
    annual_df  = None
    cumul_df   = None  # ← track cumul separately

    for month, valueDict in months_details_hash.items():

        print(f"Processing data for Month - {month}")

        monthly_data_df = pd.read_excel(
            file_path,
            sheet_name=sheet_name,
            header=header_row,
            usecols=valueDict["cols"],
            engine="openpyxl"
        )

        # Clean column names
        monthly_data_df.columns = monthly_data_df.columns.str.replace("\n", "")

        print(monthly_data_df.columns.tolist())

        column_prefixes = {
            "real_value":           "Réel",
            "budget_value":         f"{year} Budget",
            "actual1_value":        f"{year} Actu1",
            "actual2_value":        f"{year} Actu2",
            "actual3_value":        f"{year} Actu3",
            "last_year_real_value": "2024 Réel"
        }

        # Find matching columns dynamically
        matched_columns = {}
        for new_name, prefix in column_prefixes.items():
            for col in monthly_data_df.columns:
                if prefix in col:
                    matched_columns[col] = new_name
                    break

        # Rename and select columns
        monthly_data_df.rename(columns=matched_columns, inplace=True)
        existing_columns = list(matched_columns.values())
        monthly_data_df = monthly_data_df[existing_columns]

        # Map entity IDs and types
        for index, row in monthly_data_df.iterrows():
            updated_index = index + 1 + header_row + zero_index

            if updated_index in collapse_type_row_mapping.keys():
                monthly_data_df.at[index, "entity_id"]   = int(collapse_type_row_mapping[updated_index])
                monthly_data_df.at[index, "entity_type"] = entity_type_mapping["type"]
            elif updated_index in collapse_category_row_mapping.keys():
                monthly_data_df.at[index, "entity_id"]   = int(collapse_category_row_mapping[updated_index])
                monthly_data_df.at[index, "entity_type"] = entity_type_mapping["category"]
            elif updated_index in collapse_subcategory_row_mapping.keys():
                monthly_data_df.at[index, "entity_id"]   = int(collapse_subcategory_row_mapping[updated_index])
                monthly_data_df.at[index, "entity_type"] = entity_type_mapping["subcategory"]

        # Filter required rows
        monthly_data_df = monthly_data_df.iloc[[r - 1 for r in required_rows]]

        # Cast ID column
        monthly_data_df["entity_id"] = monthly_data_df["entity_id"].astype("Int64")

        # Set date
        monthly_data_df["date"] = valueDict["date"]

        # Track special months
        if month == "annual":
            annual_df = monthly_data_df
            dataframes.append(monthly_data_df)
        elif month == "cumul":
            cumul_df = monthly_data_df        # ← track cumul
            dataframes.append(monthly_data_df)
        else:
            dataframes.append(monthly_data_df)

    # ── Combine all dataframes ────────────────────────────────────────────────
    data_df = pd.concat(dataframes, ignore_index=True)
    data_df = data_df.replace(r'^\s*$', np.nan, regex=True)

    numeric_cols = [
        "real_value", "budget_value", "actual1_value",
        "actual2_value", "actual3_value", "last_year_real_value"
    ]
    for col in numeric_cols:
        if col in data_df.columns:
            data_df[col] = pd.to_numeric(data_df[col], errors='coerce')

    data_df = data_df.where(pd.notnull(data_df), None)

    # ── Save CSVs ─────────────────────────────────────────────────────────────
    output_data = f"{base_path}/may_collapsible_output"

    # Main CSV
    data_df.to_csv(f"{output_data}/{output_file_name}.csv", index=False)
    print(f"✓ Main CSV saved      : {output_file_name}.csv")

    # Annual CSV
    if annual_df is not None:
        annual_df.to_csv(f"{output_data}/annual_{output_file_name}.csv", index=False)
        print(f"✓ Annual CSV saved    : annual_{output_file_name}.csv")

    # Cumulative CSV
    if cumul_df is not None:
        cumul_df.to_csv(f"{output_data}/cumulative_{output_file_name}.csv", index=False)
        print(f"✓ Cumulative CSV saved: cumulative_{output_file_name}.csv")