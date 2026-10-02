-- Marge Mobile SQL Queries

INSERT INTO financial_types (name, financial_category_id, sequence_id, created_at, updated_at)  
VALUES  
('Total Revenu', 6, 10, NOW(), NOW()),  
('Coûts des ventes', 6, 20, NOW(), NOW()),  
('Marge Brute', 6, 30, NOW(), NOW()),  
('En % du CA', 6, 40, NOW(), NOW());


INSERT INTO financial_metric (financial_type_id, name, sequence_id, created_at, updated_at)  
VALUES  
(25, 'Trafic (mn)', 10, NOW(), NOW()),  
(25, 'Coût unitaire-Trafic', 20, NOW(), NOW()),  
(25, 'International', 30, NOW(), NOW()),  
(25, 'Reversements SVA', 40, NOW(), NOW()),  
(25, 'Achat de capacité', 50, NOW(), NOW()),  
(25, 'Nbre SMS', 60, NOW(), NOW()),  
(25, 'Coût unitaire-SMS', 70, NOW(), NOW()),  
(25, 'Interconnexion SMS', 80, NOW(), NOW()),  
(25, 'Roaming out', 90, NOW(), NOW()),  
(25, 'Coûts des terminaux et cartes', 100, NOW(), NOW()),  
(25, 'Commissions', 110, NOW(), NOW());  


INSERT INTO financial_submetric (financial_metric_id, name, sequence_id, created_at, updated_at)  
VALUES  
-- financial_metric_id = 77  
(77, 'Dont coût des terminaux.', 10, NOW(), NOW()),  
(77, 'Dont provisions sur stocks', 20, NOW(), NOW()),  

-- financial_metric_id = 78  
(78, 'Dont commissions up-front', 10, NOW(), NOW()),  
(78, 'Dont avoirs de performance', 20, NOW(), NOW()),  
(78, 'Dont Commissions Flooz', 30, NOW(), NOW());  
