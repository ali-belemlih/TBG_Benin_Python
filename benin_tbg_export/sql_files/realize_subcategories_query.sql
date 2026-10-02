SELECT cd.entity_id,
       csc.name AS designation,
       cd.entity_type,
       cd.year,
       cd.last_year_total,
       cd.current_year_total,
       (COALESCE(cd.jan, 0) + COALESCE(cd.adjusted_jan, 0)) AS january,
       (COALESCE(cd.feb, 0) + COALESCE(cd.adjusted_feb, 0)) AS february,
       (COALESCE(cd.mar, 0) + COALESCE(cd.adjusted_mar, 0)) AS march,
       (COALESCE(cd.apr, 0) + COALESCE(cd.adjusted_apr, 0)) AS april,
       (COALESCE(cd.may, 0) + COALESCE(cd.adjusted_may, 0)) AS may,
       (COALESCE(cd.jun, 0) + COALESCE(cd.adjusted_jun, 0)) AS june,
       (COALESCE(cd.jul, 0) + COALESCE(cd.adjusted_jul, 0)) AS july,
       (COALESCE(cd.aug, 0) + COALESCE(cd.adjusted_aug, 0)) AS august,
       (COALESCE(cd.sep, 0) + COALESCE(cd.adjusted_sep, 0)) AS september,
       (COALESCE(cd.oct, 0) + COALESCE(cd.adjusted_oct, 0)) AS october,
       (COALESCE(cd.nov, 0) + COALESCE(cd.adjusted_nov, 0)) AS november,
       (COALESCE(cd.dec, 0) + COALESCE(cd.adjusted_dec, 0)) AS december
FROM public.cashflow_data AS cd
         LEFT JOIN public.cashflow_subcategories AS csc ON cd.entity_id = csc.id
WHERE cd.entity_type = 'subcategory'
  AND cd.version_id = {version_id}
ORDER BY cd.entity_id;