-- Collapse CA Mobile SQL Queries
--id from 17

INSERT INTO collapsible_items (id, name, created_at, updated_at)
VALUES
(17, 'Prépayé (yc commissions)', NOW(), NOW()),
(18, 'Redevance d''abonnement', NOW(), NOW()),
(19, 'Trafic sortant', NOW(), NOW()),
(20, 'Internet Mobile (PrP+PoP)', NOW(), NOW()),
(21, 'CA entrant', NOW(), NOW()),
(22,  'International', NOW(), NOW());

-- Insert into collapse_types (starting from id 160)
INSERT INTO collapse_types (id, collapsible_item_id, name, sequence_id, created_at, updated_at)
VALUES
-- For collapsible_item_id 17
(160, 17, 'Consumer Prepaid', 10, NOW(), NOW()),

-- For collapsible_item_id 18
(161, 18, 'Consumer Postpaid', 10, NOW(), NOW()),
(162, 18, 'Business Postpaid', 20, NOW(), NOW()),
(163, 18, 'Business Prepaid', 30, NOW(), NOW()),

-- For collapsible_item_id 19
(164, 19, 'Consumer Postpaid', 10, NOW(), NOW()),
(165, 19, 'Business Postpaid', 20, NOW(), NOW()),
(166, 19, 'Business Prepaid', 30, NOW(), NOW()),

-- For collapsible_item_id 20
(167, 20, 'dont voix+data', 10, NOW(), NOW()),
(168, 20, 'dont data only', 20, NOW(), NOW()),

-- For collapsible_item_id 22
(169, 22, 'Consumer Prepaid', 10, NOW(), NOW()),
(170, 22, 'Consumer Postpaid', 20, NOW(), NOW()),
(171, 22, 'Business Postpaid', 30, NOW(), NOW()),
(172, 22, 'Business Prepaid', 40, NOW(), NOW());




-- Insert into collapse_categories
INSERT INTO collapse_categories (id, collapse_type_id, name, sequence_id, created_at, updated_at)
VALUES
-- For collapse_type_id 160
(1, 160, 'Frais d''activation & Sim swap', 10, NOW(), NOW()),
(2, 160, 'Total VOIX Sortant', 20, NOW(), NOW()),
(3, 160, 'Total SMS Sortant', 30, NOW(), NOW()),
(4, 160, 'Revenu Internet 3G', 40, NOW(), NOW()),
(5, 160, 'Total Data', 50, NOW(), NOW()),

-- For collapse_type_id 164
(6, 164, 'Total VOIX Sortant', 10, NOW(), NOW()),
(7, 164, 'Total SMS Sortant', 20, NOW(), NOW()),
(8, 164, 'Revenu Internet 3G', 30, NOW(), NOW()),
(9, 164, 'Total Data', 40, NOW(), NOW()),

-- For collapse_type_id 165
(10, 165, 'Total VOIX Sortant', 10, NOW(), NOW()),
(11, 165, 'Total SMS Sortant', 20, NOW(), NOW()),
(12, 165, 'Revenu Internet 3G', 30, NOW(), NOW()),
(13, 165, 'Total Data', 40, NOW(), NOW()),

-- For collapse_type_id 166
(14, 166, 'Total VOIX Sortant', 10, NOW(), NOW()),
(15, 166, 'Total SMS Sortant', 20, NOW(), NOW()),
(16, 166, 'Revenu Internet 3G', 30, NOW(), NOW()),
(17, 166, 'Total Data', 40, NOW(), NOW()),
(18, 166, 'dont CA voix', 50, NOW(), NOW()),
(19, 166, 'dont CA SMS', 60, NOW(), NOW()),
(20, 166, 'dont SVA (Sce à Val. Ajoutée)', 70, NOW(), NOW()),
(21, 166, 'dont CA Internet 3G', 80, NOW(), NOW());

-- Insert into collapse_subcategories
-- Each collapse_category_id group starts with sequence_id 10
-- Removed the unique_name column as requested
INSERT INTO collapse_subcategories (id, collapse_category_id, name, sequence_id, created_at, updated_at)
VALUES
-- For collapse_category_id 2 (Total VOIX Sortant)
(1, 2, 'Sortant voix on net', 10, NOW(), NOW()),
(2, 2, 'Sortant voix MTN', 20, NOW(), NOW()),
(3, 2, 'Sortant voix GLO', 30, NOW(), NOW()),
(4, 2, 'Sortant voix BBCOM', 40, NOW(), NOW()),
(5, 2, 'Sortant voix LIBERCOM', 50, NOW(), NOW()),
(6, 2, 'Sortant voix BTSA', 60, NOW(), NOW()),
(7, 2, 'Sortant voix INTERNATIONAL', 70, NOW(), NOW()),
(8, 2, 'Sortant voix roaming', 80, NOW(), NOW()),

-- For collapse_category_id 3 (Total SMS Sortant)
(9, 3, 'Sortant sms on net', 10, NOW(), NOW()),
(10, 3, 'Sortant sms MTN', 20, NOW(), NOW()),
(11, 3, 'Sortant sms GLO', 30, NOW(), NOW()),
(12, 3, 'Sortant sms BBCOM', 40, NOW(), NOW()),
(13, 3, 'Sortant sms LIBERCOM', 50, NOW(), NOW()),
(14, 3, 'Sortant sms INTERNATIONAL', 60, NOW(), NOW()),

