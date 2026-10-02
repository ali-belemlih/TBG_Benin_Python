-- collapsible_items_query.sql
SELECT cmd.id  AS monthly_data_id,
       cmd.date,
       ci.id   AS collapsible_item_id,
       ci.name AS collapsible_item_name,
       ct.id AS collapse_type_id,
       ct.name AS collapse_type_name,
       cmd.real_value,
       cmd.budget_value,
       cmd.actual1_value,
       cmd.actual2_value,
       cmd.actual3_value,
       cmd.last_year_real_value,
               (coalesce(cmd.real_value,0) -coalesce(cmd.budget_value,0)) AS ecart_budget,
                          (coalesce(cmd.real_value,0) - coalesce(cmd.actual1_value,0)) AS ecart_actual1_value,
                          (coalesce(cmd.real_value,0) - coalesce(cmd.actual2_value,0)) AS ecart_actual2_value,
                          (coalesce(cmd.real_value,0) - coalesce(cmd.actual3_value,0)) AS ecart_actual3_value,


              	CASE
                      WHEN cmd.last_year_real_value IS NOT NULL AND cmd.last_year_real_value != 0
                      THEN (cmd.real_value / cmd.last_year_real_value) - 1
                      ELSE NULL
                  END AS evol_percent
FROM public.collapse_monthly_data cmd
         JOIN
     public.collapse_types ct ON cmd.entity_id = ct.id
         JOIN
     public.collapsible_items ci ON ct.collapsible_item_id = ci.id
WHERE cmd.entity_type = 'type'
  AND cmd.date = '{{date}}'
  AND cmd.version_id = {version_id}
  AND  ct.collapsible_item_id > 16
ORDER BY ci.id, ct.sequence_id, cmd.date;
