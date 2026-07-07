-- Mission assistance décla Ecologic T2 2026 — requêtes read-only
-- Dump canon : references/_depot/recyclic_db_export_20260707_152448.dump
-- Miroir local (session agent) : docker container recyclic-mirror-t2 / DB recyclic_la_clique_mirror
-- Période T2 : 2026-04-01 (inclus) → 2026-06-30 (inclus) — filtre SQL : [2026-04-01, 2026-07-01)

-- =============================================================================
-- Paramètres
-- =============================================================================
-- Champ date ventes DEC_REE : COALESCE(sales.sale_date, sales.created_at)
--   → validé golden T1 PAM DEC_REE = 0,184 t (pro forma) avec ce filtre.
-- Champ date entrées LIV (contrôle) : ticket_depot.created_at

-- =============================================================================
-- Mapping catégorie Recyclique → code Ecologic (prouvé golden T1 DEC_REE)
-- =============================================================================
-- PAM        ← categories.name = '1- Petits appareils em melange(PAM)'
-- ECR        ← '2- Ecrans'
-- GHF        ← '3- Gros électroménager hors froid (GEMHF)'
-- GEF        ← '4- Gros électroménager froid (GEMF)'
-- ASL-CAT1   ← '1- Cycles et engins de déplacement non motorisés'  (parent ASL)
-- ASL-CAT2   ← '2- Autres ASL'                                     (parent ASL)
-- ABJ-TONA   ← '1- Tondeuses autoportées'                           (parent ABJTH)
-- ABJ-TONM   ← '2- Tondeuses à conducteur marchant'                 (parent ABJTH)
-- ABJ-AUT    ← '3- Autres ABJ thermique'                             (parent ABJTH) — pièces

-- =============================================================================
-- DEC_REE T2 — agrégats ventes caisse (source principale réemploi)
-- =============================================================================
WITH periode AS (
  SELECT TIMESTAMP WITH TIME ZONE '2026-04-01 00:00:00+00' AS t_start,
         TIMESTAMP WITH TIME ZONE '2026-07-01 00:00:00+00' AS t_end
),
ventes AS (
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
    END AS code_article,
    c.name AS category_name,
    COUNT(*) AS nb_lignes,
    SUM(si.quantity) AS qty,
    ROUND(SUM(COALESCE(si.weight, 0))::numeric / 1000, 3) AS volume_t
  FROM sale_items si
  JOIN sales s ON s.id = si.sale_id
  JOIN categories c ON c.id::text = si.category
  CROSS JOIN periode p
  WHERE COALESCE(s.sale_date, s.created_at) >= p.t_start
    AND COALESCE(s.sale_date, s.created_at) < p.t_end
    AND c.name IN (
      '1- Petits appareils em melange(PAM)',
      '2- Ecrans',
      '3- Gros électroménager hors froid (GEMHF)',
      '4- Gros électroménager froid (GEMF)',
      '1- Cycles et engins de déplacement non motorisés',
      '2- Autres ASL',
      '1- Tondeuses autoportées',
      '2- Tondeuses à conducteur marchant',
      '3- Autres ABJ thermique'
    )
  GROUP BY c.name
)
SELECT code_article, category_name, nb_lignes, qty, volume_t
FROM ventes
ORDER BY code_article;

-- =============================================================================
-- DEC_REE T2 — pièces ABJ (ABJ-AUT, ABJ-TONA, ABJ-TONM si unité = pièces)
-- =============================================================================
WITH periode AS (
  SELECT TIMESTAMP WITH TIME ZONE '2026-04-01 00:00:00+00' AS t_start,
         TIMESTAMP WITH TIME ZONE '2026-07-01 00:00:00+00' AS t_end
)
SELECT
  CASE c.name
    WHEN '1- Tondeuses autoportées'           THEN 'ABJ-TONA'
    WHEN '2- Tondeuses à conducteur marchant' THEN 'ABJ-TONM'
    WHEN '3- Autres ABJ thermique'            THEN 'ABJ-AUT'
  END AS code_article,
  c.name,
  COUNT(*) AS nb_lignes,
  SUM(si.quantity) AS pieces
FROM sale_items si
JOIN sales s ON s.id = si.sale_id
JOIN categories c ON c.id::text = si.category
CROSS JOIN periode p
WHERE COALESCE(s.sale_date, s.created_at) >= p.t_start
  AND COALESCE(s.sale_date, s.created_at) < p.t_end
  AND c.parent_id = '192b6d5b-aabe-40ac-bace-68aabcdf3a4e'  -- (ABJTH) Articles de bricolage et de jardin thermiques
