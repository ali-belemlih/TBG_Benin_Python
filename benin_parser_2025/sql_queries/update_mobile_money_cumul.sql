BEGIN;

UPDATE financial_cumulative_data fcd
SET real_value = fmd.real_value
FROM financial_metrics_data fmd
WHERE fcd.financial_type_id = fmd.financial_type_id
  AND fcd.version_id = fmd.version_id
  AND fcd.date = fmd.date
  AND fcd.date BETWEEN '2025-01-01' AND '2025-12-31'
  AND fcd.financial_type_id IN (33, 34, 35, 36, 41);

UPDATE financial_cumulative_data fcd
SET budget_value = fmd.budget_value
FROM financial_metrics_data fmd
WHERE fcd.financial_type_id = fmd.financial_type_id
  AND fcd.version_id = fmd.version_id
  AND fcd.date = fmd.date
  AND fcd.date BETWEEN '2025-01-01' AND '2025-12-31'
  AND fcd.financial_type_id IN (33, 34, 35, 36, 41);

UPDATE financial_cumulative_data fcd
SET last_year_real_value = fmd.last_year_real_value
FROM financial_metrics_data fmd
WHERE fcd.financial_type_id = fmd.financial_type_id
  AND fcd.version_id = fmd.version_id
  AND fcd.date = fmd.date
  AND fcd.date BETWEEN '2025-01-01' AND '2025-12-31'
  AND fcd.financial_type_id IN (33, 34, 35, 36, 41);

COMMIT;



BEGIN;

UPDATE financial_cumulative_data fcd
SET real_value = fmd.real_value
FROM financial_metrics_data fmd
WHERE fcd.financial_type_id = fmd.financial_type_id
  AND fcd.version_id = fmd.version_id
  AND fcd.date = fmd.date
  AND fcd.date BETWEEN '2025-01-01' AND '2025-12-31'
  AND fcd.financial_metric_id IN (120, 121, 122);

UPDATE financial_cumulative_data fcd
SET budget_value = fmd.budget_value
FROM financial_metrics_data fmd
WHERE fcd.financial_type_id = fmd.financial_type_id
  AND fcd.version_id = fmd.version_id
  AND fcd.date = fmd.date
  AND fcd.date BETWEEN '2025-01-01' AND '2025-12-31'
  AND fcd.financial_metric_id IN (120, 121, 122);

UPDATE financial_cumulative_data fcd
SET last_year_real_value = fmd.last_year_real_value
FROM financial_metrics_data fmd
WHERE fcd.financial_type_id = fmd.financial_type_id
  AND fcd.version_id = fmd.version_id
  AND fcd.date = fmd.date
  AND fcd.date BETWEEN '2025-01-01' AND '2025-12-31'
  AND fcd.financial_metric_id IN (120, 121, 122);

COMMIT;
