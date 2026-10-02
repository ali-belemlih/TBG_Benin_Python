-- Trafic Mobile SQL Queries

INSERT INTO financial_types (id,name, financial_category_id, sequence_id, created_at, updated_at)  
VALUES  
(31,'Total  Trafic sortant', 7, 10, NOW(), NOW()),  
(32,'Total  Trafic entrant', 7, 20, NOW(), NOW());

INSERT INTO financial_metric (id,financial_type_id, name, sequence_id, created_at, updated_at)  
VALUES  
--financial_type_id = 100
(89, 31, 'Trafic sortant prépayé (Consumer)', 10, NOW(), NOW()),  
(90, 31, 'Trafic sortant postpayé', 20, NOW(), NOW()), 

--financial_type_id = 101 
(91,32, 'Trafic entrant prépayé (Consumer)', 10, NOW(), NOW()),  
(92,32, 'Trafic entrant postpayé', 20, NOW(), NOW());


INSERT INTO financial_submetric (id,financial_metric_id, name, sequence_id, created_at, updated_at)  
VALUES

-- financial_metric_id = 89  
(23,89, 'vers le fixe', 10, NOW(), NOW()),  
(24,89, 'vers l''international', 20, NOW(), NOW()),  
(25,89, 'vers Mobile (on net)', 30, NOW(), NOW()),
(26,89, 'vers MTN', 40, NOW(), NOW()),
(27,89,'vers SBIN', 50, NOW(), NOW()),
(28,89, 'vers BBCOM, LIBERCOM', 60,NOW(), NOW()),
(29,89,'Outbound roaming',70, NOW(), NOW()),

--financial_metric_id = 90
(30,90, 'vers le fixe', 10, NOW(), NOW()),
(31,90, 'vers l''international', 20 ,NOW(), NOW()),
(32,90, 'vers Mobile (on net)', 30 ,NOW(), NOW()),
(33,90, ' vers MTN', 40 ,NOW(), NOW()),
(34,90, 'vers SBIN', 50 ,NOW(),NOW()),
(35,90, 'vers BBCOM, LIBERCOM', 60 ,NOW(), NOW()),
(36,90, 'Outbound roaming', 70 ,NOW(), NOW()),

--financial_type_id = 91
(37,91,'du fixe', 10,NOW(), NOW()),
(38,91,'de l''international', 20,NOW(), NOW()),
(39,91,'de MTN',30,NOW(), NOW()),
(40,91,'de SBIN', 40,NOW(), NOW()),
(41,91,'de BBCOM, LIBERCOM', 50,NOW(), NOW()),

-- financial_metric_id = 92
(42,92,'du fixe',10,NOW(), NOW()),
(43,92,'de l''international',20,NOW(), NOW()),
(44,92,'de MTN',30,NOW(), NOW()),
(45,92,'de SBIN',40,NOW(), NOW()),
(46,92,'de BBCOM, LIBERCOM',50,NOW(), NOW());
