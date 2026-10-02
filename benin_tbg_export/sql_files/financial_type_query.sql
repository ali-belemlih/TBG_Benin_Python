-- financial_data_query.sql
WITH category AS (
    SELECT id FROM financial_categories WHERE name = '{sheet_name}'
),
     types AS (
         SELECT id FROM financial_types WHERE financial_category_id IN (SELECT id FROM category)
     ),
     metrics AS (
         SELECT id FROM financial_metric WHERE financial_type_id IN (SELECT id FROM types)
     ),
     submetrics AS (
         SELECT id FROM financial_submetric WHERE financial_metric_id IN (SELECT id FROM metrics)
     )
SELECT
    fmd.id AS data_id,
    fc.name AS category_name,
    ft.name AS type_name,
    fm.name AS metric_name,
    fs.name AS submetric_name,
    fmd.date,
    fmd.real_value,
    fmd.adjusted_value,
    (COALESCE(fmd.real_value, 0) + COALESCE(fmd.adjusted_value, 0)) AS effective_real_value,
    fmd.budget_value,
    fmd.actual1_value,
    fmd.actual2_value,
    fmd.actual3_value,
    fmd.last_year_real_value,
    -- Calculated fields using effective_real_value (real + adjusted)
    ((COALESCE(fmd.real_value, 0) + COALESCE(fmd.adjusted_value, 0)) - fmd.budget_value)          AS ecart_budget,
    ((COALESCE(fmd.real_value, 0) + COALESCE(fmd.adjusted_value, 0)) - fmd.actual1_value)         AS ecart_actual1_value,
    ((COALESCE(fmd.real_value, 0) + COALESCE(fmd.adjusted_value, 0)) - fmd.actual2_value)         AS ecart_actual2_value,
    ((COALESCE(fmd.real_value, 0) + COALESCE(fmd.adjusted_value, 0)) - fmd.actual3_value)         AS ecart_actual3_value,
    CASE
        WHEN fmd.last_year_real_value IS NOT NULL AND fmd.last_year_real_value != 0
        THEN ((COALESCE(fmd.real_value, 0) + COALESCE(fmd.adjusted_value, 0)) / fmd.last_year_real_value) - 1
        ELSE NULL
    END AS evol_percent

FROM financial_metrics_data fmd
         LEFT JOIN financial_types ft ON fmd.financial_type_id = ft.id
         LEFT JOIN financial_metric fm ON fmd.financial_metric_id = fm.id
         LEFT JOIN financial_submetric fs ON fmd.financial_submetric_id = fs.id
         LEFT JOIN financial_categories fc ON ft.financial_category_id = fc.id
WHERE fc.name = '{sheet_name_param}'
  AND fmd.date = '{date_param}'
  AND fmd.version_id = {version_id};