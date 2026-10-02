SELECT
    COALESCE(fc.name, fmc.name, fsm_category.name, 'Unknown') AS category_name,

    -- Financial Type should come from the correct level
    CASE
        WHEN fmd.financial_submetric_id IS NOT NULL
            THEN COALESCE(fsm_type.name, 'N/A') -- Financial Type for Submetric
        ELSE COALESCE(ft.name, fmt.name, 'N/A') -- Financial Type for Metric
        END AS financial_type_name,

    -- Metric should be assigned properly
    CASE
        WHEN fmd.financial_submetric_id IS NOT NULL
            THEN COALESCE(fsm_metric.name, 'N/A') -- Metric Name for Submetric
        ELSE COALESCE(fm.name, 'N/A') -- Metric Name for Metric
        END AS metric_name,

    -- Submetric should retain its own name
    COALESCE(fsm.name, 'N/A') AS submetric_name,

    fmd.date,

    -- Replace NULL values with 0
    COALESCE(fmd.real_value, 0) AS real_value,
    COALESCE(fmd.budget_value, 0) AS budget_value,
    COALESCE(fmd.actual1_value, 0) AS actual1_value,
    COALESCE(fmd.actual2_value, 0) AS actual2_value,
    COALESCE(fmd.actual3_value, 0) AS actual3_value,
    COALESCE(fmd.last_year_real_value, 0) AS last_year_real_value,

    -- Ecart calculations with null-safe math
    COALESCE(fmd.real_value, 0) - COALESCE(fmd.budget_value, 0) AS ecart_budget,
    COALESCE(fmd.real_value, 0) - COALESCE(fmd.actual1_value, 0) AS ecart_actual1_value,
    COALESCE(fmd.real_value, 0) - COALESCE(fmd.actual2_value, 0) AS ecart_actual2_value,
    COALESCE(fmd.real_value, 0) - COALESCE(fmd.actual3_value, 0) AS ecart_actual3_value,

        fmd.version_id as version_id

FROM financial_cumulative_data fmd
         LEFT JOIN financial_types ft ON fmd.financial_type_id = ft.id
         LEFT JOIN financial_categories fc ON ft.financial_category_id = fc.id

         LEFT JOIN financial_metric fm ON fmd.financial_metric_id = fm.id
         LEFT JOIN financial_types fmt ON fm.financial_type_id = fmt.id
         LEFT JOIN financial_categories fmc ON fmt.financial_category_id = fmc.id

         LEFT JOIN financial_submetric fsm ON fmd.financial_submetric_id = fsm.id
         LEFT JOIN financial_metric fsm_metric ON fsm.financial_metric_id = fsm_metric.id
         LEFT JOIN financial_types fsm_type ON fsm_metric.financial_type_id = fsm_type.id
         LEFT JOIN financial_categories fsm_category ON fsm_type.financial_category_id = fsm_category.id

WHERE COALESCE(fc.name, fmc.name, fsm_category.name) = '{sheet_name}'
  AND fmd.date = '{date_param}'
AND fmd.version_id = {version_id}
ORDER BY fmd.date, category_name, financial_type_name, metric_name, submetric_name;
