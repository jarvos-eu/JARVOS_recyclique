# README — Complément DEC_REE T2 2026

**Objectif :** compléter les **sorties réemploi** de l'ODS / portail Ecologic T2.

**Statut (14/07) :** volumes **validés agent** — document rempli disponible pour l'équipe.

---

## Fichiers produits

| Fichier | Origine | Usage |
|---------|---------|--------|
| **[`2026-07-14_brouillon-proforma-ecologic-T2-2026.csv`](2026-07-14_brouillon-proforma-ecologic-T2-2026.csv)** | Agent | **Document rempli** — 18 lignes, format pro forma T1 |
| **[`2026-07-14_sorties-reemploi-T2-pour-tableur.csv`](2026-07-14_sorties-reemploi-T2-pour-tableur.csv)** | Agent | Fiche simple à recopier dans l'ODS (colonnes B–J) |
| [`2026-07-14_guide-documents-T2-equipe.md`](2026-07-14_guide-documents-T2-equipe.md) | Agent | Quel fichier remettre à l'équipe |
| [`Complément-DEC_REE-T2-2026.csv`](Complément-DEC_REE-T2-2026.csv) | Agent | Synthèse DEC_REE (volumes + confiance) |
| [`HITL-questions-decla-ecologic-t2-2026.md`](HITL-questions-decla-ecologic-t2-2026.md) | Agent | Décisions tranchées 14/07 |
| [`queries-decla-t2.sql`](queries-decla-t2.sql) | Agent | Requêtes de contrôle / audit |
| [`NOTE-schema-dump-20260707.md`](NOTE-schema-dump-20260707.md) | Agent | Schéma dump + reproductibilité miroir |
| [`DeclarationESS-ECOLOGIC-ECOMAISON-EntreesSorties-REMPLI.ods`](DeclarationESS-ECOLOGIC-ECOMAISON-EntreesSorties-REMPLI.ods) | **La Clique** | Tableur rempli T2 (Ecologic + Ecomaison) |

---

## Transposition ODS → portail

1. Recopier depuis [`2026-07-14_sorties-reemploi-T2-pour-tableur.csv`](2026-07-14_sorties-reemploi-T2-pour-tableur.csv) dans la feuille **Sortie-VenteDonsReemploi** (colonnes B–J).
2. Renommer la ligne TOTAL « 4T 2025 » → **« TOTAL 2T 2026 »**.
3. **Ne pas modifier** les entrées déjà saisies (feuille Entrees-Reception).
4. Contrôle avant portail : [`2026-07-14_brouillon-proforma-ecologic-T2-2026.csv`](2026-07-14_brouillon-proforma-ecologic-T2-2026.csv) (18 volumes LIV + DEC_REE).

---

## Ce qui n'a pas été recalculé

- **`LIV` entrées** : totaux tableur (ex. PAM 246,5 t) = pesées enlèvements — source métier, pas Recyclique tickets.
- **Colonnes Ecomaison K–T** : hors périmètre Ecologic.

---

## Source calcul DEC_REE

Ventes caisse Recyclique 1.4.4 (dump 2026-07-07), mapping validé sur golden T1 DEC_REE. Confiance globale **92 %** (décisions 14/07).