GROUP BY c.name
ORDER BY code_article;

-- =============================================================================
-- Golden test T1 — validation mapping DEC_REE (doit matcher pro forma T1)
-- =============================================================================
-- Attendu : PAM 0,184 · ECR 0,012 · ASL-CAT1 0,050 · ASL-CAT2 0,012 · ABJ-AUT 2 pièces
WITH periode AS (
  SELECT TIMESTAMP WITH TIME ZONE '2026-01-01 00:00:00+00' AS t_start,
         TIMESTAMP WITH TIME ZONE '2026-04-01 00:00:00+00' AS t_end
)
SELECT
  CASE c.name
    WHEN '1- Petits appareils em melange(PAM)'              THEN 'PAM'
    WHEN '2- Ecrans'                                        THEN 'ECR'
    WHEN '1- Cycles et engins de déplacement non motorisés' THEN 'ASL-CAT1'
    WHEN '2- Autres ASL'                                    THEN 'ASL-CAT2'
    WHEN '3- Autres ABJ thermique'                          THEN 'ABJ-AUT'
  END AS code_article,
  ROUND(SUM(COALESCE(si.weight, 0))::numeric / 1000, 3) AS volume_t,
  SUM(si.quantity) AS pieces
FROM sale_items si
JOIN sales s ON s.id = si.sale_id
JOIN categories c ON c.id::text = si.category
CROSS JOIN periode p
WHERE COALESCE(s.sale_date, s.created_at) >= p.t_start
  AND COALESCE(s.sale_date, s.created_at) < p.t_end
  AND c.name IN (
    '1- Petits appareils em melange(PAM)',
    '2- Ecrans',
    '1- Cycles et engins de déplacement non motorisés',
    '2- Autres ASL',
    '3- Autres ABJ thermique'
  )
GROUP BY c.name
ORDER BY code_article;

-- =============================================================================
-- Contrôle LIV T2 (optionnel — écarts majeurs vs ODS attendus → HITL)
-- =============================================================================
WITH periode AS (
  SELECT TIMESTAMP WITH TIME ZONE '2026-04-01 00:00:00+00' AS t_start,
         TIMESTAMP WITH TIME ZONE '2026-07-01 00:00:00+00' AS t_end
)
SELECT
  CASE c.name
    WHEN '1- Petits appareils em melange(PAM)'              THEN 'PAM'
    WHEN '2- Ecrans'                                        THEN 'ECR'
    WHEN '3- Gros électroménager hors froid (GEMHF)'        THEN 'GHF'
    WHEN '4- Gros électroménager froid (GEMF)'              THEN 'GEF'
    WHEN '1- Cycles et engins de déplacement non motorisés' THEN 'ASL-CAT1'
    WHEN '2- Autres ASL'                                    THEN 'ASL-CAT2'
  END AS code_article,
  ROUND(FLOOR(SUM(ld.poids_kg))::numeric / 1000, 3) AS liv_t,
  COUNT(*) AS nb_lignes
FROM ligne_depot ld
JOIN ticket_depot t ON t.id = ld.ticket_id
JOIN categories c ON c.id = ld.category_id
CROSS JOIN periode p
WHERE ld.is_exit = false
  AND t.created_at >= p.t_start
  AND t.created_at < p.t_end
  AND c.name IN (
    '1- Petits appareils em melange(PAM)',
    '2- Ecrans',
    '3- Gros électroménager hors froid (GEMHF)',
    '4- Gros électroménager froid (GEMF)',
    '1- Cycles et engins de déplacement non motorisés',
    '2- Autres ASL'
  )
GROUP BY c.name
ORDER BY code_article;

-- =============================================================================
-- Sorties ligne_depot is_exit=true T2 — quasi exclusivement RECYCLAGE (hors DEC_REE)
-- =============================================================================
SELECT ld.destination, COUNT(*) AS nb, ROUND(SUM(ld.poids_kg)::numeric, 2) AS kg
FROM ligne_depot ld
JOIN ticket_depot t ON t.id = ld.ticket_id
WHERE ld.is_exit = true
  AND t.created_at >= '2026-04-01' AND t.created_at < '2026-07-01'
GROUP BY ld.destination
ORDER BY kg DESC;
