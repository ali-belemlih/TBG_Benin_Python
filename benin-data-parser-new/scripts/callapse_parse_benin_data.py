import pandas as pd

def generate_data(sheet_name,
                  output_file_name,
                  required_rows,
                  collapse_type_row_mapping={},
                  collapse_category_row_mapping={},
                  collapse_subcategory_row_mapping={}
                  ):
    
    # Load the Excel file
    file_path = 'benin-data-parser-new/ECHANTILLON_TBG_Updated_Format.xlsx'
    df = pd.read_excel(file_path, sheet_name=sheet_name, header=None)

    year = "2025"

    header_row = 4
    zero_index = 1 # Row numbers in required rows and mapping is based on 1-indexed but in loop below it is 0-indexed thus this variable is used to convert 1-indexed to 0-indexed

    entity_type_mapping = {
        "type": "type",
        "category": "category",
        "subcategory": "subcategory"
    }

    required_rows = [x - header_row - zero_index for x in required_rows]

    months_details_hash = {
        "jan": {"date": f"01-01-{year}", "cols": "D:H"},
        "feb": {"date": f"02-01-{year}", "cols": "J:N"},
        "mar": {"date": f"03-01-{year}", "cols": "P:T"},
        "apr": {"date": f"04-01-{year}", "cols": "V:AB"},
        "may": {"date": f"05-01-{year}", "cols": "AD:AJ"},
        "jun": {"date": f"06-01-{year}", "cols": "AL:AS"},
        "jul": {"date": f"07-01-{year}", "cols": "AU:BA"},
        "aug": {"date": f"08-01-{year}", "cols": "BC:BI"},
        "sep": {"date": f"09-01-{year}", "cols": "BK:BR"},
        "oct": {"date": f"10-01-{year}", "cols": "BT:BZ"},
        "nov": {"date": f"11-01-{year}", "cols": "CB:CH"},
        "dec": {"date": f"12-01-{year}", "cols": "CJ:CP"},
        "annual": {"date": f"01-01-{year}", "cols": "CZ:DH"}
    }

    dataframes = []  # List to store all monthly_data_df

    for month, valueDict in months_details_hash.items():

        print(f"Processing data for Month - {month}")

        monthly_data_df = pd.read_excel(
            file_path,
            sheet_name=sheet_name,
            header=header_row,
            usecols=valueDict["cols"],
        )

        # Clean column names by replacing newline characters
        monthly_data_df.columns = monthly_data_df.columns.str.replace("\n", "")

        print(monthly_data_df.columns.tolist())

        column_prefixes = {
            "real_value": "Réel",
            "budget_value": "2024 Budget",
            "actual1_value": "2024 Actu1",
            "actual2_value": "2024 Actu2",
            "actual3_value": "2024 Actu3",
            "last_year_real_value": "2023 Réel"
        }

        # Find matching columns dynamically
        matched_columns = {}
        for new_name, prefix in column_prefixes.items():
            for col in monthly_data_df.columns:
                if prefix in col:  # Checks if column name contains the prefix
                    matched_columns[col] = new_name
                    break  # Stop once we find the first match

        # Rename columns
        monthly_data_df.rename(columns=matched_columns, inplace=True)

        # Select only the required columns that exist
        existing_columns = list(matched_columns.values())
        monthly_data_df = monthly_data_df[existing_columns]

        for index, row in monthly_data_df.iterrows():
            updated_index = index+1+header_row+zero_index

            if updated_index in collapse_type_row_mapping.keys():
                monthly_data_df.at[index, "entity_id"] = int(collapse_type_row_mapping[updated_index])
                monthly_data_df.at[index, "entity_type"] = entity_type_mapping["type"]
            elif updated_index in collapse_category_row_mapping.keys():
                monthly_data_df.at[index, "entity_id"] = int(collapse_category_row_mapping[updated_index])
                monthly_data_df.at[index, "entity_type"] = entity_type_mapping["category"]
            elif updated_index in collapse_subcategory_row_mapping.keys():
                monthly_data_df.at[index, "entity_id"] = int(collapse_subcategory_row_mapping[updated_index])
                monthly_data_df.at[index, "entity_type"] = entity_type_mapping["subcategory"]

        monthly_data_df = monthly_data_df.iloc[[r - 1 for r in required_rows]]

        monthly_data_df["entity_id"] = monthly_data_df["entity_id"].astype("Int64")

        annual_df = None
        if(month == "annual"):
            annual_df = monthly_data_df
        else:
            dataframes.append(monthly_data_df)

        monthly_data_df["date"] = valueDict["date"]

    data_df = pd.concat(dataframes, ignore_index=True)

    output_data = "benin-data-parser-new/output_data"

    data_df.to_csv(f"{output_data}/{output_file_name}.csv", index=False)

    if annual_df is not None:
        annual_df.to_csv(f"{output_data}/annual_{output_file_name}.csv", index=False)
