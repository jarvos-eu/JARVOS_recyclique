
WITH periode AS (
  SELECT '2026-04-01'::timestamptz AS t_start, '2026-07-01'::timestamptz AS t_end
),
dec_ree AS (
  SELECT CASE c.name
    WHEN '1- Petits appareils em melange(PAM)' THEN 'B'
    WHEN '2- Ecrans' THEN 'C'
    WHEN '3- Gros électroménager hors froid (GEMHF)' THEN 'D'
    WHEN '4- Gros électroménager froid (GEMF)' THEN 'E'
    WHEN '1- Cycles et engins de déplacement non motorisés' THEN 'F'
    WHEN '2- Autres ASL' THEN 'G'
    WHEN '1- Tondeuses autoportées' THEN 'H'
    WHEN '2- Tondeuses à conducteur marchant' THEN 'I'
    WHEN '3- Autres ABJ thermique' THEN 'J'
  END AS col,
  CASE WHEN c.name IN (
    '1- Tondeuses autoportées', '2- Tondeuses à conducteur marchant', '3- Autres ABJ thermique'
  ) THEN SUM(si.quantity)::numeric
  ELSE ROUND(SUM(COALESCE(si.weight, 0))::numeric / 1000, 3) END AS val
  FROM sale_items si
  JOIN sales s ON s.id = si.sale_id
  JOIN categories c ON c.id::text = si.category
  CROSS JOIN periode p
  WHERE COALESCE(s.sale_date, s.created_at) >= p.t_start
    AND COALESCE(s.sale_date, s.created_at) < p.t_end
    AND c.name IN (
      '1- Petits appareils em melange(PAM)', '2- Ecrans',
      '3- Gros électroménager hors froid (GEMHF)', '4- Gros électroménager froid (GEMF)',
      '1- Cycles et engins de déplacement non motorisés', '2- Autres ASL',
      '1- Tondeuses autoportées', '2- Tondeuses à conducteur marchant', '3- Autres ABJ thermique'
    )
  GROUP BY c.name
),
-- LIV Ecologic (entrées tickets)
liv AS (
  SELECT CASE c.name
    WHEN '1- Petits appareils em melange(PAM)' THEN 'B'
    WHEN '2- Ecrans' THEN 'C'
    WHEN '3- Gros électroménager hors froid (GEMHF)' THEN 'D'
    WHEN '4- Gros électroménager froid (GEMF)' THEN 'E'
    WHEN '1- Cycles et engins de déplacement non motorisés' THEN 'F'
    WHEN '2- Autres ASL' THEN 'G'
  END AS col,
  ROUND(FLOOR(SUM(ld.poids_kg))::numeric / 1000, 3) AS val
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
  GROUP BY c.name
),
-- Ecomaison sorties réemploi (ventes)
eco_sale AS (
  SELECT col, ROUND(SUM(kg)::numeric / 1000, 3) AS val_t
  FROM (
    SELECT CASE
      WHEN c.name IN ('Jardin', '*Pots de fleurs', '* Gros équipement de jardin sup80cm',
        'NE PLUS UTILISER Materiel destinés à l''aménagement du jardin') THEN 'K'
      WHEN c.name IN ('A - Outillage Divers', '* Outillage à main', 'Outillage',
        'NE PLUS UTILISER- Materiel de bricolage', '* Gros Equipements de Bricolage (sup 80 cm)') THEN 'L'
      WHEN c.name = '1- Jeux de plein air' THEN 'M'
      WHEN c.name = '2- Jeux société et puzzle' THEN 'N'
      WHEN c.name IN ('3- autres jeux d''intérieur', 'A - Jeux Divers') THEN 'O'
      WHEN c.name IN ('* Assises', 'Chaises', 'Petit meuble/chaise en bois massif',
        'Gros meuble en bois massif', 'Meuble moyen en bois massif', 'A - Meuble Divers') THEN 'P'
      WHEN c.name = '* Couchage' THEN 'Q'
      WHEN c.name IN ('* Rangement', 'NE PLUS UTILISER Rangement et plan de pose et de travail') THEN 'R'
      WHEN c.name = '*Plan de pose , plan de travail' THEN 'S'
      WHEN c.name = '* Décoration textile' THEN 'T'
    END AS col,
    COALESCE(si.weight, 0) AS kg
    FROM sale_items si
    JOIN sales s ON s.id = si.sale_id
    JOIN categories c ON c.id::text = si.category
    CROSS JOIN periode p
    WHERE COALESCE(s.sale_date, s.created_at) >= p.t_start
      AND COALESCE(s.sale_date, s.created_at) < p.t_end
  ) x
  WHERE col IS NOT NULL
  GROUP BY col
),
-- Ecomaison entrées tickets
eco_entree AS (
  SELECT col, ROUND(SUM(kg)::numeric / 1000, 3) AS val_t
  FROM (
    SELECT CASE
      WHEN c.name IN ('Jardin', '*Pots de fleurs', '* Gros équipement de jardin sup80cm',
        'NE PLUS UTILISER Materiel destinés à l''aménagement du jardin') THEN 'K'
      WHEN c.name IN ('A - Outillage Divers', '* Outillage à main', 'Outillage',
        'NE PLUS UTILISER- Materiel de bricolage', '* Gros Equipements de Bricolage (sup 80 cm)') THEN 'L'
      WHEN c.name = '1- Jeux de plein air' THEN 'M'
      WHEN c.name = '2- Jeux société et puzzle' THEN 'N'
      WHEN c.name IN ('3- autres jeux d''intérieur', 'A - Jeux Divers') THEN 'O'
      WHEN c.name IN ('* Assises', 'Chaises', 'Petit meuble/chaise en bois massif',
        'Gros meuble en bois massif', 'Meuble moyen en bois massif', 'A - Meuble Divers') THEN 'P'
      WHEN c.name = '* Couchage' THEN 'Q'
      WHEN c.name IN ('* Rangement', 'NE PLUS UTILISER Rangement et plan de pose et de travail') THEN 'R'
      WHEN c.name = '*Plan de pose , plan de travail' THEN 'S'
      WHEN c.name = '* Décoration textile' THEN 'T'
    END AS col,
    ld.poids_kg AS kg
    FROM ligne_depot ld
    JOIN ticket_depot t ON t.id = ld.ticket_id
    JOIN categories c ON c.id = ld.category_id
    CROSS JOIN periode p
    WHERE ld.is_exit = false
      AND t.created_at >= p.t_start AND t.created_at < p.t_end
  ) x
  WHERE col IS NOT NULL
  GROUP BY col
),
-- Recyclage interne (kg) — section 2
recyclage AS (
  SELECT col, ROUND(SUM(kg)::numeric, 1) AS val_kg
  FROM (
    SELECT CASE
      WHEN c.name IN ('Jardin', '*Pots de fleurs', '* Gros équipement de jardin sup80cm',
        'NE PLUS UTILISER Materiel destinés à l''aménagement du jardin') THEN 'K'
      WHEN c.name IN ('A - Outillage Divers', '* Outillage à main', 'Outillage',
        'NE PLUS UTILISER- Materiel de bricolage', '* Gros Equipements de Bricolage (sup 80 cm)') THEN 'L'
      WHEN c.name = '1- Jeux de plein air' THEN 'M'
      WHEN c.name = '2- Jeux société et puzzle' THEN 'N'
      WHEN c.name IN ('3- autres jeux d''intérieur', 'A - Jeux Divers') THEN 'O'
      WHEN c.name IN ('* Assises', 'Chaises', 'Petit meuble/chaise en bois massif',
        'Gros meuble en bois massif', 'Meuble moyen en bois massif', 'A - Meuble Divers') THEN 'P'
      WHEN c.name = '* Couchage' THEN 'Q'
      WHEN c.name IN ('* Rangement', 'NE PLUS UTILISER Rangement et plan de pose et de travail') THEN 'R'
      WHEN c.name = '*Plan de pose , plan de travail' THEN 'S'
      WHEN c.name = '* Décoration textile' THEN 'T'
    END AS col,
    ld.poids_kg AS kg
    FROM ligne_depot ld
    JOIN ticket_depot t ON t.id = ld.ticket_id
    JOIN categories c ON c.id = ld.category_id
    CROSS JOIN periode p
    WHERE ld.is_exit = true AND ld.destination = 'RECYCLAGE'
      AND t.created_at >= p.t_start AND t.created_at < p.t_end
  ) x
  WHERE col IS NOT NULL
  GROUP BY col
)
SELECT 'dec_ree' AS kind, col, val::text FROM dec_ree
UNION ALL SELECT 'liv', col, val::text FROM liv
UNION ALL SELECT 'eco_sale', col, val_t::text FROM eco_sale
UNION ALL SELECT 'eco_entree', col, val_t::text FROM eco_entree
UNION ALL SELECT 'recyclage', col, val_kg::text FROM recyclage
ORDER BY kind, col;
