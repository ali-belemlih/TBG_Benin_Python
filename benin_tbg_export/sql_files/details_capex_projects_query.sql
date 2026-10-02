SELECT p.id, p.project_title, p.contract_no, p.contract_date, p.supplier_name, p.direction_name
FROM public.capex_projects p
WHERE EXISTS (
    SELECT 1
    FROM public.capex_data d
    WHERE d.capex_projects_id = p.id AND d.year ='{year_to_process}'
)
ORDER BY p.sequence_id;
