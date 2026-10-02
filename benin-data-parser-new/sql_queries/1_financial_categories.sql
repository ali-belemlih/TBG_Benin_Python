INSERT INTO financial_categories (id, name) VALUES
(1, 'P&L consolidé'),
(2, 'Capex Consolidés'),
(3, 'Flux Financiers consolidés'),
(4, 'Opex Consolidés'),
(5, 'CA Mobile'),
(6, 'Marge brute Mobile')
(7,'Trafic mobile'),
(8, 'Mobile Money'),
(9,'Data Mobile'),
(10,'Parc Mobile'),
(11,'Indicateurs Mobile')
ON CONFLICT (id) DO NOTHING;


-- INSERT INTO financial_categories (id, name) VALUES
-- (7,'Trafic mobile'),
-- (8, 'Mobile Money'),
-- (9,'Data Mobile'),
-- (10,'Parc Mobile');
