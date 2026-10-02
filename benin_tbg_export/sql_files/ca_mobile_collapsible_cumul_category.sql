SELECT cc.id   AS category_id,
       cc.name AS category_name,
       cmd.date,
       cmd.real_value,
       cmd.budget_value,
       cmd.actual1_value,
       cmd.actual2_value,
       cmd.actual3_value,
       cmd.last_year_real_value,
       (cmd.real_value - cmd.budget_value) AS ecart_budget,
              (cmd.real_value - cmd.actual1_value) AS ecart_actual1_value,
              (cmd.real_value - cmd.actual2_value) AS ecart_actual2_value,
              (cmd.real_value - cmd.actual3_value) AS ecart_actual3_value
        FROM public.collapse_cumul_data cmd
         JOIN
     public.collapse_categories cc
     ON cmd.entity_id = cc.id
where cmd.date = '{{date}}'
  and cmd.entity_type = 'category'
  AND cmd.version_id = {version_id}
ORDER BY cc.id,
         cmd.date;