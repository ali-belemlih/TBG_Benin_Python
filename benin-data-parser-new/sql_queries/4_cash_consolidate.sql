-- Cash Consolidate SQL Queries

INSERT INTO financial_types (name, financial_category_id, sequence_id, created_at, updated_at)  
VALUES  
('EBITDA', 3, 10, NOW(), NOW()),  
('CFFO', 3, 20, NOW(), NOW()),  
('Net cash flow', 3, 30, NOW(), NOW()),  
('Trésorerie nette fin de période', 3, 40, NOW(), NOW());

INSERT INTO financial_metric (financial_type_id, name, sequence_id, created_at, updated_at)  
VALUES  
-- financial_type_id = 14  
(14, 'Neutralisation de la var. de provisions incluses dans l''Ebitda (-)', 10, NOW(), NOW()),  
(14, 'Variation de BFR opérationnel (+/-)', 20, NOW(), NOW()),  
(14, 'Dividendes reçus des participations non consolidées (+)', 30, NOW(), NOW()),  
(14, 'Investissements bruts (Flux d''augmentation des immos corporelles et incorporelles bruts de la période) (-)', 40, NOW(), NOW()),  
(14, 'Produit de cession des immobilisations corporelles et incorporelles (+)', 50, NOW(), NOW()),  
(14, 'Cession d''immobilisations', 60, NOW(), NOW()),  
(14, 'Investissements nets (Capex brutes - cession d''immo.) (-)', 70, NOW(), NOW()),  
(14, 'Plan de restructuration', 80, NOW(), NOW()),  

-- financial_type_id = 15  
(15, 'Cash flow used for financing and taxes', 10, NOW(), NOW()),  
(15, 'Cash flow used for investment (+/-)', 20, NOW(), NOW()),  
(15, 'Autres éléments non cash', 30, NOW(), NOW()),  

-- financial_type_id = 16  
(16, 'Dettes brutes (-)', 10, NOW(), NOW()),  
(16, 'Trésorerie brute (+)', 20, NOW(), NOW());  



INSERT INTO financial_submetric (financial_metric_id, name, sequence_id, created_at, updated_at)  
VALUES  
(53, 'Résultat financier hors dividendes des stés non consolidées (+/-)', 10, NOW(), NOW()),  
(53, 'Impôts payés (-)', 20, NOW(), NOW()),  
(53, 'Dividendes payés (-)', 30, NOW(), NOW());  
