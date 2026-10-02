SELECT cad.id  AS cumul_data_id,
       cad.date,
       ci.id   AS collapsible_item_id,
       ci.name AS collapsible_item_name,
       ct.id   AS collapse_type_id,
       ct.name AS collapse_type_name,
       cad.real_value,
       cad.budget_value,
       cad.actual1_value,
       cad.actual2_value,
       cad.actual3_value,
       cad.last_year_real_value,
       (cad.real_value - cad.budget_value) AS ecart_budget,
                            (cad.real_value - cad.actual1_value) AS ecart_actual1_value,
                            (cad.real_value - cad.actual2_value) AS ecart_actual2_value,
                            (cad.real_value - cad.actual3_value) AS ecart_actual3_value
FROM public.collapse_cumul_data cad
         JOIN
     public.collapse_types ct ON cad.entity_id = ct.id
         JOIN
     public.collapsible_items ci ON ct.collapsible_item_id = ci.id
WHERE cad.entity_type = 'type' -- adjust this if using different entity_type value
  AND cad.date = '{{date}}'
  AND cad.version_id = '{version_id}'
ORDER BY ci.id, ct.sequence_id, cad.date;