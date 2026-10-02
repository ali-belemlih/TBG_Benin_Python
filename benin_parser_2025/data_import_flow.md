Sage Import:

Real Import:
  - Parallel Execution
    1. benin-parser-2025/reel_import/pnl_import.py
    2. benin-parser-2025/reel_import/ca_mobile.py
    3. benin-parser-2025/reel_import/marge_brute_mobile.py
    4. benin-parser-2025/reel_import/traffic_mobile.py
    5. benin-parser-2025/reel_import/mobile_money.py
    6. benin-parser-2025/reel_import/data_mobile.py
    7. benin-parser-2025/reel_import/parc_mobile.py
    8. benin-parser-2025/reel_import/realise.py

  - Serial Execution
    1. benin-parser-2025/reel_import/indicateurs_mobile.py
    2. benin-parser-2025/reel_import/cash_conso.py

Gap Corrections:

Budget:

1. benin-parser-2025/budget_import/budget.py
2. benin-parser-2025/budget_import/opex_budget.py
3. benin-parser-2025/budget_import/collapse_opex_conso.py
4. benin-parser-2025/budget_import/collapse_ca_mobile.py
5. benin-parser-2025/budget_import/mobile_money_budget.py
6. benin-parser-2025/budget_import/data_mobile_budget.py

Cumulative Data import:
1. Truncate table: TRUNCATE financial_cumulative_data RESTART IDENTITY;
2. benin-data-parser-new/scripts/cum_data_import.py
3. benin-data-parser-new/scripts/collapse_cum_data_import.py

Update Parent ID:
1. benin-parser-2025/sql_queries/00_update_parent_id.sql
    - financial_metrics_data
    - financial_annual_data
    - financial_cumulative_data

Update Last Year Real:
  1. benin-parser-2025/sql_queries/update_last_year_real.sql
    - financial_metrics_data
    - financial_annual_data
    - financial_cumulative_data (Remaining)

Update Realise Data:
1. benin-parser-2025/sql_queries/update_realise_data.sql
