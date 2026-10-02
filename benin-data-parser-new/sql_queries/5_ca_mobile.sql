-- CA Mobile SQL Queries

INSERT INTO financial_types (name, financial_category_id, sequence_id, created_at, updated_at)  
VALUES  
('CA Global', 5, 10, NOW(), NOW()),  
('CA services Mobile', 5, 20, NOW(), NOW()),  
('CA récurrent', 5, 30, NOW(), NOW()),  
('CA sortant', 5, 40, NOW(), NOW()),  
('CA entrant', 5, 50, NOW(), NOW()),  
('Colocalisation', 5, 60, NOW(), NOW()),  
('Roaming in', 5, 70, NOW(), NOW()),  
('CA Non récurrent', 5, 80, NOW(), NOW());


INSERT INTO financial_metric (financial_type_id, name, sequence_id, created_at, updated_at)  
VALUES  
-- financial_type_id = 20  
(20, 'Prépayé (yc commissions)', 10, NOW(), NOW()),  
(20, 'Postpayé', 20, NOW(), NOW()),  
(20, 'Mobile Money', 30, NOW(), NOW()),  
(20, 'Liaisons Spécialisées', 40, NOW(), NOW()),  
(20, 'Internet Mobile (PrP+PoP)', 50, NOW(), NOW()),  

-- financial_type_id = 21  
(21, 'International', 10, NOW(), NOW()),  

-- financial_type_id = 23  
(23, 'Dont Roaming National', 10, NOW(), NOW()),  

-- financial_type_id = 24  
(24, 'Terminaux', 10, NOW(), NOW()),  
(24, 'Clé Internet Mobile', 20, NOW(), NOW()),  
(24, 'Autres', 30, NOW(), NOW());  


INSERT INTO financial_submetric (financial_metric_id, name, sequence_id, created_at, updated_at)  
VALUES  
(59, 'Redevance d''abonnement', 10, NOW(), NOW()),  
(59, 'Trafic sortant', 20, NOW(), NOW());  
