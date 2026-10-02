-- Mobile Money SQL Queries
--id from 33
INSERT INTO financial_types (id,name, financial_category_id, sequence_id, created_at, updated_at)  
VALUES  
(33,'Parc clients Total	', 8, 10, NOW(), NOW()),  
(34,'Parc clients actif (90 jours)', 8, 20, NOW(), NOW()),
(35,'Nombre de points de ventes', 8, 30, NOW(), NOW()),
(36,'Nombre de points de Marchand', 8, 40, NOW(), NOW()),
(37,'Total Montant des transactions', 8,50, NOW(), NOW()),
(38, 'Chiffre d''affaires', 8,60, NOW(), NOW()),
(39, 'Total Commissions', 8,70, NOW(), NOW()),
(40, 'Marge Brute (en monnaie locale)', 8, 80, NOW(), NOW());


--id from 93
INSERT INTO financial_metric (id,financial_type_id, name, sequence_id, created_at, updated_at)  
VALUES  

(93,37,'Dépôt d''argent', 10,NOW(), NOW()),
(94,37,'Retrait d''argent', 20,NOW(), NOW()),
(95,37,'Transfert d''argent national', 30,NOW(), NOW()),
(96,37,'Transfert d''argent international', 40,NOW(), NOW()),
(97,37,'Recharge Mobile', 50,NOW(), NOW()),
(98,37,'Achat de forfaits', 60,NOW(), NOW()),
(99,37,'Achat de biens et services', 70,NOW(), NOW()),
(100,37,'Parie en ligne',80,NOW(), NOW()),
(101,37,'Paiement de factures',90,NOW(), NOW()),
(102,37,'Paiement de salaires',100,NOW(), NOW()),
(103,37,'Autres (Push & Pull_paiements en ligne inclus)', 110,NOW(), NOW()),

(104,38,'Dépôt d''argent',10,NOW(), NOW()),
(105,38,'Retrait d''argent',20,NOW(), NOW()),
(106,38,'Transfert d''argent national',30,NOW(), NOW()),
(107,38,'Transfert d''argent international',40,NOW(), NOW()),
(108,38,'Recharge Mobile (Activation de forfaits inclue)',50,NOW(), NOW()),
(109,38,'Achat de biens et services',60,NOW(), NOW()),
(110,38,'Pari en ligne', 70,NOW(), NOW()),
(111,38,'Paiement de factures',80,NOW(), NOW()),
(112,38,'Paiement de salaires',90,NOW(), NOW()),
(113,38,'Pack Moov Money',100,NOW(), NOW()),
(114,38,'Reversement MAB A MM',110,NOW(), NOW()),
(115,38,'Autres (Push & Pull)',120,NOW(), NOW()),

(116,39,'Dont commissions Revendeurs', 10, NOW(), NOW()),
(117,39,'Dont commissions ETB', 20, NOW(), NOW()),
(118,39,'Dont commissions Banques', 30, NOW(), NOW()),

(119, 40, '% Marge Brute/CA', 10, NOW(), NOW());


--id from 47
INSERT INTO financial_submetric (id,financial_metric_id, name, sequence_id, created_at, updated_at)  
VALUES
(47,116,'Dépôt d''argent', 10,NOW(), NOW()),
(48,116,'Retrait d''argent', 20,NOW(), NOW()),
(49,116,'Transfert d''argent national', 30,NOW(), NOW()),
(50,116,'Transfert d''argent international', 40,NOW(), NOW()),
(51,116,'Recharge Mobile', 50,NOW(), NOW()),
(52,116,'Achat de biens et services',60,NOW(), NOW()),
(53,116,'Paiement de factures',70,NOW(),NOW()),
(54,116,'Paiement de salaires',80,NOW(),NOW()),
(55,116,'Autres (à préciser)',90,NOW(),NOW()),


(56,117,'Dépôt d''argent', 10,NOW(),NOW()),
(57,117,'Retrait d''argent', 20,NOW(),NOW()),
(58,117,'Transfert d''argent national',30,NOW(),NOW()),
(59,117,'Transfert d''argent international',40,NOW(),NOW()),
(60,117,'Recharge Mobile',50,NOW(),NOW()),
(61,117,'Achat de biens et services',60,NOW(),NOW()),
(62,117,'Paiement de factures',70, NOW(),NOW()),
(63,117,'Paiement de salaires',80,NOW(),NOW()),
(64,117,'Autres (à préciser)',90,NOW(),NOW()),

(65,118,'Dépôt d''argent',10,NOW(),NOW()),
(66,118,'Retrait d''argent',20,NOW(), NOW()),
(67,118,'Transfert d''argent national',30,NOW(), NOW()),
(68,118,'Transfert d''argent international',40,NOW(), NOW()),
(69,118,'Recharge Mobile',50,NOW(), NOW()),
(70,118,'Achat de biens et services',60,NOW(), NOW()),
(71,118,'Paiement de factures',70,NOW(), NOW()),
(72,118,'Paiement de salaires',80,NOW(), NOW()),
(73,118,'Autres (Push & Pull)',90,NOW(), NOW());
