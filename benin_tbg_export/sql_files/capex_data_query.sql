SELECT capex_projects_id, month, year, equipment, services, additional_costs
FROM public.capex_data
WHERE year ='{year_to_process}';