-- Capex Consolidate SQL Queries

INSERT INTO financial_types (name, financial_category_id, sequence_id)  
VALUES  
('Total capex', 2, 10),  
('Réseau', 2, 20),  
('Commercial et Marketing', 2, 30),  
('Administratif et Financier', 2, 40);  


INSERT INTO financial_metric (financial_type_id, name, sequence_id, created_at, updated_at)  
VALUES  
-- financial_type_id = 2
(2, 'Réseau d''accès', 10, NOW(), NOW()),  
(2, 'Activation du personnel', 20, NOW(), NOW()),  
(2, 'Commutation & plates-formes', 30, NOW(), NOW()),  
(2, 'Transmission', 40, NOW(), NOW()),  
(2, 'Energie & climatisation', 50, NOW(), NOW()),  
(2, 'Réseau International et interconnexion', 60, NOW(), NOW()),  
(2, 'Internet', 70, NOW(), NOW()),  
(2, 'Système d''information', 80, NOW(), NOW()),  
(2, 'Matériel industriel', 90, NOW(), NOW()),  
(2, 'Installation et agencement', 100, NOW(), NOW()),  
(2, 'Matériel informatique', 110, NOW(), NOW()),  

-- financial_type_id = 3
(3, 'Commercial', 10, NOW(), NOW()),  
(3, 'Marketing', 20, NOW(), NOW()),  
(3, 'Capexisation des kits', 30, NOW(), NOW()),  

-- financial_type_id = 4
(4, 'Logistique', 10, NOW(), NOW()),  
(4, 'Matériel et outillage industriels', 20, NOW(), NOW()),  
(4, 'Materiel informatique', 30, NOW(), NOW()),  
(4, 'Matériels et mobiliers', 40, NOW(), NOW()),  
(4, 'Climatiseurs', 50, NOW(), NOW()),  
(4, 'Autres matériels et mobiliers', 60, NOW(), NOW()),  
(4, 'Autres agencements (eau electricité, autres)', 70, NOW(), NOW()),  
(4, 'Autres installations', 80, NOW(), NOW()),  
(4, 'Terrains et Batiments', 90, NOW(), NOW()),  
(4, 'Transport', 100, NOW(), NOW()),  
(4, 'Autres(mat. Bureau, bureautique, …)', 110, NOW(), NOW()),  
(4, 'Materiel bureautique', 120, NOW(), NOW()),  
(4, 'Mobilier de bureau', 130, NOW(), NOW());  
