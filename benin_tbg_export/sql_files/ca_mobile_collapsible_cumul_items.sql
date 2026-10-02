-- collapsible_items_query.sql
SELECT cmd.id  AS cumul_data_id,
       cmd.date,
       ci.id   AS collapsible_item_id,
       ci.name AS collapsible_item_name,
       ct.name AS collapse_type_name,
       cmd.real_value,
       cmd.budget_value,
       cmd.actual1_value,
       cmd.actual2_value,
       cmd.actual3_value,
       cmd.last_year_real_value,
       (cmd.real_value - cmd.budget_value) AS ecart_budget,
                     (cmd.real_value - cmd.actual1_value) AS ecart_actual1_value,
                     (cmd.real_value - cmd.actual2_value) AS ecart_actual2_value,
                     (cmd.real_value - cmd.actual3_value) AS ecart_actual3_value,
       ct.id   AS collapse_type_id
FROM public.collapse_cumul_data cmd
         JOIN
     public.collapse_types ct ON cmd.entity_id = ct.id
         JOIN
     public.collapsible_items ci ON ct.collapsible_item_id = ci.id
WHERE cmd.entity_type = 'type'
  AND cmd.date = '{{date}}'
  AND cmd.version_id = {version_id}
  AND  ct.collapsible_item_id > 16
ORDER BY ci.id, ct.sequence_id, cmd.date;
