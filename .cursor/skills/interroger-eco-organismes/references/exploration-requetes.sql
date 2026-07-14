-- Exploration read-only — skill interroger-eco-organismes
-- Miroir : docker exec recyclic-mirror-t2 psql -U postgres -d recyclic_la_clique_mirror -f /tmp/explore.sql
-- Copier : docker cp exploration-requetes.sql recyclic-mirror-t2:/tmp/explore.sql

-- =============================================================================
-- 0. Smoke — tables présentes
-- =============================================================================
-- \dt

-- =============================================================================
-- 1. Golden test T1 PAM DEC_REE (doit ≈ 0,184 t)
-- =============================================================================
WITH periode AS (
  SELECT '2026-01-01'::timestamptz AS t_start, '2026-04-01'::timestamptz AS t_end
)
SELECT
  ROUND(SUM(COALESCE(si.weight, 0))::numeric / 1000, 3) AS pam_dec_ree_t
FROM sale_items si
JOIN sales s ON s.id = si.sale_id
JOIN categories c ON c.id::text = si.category
CROSS JOIN periode p
WHERE c.name = '1- Petits appareils em melange(PAM)'
  AND COALESCE(s.sale_date, s.created_at) >= p.t_start
  AND COALESCE(s.sale_date, s.created_at) < p.t_end;

-- =============================================================================
-- 2. Golden test T1 PAM LIV (doit ≈ 2,223 t)
-- =============================================================================
WITH periode AS (
  SELECT '2026-01-01'::timestamptz AS t_start, '2026-04-01'::timestamptz AS t_end
)
SELECT
  ROUND(FLOOR(SUM(ld.poids_kg))::numeric / 1000, 3) AS pam_liv_t,
  SUM(ld.poids_kg)::bigint AS pam_kg_brut
FROM ligne_depot ld
JOIN ticket_depot t ON t.id = ld.ticket_id
JOIN categories c ON c.id = ld.category_id
CROSS JOIN periode p
WHERE ld.is_exit = false
  AND c.name = '1- Petits appareils em melange(PAM)'
  AND t.created_at >= p.t_start AND t.created_at < p.t_end;

-- =============================================================================
-- 3. DEC_REE — agrégat par filière Ecologic (remplacer période)
-- =============================================================================
WITH periode AS (
  SELECT '2026-04-01'::timestamptz AS t_start, '2026-07-01'::timestamptz AS t_end
)
SELECT
  CASE c.name
    WHEN '1- Petits appareils em melange(PAM)'              THEN 'PAM'
    WHEN '2- Ecrans'                                        THEN 'ECR'
    WHEN '3- Gros électroménager hors froid (GEMHF)'        THEN 'GHF'
    WHEN '4- Gros électroménager froid (GEMF)'              THEN 'GEF'
    WHEN '1- Cycles et engins de déplacement non motorisés' THEN 'ASL-CAT1'
    WHEN '2- Autres ASL'                                    THEN 'ASL-CAT2'
    WHEN '1- Tondeuses autoportées'                         THEN 'ABJ-TONA'
    WHEN '2- Tondeuses à conducteur marchant'               THEN 'ABJ-TONM'
    WHEN '3- Autres ABJ thermique'                          THEN 'ABJ-AUT'
  END AS code,
  COUNT(*) AS nb_lignes,
  ROUND(SUM(COALESCE(si.weight, 0))::numeric / 1000, 3) AS volume_t,
  SUM(si.quantity) AS qty
FROM sale_items si
JOIN sales s ON s.id = si.sale_id
JOIN categories c ON c.id::text = si.category
CROSS JOIN periode p
WHERE COALESCE(s.sale_date, s.created_at) >= p.t_start
  AND COALESCE(s.sale_date, s.created_at) < p.t_end
  AND (si.notes IS NULL OR si.notes NOT ILIKE '%recyclage%')
  AND c.name IN (
    '1- Petits appareils em melange(PAM)', '2- Ecrans',
    '3- Gros électroménager hors froid (GEMHF)', '4- Gros électroménager froid (GEMF)',
    '1- Cycles et engins de déplacement non motorisés', '2- Autres ASL',
    '1- Tondeuses autoportées', '2- Tondeuses à conducteur marchant', '3- Autres ABJ thermique'
  )
GROUP BY c.name ORDER BY code;

-- =============================================================================
-- 4. LIV — entrées tickets par filière Ecologic
-- =============================================================================
WITH periode AS (
  SELECT '2026-04-01'::timestamptz AS t_start, '2026-07-01'::timestamptz AS t_end
)
SELECT
  CASE c.name
    WHEN '1- Petits appareils em melange(PAM)'              THEN 'PAM'
    WHEN '2- Ecrans'                                        THEN 'ECR'
    WHEN '3- Gros électroménager hors froid (GEMHF)'        THEN 'GHF'
    WHEN '4- Gros électroménager froid (GEMF)'              THEN 'GEF'
    WHEN '1- Cycles et engins de déplacement non motorisés' THEN 'ASL-CAT1'
    WHEN '2- Autres ASL'                                    THEN 'ASL-CAT2'
  END AS code,
  ROUND(FLOOR(SUM(ld.poids_kg))::numeric / 1000, 3) AS liv_t,
  COUNT(*) AS nb_lignes
FROM ligne_depot ld
JOIN ticket_depot t ON t.id = ld.ticket_id
JOIN categories c ON c.id = ld.category_id
CROSS JOIN periode p
WHERE ld.is_exit = false
  AND t.created_at >= p.t_start AND t.created_at < p.t_end
  AND c.name IN (
    '1- Petits appareils em melange(PAM)', '2- Ecrans',
    '3- Gros électroménager hors froid (GEMHF)', '4- Gros électroménager froid (GEMF)',
    '1- Cycles et engins de déplacement non motorisés', '2- Autres ASL'
  )
GROUP BY c.name ORDER BY code;

-- =============================================================================
-- 5. RECYCLAGE — sorties benne (is_exit=true, destination RECYCLAGE)
-- =============================================================================
WITH periode AS (
  SELECT '2026-04-01'::timestamptz AS t_start, '2026-07-01'::timestamptz AS t_end
)
SELECT c.name, COUNT(*) AS nb, ROUND(SUM(ld.poids_kg)::numeric, 1) AS kg
FROM ligne_depot ld
JOIN ticket_depot t ON t.id = ld.ticket_id
JOIN categories c ON c.id = ld.category_id
CROSS JOIN periode p
WHERE ld.is_exit = true AND ld.destination = 'RECYCLAGE'
  AND t.created_at >= p.t_start AND t.created_at < p.t_end
GROUP BY c.name ORDER BY kg DESC LIMIT 30;

-- =============================================================================
-- 6. Destinations is_exit=true (comprendre le schéma dépôt)
-- =============================================================================
WITH periode AS (
  SELECT '2026-04-01'::timestamptz AS t_start, '2026-07-01'::timestamptz AS t_end
)
SELECT ld.destination, COUNT(*) AS nb, ROUND(SUM(ld.poids_kg)::numeric, 2) AS kg
FROM ligne_depot ld
JOIN ticket_depot t ON t.id = ld.ticket_id
CROSS JOIN periode p
WHERE ld.is_exit = true
  AND t.created_at >= p.t_start AND t.created_at < p.t_end
GROUP BY ld.destination ORDER BY kg DESC;

-- =============================================================================
-- 7. Catégories « NE PLUS UTILISER » (à exclure des agrégats)
-- =============================================================================
SELECT name, id FROM categories WHERE name ILIKE '%NE PLUS UTILISER%' ORDER BY name;
