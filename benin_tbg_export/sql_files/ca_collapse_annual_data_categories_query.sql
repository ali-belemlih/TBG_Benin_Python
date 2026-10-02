SELECT
    cc.id   AS category_id,
    cc.name AS category_name,
    cad.date,
    cad.real_value,
    cad.budget_value,
    cad.actual1_value,
    cad.actual2_value,
    cad.actual3_value,
    cad.last_year_real_value
FROM
    public.collapse_annual_data cad
        JOIN
    public.collapse_categories cc ON cad.entity_id = cc.id
WHERE
    cad.entity_type = 'category'  -- ensure the entity type matches
-- AND cad.date = '2024-01-01'  -- optionally filter for a specific year
AND cad.version_id = {version_id}

ORDER BY
    cc.id,
    cad.date;