import pandas as pd

def generate_data(sheet_name, output_file_name, required_rows, financial_type_row_mapping, financial_metric_row_mapping, financial_submetric_row_mapping={}):
    # Load the Excel file
    # file_path = 'ECHANTILLON_TBG.xlsx'
    # file_path = 'ECHANTILLON_TBG_Updated_Format.xlsx'
    file_path = 'ECHANTILLON_TBG_Mobile_Money_With_Annual.xlsx'
    df = pd.read_excel(file_path, sheet_name=sheet_name, header=None)

    if sheet_name == "Data Mobile" or sheet_name == "Mobile Money":
        header_row = 3
    else:
        header_row = 4
    zero_index = 1 # Row numbers in required rows and mapping is based on 1-indexed but in loop below it is 0-indexed thus this variable is used to convert 1-indexed to 0-indexed

    required_rows = [x - header_row - zero_index for x in required_rows]

    if sheet_name == 'Mobile Money':
        months_details_hash = {
            "jan": {"date": "01-01-2024", "cols": "D:H"},
            "feb": {"date": "02-01-2024", "cols": "J:N"},
            "mar": {"date": "03-01-2024", "cols": "P:T"},
            "apr": {"date": "04-01-2024", "cols": "V:AB"},
            "may": {"date": "05-01-2024", "cols": "AD:AJ"},
            "jun": {"date": "06-01-2024", "cols": "AL:AR"},
            "jul": {"date": "07-01-2024", "cols": "AT:AZ"},
            "aug": {"date": "08-01-2024", "cols": "BB:BH"},
            "sep": {"date": "09-01-2024", "cols": "BJ:BQ"},
            "oct": {"date": "10-01-2024", "cols": "BS:BY"},
            "nov": {"date": "11-01-2024", "cols": "CA:CG"},
            "dec": {"date": "12-01-2024", "cols": "CI:CO"},
            "annual": {"date": "01-01-2024", "cols": "CY:DG"}
        }
    else:
        months_details_hash = {
            "jan": {"date": "01-01-2024", "cols": "D:H"},
            "feb": {"date": "02-01-2024", "cols": "J:N"},
            "mar": {"date": "03-01-2024", "cols": "P:T"},
            "apr": {"date": "04-01-2024", "cols": "V:AB"},
            "may": {"date": "05-01-2024", "cols": "AD:AJ"},
            "jun": {"date": "06-01-2024", "cols": "AL:AS"},
            "jul": {"date": "07-01-2024", "cols": "AU:BA"},
            "aug": {"date": "08-01-2024", "cols": "BC:BI"},
            "sep": {"date": "09-01-2024", "cols": "BK:BR"},
            "oct": {"date": "10-01-2024", "cols": "BT:BZ"},
            "nov": {"date": "11-01-2024", "cols": "CB:CH"},
            "dec": {"date": "12-01-2024", "cols": "CJ:CP"},
            "annual": {"date": "01-01-2024", "cols": "CZ:DH"}
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
        
        # monthly_data_df["date"] = pd.to_datetime(valueDict["date"]).dt.strftime("%d-%m-%Y")

        # Clean column names by replacing newline characters
        monthly_data_df.columns = monthly_data_df.columns.str.replace("\n", "")

        print(monthly_data_df.columns.tolist())

        # Define column name mappings
        if sheet_name == "Data Mobile":
            column_prefixes = {
                "real_value": "Réel 2024",
                "budget_value": "Budget",
                "actual1_value": "Actu1",		
                "actual2_value": "Actu2",
                "actual3_value": "Actu3",
                "last_year_real_value": "Réel 2023"
            }
        elif sheet_name == "Mobile Money":
            column_prefixes = {
                "real_value": "Réel <Mois>-24",
                "budget_value": "Budget",
                "actual1_value": "Actu1",		
                "actual2_value": "Actu2",
                "actual3_value": "Actu3",
                "last_year_real_value": "Réel <Mois>-23"
            }
        else:
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
            
            if updated_index in financial_type_row_mapping.keys():
                monthly_data_df.at[index, "financial_type_id"] = int(financial_type_row_mapping[updated_index])
            elif updated_index in financial_metric_row_mapping.keys():
                monthly_data_df.at[index, "financial_metric_id"] = int(financial_metric_row_mapping[updated_index])
            elif updated_index in financial_submetric_row_mapping.keys():
                monthly_data_df.at[index, "financial_submetric_id"] = int(financial_submetric_row_mapping[updated_index])

        monthly_data_df = monthly_data_df.iloc[[r - 1 for r in required_rows]]
        
        monthly_data_df["financial_type_id"] = monthly_data_df["financial_type_id"].astype("Int64")
        monthly_data_df["financial_metric_id"] = monthly_data_df["financial_metric_id"].astype("Int64")
        
        if "financial_submetric_id" in monthly_data_df.columns:
            monthly_data_df["financial_submetric_id"] = monthly_data_df["financial_submetric_id"].astype("Int64")

        if sheet_name == "Marge Mobile":
            columns_to_multiply = ["real_value", "budget_value", "actual1_value", "actual2_value", "actual3_value", "last_year_real_value"]
            available_columns = [col for col in columns_to_multiply if col in monthly_data_df.columns]
            monthly_data_df.loc[monthly_data_df["financial_type_id"] == 28, available_columns] *= 100
        
        elif sheet_name == "P&L conso":
            columns_to_multiply = ["real_value", "budget_value", "actual1_value", "actual2_value", "actual3_value", "last_year_real_value"]
            available_columns = [col for col in columns_to_multiply if col in monthly_data_df.columns]
            monthly_data_df.loc[monthly_data_df["financial_metric_id"] == 88, available_columns] *= 100
            monthly_data_df.loc[monthly_data_df["financial_submetric_id"] == 14, available_columns] *= 100
            monthly_data_df.loc[monthly_data_df["financial_submetric_id"] == 18, available_columns] *= 100
            monthly_data_df.loc[monthly_data_df["financial_submetric_id"] == 20, available_columns] *= 100

        annual_df = None
        if(month == "annual"):
            annual_df = monthly_data_df
        else:
            dataframes.append(monthly_data_df)
        
        # Convert single value to datetime
        date = pd.to_datetime(valueDict["date"])  # `date` is a single Timestamp object

        monthly_data_df["date"] = valueDict["date"]

        # print(monthly_data_df)

    data_df = pd.concat(dataframes, ignore_index=True)

    data_df.to_csv(f"output_data/{output_file_name}.csv", index=False)
    
    if annual_df is not None:
        annual_df.to_csv(f"output_data/annual_{output_file_name}.csv", index=False)
