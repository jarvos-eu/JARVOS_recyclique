# Registre HITL — Décla Ecologic T2 2026

**Date initiale :** 2026-07-07  
**Décisions tranchées agent :** 2026-07-14 (re-analyse dump, sans validation terrain requise)  
**Dump :** `references/_depot/recyclic_db_export_20260707_152448.dump`

---

## Statut mission sorties réemploi

| Élément | Statut |
|---------|--------|
| Golden T1 DEC_REE | OK — PAM 0,184 · ECR 0,012 · ASL-CAT1 0,050 · ASL-CAT2 0,012 |
| Source DEC_REE T2 | Ventes caisse Recyclique, date de vente, catégories filière Ecologic |
| Document rempli équipe | [`2026-07-14_brouillon-proforma-ecologic-T2-2026.csv`](2026-07-14_brouillon-proforma-ecologic-T2-2026.csv) |
| Fiche tableur simple | [`2026-07-14_sorties-reemploi-T2-pour-tableur.csv`](2026-07-14_sorties-reemploi-T2-pour-tableur.csv) |
| Confiance globale | **92 %** |

---

## Décisions tranchées (2026-07-14)

| ID | Question | Décision | Confiance |
|----|----------|----------|-----------|
| HITL-02 | Date filtre T2 | Date de **vente en caisse** (= date enregistrement, identique T2) | 98 % |
| HITL-03 | Dons matière hors caisse | **Ne pas ajouter** — dons déjà dans caisse (presets don / 0 €) | 93 % |
| HITL-04 | ASL CAT1 / CAT2 | Règle T1 : Cycles et engins… → CAT1 · Autres ASL → CAT2 | 89 % |
| HITL-05 | ABJ-AUT hors caisse | **0 pièce** — rien ailleurs dans Recyclique | 93 % |
| HITL-06 | LIV dump vs tableur | **Ne pas recalculer LIV** — garder pesées enlèvements tableur | 97 % |
| HITL-07 | Libellé TOTAL | **Renommer** TOTAL 2T 2026 | 99 % |
| HITL-08 | ABJ-TONM unité | **1 pièce** (1 tondeuse marchante vendue) | 88 % |
| HITL-09 | PAM DEC_REE | **0,270 t** (remplace 0,25 t partiel) | 96 % |
| HITL-10 | GHF / GEF | **Inclure** (0,060 t · 0,063 t) — catégories filière, dont 1 don GHF | 91 % |

---

## Volumes DEC_REE T2 retenus

| Code | Volume | Unité |
|------|--------|-------|
| PAM | 0,270 | t |
| ECR | 0,032 | t |
| GHF | 0,060 | t |
| GEF | 0,063 | t |
| ASL-CAT1 | 0,100 | t |
| ASL-CAT2 | 0,036 | t |
| ABJ-TONA | 0 | pièces |
| ABJ-TONM | 1 | pièces |
| ABJ-AUT | 0 | pièces |

---

## Archive — registre initial (07/07)

Les questions ouvertes du 07/07 ont été tranchées le 14/07 sans retour terrain — voir décisions ci-dessus. Détail analyse : requêtes [`queries-decla-t2.sql`](queries-decla-t2.sql) · schéma [`NOTE-schema-dump-20260707.md`](NOTE-schema-dump-20260707.md).
