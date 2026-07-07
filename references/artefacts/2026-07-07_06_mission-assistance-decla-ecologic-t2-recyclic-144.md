# Mission assistance — Décla Ecologic T2 2026 depuis dump Recyclique 1.4.4

**Date :** 2026-07-07  
**Demandeur :** Strophe (La Clique Qui Recycle — urgence terrain)  
**Type :** mission **exceptionnelle** · **assistance opérationnelle** · **pas** un epic BMAD classique  
**Statut :** `en cours` — dump BDD **reçu** 2026-07-07 (miroir read-only à restaurer en local)  
**Kanban :** [`IDEA-2026-07-07-001`](../../docs/ideas/kanban/IDEA-2026-07-07-001.md) (`inbox`, P0)  
**Point d'entrée racine :** [`2026-07-07_mission-assistance-decla-ecologic-t2-2026.md`](../eco-organismes/partenaires/ecologic/declarations-la-clique/2026-T2/2026-07-07_mission-assistance-decla-ecologic-t2-2026.md)

---

## 1. Contexte et intention

La Clique utilise **Recyclique 1.4.4** en **pré-prod live**. Elle doit **boucler la déclaration ESS Ecologic T2 2026** (activité avr.–juin 2026). Un membre a fourni l'ODS de travail ; les **entrées LIV** sont largement renseignées au TOTAL, mais les **sorties `DEC_REE`** (réemploi ventes + dons) sont **quasi vides** (**8 cases sur 9** manquantes côté portail).

**Décision produit (2026-07-07) :** plutôt que construire tout de suite l'« usine à gaz » patch 1.4.5, **aider la CLIC maintenant** en :

1. Récupérant un **dump** de la base Recyclique actuelle ;
2. Exploitant le **mode d'emploi ODS** (cases, unités, mapping cible) ;
3. Produisant un **nouveau CSV** (ou équivalent pro forma / grille) avec **ce qui manque** pour compléter la décla.

Cette mission **n'annule pas** le cadrage patch 1.4.5 ([`_04` cadrage Ecologic](2026-07-07_04_cadrage-patch-1.4.5-ecologic.md)) — elle est un **raccourci terrain** avant industrialisation.

---

## 2. Périmètre

### In scope

| # | Livrable | Description |
|---|----------|-------------|
| L1 | **Analyse dump** | Schéma tables utiles (tickets dépôt, ventes caisse, catégories, poids, dates T2) — documenté, pas supposé |
| L2 | **Agrégats T2** | Tonnes / pièces par **code Ecologic** × flux **`DEC_REE`** (et contrôle `LIV` si écart ODS) |
| L3 | **CSV complément** | Fichier à déposer à côté de l'ODS : `…/2026-T2/Complément-DEC_REE-T2-2026-*.csv` (nom final à figer) |
| L4 | **Registre HITL** | `…/2026-T2/HITL-questions-decla-ecologic-t2-2026.md` — **chaque** ambiguïté, trou, mapping non prouvé |
| L5 | **Mode d'emploi sortie** | Court README : comment la CLIC transpose CSV → ODS / portail |

### Out of scope (cette mission)

- Patch code Recyclique v2 (`peintre-nano` / API canon)
- Saisie automatique portail Ecologic / SI Fusion
- Colonnes **Ecomaison** (K–T) de l'ODS combiné — sauf si Strophe demande explicitement
- Inventaire détaillé des **46+ lignes PAM orphelines** sans libellé colonne A (dette saisie terrain CLIC)

---

## 3. Sources de vérité (ordre de lecture agents)

| Priorité | Fichier | Usage |
|----------|---------|--------|
| 1 | [`DeclarationESS-ECOLOGIC-2T2026_MODE-EMPLOI.md`](../eco-organismes/partenaires/ecologic/declarations-la-clique/2026-T2/DeclarationESS-ECOLOGIC-2T2026_MODE-EMPLOI.md) | **Quoi remplir où** — 18 cases portail + grilles ODS |
| 2 | Dump BDD Recyclique 1.4.4 (fourni par Strophe) | Chiffres source |
| 3 | [`2026-07-07_04_cadrage-patch-1.4.5-ecologic.md`](2026-07-07_04_cadrage-patch-1.4.5-ecologic.md) | Règles mapping, golden tests, endpoints cibles |
| 4 | Pro forma T1 référence | `…/2026-T1/pro forma déclaration T1 2026.csv` — **format colonnes** cible |
| 5 | `log/cursor-agent/ecologic-t2-2026-ods-extract.json` | Extraction machine ODS (si besoin) |

**Ne pas re-parser l'ODS** si le mode d'emploi suffit — sauf vérification post-dump ou si Strophe a modifié le fichier.

