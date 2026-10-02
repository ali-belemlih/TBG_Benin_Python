SELECT * FROM (
                  SELECT
                      COALESCE(fc.name, fmc.name, fsm_category.name, 'Unknown') AS category_name,
                      COALESCE(ft.name, fmt.name, fsm_type.name, 'N/A') AS financial_type_name,
                      COALESCE(fm.name, 'N/A') AS metric_name,
                      COALESCE(fsm.name, 'N/A') AS submetric_name,
                      fmd.date,
                      fmd.real_value,
                      fmd.budget_value,
                      fmd.actual1_value,
                      fmd.actual2_value,
                      fmd.actual3_value,
                      fmd.last_year_real_value,
                      (fmd.real_value - fmd.budget_value) AS ecart_budget,
                      (fmd.real_value - fmd.actual1_value) AS ecart_actual1_value,
                      (fmd.real_value - fmd.actual2_value) AS ecart_actual2_value,
                      (fmd.real_value - fmd.actual3_value) AS ecart_actual3_value,
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
                  ORDER BY fmd.date, category_name, financial_type_name, metric_name, submetric_name
              ) q
WHERE q.category_name = '{sheet_name}'
  AND q.date = '{date_param}'
  AND q.version_id = {version_id};