# README — Complément DEC_REE T2 2026

**Objectif :** compléter les **8 cases `DEC_REE`** vides (ou partielles) de l’ODS / portail Ecologic T2.

---

## Fichiers produits

| Fichier | Usage |
|---------|--------|
| [`Complément-DEC_REE-T2-2026.csv`](Complément-DEC_REE-T2-2026.csv) | Volumes proposés par code filière |
| [`HITL-questions-decla-ecologic-t2-2026.md`](HITL-questions-decla-ecologic-t2-2026.md) | Points à trancher avant soumission |
| [`queries-decla-t2.sql`](queries-decla-t2.sql) | Requêtes de contrôle / audit |
| [`NOTE-schema-dump-20260707.md`](NOTE-schema-dump-20260707.md) | Schéma dump + reproductibilité miroir |

---

## Transposition ODS → portail

1. **Lire le HITL** — valider les lignes marquées HITL-04, 08, 09, 10 minimum.
2. **Feuille `Sortie-VenteDonsReemploi`** — colonnes B–J (Ecologic) :
   - Col. **B** PAM → **0,270 t** *(remplace le 0,25 t partiel L4 si validation HITL-09)*
   - Col. **C** ECR → **0,032 t**
   - Col. **D** GHF → **0,060 t**
   - Col. **E** GEF → **0,063 t**
   - Col. **F** ASL-CAT1 → **0,100 t**
   - Col. **G** ASL-CAT2 → **0,036 t**
   - Col. **H** ABJ-TONA → **0**
   - Col. **I** ABJ-TONM → **1** *(pièce — cf. HITL-08)*
   - Col. **J** ABJ-AUT → **0** pièce
3. **Consolider ligne TOTAL 2T 2026** (corriger libellé « 4T 2025 » — cf. mode d’emploi §4.2).
4. **Portail SI Fusion** — saisir les 9 volumes `DEC_REE` (+ 9 `LIV` déjà dans ODS entrées) → export pro forma CSV.

---

## Ce qui n’a pas été recalculé

- **`LIV` entrées** : l’ODS TOTAL (ex. PAM 246,5 t) provient des **pesées enlèvements** saisies manuellement — le dump tickets ne reproduit pas ces masses (écart documenté HITL-06).
- **Colonnes Ecomaison K–T** : hors périmètre Ecologic.
- **Dons matière (kg)** : non ventilés dans le dump → HITL-03.

---

## Source calcul

Ventes caisse Recyclique 1.4.4 (dump 2026-07-07), mapping catégories validé sur **golden T1 DEC_REE** (pro forma T1 2026).
