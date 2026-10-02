SELECT cd.entity_id,
       cs.name AS designation,
       cs.type AS section_type,
       cd.entity_type,
       cd.year,
       cd.last_year_total,
       cd.current_year_total,
       (COALESCE(cd.jan, 0) + COALESCE(cd.adjusted_jan, 0)) AS January,
       (COALESCE(cd.feb, 0) + COALESCE(cd.adjusted_feb, 0)) AS February,
       (COALESCE(cd.mar, 0) + COALESCE(cd.adjusted_mar, 0)) AS March,
       (COALESCE(cd.apr, 0) + COALESCE(cd.adjusted_apr, 0)) AS April,
       (COALESCE(cd.may, 0) + COALESCE(cd.adjusted_may, 0)) AS May,
       (COALESCE(cd.jun, 0) + COALESCE(cd.adjusted_jun, 0)) AS June,
       (COALESCE(cd.jul, 0) + COALESCE(cd.adjusted_jul, 0)) AS July,
       (COALESCE(cd.aug, 0) + COALESCE(cd.adjusted_aug, 0)) AS August,
       (COALESCE(cd.sep, 0) + COALESCE(cd.adjusted_sep, 0)) AS September,
       (COALESCE(cd.oct, 0) + COALESCE(cd.adjusted_oct, 0)) AS October,
       (COALESCE(cd.nov, 0) + COALESCE(cd.adjusted_nov, 0)) AS November,
       (COALESCE(cd.dec, 0) + COALESCE(cd.adjusted_dec, 0)) AS December
FROM public.cashflow_data AS cd
         LEFT JOIN public.cashflow_sections AS cs ON cd.entity_id = cs.id
WHERE cd.entity_type = 'section'
  AND cs.type = '{section_type}'
  AND cd.version_id = {version_id}
ORDER BY cd.entity_id;