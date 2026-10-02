SELECT cs.id   AS subcategory_id,
       cs.name AS subcategory_name,
       cad.date,
       cad.budget_value,
       cad.actual1_value,
       cad.actual2_value,
       cad.actual3_value,
       cad.last_year_real_value
FROM public.collapse_annual_data cad
         JOIN public.collapse_subcategories cs
              ON cad.entity_id = cs.id
WHERE cad.entity_type = 'subcategory'
  AND cad.date = '2024-01-01' -- or dynamically injected
  AND cad.version_id = {version_id}
ORDER BY cs.id;
