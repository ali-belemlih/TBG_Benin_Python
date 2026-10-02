-- Collapse Opex Consolidate
psql -h localhost -U digiwise_user -d digiwise_db -W -c "\copy public.collapse_monthly_data (real_value, budget_value, last_year_real_value, entity_id, entity_type, date, actual1_value, actual2_value, actual3_value) FROM '/home/ec2-user/benin-financial-data/collapse_opex_consolidate.csv' WITH (FORMAT csv, HEADER true, DELIMITER ',');"

-- Collapse CA Mobile
psql -h localhost -U digiwise_user -d digiwise_db -W -c "\copy public.collapse_monthly_data (real_value, budget_value, last_year_real_value, entity_id, entity_type, date, actual1_value, actual2_value, actual3_value) FROM '/home/ec2-user/benin-financial-data/collapse_ca_mobile.csv' WITH (FORMAT csv, HEADER true, DELIMITER ',');"


-- Collapse Annual Opex Consolidate
psql -h localhost -U digiwise_user -d digiwise_db -W -c "\copy public.collapse_annual_data (last_year_real_value, budget_value, actual1_value, actual2_value, actual3_value, entity_id, entity_type, date) FROM '/home/ec2-user/benin-financial-data/annual_collapse_opex_consolidate.csv' WITH (FORMAT csv, HEADER true, DELIMITER ',');"

-- Collapse Annual CA Mobile
psql -h localhost -U digiwise_user -d digiwise_db -W -c "\copy public.collapse_annual_data (last_year_real_value, budget_value, actual1_value, actual2_value, actual3_value, entity_id, entity_type, date) FROM '/home/ec2-user/benin-financial-data/annual_collapse_ca_mobile.csv' WITH (FORMAT csv, HEADER true, DELIMITER ',');"
