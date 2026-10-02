-- Opex Consolidate SQL Queries

INSERT INTO financial_types (name, financial_category_id, sequence_id, created_at, updated_at)  
VALUES  
('Total Opex', 4, 10, NOW(), NOW()),  
('Personnel', 4, 20, NOW(), NOW()),  
('Communication', 4, 30, NOW(), NOW()),  
('Exploitation & maintenance', 4, 40, NOW(), NOW()),  
('Frais généraux', 4, 50, NOW(), NOW()),  
('Impôts, taxes et redevances', 4, 60, NOW(), NOW()),  
('Provision clients, R&C & NC', 4, 70, NOW(), NOW()),  
('Ecart de change sur exploitation', 4, 80, NOW(), NOW());  


INSERT INTO financial_metric (financial_type_id, name, sequence_id, created_at, updated_at)  
VALUES  
-- financial_type_id = 8  
(8, 'Achat d''énergie - Bâtiment - Gardiennage', 10, NOW(), NOW()),  
(8, 'Lignes et réseaux (entretien & achats)', 20, NOW(), NOW()),  
(8, 'Fees du contrat GMNS', 30, NOW(), NOW()),  
(8, 'Matériel de transport (Entretien et locat°)', 40, NOW(), NOW()),  
(8, 'Maintenance informatique', 50, NOW(), NOW()),  

-- financial_type_id = 9  
(9, 'Frais d''achats d''études, honoraires', 10, NOW(), NOW()),  
(9, 'Management fees', 20, NOW(), NOW()),  
(9, 'Transport, déplacement, mission', 30, NOW(), NOW()),  
(9, 'Frais postaux, bancaires et assurances', 40, NOW(), NOW()),  
(9, 'Achats de mat. et fournitures consom.', 50, NOW(), NOW()),  

-- financial_type_id = 10  
(10, 'Redevances régulateur', 10, NOW(), NOW()),  
(10, 'Droits sur le trafic International Entrant', 20, NOW(), NOW()),  
(10, 'Autres impôts et taxes', 30, NOW(), NOW()),  

-- financial_type_id = 11  
(11, 'Prov. Créances clients', 10, NOW(), NOW()),  
(11, 'Prov. R&C', 20, NOW(), NOW()),  
(11, 'PIDR', 30, NOW(), NOW()),  
(11, 'Autres provisions', 40, NOW(), NOW());  
