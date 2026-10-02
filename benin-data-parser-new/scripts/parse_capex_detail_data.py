import pandas as pd
from datetime import datetime

def extract_and_combine_capex_data(input_file):
    # Read the Excel file
    xls = pd.ExcelFile(input_file)
    df = pd.read_excel(xls, sheet_name='Détail projets Capex', header=None)

    # Find the header row (row 4) and set it as column names
    headers = df.iloc[3].tolist()
    df.columns = headers

    # Print actual headers for debugging
    print("Actual headers in Excel file:", headers)

    # Remove the first 4 rows (metadata and headers)
    df = df.iloc[4:]

    # Reset index after removing rows
    df.reset_index(drop=True, inplace=True)

    # Extract project details just to assign capex_projects_id
    project_columns = ['Intitulé du projet']
    capex_projects = df[project_columns].copy()
    capex_projects = capex_projects.dropna(subset=['Intitulé du projet'])
    capex_projects['capex_projects_id'] = range(1, len(capex_projects) + 1)

    # Define month columns mapping
    month_columns = {
        'Janvier': ['Réalisé Janvier 2024', [0, 1, 2]],  # Equipment, Prestations, Frais annexe(DD)
        'Février': ['Réalisé Février 2024', [4, 5, 6]],
        'Mars': ['Réalisé Mars 2024', [8, 9, 10]],
        'Avril': ['Réalisé Avril 2024', [12, 13, 14]],
        'Mai': ['Réalisé Mai 2024', [16, 17, 18]],
        'Juin': ['Réalisé Juin 2024', [20, 21, 22]],
        'Juillet': ['Réalisé Juillet 2024', [24, 25, 26]],
        'Août': ['Réalisé Août 2024', [28, 29, 30]],
        'Septembre': ['Réalisé Septembre 2024', [32, 33, 34]],
        'Octobre': ['Réalisé Octobre 2024', [36, 37, 38]],
        'Novembre': ['Réalisé Novembre 2024', [40, 41, 42]],
        'Décembre': ['Réalisé Décembre 2024', [44, 45, 46]]
    }

    # Prepare combined data with monthly details
    combined_data = []

    for index, project_row in capex_projects.iterrows():
        capex_projects_id = project_row['capex_projects_id']

        # Get original row from df to access monthly data
        original_row = df.iloc[index]

        # Extract monthly data
        for month, (month_prefix, col_indices) in month_columns.items():
            equipment = original_row.iloc[5 + col_indices[0]] if (5 + col_indices[0]) < len(original_row) else 0
            services = original_row.iloc[5 + col_indices[1]] if (5 + col_indices[1]) < len(original_row) else 0
            additional_costs = original_row.iloc[5 + col_indices[2]] if (5 + col_indices[2]) < len(original_row) else 0

            # Convert NaN to 0
            equipment = 0 if pd.isna(equipment) else equipment
            services = 0 if pd.isna(services) else services
            additional_costs = 0 if pd.isna(additional_costs) else additional_costs

            # Add row only if there's data
            #if equipment != 0 or services != 0 or additional_costs != 0:
            month_num = {
                    'Janvier': 1, 'Février': 2, 'Mars': 3, 'Avril': 4, 'Mai': 5, 'Juin': 6,
                    'Juillet': 7, 'Août': 8, 'Septembre': 9, 'Octobre': 10, 'Novembre': 11, 'Décembre': 12
                }[month]

            row_data = {
                    'id': len(combined_data) + 1,  # Incremental ID for each row
                    'capex_projects_id': capex_projects_id,
                    'month': month_num,
                    'year': 2024,
                    'equipment': equipment,
                    'services': services,
                    'additional_costs': additional_costs
                }
            combined_data.append(row_data)

    # Convert to DataFrame
    result_df = pd.DataFrame(combined_data)

    # Order columns
    result_df = result_df[[
        'id',
        'capex_projects_id',
        'month',
        'year',
        'equipment',
        'services',
        'additional_costs'
    ]]

    return result_df

def main():
    input_file = 'ECHANTILLON_TBG_Updated_Format.xlsx'
    output_file = 'capex_data.csv'

    # Extract and combine data
    combined_df = extract_and_combine_capex_data(input_file)

    combined_df[['equipment', 'services', 'additional_costs']] = combined_df[['equipment', 'services', 'additional_costs']].astype(int)
    # Save to CSV
    combined_df.to_csv(output_file, index=False)

    print(f"Data extracted and combined successfully. Saved to {output_file}")

if __name__ == '__main__':
    main()