-- For collapse_category_id 5 (Total Data)
(15, 5, 'CRBT', 10, NOW(), NOW()),
(16, 5, 'Crédit secours', 20, NOW(), NOW()),
(17, 5, 'Story Box', 30, NOW(), NOW()),
(18, 5, 'Phonebook STK', 40, NOW(), NOW()),
(19, 5, 'Gaming', 50, NOW(), NOW()),
(20, 5, 'Autres dont BAC17 (VOICEALERT,MOOVKDO...) & SAV agences', 60, NOW(), NOW()),
(21, 5, 'Videos', 70, NOW(), NOW()),

-- For collapse_category_id 6 (Total VOIX Sortant)
(22, 6, 'Sortant voix on net', 10, NOW(), NOW()),
(23, 6, 'Sortant voix MTN', 20, NOW(), NOW()),
(24, 6, 'Sortant voix GLO', 30, NOW(), NOW()),
(25, 6, 'Sortant voix BBCOM', 40, NOW(), NOW()),
(26, 6, 'Sortant voix LIBERCOM', 50, NOW(), NOW()),
(27, 6, 'Sortant voix BTSA', 60, NOW(), NOW()),
(28, 6, 'Sortant voix INTERNATIONAL', 70, NOW(), NOW()),
(29, 6, 'Sortant voix roaming', 80, NOW(), NOW()),

-- For collapse_category_id 7 (Total SMS Sortant)
(30, 7, 'Sortant sms on net', 10, NOW(), NOW()),
(31, 7, 'Sortant sms MTN', 20, NOW(), NOW()),
(32, 7, 'Sortant sms GLO', 30, NOW(), NOW()),
(33, 7, 'Sortant sms BBCOM', 40, NOW(), NOW()),
(34, 7, 'Sortant sms LIBERCOM', 50, NOW(), NOW()),
(35, 7, 'Sortant sms INTERNATIONAL', 60, NOW(), NOW()),

-- For collapse_category_id 9 (Total Data)
(36, 9, 'Transport and Automotive (Traking)', 10, NOW(), NOW()),
(37, 9, 'Banking', 20, NOW(), NOW()),
(38, 9, 'TPE', 30, NOW(), NOW()),

-- For collapse_category_id 10 (Total VOIX Sortant)
(39, 10, 'Sortant voix on net', 10, NOW(), NOW()),
(40, 10, 'Sortant voix MTN', 20, NOW(), NOW()),
(41, 10, 'Sortant voix GLO', 30, NOW(), NOW()),
(42, 10, 'Sortant voix BBCOM', 40, NOW(), NOW()),
(43, 10, 'Sortant voix LIBERCOM', 50, NOW(), NOW()),
(44, 10, 'Sortant voix BTSA', 60, NOW(), NOW()),
(45, 10, 'Sortant voix INTERNATIONAL', 70, NOW(), NOW()),
(46, 10, 'Sortant voix roaming', 80, NOW(), NOW()),

-- For collapse_category_id 11 (Total SMS Sortant)
(47, 11, 'Sortant sms on net', 10, NOW(), NOW()),
(48, 11, 'Sortant sms MTN', 20, NOW(), NOW()),
(49, 11, 'Sortant sms GLO', 30, NOW(), NOW()),
(50, 11, 'Sortant sms BBCOM', 40, NOW(), NOW()),
(51, 11, 'Sortant sms LIBERCOM', 50, NOW(), NOW()),
(52, 11, 'Sortant sms INTERNATIONAL', 60, NOW(), NOW()),

-- For collapse_category_id 13 (Total Data)
(53, 13, 'Transport and Automotive (Traking)', 10, NOW(), NOW()),
(54, 13, 'Banking', 20, NOW(), NOW()),
(55, 13, 'TPE', 30, NOW(), NOW()),

-- For collapse_category_id 14 (Total VOIX Sortant)
(56, 14, 'Sortant voix on net', 10, NOW(), NOW()),
(57, 14, 'Sortant voix MTN', 20, NOW(), NOW()),
(58, 14, 'Sortant voix GLO', 30, NOW(), NOW()),
(59, 14, 'Sortant voix BBCOM', 40, NOW(), NOW()),
(60, 14, 'Sortant voix LIBERCOM', 50, NOW(), NOW()),
(61, 14, 'Sortant voix BTSA', 60, NOW(), NOW()),
(62, 14, 'Sortant voix INTERNATIONAL', 70, NOW(), NOW()),
(63, 14, 'Sortant voix roaming', 80, NOW(), NOW()),

-- For collapse_category_id 15 (Total SMS Sortant)
(64, 15, 'Sortant sms on net', 10, NOW(), NOW()),
(65, 15, 'Sortant sms MTN', 20, NOW(), NOW()),
(66, 15, 'Sortant sms GLO', 30, NOW(), NOW()),
(67, 15, 'Sortant sms BBCOM', 40, NOW(), NOW()),
(68, 15, 'Sortant sms LIBERCOM', 50, NOW(), NOW()),
(69, 15, 'Sortant sms INTERNATIONAL', 60, NOW(), NOW()),

-- For collapse_category_id 17 (Total Data)
(70, 17, 'Transport and Automotive (Traking)', 10, NOW(), NOW()),
(71, 17, 'Banking', 20, NOW(), NOW()),
(72, 17, 'Revenu SAV agences (Call Hystory, Sim swap, Sauvegarde répertoire)', 30, NOW(), NOW()),
(73, 17, 'Autres vas: Service foot, M2u, Moov job, immatriculation, voice alert, parrainage epiq, migration, moov fun.', 40, NOW(), NOW()),
(74, 17, 'CRBT', 50, NOW(), NOW()),
(75, 17, 'Story Box', 60, NOW(), NOW()),
(76, 17, 'Phonebook STK', 70, NOW(), NOW()),
(77, 17, 'Gaming', 80, NOW(), NOW());
