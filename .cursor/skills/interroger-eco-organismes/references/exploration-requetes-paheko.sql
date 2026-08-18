-- Paheko SQLite — COMPTA euros uniquement (SELECT only, mode=ro).
-- PAS une source de volumes éco-organismes (DEC_REE / LIV / poids).
-- Recyclique = skill interroger-eco-organismes + exploration-requetes.sql
-- Décision 2026-08-18 : désinstaller saisie_poids + plugin Caisse dans Paheko.

-- 1. Signature
SELECT value FROM config WHERE key = 'org_name';
SELECT name, label, enabled FROM modules ORDER BY name;
SELECT name, label, enabled FROM plugins;
SELECT id, label, start_date, end_date, status FROM acc_years;

-- 2. Checklist désinstallation (doit rester vide / désactivé)
SELECT name, enabled FROM modules WHERE name = 'saisie_poids';
SELECT name FROM sqlite_master
WHERE type = 'table'
  AND (name = 'module_data_saisie_poids' OR name LIKE 'plugin_pos_%');

-- 3. Périmètre utile : exercices et écritures
SELECT MIN(date), MAX(date), COUNT(*) FROM acc_transactions;
SELECT y.label, COUNT(t.id) AS n_tx
FROM acc_years y
LEFT JOIN acc_transactions t ON t.id_year = y.id
GROUP BY y.id, y.label;

-- 4. Ne PAS agréger de poids ici.
-- Les requêtes json_extract(module_data_saisie_poids…) / plugin_pos_* sont retirées.
