import os
import pandas as pd
from openpyxl import load_workbook

def generate_data(sheet_name, output_file_name, required_rows, financial_type_row_mapping, financial_metric_row_mapping, financial_submetric_row_mapping={}):
    base_path = "historical_data_scripts"
    file_path = f'{base_path}/excel_files/TBG_Moov Africa-Centrafrique_Décembre_2024.xlsx'
    
    # Load workbook for logic checks if needed, but we primarily use pandas for speed
    # Note: header_row is 0-indexed for pandas. 
    # If Excel row 3 is the header, pandas header should be 2.
    if sheet_name in ["Data Mobile", "Mobile Money", "P&L"]:
        header_row_idx = 2  # Excel Row 3
    elif sheet_name in ["Trafic", "MB"]:
        header_row_idx = 3
    else:
        header_row_idx = 4  # Excel Row 4

    year = 2025

    # Month mapping with column ranges
    if sheet_name in ["Data Mobile", "Mobile Money"]:
        months_details_hash = {
            "jan": {"date": f"01-01-{year}", "cols": "D:H"},
            # "feb": {"date": f"02-01-{year}", "cols": "J:N"},
            # "mar": {"date": f"03-01-{year}", "cols": "P:T"},
            # "apr": {"date": f"04-01-{year}", "cols": "V:AA"},
            # "may": {"date": f"05-01-{year}", "cols": "AC:AH"},
            # "jun": {"date": f"06-01-{year}", "cols": "AJ:AO"},
            # "jul": {"date": f"07-01-{year}", "cols": "AQ:AV"},
            # "aug": {"date": f"08-01-{year}", "cols": "AX:BC"},
            # "sep": {"date": f"09-01-{year}", "cols": "BE:BJ"},
            # "oct": {"date": f"10-01-{year}", "cols": "BL:BQ"},
            # "nov": {"date": f"11-01-{year}", "cols": "CB:CH"},
            # "dec": {"date": f"12-01-{year}", "cols": "CJ:CP"},
            "annual": {"date": f"01-01-{year}", "cols": "CN:CS"}
        }

        column_prefixes = {
            "real_value": f"Réel {year}",
            "budget_value": f"Budget",
            "actual1_value": f"Actu1",
            "actual2_value": f"Actu2",
            "actual3_value": f"Actu3",
            "last_year_real_value": f"Réel {year-1}"
        }
    else:
        months_details_hash = {
            "jan": {"date": f"01-01-{year}", "cols": "D:H"},
            # "feb": {"date": f"02-01-{year}", "cols": "J:N"},
            # "mar": {"date": f"03-01-{year}", "cols": "P:T"},
            # "apr": {"date": f"04-01-{year}", "cols": "V:AB"},
            # "may": {"date": f"05-01-{year}", "cols": "AD:AJ"},
            # "jun": {"date": f"06-01-{year}", "cols": "AL:AR"},
            # "jul": {"date": f"07-01-{year}", "cols": "AT:AZ"},
            # "aug": {"date": f"08-01-{year}", "cols": "BB:BH"},
            # "sep": {"date": f"09-01-{year}", "cols": "BJ:BP"},
            # "oct": {"date": f"10-01-{year}", "cols": "BR:BX"},
            # "nov": {"date": f"11-01-{year}", "cols": "CB:CH"},
            # "dec": {"date": f"12-01-{year}", "cols": "CJ:CP"},
            "annual": {"date": f"01-01-{year}", "cols": "CX:DC"}
        }

        column_prefixes = {
            "real_value": f"{year} Réel",
            "budget_value": f"{year} Budget",
            "actual1_value": f"{year} Actu 1",
            "actual2_value": f"{year} Actu 2",
            "actual3_value": f"{year} Actu 3",
            "last_year_real_value": f"{year-1} Réel"
        }

    dataframes = []
    annual_df = None

    for month, valueDict in months_details_hash.items():
        print(f"Processing data for Month - {month}")

        # Load the specific range
        monthly_data_df = pd.read_excel(
            file_path,
            sheet_name=sheet_name,
            header=header_row_idx,
            usecols=valueDict["cols"],
            engine="openpyxl"
        )
        
        # Clean column names
        monthly_data_df.columns = [str(col).replace("\n", " ").strip() for col in monthly_data_df.columns]

        # IMPROVED MATCHING: Look for exact or very specific matches
        matched_columns = {}
        for new_name, prefix in column_prefixes.items():
            # print(f'name: {new_name} & Prefix: {prefix}')
            for col in monthly_data_df.columns:
                # print(f"Sheet Cols: {col}")
                # This ensures "Actu1" matches "Actu1" but "Actu" doesn't accidentally grab "Actu1"
                if prefix.lower() in col.lower():
                    matched_columns[col] = new_name
                    break

        monthly_data_df.rename(columns=matched_columns, inplace=True)
        
        # Filter to only the columns we successfully mapped
        existing_cols = [c for c in matched_columns.values() if c in monthly_data_df.columns]
        monthly_data_df = monthly_data_df[existing_cols].copy()

        # Initialize ID columns as nullable integers
        monthly_data_df["financial_type_key"] = pd.Series(dtype="object")
        monthly_data_df["financial_metric_key"] = pd.Series(dtype="object")
        if financial_submetric_row_mapping:
            monthly_data_df["financial_submetric_key"] = pd.Series(dtype="object")
        # ROW MAPPING LOGIC FIX
        # In pandas, if header is row 3 (idx 2), index 0 is Excel row 4.
        # Formula: Excel_Row = df_index + header_row_idx + 2
        for index in monthly_data_df.index:
            excel_row = index + header_row_idx + 2
            
            if excel_row in financial_type_row_mapping:
                monthly_data_df.at[index, "financial_type_key"] = financial_type_row_mapping[excel_row]
            elif excel_row in financial_metric_row_mapping:
                monthly_data_df.at[index, "financial_metric_key"] = financial_metric_row_mapping[excel_row]
            elif excel_row in financial_submetric_row_mapping:
                monthly_data_df.at[index, "financial_submetric_key"] = financial_submetric_row_mapping[excel_row]

        # Filter the DataFrame to only the rows specified in the mapping
        # We find the indices where the excel_row was in our required_rows list
        valid_df_indices = [idx for idx in monthly_data_df.index if (idx + header_row_idx + 2) in required_rows]
        monthly_data_df = monthly_data_df.loc[valid_df_indices]

        # Add the date
        monthly_data_df["date"] = valueDict["date"]

        if month == "annual":
            annual_df = monthly_data_df
        else:
            dataframes.append(monthly_data_df)

    # Save outputs
    output_path = f"{base_path}/ca_outputs"
    os.makedirs(output_path, exist_ok=True)

    if dataframes:
        final_data_df = pd.concat(dataframes, ignore_index=True)
        final_data_df.to_csv(f"{output_path}/{output_file_name}.csv", index=False)
        print(f"Monthly file saved to {output_path}")

    if annual_df is not None:
        annual_df.to_csv(f"{output_path}/annual_{output_file_name}.csv", index=False)
        print(f"Annual file saved to {output_path}")