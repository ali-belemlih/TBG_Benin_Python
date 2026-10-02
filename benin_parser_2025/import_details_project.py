import sys
import pandas as pd
from helpers.db_utils import get_db_connection
from services.minio_factory import get_minio_service
from helpers.capex_details_utils.db_utils import get_uploaded_file_details
from helpers.capex_details_utils.helpers import FILE_MONTH_MAPPING, safe_number, safe_date

def process_details_project_capex(df: pd.DataFrame, target_month: int, target_year: int):
    conn = get_db_connection()
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute("""
                    DELETE FROM capex_data
                    WHERE year = %s;
                """, (target_year,))

                cur.execute("""
                    DELETE FROM capex_projects
                    WHERE id NOT IN (
                        SELECT capex_projects_id FROM capex_data
                    );
                """)

                print(f"🧹 Deleted existing capex_data and capex_projects entries for year {target_year}.")

                for idx, row in df.iloc[:-1].iterrows():  # Skip last row (Total)
                    print(f"Processing row {idx}")
                    project_title = row[("Intitulé du projet", "Unnamed: 0_level_1")]

                    if str(project_title).strip().upper() in ["TOTAL", "", "NAN"]:
                        print(f"⏭️ Skipping row {idx} with title: '{project_title}'")
                        break

                    contract_no = row[("N° Bon Commande/ Contrat", "Unnamed: 1_level_1")]
                    contract_date = safe_date(row[("Date Emission BC/Contrat", "Unnamed: 2_level_1")])
                    supplier_name = row[("Fournissseurs", "Unnamed: 3_level_1")]
                    direction_name = row[("Direction", "Unnamed: 4_level_1")]
                    sequence_id = idx + 1

                    print("DEBUG contract_date =", contract_date, type(contract_date))

                    cur.execute("""
                        INSERT INTO public.capex_projects (
                            supplier_name, direction_name, project_title, contract_no,
                            contract_date, sequence_id, created_at, updated_at
                        ) VALUES (%s, %s, %s, %s, %s, %s, now(), now())
                        RETURNING id;
                    """, (
                        supplier_name,
                        direction_name,
                        project_title,
                        contract_no,
                        contract_date,  # This ensures NaT → None
                        sequence_id
                    ))
                    project_id = cur.fetchone()[0]
                    print(f"✅ Inserted project_id={project_id} for '{project_title}'")

                    for month in range(1, target_month + 1):
                        month_label = FILE_MONTH_MAPPING[month]
                        col_base = f"Réalisé {month_label} {target_year}"

                        try:
                            equipment = safe_number(row.get((col_base, "Equipement")))
                            services = safe_number(row.get((col_base, "Prestations")))
                            additional_costs = safe_number(row.get((col_base, "Frais annexe(DD)")))
                        except KeyError:
                            continue  # Month not present

                        if pd.isna(equipment) and pd.isna(services) and pd.isna(additional_costs):
                            continue

                        cur.execute("""
                            INSERT INTO public.capex_data (
                                capex_projects_id, month, year, equipment, services, additional_costs
                            ) VALUES (%s, %s, %s, %s, %s, %s);
                        """, (
                            project_id, month, target_year,
                            equipment or 0, services or 0, additional_costs or 0
                        ))
                        print(f"  📦 Inserted capex_data for {FILE_MONTH_MAPPING[month]} - Equip: {equipment}, Serv: {services}, Cost: {additional_costs}")
    finally:
        conn.close()

if __name__ == "__main__":
    id = sys.argv[1]
    bucket_name = sys.argv[2]
    target_month, target_year, file_path = get_uploaded_file_details(id)
    date = f"{target_year}-{target_month}-01"

    print(f"Fetching file from MinIO path: {file_path}")
    minio_service = get_minio_service(bucket_name)
    try:
        excel_df = minio_service.read_excel(object_name=file_path, sheet_name='Détail projets Capex', header=[3, 4])
        process_details_project_capex(excel_df, target_month, target_year)

        print("✅ Data successfully inserted into DB.")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
