import pandas as pd
import numpy as np
from openpyxl import load_workbook


def generate_data(sheet_name, output_file_name, required_rows, financial_type_row_mapping, financial_metric_row_mapping,
                  financial_submetric_row_mapping={}):
    # Load the Excel file
    base_path = "benin-data-parser-new/2025"
    file_path = f'{base_path}/TBG Moov_Africa_Bénin DEC 2025 DF FINALE SL - Copy.xlsx'

    wb = load_workbook(file_path, read_only=True, data_only=True, keep_links=False)
    sheet = wb[sheet_name]

    data = sheet.values
    df = pd.DataFrame(data)

    if sheet_name == "Data Mobile" or sheet_name == "Mobile Money":
        header_row = 2
    else:
        header_row = 4

    zero_index = 1
    required_rows = [x - header_row - zero_index for x in required_rows]

    year = 2025

    if sheet_name == 'Mobile Money':
        months_details_hash = {
            # "jan": {"date": f"01-01-{year}", "cols": "D:H"},
            # "feb": {"date": f"02-01-{year}", "cols": "J:N"},
            # "mar": {"date": f"03-01-{year}", "cols": "P:T"},
            # "apr": {"date": f"04-01-{year}", "cols": "V:AB"},
            # "may": {"date": f"05-01-{year}", "cols": "AD:AJ"},
            # "jun": {"date": f"06-01-{year}", "cols": "AL:AR"},
            # "jul": {"date": f"07-01-{year}", "cols": "AT:AZ"},
            # "aug": {"date": f"08-01-{year}", "cols": "BB:BH"},
            # "sep": {"date": f"09-01-{year}", "cols": "BJ:BQ"},
            # "oct": {"date": f"10-01-{year}", "cols": "BS:BY"},
            # "nov": {"date": f"11-01-{year}", "cols": "CA:CG"},
            # "dec": {"date": f"12-01-{year}", "cols": "CI:CO"},
            "cumul": {"date": f"12-01-{year}", "cols": "CQ:CW"},
            # "annual": {"date": f"01-01-{year}", "cols": "CY:DG"}
        }
    else:
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
            "cumul": {"date": f"12-01-{year}", "cols": "CR:CX"},
            # "annual": {"date": f"01-01-{year}", "cols": "CZ:DH"}
        }

    dataframes  = []
    annual_df   = None
    cumul_df    = None  # ← track cumul separately

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

        # Define column name mappings
        print(f"Réel {year}")
        if sheet_name == "Data Mobile":
            column_prefixes = {
                "real_value":           f"Réel {year}",
                "budget_value":         "Budget",
                "actual1_value":        "Actu1",
                "actual2_value":        "Actu2",
                "actual3_value":        "Actu3",
                "last_year_real_value": f"Réel {year - 1}"
            }
        elif sheet_name == "Mobile Money":
            column_prefixes = {
                "real_value":           f"Réel {year}",
                "budget_value":         "Budget",
                "actual1_value":        "Actu 1",
                "actual2_value":        "Actu 2",
                "actual3_value":        "Actu 3",
                "last_year_real_value": f"Réel {year - 1}"
            }
        else:
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

        # Map financial IDs
        for index, row in monthly_data_df.iterrows():
            updated_index = index + 1 + header_row + zero_index

            if updated_index in financial_type_row_mapping.keys():
                monthly_data_df.at[index, "financial_type_id"] = int(financial_type_row_mapping[updated_index])
            elif updated_index in financial_metric_row_mapping.keys():
                monthly_data_df.at[index, "financial_metric_id"] = int(financial_metric_row_mapping[updated_index])
            elif updated_index in financial_submetric_row_mapping.keys():
                monthly_data_df.at[index, "financial_submetric_id"] = int(
                    financial_submetric_row_mapping[updated_index])

        # Filter required rows
        monthly_data_df = monthly_data_df.iloc[[r - 1 for r in required_rows]]

        # Cast ID columns
        monthly_data_df["financial_type_id"]   = monthly_data_df["financial_type_id"].astype("Int64")
        monthly_data_df["financial_metric_id"] = monthly_data_df["financial_metric_id"].astype("Int64")
        if "financial_submetric_id" in monthly_data_df.columns:
            monthly_data_df["financial_submetric_id"] = monthly_data_df["financial_submetric_id"].astype("Int64")

        # Apply multipliers
        if sheet_name == "Marge Mobile":
            columns_to_multiply = ["real_value", "budget_value", "actual1_value", "actual2_value", "actual3_value",
                                   "last_year_real_value"]
            available_columns = [col for col in columns_to_multiply if col in monthly_data_df.columns]
            monthly_data_df.loc[monthly_data_df["financial_type_id"] == 28, available_columns] *= 100

        elif sheet_name == "P&L conso":
            columns_to_multiply = ["real_value", "budget_value", "actual1_value", "actual2_value", "actual3_value",
                                   "last_year_real_value"]
            available_columns = [col for col in columns_to_multiply if col in monthly_data_df.columns]
            monthly_data_df.loc[monthly_data_df["financial_metric_id"]   == 88, available_columns] *= 100
            monthly_data_df.loc[monthly_data_df["financial_submetric_id"] == 14, available_columns] *= 100
            monthly_data_df.loc[monthly_data_df["financial_submetric_id"] == 18, available_columns] *= 100
            monthly_data_df.loc[monthly_data_df["financial_submetric_id"] == 20, available_columns] *= 100

        # Set date
        monthly_data_df["date"] = valueDict["date"]

        # Track special months
        if month == "annual":
            annual_df = monthly_data_df
            dataframes.append(monthly_data_df)
        elif month == "cumul":
            cumul_df = monthly_data_df       # ← track cumul
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
    output_path = f"{base_path}/may_output"

    # Main CSV
    data_df.to_csv(f"{output_path}/{output_file_name}.csv", index=False)
    print(f"✓ Main CSV saved     : {output_file_name}.csv")

    # Annual CSV
    if annual_df is not None:
        annual_df.to_csv(f"{output_path}/annual_{output_file_name}.csv", index=False)
        print(f"✓ Annual CSV saved   : annual_{output_file_name}.csv")

    # Cumulative CSV
    if cumul_df is not None:
        cumul_df.to_csv(f"{output_path}/cumulative_{output_file_name}.csv", index=False)
        print(f"✓ Cumulative CSV saved: cumulative_{output_file_name}.csv")