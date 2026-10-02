-- Mobile Money SQL Queries
--id from 41
INSERT INTO financial_types (id,name, financial_category_id, sequence_id, created_at, updated_at)  
VALUES  

(41,'Parc Data Mobile actif (90 jrs)',9,10,NOW(), NOW()),	
(42,'Trafic data (en millions de Go)',9,20,NOW(), NOW()),	
(43,'Chiffre d''affaires',9,30,NOW(), NOW()),
(44,'ARPU',9,40,NOW(), NOW()),
(45,'Usage (en Go/client)',9,50, NOW(), NOW()),
(46,'Prix / Go',9,60,NOW(), NOW());		


--id from 120
INSERT INTO financial_metric (id,financial_type_id, name, sequence_id, created_at, updated_at)  
VALUES  

(120,41,'2G', 10,NOW(), NOW()),	
(121,41,'3G', 20, NOW(), NOW()),
(122,41,'4G',30,NOW(), NOW()),	

(123,42,'2G', 10,NOW(), NOW()),	
(124,42,'3G', 20, NOW(), NOW()),
(125,42,'4G',30,NOW(), NOW()),	


(126,43,'2G', 10,NOW(), NOW()),	
(127,43,'3G', 20, NOW(), NOW()),
(128,43,'4G',30,NOW(), NOW()),	

(129,44,'2G', 10,NOW(), NOW()),	
(130,44,'3G', 20, NOW(), NOW()),
(131,44,'4G',30,NOW(), NOW()),	

(132,45,'2G', 10,NOW(), NOW()),	
(133,45,'3G', 20, NOW(), NOW()),
(134,45,'4G',30,NOW(), NOW()),	

(135,46,'2G', 10,NOW(), NOW()),	
(136,46,'3G', 20, NOW(), NOW()),
(137,46,'4G',30,NOW(), NOW());
