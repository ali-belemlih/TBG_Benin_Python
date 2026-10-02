-- Update in table financial_metrics_data
-- Update last year's real values for 2025 data by looking up corresponding 2024 values
UPDATE financial_metrics_data fmd_current
SET last_year_real_value = fmd_last_year.real_value
FROM financial_metrics_data fmd_last_year
WHERE 
    (
        (fmd_last_year.financial_type_id = fmd_current.financial_type_id AND fmd_last_year.financial_metric_id IS NULL AND fmd_last_year.financial_submetric_id IS NULL)
        OR (fmd_last_year.financial_metric_id = fmd_current.financial_metric_id AND fmd_last_year.financial_type_id IS NULL AND fmd_last_year.financial_submetric_id IS NULL)
        OR (fmd_last_year.financial_submetric_id = fmd_current.financial_submetric_id AND fmd_last_year.financial_type_id IS NULL AND fmd_last_year.financial_metric_id IS NULL)
    )
    AND DATE_TRUNC('month', fmd_last_year.date) = DATE_TRUNC('month', fmd_current.date - INTERVAL '1 year')
    AND fmd_current.date >= '2025-01-01';


-- Update in table financial_annual_data
-- Update last year's real values for 2025 data by looking up corresponding 2024 values
UPDATE financial_annual_data fa
SET last_year_real_value = fc.real_value
FROM financial_cumulative_data fc
WHERE 
    fc.date = CAST(CONCAT(EXTRACT(YEAR FROM fa.date) - 1, '-12-01') AS DATE)
    AND (
        (fa.financial_type_id = fc.financial_type_id AND fa.financial_metric_id IS NULL AND fa.financial_submetric_id IS NULL AND fc.financial_metric_id IS NULL AND fc.financial_submetric_id IS NULL)
        OR (fa.financial_metric_id = fc.financial_metric_id AND fa.financial_type_id IS NULL AND fa.financial_submetric_id IS NULL AND fc.financial_type_id IS NULL AND fc.financial_submetric_id IS NULL)
        OR (fa.financial_submetric_id = fc.financial_submetric_id AND fa.financial_type_id IS NULL AND fa.financial_metric_id IS NULL AND fc.financial_type_id IS NULL AND fc.financial_metric_id IS NULL)
    )
    AND fa.date >= '2025-01-01';

UPDATE collapse_monthly_data fa
SET last_year_real_value = fc.real_value
FROM collapse_monthly_data fc
WHERE
    -- Match same month last year
    fc.date = (fa.date - interval '1 year')

    AND fa.entity_type = 'category'
    AND fc.entity_type = 'category'

    AND fa.entity_id = fc.entity_id

    AND fa.date >= '2025-01-01';

UPDATE collapse_monthly_data fa
SET last_year_real_value = fc.real_value
FROM collapse_monthly_data fc
WHERE
    -- Match same month last year
    fc.date = (fa.date - interval '1 year')

    AND fa.entity_type = 'subcategory'
    AND fc.entity_type = 'subcategory'

    AND fa.entity_id = fc.entity_id

    AND fa.date >= '2025-01-01';


UPDATE collapse_monthly_data fa
SET last_year_real_value = fc.real_value
FROM collapse_monthly_data fc
WHERE
    -- Match same month last year
    fc.date = (fa.date - interval '1 year')

    AND fa.entity_type = 'type'
    AND fc.entity_type = 'type'

    AND fa.entity_id = fc.entity_id

    AND fa.date >= '2025-01-01';

UPDATE collapse_annual_data fa
SET last_year_real_value = fc.real_value
FROM collapse_cumul_data fc
WHERE
    -- always take last year's December
    fc.date = CAST(CONCAT(EXTRACT(YEAR FROM fa.date) - 1, '-12-01') AS DATE)

    -- ensure entity_type and entity_id match
    AND fa.entity_type = fc.entity_type
    AND fa.entity_id   = fc.entity_id

    -- only apply for dates from 2025 onward
    AND fa.date >= '2025-01-01';


-- For debugging purposes only
-- Query to select the last year real value updates by comparing 2025 data with corresponding 2024 values
SELECT
	fmd_current.id AS current_id,
	fmd_last_year.id AS last_year_id,
    fmd_current.date AS current_date, 
    fmd_last_year.date AS last_year_date, 
    fmd_current.financial_type_id,
    fmd_current.financial_metric_id,
    fmd_current.financial_submetric_id,
    fmd_current.real_value AS current_real_value,
    fmd_last_year.real_value AS last_year_real_value,
    fmd_current.last_year_real_value AS current_last_year_real_value
FROM financial_annual_data fmd_current
LEFT JOIN financial_annual_data fmd_last_year
    ON (
        (fmd_last_year.financial_type_id = fmd_current.financial_type_id AND fmd_last_year.financial_metric_id IS NULL AND fmd_last_year.financial_submetric_id IS NULL)
        OR (fmd_last_year.financial_metric_id = fmd_current.financial_metric_id AND fmd_last_year.financial_type_id IS NULL AND fmd_last_year.financial_submetric_id IS NULL)
        OR (fmd_last_year.financial_submetric_id = fmd_current.financial_submetric_id AND fmd_last_year.financial_type_id IS NULL AND fmd_last_year.financial_metric_id IS NULL)
    )
    AND DATE_TRUNC('month', fmd_last_year.date) = DATE_TRUNC('month', fmd_current.date - INTERVAL '1 year')
WHERE fmd_current.date >= '2025-01-01';
