# Registre HITL — Décla Ecologic T2 2026

**Date :** 2026-07-07  
**Dump :** `references/_depot/recyclic_db_export_20260707_152448.dump` (restauré miroir Docker `recyclic-mirror-t2`)  
**Période :** T2 2026 — 2026-04-01 → 2026-06-30 inclus

---

## Synthèse agent

| Élément | Résultat |
|---------|----------|
| Golden T1 DEC_REE | **OK** — PAM 0,184 t · ECR 0,012 t · ASL-CAT1 0,050 t · ASL-CAT2 0,012 t (pro forma T1) |
| Source DEC_REE retenue | **`sale_items`** + `categories` (ventes caisse), date `COALESCE(sale_date, created_at)` |
| Sorties `ligne_depot` is_exit=true T2 | **RECYCLAGE** quasi exclusivement — **non** utilisées pour DEC_REE |
| Livrable CSV | [`Complément-DEC_REE-T2-2026.csv`](Complément-DEC_REE-T2-2026.csv) |
| Requêtes SQL | [`queries-decla-t2.sql`](queries-decla-t2.sql) |

---

## Registre des points ouverts

| ID | Sujet | Constat | Impact | Question Strophe | Statut |
|----|-------|---------|--------|------------------|--------|
| HITL-01 | Chemin dump | — | — | — | **résolu** — dump 20260707_152448 |
| HITL-02 | Champ date filtre T2 | Golden T1 DEC_REE validé avec `COALESCE(sales.sale_date, sales.created_at)` sur ventes ; entrées LIV avec `ticket_depot.created_at` | Reproductibilité | Valider ce couple date pour soumission T2 ? | **ouvert** |
| HITL-03 | Split vente / don / recyclage | `sales.donation` = montant € (1 vente, 69 € T2), pas de kg par don ; sorties ticket = RECYCLAGE | DEC_REE = ventes caisse uniquement dans ce calcul | Les dons matière (kg) sont-ils saisis ailleurs que caisse ? Faut-il les ajouter aux DEC_REE ? | **ouvert** |
| HITL-04 | Mapping ASL CAT1/CAT2 | Règle inférée du golden T1 : `1- Cycles et engins…` → ASL-CAT1 · `2- Autres ASL` → ASL-CAT2 | ASL-CAT1 0,100 t · ASL-CAT2 0,036 t proposés | Confirmer que cette règle reste valide T2 (vs photobook ligne à ligne) ? | **ouvert** |
| HITL-05 | ABJ-AUT comptage | 0 vente T2 cat. « 3- Autres ABJ thermique » | DEC_REE = **0 pièce** proposé | Y a-t-il des sorties ABJ thermique non passées par caisse (dons, autre) ? | **ouvert** |
| HITL-06 | Écart LIV dump vs ODS | ODS TOTAL entrées PAM **246,5 t** ; dump tickets cat. PAM **1,136 t** (même période) | Contrôle LIV non fiable depuis seul dump tickets | LIV ODS = pesées enlèvements manuels ? Ne pas recalculer LIV depuis Recyclique pour T2 ? | **ouvert** |
| HITL-07 | Libellé TOTAL ODS erroné | L51 / L125 « TOTAL 4T 2025 » | Cosmétique | Renommer en TOTAL 2T 2026 avant portail ? | **ouvert** |
| HITL-08 | ABJ-TONM unité | 1 vente tondeuse marchante (10,33 kg) | CSV propose **1 pièce** ; alternative **0,010 t** | Portail T2 : saisir en pièces ou tonnes pour ABJ-TONM DEC_REE ? | **ouvert** |
| HITL-09 | PAM DEC_REE ODS vs dump | ODS partiel **0,25 t** (B4) ; dump ventes **0,270 t** (119 lignes) | +0,020 t | Garder 0,270 t (dump) ou ajuster manuellement ? | **ouvert** |
| HITL-10 | GHF / GEF DEC_REE faible effectif | 1 vente chacun (0,060 t · 0,063 t) | Valeurs calculées mais effectif n=1 | Confirmer que ces ventes sont bien réemploi ESS Ecologic ? | **ouvert** |

---

## Mapping prouvé (golden T1 → réutilisé T2)

| Code Ecologic | Catégorie Recyclique | Preuve |
|---------------|---------------------|--------|
| PAM | `1- Petits appareils em melange(PAM)` | T1 DEC_REE 0,184 t = pro forma |
| ECR | `2- Ecrans` | T1 DEC_REE 0,012 t = pro forma |
| ASL-CAT1 | `1- Cycles et engins de déplacement non motorisés` | T1 DEC_REE 0,050 t = pro forma |
| ASL-CAT2 | `2- Autres ASL` | T1 DEC_REE 0,012 t = pro forma |
| ABJ-AUT | `3- Autres ABJ thermique` | T1 DEC_REE 2 pièces = pro forma |
| GHF | `3- Gros électroménager hors froid (GEMHF)` | T1 DEC_REE 0 (cohérent pro forma) |
| GEF | `4- Gros électroménager froid (GEMF)` | T1 DEC_REE 0,018 t = pro forma (T2 ventes présentes) |

---

## Proposition DEC_REE T2 (à valider)

| Code | Volume proposé | Unité | ODS actuel |
|------|----------------|-------|------------|
| PAM | **0,270** | t | 0,25 (partiel) |
| ECR | **0,032** | t | vide |
| GHF | **0,060** | t | vide |
| GEF | **0,063** | t | vide |
| ASL-CAT1 | **0,100** | t | vide |
| ASL-CAT2 | **0,036** | t | vide |
| ABJ-TONA | **0** | pièces | vide |
| ABJ-TONM | **1** | pièces *(HITL-08)* | vide |
| ABJ-AUT | **0** | pièces | vide |
