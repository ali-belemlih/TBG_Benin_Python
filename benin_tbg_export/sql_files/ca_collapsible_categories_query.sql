SELECT cc.id   AS category_id,
       cc.name AS category_name,
       cmd.date,
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
     public.collapse_categories cc
     ON cmd.entity_id = cc.id
where cmd.date = '{{date}}'
  and cmd.entity_type = 'category'
  AND cmd.version_id = {version_id}
ORDER BY cc.id,
         cmd.date;