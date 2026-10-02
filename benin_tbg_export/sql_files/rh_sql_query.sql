SELECT
    rmv.id,
    rt.type_name AS resource_type_name,
    rs.subtype_name AS resource_subtype_name,
    rmv.year,
    rmv.month,
    rmv.value,
    rmv.created_at,
    rmv.updated_at
FROM
    public.resource_monthly_values AS rmv
        LEFT JOIN
    public.resource_type AS rt ON rmv.resource_type_id = rt.id
        LEFT JOIN
    public.resource_subtype AS rs ON rmv.resource_subtype_id = rs.id
WHERE
    rmv.year = '{year_param}'
  AND rmv.month = '{month_param}'
order by rmv.id;