-- Capex Consolidate
psql -h localhost -U digiwise_user -d digiwise_db -W -c "\copy public.financial_metrics_data (real_value, budget_value, last_year_real_value, financial_type_id, financial_metric_id, date, actual1_value, actual2_value, actual3_value) FROM '/home/ec2-user/benin-financial-data/capex_consolidate.csv' WITH (FORMAT csv, HEADER true, DELIMITER ',');"


-- Opex Consolidate
psql -h localhost -U digiwise_user -d digiwise_db -W -c "\copy public.financial_metrics_data (real_value, budget_value, last_year_real_value, financial_type_id, financial_metric_id, date, actual1_value, actual2_value, actual3_value) FROM '/home/ec2-user/benin-financial-data/opex_consolidate.csv' WITH (FORMAT csv, HEADER true, DELIMITER ',');"


-- Cash Consolidate
psql -h localhost -U digiwise_user -d digiwise_db -W -c "\copy public.financial_metrics_data (real_value, budget_value, last_year_real_value, financial_type_id, financial_metric_id, financial_submetric_id, date, actual1_value, actual2_value, actual3_value) FROM '/home/ec2-user/benin-financial-data/cash_consolidate.csv' WITH (FORMAT csv, HEADER true, DELIMITER ',');"


-- CA Mobile
psql -h localhost -U digiwise_user -d digiwise_db -W -c "\copy public.financial_metrics_data (real_value, budget_value, last_year_real_value, financial_type_id, financial_metric_id, financial_submetric_id, date, actual1_value, actual2_value, actual3_value) FROM '/home/ec2-user/benin-financial-data/ca_mobile.csv' WITH (FORMAT csv, HEADER true, DELIMITER ',');"


-- Marge Mobile
psql -h localhost -U digiwise_user -d digiwise_db -W -c "\copy public.financial_metrics_data (real_value, budget_value, last_year_real_value, financial_type_id, financial_metric_id, financial_submetric_id, date, actual1_value, actual2_value, actual3_value) FROM '/home/ec2-user/benin-financial-data/marge_mobile.csv' WITH (FORMAT csv, HEADER true, DELIMITER ',');"

-- Profit and Loss Consolidate
psql -h localhost -U digiwise_user -d digiwise_db -W -c "\copy public.financial_metrics_data (real_value, budget_value, last_year_real_value, financial_type_id, financial_metric_id, financial_submetric_id, date, actual1_value, actual2_value, actual3_value) FROM '/home/ec2-user/benin-financial-data/profit_and_loss_consolidate.csv' WITH (FORMAT csv, HEADER true, DELIMITER ',');"


-- Traffic Mobile
psql -h localhost -U digiwise_user -d digiwise_db -W -c "\copy public.financial_metrics_data (real_value, budget_value, last_year_real_value, financial_type_id, financial_metric_id, financial_submetric_id, date, actual1_value, actual2_value, actual3_value) FROM '/home/ec2-user/benin-financial-data/traffic_mobile.csv' WITH (FORMAT csv, HEADER true, DELIMITER ',');"


-- Parc Mobile
psql -h localhost -U digiwise_user -d digiwise_db -W -c "\copy public.financial_metrics_data (real_value, budget_value, last_year_real_value, financial_type_id, financial_metric_id, financial_submetric_id, date, actual1_value, actual2_value, actual3_value) FROM '/home/ec2-user/benin-financial-data/parc_mobile.csv' WITH (FORMAT csv, HEADER true, DELIMITER ',');"



-- Indicateurs Mobile
psql -h localhost -U digiwise_user -d digiwise_db -W -c "\copy public.financial_metrics_data (real_value, budget_value, last_year_real_value, financial_type_id, financial_metric_id, financial_submetric_id, date, actual1_value, actual2_value, actual3_value) FROM '/home/ec2-user/benin-financial-data/indicateurs_mobile.csv' WITH (FORMAT csv, HEADER true, DELIMITER ',');"

-- Data Mobile
psql -h localhost -U digiwise_user -d digiwise_db -W -c "\copy public.financial_metrics_data (real_value, budget_value, last_year_real_value, financial_type_id, financial_metric_id, date, actual1_value, actual2_value, actual3_value) FROM '/home/ec2-user/benin-financial-data/data_mobile.csv' WITH (FORMAT csv, HEADER true, DELIMITER ',');"

-- Mobile Money
psql -h localhost -U digiwise_user -d digiwise_db -W -c "\copy public.financial_metrics_data (real_value, budget_value, last_year_real_value, financial_type_id, financial_metric_id, financial_submetric_id, date, actual1_value, actual2_value, actual3_value) FROM '/home/ec2-user/benin-financial-data/mobile_money.csv' WITH (FORMAT csv, HEADER true, DELIMITER ',');"



