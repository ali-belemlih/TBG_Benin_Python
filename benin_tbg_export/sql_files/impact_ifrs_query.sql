SELECT
    simv.id AS monthly_value_id,
    si.id AS standard_id,
    si.standard_name,
    si.sequence_id,
    simv.year,
    simv.month,
    simv.value,
    simv.created_at AS monthly_value_created_at,
    simv.updated_at AS monthly_value_updated_at,
    si.created_at AS standard_created_at,
    si.updated_at AS standard_updated_at
FROM
    public.standard_impact_monthly_values AS simv
        JOIN
    public.standard_impact AS si
    ON
        simv.standard_impact_id = si.id
where simv.month = '{month_param}'
  and simv.year = '{year_param}'
ORDER BY
    simv.id