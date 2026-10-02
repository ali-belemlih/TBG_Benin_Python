-- Mobile Money SQL Queries
--id from 50
INSERT INTO financial_types (id,name, financial_category_id, sequence_id, created_at, updated_at)  
VALUES  


(50,'ARPU Global',11,10,NOW(), NOW()),
(51,'ARPU Prépayé',11,20,NOW(), NOW()),
(52,'ARPU Postpayé',11,30,NOW(), NOW()),
(53,'Usage / client / mois',11,40,NOW(), NOW()),
(54,'Prix mn',11,50, NOW(), NOW());

--id from 145
INSERT INTO financial_metric (id,financial_type_id, name, sequence_id, created_at, updated_at)  
VALUES  

    (145, 50,'ARPU Sortant', 10, NOW(), NOW()),
	(146,50,'ARPU Entrant', 20, NOW(), NOW()),

    (147, 51,'ARPU Sortant', 10, NOW(), NOW()),
	(148,51,'ARPU Entrant', 20, NOW(), NOW()),

    (149, 52,'ARPU Sortant', 10, NOW(), NOW()),
	(150,52,'ARPU Entrant', 20, NOW(), NOW()),

    (151,53,'Usage Sortant',10, NOW(), NOW()),
	(152,53,'Usage Entrant',20, NOW(), NOW()),
	
    (153,54,'Prix mn Sortant',10,NOW(), NOW()),
    (154,54,'Prix mn Entrant',20,NOW(), NOW());
    

--id from 93
INSERT INTO financial_submetric (id,financial_metric_id, name, sequence_id, created_at, updated_at)  
VALUES


    (93, 151,'Prépayé', 10, NOW(), NOW()),
    (94, 151, 'Postpayé', 20, NOW(), NOW()),

    (95, 152,'Prépayé', 10, NOW(), NOW()),
    (96, 152, 'Postpayé', 20, NOW(), NOW()),

    (97, 153,'Prépayé', 10, NOW(), NOW()),
    (98, 153, 'Postpayé', 20, NOW(), NOW()),

    (99, 154,'Prépayé', 10, NOW(), NOW()),
    (100, 154, 'Postpayé', 20, NOW(), NOW());