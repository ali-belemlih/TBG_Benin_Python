-- Profit & Loss SQL Queries

INSERT INTO financial_types (name, financial_category_id, sequence_id, created_at, updated_at)  
VALUES  
('Chiffre d''affaires', 1, 10, NOW(), NOW()),  
('RESULTAT NET', 1, 20, NOW(), NOW()),  


INSERT INTO financial_metric (financial_type_id, name, sequence_id, created_at, updated_at)  
VALUES  
-- financial_type_id = 29
(29, 'Mobile', 10, NOW(), NOW()),  
(29, 'Coût des ventes', 20, NOW(), NOW()),  
(29, 'Marge Brute', 30, NOW(), NOW()),  
(29, 'Coûts opérationnels', 40, NOW(), NOW()),  
(29, 'EBITDA', 50, NOW(), NOW()),  
(29, 'Amortissements et déprec. Courant', 60, NOW(), NOW()),  
(29, 'EBITA', 70, NOW(), NOW()),  
(29, 'Résultat financier', 80, NOW(), NOW()),  
(29, 'RESULTAT avant IS', 90, NOW(), NOW()),  

-- financial_type_id = 30
(30, '% CA', 10, NOW(), NOW());


INSERT INTO financial_submetric (financial_metric_id, name, sequence_id, created_at, updated_at)  
VALUES  
-- financial_metric_id = 79
(79, 'Intercompagnie Mobile', 10, NOW(), NOW()),  

-- financial_metric_id = 80
(80, 'Mobile', 10, NOW(), NOW()),  
(80, 'Intercompagnie Mobile', 20, NOW(), NOW()),  

-- financial_metric_id = 81
(81, '% CA', 10, NOW(), NOW()),  
(81, 'Mobile', 20, NOW(), NOW()),  

-- financial_metric_id = 82
(82, 'Mobile', 10, NOW(), NOW()),  
(82, 'Intercompagnie Mobile', 20, NOW(), NOW()),  

-- financial_metric_id = 83
(83, '% CA', 10, NOW(), NOW()),  
(83, 'Mobile', 20, NOW(), NOW()),  

-- financial_metric_id = 85
(85, '% CA', 10, NOW(), NOW()),  

-- financial_metric_id = 87
(87, 'IS', 10, NOW(), NOW()),  
(87, 'ID', 20, NOW(), NOW());
