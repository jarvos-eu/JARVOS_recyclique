# Story 9.1: Modèle et persistance des données déclaratives







Status: done







<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->







## Story







En tant que **système**,



je veux **stocker les données nécessaires aux déclarations éco-organismes dans RecyClique**,



afin qu'**elles soient la source de vérité pour les déclarations officielles**.







## Acceptance Criteria







1. **Étant donné** les flux réception et caisse opérationnels (Epics 5, 6) et les catégories mappées (Epic 2)  



   **Quand** des données déclaratives sont produites (agrégats par période, catégorie, flux)  



   **Alors** elles sont persistées en BDD RecyClique (tables ou vues dédiées) ; exports ou requêtes pour déclarations possibles (FR22)  



   **Et** traçabilité et périmètre documentés.







## Tasks / Subtasks







- [x] Task 1 — Modèle de données déclaratives (AC: #1)



  - [x] Définir le schéma (tables ou vues) : agrégats par période (ex. T1–T4 ou mois/trimestre), catégorie (`category_id` FK vers `categories`), type de flux (caisse vs réception), poids / quantités.



  - [x] Créer les migrations Alembic ; conventions snake_case, index `idx_{table}_{colonne}`. **Tables additives uniquement** : ne pas modifier `sales`, `sale_items`, `ligne_depot`, `categories`.



- [x] Task 2 — Alimentation et persistance (AC: #1)



  - [x] Définir la source des agrégats : **`sale_items`** (colonne `weight` en kg, `category_id` ; période dérivée de `sales.created_at` ou date de vente) ; **`ligne_depot`** (colonne `poids_kg`, `category_id` ; période dérivée de `created_at` ou ticket).



  - [x] Implémenter un **service** de calcul des agrégats déclaratifs, **réexécutable** (recalcul d'une période donnée pour backfill/corrections), appelable par un job planifié ou manuellement ; persister les résultats en BDD.



- [x] Task 3 — Requêtes et exports (AC: #1)



  - [x] Exposer les données pour requêtes (ex. API read-only ou vues SQL) afin que les exports ou déclarations soient possibles.



- [x] Task 4 — Documentation traçabilité et périmètre (AC: #1)



  - [x] Documenter le périmètre v1 (champs, périodes, flux caisse/réception) et la traçabilité (source des agrégats, règles de calcul).



- **Review Follow-ups (AI)** — 2026-02-27



  - [x] [AI-Review][MEDIUM] Valider le paramètre `flow_type` sur GET `/v1/declarative/aggregates` : accepter uniquement `caisse` | `reception` et retourner 422 si valeur invalide (au lieu d'une liste vide). [api/routers/declarative.py]

  - [x] [AI-Review][MEDIUM] Ajouter un test d'intégration : créer une vente (Sale + SaleItem) dans une période, appeler `compute_and_persist_aggregates`, vérifier une ligne dans `declarative_aggregates` avec les bons `weight_kg`/`quantity`. [api/tests/test_declarative.py]

  - [x] [AI-Review][LOW] Ajouter un test 403 pour GET/POST déclaratifs sans permission admin (alignement test_admin_rbac). [api/tests/test_declarative.py]

  - [x] [AI-Review][LOW] Optionnel : borner `year` sur POST `/aggregates/compute` (ex. 1900–2100) ; ou documenter. [api/routers/declarative.py]







- **FR22** : Le système peut produire et conserver les données déclaratives (poids, flux, catégories, périodes) dans RecyClique pour les déclarations éco-organismes.



- **Source de vérité** : RecyClique produit et conserve ; pas de sync bidirectionnelle avec Paheko pour ces données (artefact 08 §2.7). Données déclaratives = agrégats par période, catégorie, flux (caisse / réception).



- **Référentiel catégories** : table `categories` existante (Epic 2) ; `category_id` dans `sale_items` et `ligne_depot` déjà disponibles.



- **Colonnes source (ne pas réinventer)** : caisse = `sale_items.weight` (kg), `sale_items.category_id` ; réception = `ligne_depot.poids_kg`, `ligne_depot.category_id`. Périodes à dériver des dates (`sales.created_at`, `ligne_depot.created_at` ou ticket).



- **Périodes** : T1–T4 (trimestres) ou mois/année selon périmètre v1 à valider (HITL-9.0 recommandé).



- **Story 9.2** (post-MVP) : module décla éco-organismes (exports, multi-éco-organismes) ; cette story 9.1 ne livre que le **modèle et la persistance** + capacité à requêter/exporter les agrégats, pas l'UI ni les formats par éco-organisme.







### Architecture Compliance







- BDD : snake_case, tables au pluriel, index `idx_{table}_{colonne}`. Pas de secret en clair.



- API : si endpoints exposés, pluriel snake_case, JSON, erreur `{ "detail": "..." }`, dates ISO 8601.



- Pas de règle brownfield 1.4.4 pour ce domaine : les données déclaratives sont produites côté RecyClique (artefact 08) ; s'appuyer sur les tables existantes (sales, sale_items, ligne_depot, categories) pour les sources.







### Project Structure Notes







- Migrations : `api/db/migrations/` (Alembic) — ou `api/db/alembic/versions/` selon structure existante.



- Modèles : **`api/models/`** avec un module dédié (ex. `api/models/declarative.py` ou `api/models/declarative/`) ; ne pas modifier les modèles existants `sale_item`, `ligne_depot`, `category`.



- Routes API (si exposées) : sous `api/routers/` (ex. `api/routers/declarative/` ou sous `api/routers/v1/admin/` selon périmètre lecture seule).



- Référence structure : `_bmad-output/planning-artifacts/architecture.md`, checklist v0.1 `references/artefacts/2026-02-26_03_checklist-v0.1-architecture.md`.







### References







- [Source: _bmad-output/planning-artifacts/epics.md — Epic 9, Story 9.1]



- [Source: references/artefacts/2026-02-26_08_catalogue-qui-stocke-quoi-recyclic-paheko.md §2.7 Données déclaratives et poids]



- [Source: references/vision-projet/vision-module-decla-eco-organismes.md — agrégats dates, flux, poids, catégories]



- [Source: references/migration-paeco/audits/matrice-correspondance-caisse-poids.md — Rapports / déclarations]



- [Source: _bmad-output/planning-artifacts/architecture.md — Conformité déclarations éco-organismes]







## Dev Agent Record







### Agent Model Used







—







### Debug Log References







—







### Completion Notes List







- Task 1 : Table `declarative_aggregates` (year, quarter, category_id, flow_type, weight_kg, quantity) ; modèle `api/models/declarative.py` ; migration Alembic `api/db/alembic/versions/2026_02_27_9_1_declarative_aggregates.py`. Index idx_declarative_aggregates_*.



- Task 2 : Service `api/services/declarative_service.py` — `compute_and_persist_aggregates(db, year, quarter)` : sources `sale_items` (JOIN sales, période COALESCE(sale_date, created_at)) et `ligne_depot` (created_at) ; réexécutable (delete puis recalc). Endpoint POST `/v1/declarative/aggregates/compute` pour appel manuel ou job.



- Task 3 : GET `/v1/declarative/aggregates` (filtres year, quarter, flow_type, category_id), permission admin. Schéma `DeclarativeAggregateResponse` (snake_case, ISO 8601).



- Task 4 : Doc `doc/declarative-aggregates-v1.md` (périmètre v1, traçabilité, règles de calcul) ; entrée dans `doc/index.md`.



- **Post-review (2026-02-27)** : (1) GET aggregates : `flow_type` validé (caisse | reception), 422 si invalide. (2) POST compute : `year` borné 1900–2100, 400 si hors plage. (3) Test d'intégration Sale+SaleItem → compute → vérif lignes declarative_aggregates. (4) Tests 403 GET et POST sans permission admin (patch get_user_permission_codes). (5) Tests 422 flow_type invalide et 400 year invalide.







### File List







- api/models/declarative.py



- api/models/__init__.py



- api/db/alembic/versions/2026_02_27_9_1_declarative_aggregates.py



- api/services/declarative_service.py



- api/schemas/declarative.py



- api/routers/declarative.py



- api/main.py



- api/tests/test_declarative.py



- doc/declarative-aggregates-v1.md



- doc/index.md



- _bmad-output/implementation-artifacts/sprint-status.yaml





## Senior Developer Review (AI)



**Date :** 2026-02-27  

**Résultat :** changes-requested  

**Git vs File List :** Aucune discordance (fichiers 9.1 listés = fichiers modifiés/ajoutés git).



### Synthèse



- **AC #1** : Implémenté — table `declarative_aggregates`, service réexécutable, GET/POST API, doc `doc/declarative-aggregates-v1.md`.

- **Tasks 1–4** : Réalisés (schéma, migrations, index, sources sale_items/ligne_depot, API read-only, doc).



### Constats (adversarial)



- **MEDIUM** : GET `/v1/declarative/aggregates` accepte tout `flow_type` en query ; la doc impose `caisse` | `reception`. Une valeur invalide renvoie une liste vide au lieu de 422 → risque de confusion.

- **MEDIUM** : Aucun test avec données source réelles (Sale + SaleItem ou LigneDepot dans la période) vérifiant le calcul des agrégats ; couverture métier incomplète.

- **LOW** : Pas de test 403 sans permission admin sur les routes déclaratives.

- **LOW** : Pas de borne sur `year` pour POST `/aggregates/compute` (optionnel).



**Pass 2 (2026-02-27) — Résultat :** approved  

**Vérification follow-ups :** (1) flow_type validé sur GET, 422 si invalide. (2) Test d'intégration Sale+SaleItem → compute → lignes declarative_aggregates. (3) Tests 403 GET/POST sans admin. (4) year borné 1900–2100 sur POST compute. Tous satisfaits ; 12 tests passent.



### Change Log



- 2026-02-27 : Code review adversarial (bmad-qa). Changes requested — follow-ups ajoutés (validation flow_type, test intégration agrégats, test 403).

- 2026-02-27 : Code review pass 2 (bmad-qa). Approved — follow-ups satisfaits ; story done.

