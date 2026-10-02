-- Capex Detail Project
psql -h localhost -U digiwise_user -d digiwise_db -W -c "\copy public.capex_projects (id, project_title, contract_no, contract_date, supplier_name, direction_name, sequence_id) FROM '/home/ec2-user/benin-financial-data/capex_project.csv' WITH (FORMAT csv, HEADER true, DELIMITER ',');"

-- Capex Detail Data
psql -h localhost -U digiwise_user -d digiwise_db -W -c "\copy public.capex_data (id, capex_projects_id, month, year, equipment, services, additional_costs) FROM '/home/ec2-user/benin-financial-data/capex_monthly_data.csv' WITH (FORMAT csv, HEADER true, DELIMITER ',');"