-- Annual Capex Consolidate
psql -h localhost -U digiwise_user -d digiwise_db -W -c "\copy public.financial_annual_data (budget_value, actual1_value, actual2_value, actual3_value, last_year_real_value, financial_type_id, financial_metric_id, date) FROM '/home/ec2-user/benin-financial-data/annual_capex_consolidate.csv' WITH (FORMAT csv, HEADER true, DELIMITER ',');"


-- Annual Opex Consolidate
psql -h localhost -U digiwise_user -d digiwise_db -W -c "\copy public.financial_annual_data (budget_value, actual1_value, actual2_value, actual3_value, last_year_real_value, financial_type_id, financial_metric_id, date) FROM '/home/ec2-user/benin-financial-data/annual_opex_consolidate.csv' WITH (FORMAT csv, HEADER true, DELIMITER ',');"


-- Annual Cash Consolidate
psql -h localhost -U digiwise_user -d digiwise_db -W -c "\copy public.financial_annual_data (budget_value, actual1_value, actual2_value, actual3_value, last_year_real_value, financial_type_id, financial_metric_id, financial_submetric_id, date) FROM '/home/ec2-user/benin-financial-data/annual_cash_consolidate.csv' WITH (FORMAT csv, HEADER true, DELIMITER ',');"


-- Annual CA Mobile
psql -h localhost -U digiwise_user -d digiwise_db -W -c "\copy public.financial_annual_data (budget_value, actual1_value, actual2_value, actual3_value, last_year_real_value, financial_type_id, financial_metric_id, financial_submetric_id, date) FROM '/home/ec2-user/benin-financial-data/annual_ca_mobile.csv' WITH (FORMAT csv, HEADER true, DELIMITER ',');"

-- Annual Marge Mobile
psql -h localhost -U digiwise_user -d digiwise_db -W -c "\copy public.financial_annual_data (budget_value, actual1_value, actual2_value, actual3_value, last_year_real_value, financial_type_id, financial_metric_id, financial_submetric_id, date) FROM '/home/ec2-user/benin-financial-data/annual_marge_mobile.csv' WITH (FORMAT csv, HEADER true, DELIMITER ',');"

-- Annual Profit and Loss Consolidate
psql -h localhost -U digiwise_user -d digiwise_db -W -c "\copy public.financial_annual_data (budget_value, actual1_value, actual2_value, actual3_value, last_year_real_value, financial_type_id, financial_metric_id, financial_submetric_id, date) FROM '/home/ec2-user/benin-financial-data/annual_profit_and_loss_consolidate.csv' WITH (FORMAT csv, HEADER true, DELIMITER ',');"


-- Annual Traffic Mobile
psql -h localhost -U digiwise_user -d digiwise_db -W -c "\copy public.financial_annual_data (budget_value, actual1_value, actual2_value, actual3_value, last_year_real_value, financial_type_id, financial_metric_id, financial_submetric_id, date) FROM '/home/ec2-user/benin-financial-data/annual_traffic_mobile.csv' WITH (FORMAT csv, HEADER true, DELIMITER ',');"


-- Annual Parc Mobile
psql -h localhost -U digiwise_user -d digiwise_db -W -c "\copy public.financial_annual_data (budget_value, actual1_value, actual2_value, actual3_value, last_year_real_value, financial_type_id, financial_metric_id, financial_submetric_id, date) FROM '/home/ec2-user/benin-financial-data/annual_parc_mobile.csv' WITH (FORMAT csv, HEADER true, DELIMITER ',');"


-- Annual Indicateurs Mobile
psql -h localhost -U digiwise_user -d digiwise_db -W -c "\copy public.financial_annual_data (budget_value, actual1_value, actual2_value, actual3_value, last_year_real_value, financial_type_id, financial_metric_id, financial_submetric_id, date) FROM '/home/ec2-user/benin-financial-data/annual_indicateurs_mobile.csv' WITH (FORMAT csv, HEADER true, DELIMITER ',');"

-- Annual Data Mobile
psql -h localhost -U digiwise_user -d digiwise_db -W -c "\copy public.financial_annual_data (budget_value, actual1_value, actual2_value, actual3_value, last_year_real_value, financial_type_id, financial_metric_id, date) FROM '/home/ec2-user/benin-financial-data/annual_data_mobile.csv' WITH (FORMAT csv, HEADER true, DELIMITER ',');"

-- Annual Mobile Money
psql -h localhost -U digiwise_user -d digiwise_db -W -c "\copy public.financial_annual_data (budget_value, actual1_value, actual2_value, actual3_value, last_year_real_value, financial_type_id, financial_metric_id, financial_submetric_id, date) FROM '/home/ec2-user/benin-financial-data/annual_mobile_money.csv' WITH (FORMAT csv, HEADER true, DELIMITER ',');"
