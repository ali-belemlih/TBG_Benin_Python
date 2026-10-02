-- Mobile Money SQL Queries
--id from 47
INSERT INTO financial_types (id,name, financial_category_id, sequence_id, created_at, updated_at)  
VALUES  

(47,'Parc Total Mobile Actif',10, 10, NOW(), NOW()),
(48,'Parc Prépayé Actif',10, 20, NOW(), NOW()),
(49,'Parc Postpayé',10, 30, NOW(), NOW());



--id from 138
INSERT INTO financial_metric (id,financial_type_id, name, sequence_id, created_at, updated_at)  
VALUES  

(138,47,'Parc début Période',10,NOW(), NOW()),
(139,47,'Parc Total (Prépayé & Postpayé)',20,NOW(), NOW()),
(140,47,'Parc Actif',30,NOW(), NOW()),

(141,48,'Parc prépayé actif début Période',10,NOW(), NOW()),
(142,48,'Parc prépayé actif fin de période',20,NOW(), NOW()),

(143,49,'Parc début Période',10,NOW(), NOW()),
(144,49,'Parc Postpayé',20,NOW(), NOW());


--id from 74
INSERT INTO financial_submetric (id,financial_metric_id, name, sequence_id, created_at, updated_at)  
VALUES

(74,138,'Activations totales',10,NOW(),NOW()),
(75,138,'Résiliations totales',20, NOW(), NOW()),
(76,138,'% résiliation',30,NOW(),NOW()),
(77,138,'Ventes nettes',40,NOW(), NOW()),
(78,138,'Acroissement net', 50,NOW(), NOW()),
(79,138,'Flux d''inactivité(Prd) et résiliations(PoP)', 60,NOW(),NOW()),
(80,138,'Taux de churn annualisé',70,NOW(), NOW()),

(81, 139, 'Parc Moyen Total', 10, NOW(), NOW()),

(82,140, 'Parc Moyen Actif', 10, NOW(), NOW()),

(83,141,'Activations totales', 10,NOW(), NOW()),
(84,141,'Flux d''inactivité', 20,NOW(), NOW()),
(85,141,'% churn annualisé', 30, NOW(), NOW()),
(86,141,'Acroissement net',40,NOW(), NOW()),

(87, 142, 'Parc Actif Moyen', 10, NOW(),NOW()),

(88,143,'Activations totales', 10,NOW(),NOW()),
(89,143,'Résiliations totales',20,NOW(),NOW()),
(90, 143,'% résiliation annualisé',30,NOW(),NOW()),
(91, 143,'Ventes nettes',40,NOW(),NOW()),

(92, 144, 'Parc Moyen Postpayé', 10, NOW(), NOW());
