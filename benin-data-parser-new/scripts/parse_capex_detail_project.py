import pandas as pd
from datetime import datetime

def clean_text(text):
    """Helper function to clean text by replacing all types of newlines with spaces"""
    if pd.isna(text):
        return text
    text = str(text)
    return ' '.join(text.replace('\r\n', ' ').replace('\n', ' ').replace('\r', ' ').split()).strip()

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

    # Extract required columns using exact header names from the document
    required_columns = [
        'Intitulé du projet',
        'N° Bon Commande/\nContrat',
        'Date Emission BC\n/Contrat',
        'Fournissseurs',
        'Direction'
    ]

    capex_projects = df[required_columns].copy()

    # Rename columns to match output requirements
    capex_projects.columns = [
        'project_title',
        'contract_no',
        'contract_date',
        'supplier_name',
        'direction_name'
    ]

    # Clean all text columns immediately after extraction
    for column in capex_projects.columns:
        if column != 'contract_date':  # Skip date column
            capex_projects[column] = capex_projects[column].apply(clean_text)

    # Clean up project data
    capex_projects = capex_projects.dropna(subset=['project_title'])

    # Convert and format date
    capex_projects['contract_date'] = pd.to_datetime(capex_projects['contract_date'], errors='coerce')
    capex_projects['contract_date'] = capex_projects['contract_date'].dt.strftime('%m/%d/%Y')

    # Add required columns
    capex_projects['id'] = range(1, len(capex_projects) + 1)
    capex_projects['sequence_id'] = range(10, 10 * len(capex_projects) + 10, 10)

    # Select and order output columns
    result_df = capex_projects[[
        'id',
        'project_title',
        'contract_no',
        'contract_date',
        'supplier_name',
        'direction_name',
        'sequence_id'
    ]]

    return result_df

def main():
    input_file = 'ECHANTILLON_TBG_Updated_Format.xlsx'
    output_file = 'capex_project.csv'

    # Extract and combine data
    combined_df = extract_and_combine_capex_data(input_file)

    # Save to CSV
    combined_df.to_csv(output_file, index=False)

    print(f"Data extracted and combined successfully. Saved to {output_file}")

if __name__ == '__main__':
    main()