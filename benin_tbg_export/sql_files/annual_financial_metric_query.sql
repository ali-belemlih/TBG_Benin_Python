SELECT ft.name AS financial_type_name,
       fm.name AS metric_name,
       'N/A'   AS submetric_name,
       fad.*
FROM financial_annual_data fad
         LEFT JOIN financial_metric fm ON fad.financial_metric_id = fm.id
         LEFT JOIN financial_types ft ON fm.financial_type_id = ft.id
         LEFT JOIN financial_categories fc ON ft.financial_category_id = fc.id
WHERE fc.name = '{sheet_name_param}'
AND fad.version_id = {version_id}
  AND fad.financial_metric_id IS NOT NULL;