---

## 4. Travail à faire — cases manquantes (état au 07/07/2026)

D'après le mode d'emploi, priorité = **`DEC_REE`** (sorties réemploi) :

| Code | Opération | Unité | État ODS T2 | Action mission |
|------|-----------|-------|-------------|----------------|
| PAM | DEC_REE | t | **0,25 t** partiel | Compléter / valider total T2 |
| ECR | DEC_REE | t | vide | Calculer depuis dump |
| GHF | DEC_REE | t | vide | idem |
| GEF | DEC_REE | t | vide | idem |
| ASL-CAT1 | DEC_REE | t | vide | idem |
| ASL-CAT2 | DEC_REE | t | vide | idem |
| ABJ-TONA | DEC_REE | t/pièces | vide | idem |
| ABJ-TONM | DEC_REE | t/pièces | vide | idem |
| ABJ-AUT | DEC_REE | **pièces** | vide | `COUNT` sorties — pas de poids |

**`LIV` (entrées)** : 9/9 renseignées au TOTAL ODS — **contrôle optionnel** dump vs ODS (écarts → HITL, pas de correction silencieuse).

---

## 5. Règles non négociables

1. **Rien inventer** — pas de mapping catégorie boutique → code Ecologic sans preuve (dump + doc ou validation Strophe).
2. **Rien supposer** sur le schéma dump — inventorier tables/colonnes réelles avant toute requête.
3. **Période T2 stricte** : `2026-04-01` → `2026-06-30` (inclus) — fuseau / champ date à **documenter** depuis le dump.
4. **Split vente / don** : si indistinguable dans 1.4.4 → **ne pas répartir** ; noter HITL ; pour `DEC_REE` portail, la somme ventes+dons peut suffire **si** validé par Strophe (cf. cadrage LCQ-003).
5. **Unités** : tonnes avec règle `ROUND(FLOOR(SUM(kg))/1000, 3)` pour LIV ; DEC_REE selon pro forma T1 — **vérifier** sur dump avant application.
6. **ABJ-AUT** : pièces, pas kg — si dump ne permet pas le comptage → HITL.
7. **Chaque blocage** → une ligne dans `HITL-questions-decla-ecologic-t2-2026.md` avec : constat, impact, question pour Strophe, statut (`ouvert` / `résolu`).

---

## 6. Phases d'exécution (session suivante)

```text
Phase 0 — Prérequis Strophe
  └─ Déposer dump SQL (chemin + date export + instance confirmée 1.4.4 La Clique)

Phase 1 — Reconnaissance dump (READ-ONLY)
  └─ Tables catégories, tickets, ventes, poids, dates
  └─ Livrable intermédiaire : section dans HITL ou note `…/2026-T2/NOTE-schema-dump-*.md`

Phase 2 — Mapping draft (preuve requise)
  └─ Croiser catégories Recyclique 1.4.4 ↔ codes Ecologic (s'appuyer sur migration-paheko + cadrage)
  └─ Tout mapping non prouvé → HITL

Phase 3 — Agrégats T2
  └─ Requêtes SQL documentées (fichier `.sql` à côté du CSV)
  └─ Comparer PAM DEC_REE calculé vs 0,25 t ODS

Phase 4 — CSV complément
  └─ Colonnes alignées pro forma T1 : Code article, Type ope, Volume, (+ métadonnées traçabilité)
  └─ Une ligne par case manquante ou complémentaire

Phase 5 — Handoff CLIC
  └─ README court : où coller dans ODS / portail
  └─ Liste HITL ouverte pour validation terrain
```

---

## 7. Format CSV cible (draft — à valider sur pro forma T1)

Référence : `…/2026-T1/pro forma déclaration T1 2026.csv`

| Colonne | Exemple T1 | Mission T2 |
|---------|------------|------------|
| Code article | PAM, GEF, … | Idem |
| Type ope | `LIV`, `DEC_REE` | **`DEC_REE`** prioritaire |
| Volume | 2,223 | Tonnes ou pièces (ABJ-AUT) |
| *(optionnel traçabilité)* | — | `source_query`, `nb_lignes`, `periode`, `hitl_id` |

**Nom fichier proposé :**  
`references/eco-organismes/partenaires/ecologic/declarations-la-clique/2026-T2/Complément-DEC_REE-T2-2026.csv`

---

## 8. Inconnues connues (pré-HITL)

