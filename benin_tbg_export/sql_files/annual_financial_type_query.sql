SELECT ft.name AS financial_type_name,
       fad.*

FROM financial_annual_data fad
         LEFT JOIN financial_types ft ON fad.financial_type_id = ft.id
         LEFT JOIN financial_categories fc ON ft.financial_category_id = fc.id
WHERE fc.name = '{sheet_name_param}'
AND fad.version_id = {version_id};