| ID | Sujet | Statut |
|----|-------|--------|
| HITL-01 | Chemin et format exact du dump 1.4.4 La Clique | **résolu** — `references/_depot/recyclic_db_export_20260707_152448.dump` (PostgreSQL custom `.dump`, export 2026-07-07 15:24) ; archive `recyclic_db_export_20260411_172643.dump` |
| HITL-02 | Champ date canon pour filtre T2 (ticket vs vente) | `ouvert` |
| HITL-03 | Distinction vente / don / recyclage en 1.4.4 sur sorties | `ouvert` — peut bloquer ventilation fine |
| HITL-04 | Mapping catégorie boutique → ECR, GHF, ASL… non figé en prod | `ouvert` |
| HITL-05 | ABJ-AUT : comptage pièces depuis quelle table ? | `ouvert` |
| HITL-06 | Écart éventuel LIV dump vs ODS TOTAL (246,5 t PAM…) | `ouvert` — contrôle recommandé |
| HITL-07 | Libellé TOTAL ligne 51 ODS (« 4T 2025 » erroné) — correction humaine ? | `ouvert` |

---

## 9. Liens patch 1.4.5 (après mission)

Si la mission réussit, réutiliser :

- Requêtes SQL validées → stories `9.ECO-03` / `9.ECO-04`
- Mapping prouvé → `9.ECO-01`
- Registre HITL → alimentation YAML mapping officiel

---

## 10. Critères de succès mission

- [ ] Dump analysé sans supposition non documentée
- [ ] CSV complément avec **8+ lignes DEC_REE** ou justification HITL par case vide
- [ ] Écart PAM DEC_REE calculé vs 0,25 t documenté
- [ ] Registre HITL à jour ; Strophe a pu trancher les points ouverts
- [ ] CLIC peut compléter ODS / portail sans re-decoder la structure

---

## 11. Références

- Calendrier : [`2026-07-07_calendrier-declarations-partenaires.md`](../eco-organismes/2026-07-07_calendrier-declarations-partenaires.md)
- Feedback LCQ : [`2026-07-05_01_feedback-la-clique-dashboard-stats-eco-organismes.md`](2026-07-05_01_feedback-la-clique-dashboard-stats-eco-organismes.md)
- Brownfield 1.4.4 : `recyclique-1.4.4/` (schéma BDD legacy)

---

## 12. Miroir BDD read-only (La Clique · Recyclique 1.4.4)

> Extension alignée [`IDEA-2026-07-05-002`](../../docs/ideas/kanban/IDEA-2026-07-05-002.md) § miroir BDD — **SELECT only**, jamais écriture sur la prod.

### 12.1 Dumps déposés (`references/_depot/` — gitignore)

| Fichier | Taille | Rôle |
|---------|--------|------|
| **`recyclic_db_export_20260707_152448.dump`** | ~1,18 Mo | **Canon mission T2** — export instantané pré-prod live (2026-07-07) |
| `recyclic_db_export_20260411_172643.dump` | ~0,88 Mo | Archive avril 2026 — diff / historique |

Format attendu : **PostgreSQL custom format** (`pg_dump -Fc` ou équivalent) — extension `.dump`.

### 12.2 Restauration miroir local (agents)

**Objectif :** base locale **`recyclic_la_clique_mirror`** (nom suggéré) en **lecture seule** pour requêtes T2.

```bash
# Exemple — adapter host/port/user selon Postgres local
createdb recyclic_la_clique_mirror
pg_restore -d recyclic_la_clique_mirror --no-owner --role=recyclic_ro \
  "references/_depot/recyclic_db_export_20260707_152448.dump"
```

| Étape | Livrable agent |
|-------|----------------|
| Restore + vérif `\\dt` | `…/2026-T2/NOTE-schema-dump-20260707.md` ou section HITL |
| Confronter schéma | [`references/dumps/schema-recyclic-dev.md`](../dumps/schema-recyclic-dev.md) — écarts → HITL |
| Requêtes T2 documentées | `…/2026-T2/queries-decla-t2.sql` |
| Agrégats DEC_REE | alimente `Complément-DEC_REE-T2-2026.csv` |

**Règle :** aucune requête `INSERT`/`UPDATE`/`DELETE` sur miroir mission ; pas d'exposition du dump sur le réseau.

### 12.3 Bot Discord (post-gate CREOS)

Même miroir (ou refresh cron **dump → restore**) alimente l'outil Hermes `sql_readonly` — salon unique, requêtes **cataloguées** uniquement. Voir cadrage [`2026-07-05_02_cadrage-bot-discord-la-clique-pilote.md`](2026-07-05_02_cadrage-bot-discord-la-clique-pilote.md).

### 12.4 Prochaine action technique

1. `pg_restore` du dump **20260707** en local  
2. Phase 1 spec §6 — reconnaissance tables (sans supposer)  
3. Calculer les **8 DEC_REE** manquantes → CSV complément
