# Story 9.2: (Post-MVP) Module décla éco-organismes

Status: review

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->
<!-- Story post-MVP : implémentation après le MVP ; les critères restent exécutables lorsque le périmètre post-MVP est activé. -->

## Story

En tant que **responsable**,
je veux **utiliser un module RecyClique dédié aux déclarations éco-organismes**,
afin de **produire les déclarations officielles sans quitter RecyClique**.

## Acceptance Criteria

1. **Étant donné** les données déclaratives persistées (Story 9.1) et le périmètre post-MVP  
   **Quand** le module décla est activé (config / feature)  
   **Alors** je peux exporter ou soumettre les données selon le format attendu (FR23)  
   **Et** la story est marquée post-MVP.

2. **Étant donné** le module décla activé et des agrégats disponibles pour une période (year, quarter)  
   **Quand** je demande un export ou une préparation de déclaration pour un éco-organisme cible (ex. Ecologic, Ecomaison)  
   **Alors** le système produit un export (fichier ou payload) conforme au format attendu par cet éco-organisme  
   **Et** les données source sont les agrégats RecyClique (table `declarative_aggregates`, API `GET /v1/declarative/aggregates`).

3. **Étant donné** la vision multi-éco-organismes (référence vision-projet)  
   **Quand** plusieurs éco-organismes sont configurés  
   **Alors** je peux choisir l'éco-organisme (ou la déclaration) et obtenir l'export au format correspondant  
   **Et** le mapping catégories RecyClique → catégories officielles par éco-organisme est documenté ou configurable (détail post-MVP).

## Tasks / Subtasks

- [x] Task 1 — Activation du module décla (AC: #1)
  - [x] Définir le critère d'activation (ex. `modules.toml`, feature flag ou config dédiée) sans casser le socle Epic 1.
  - [x] Lorsque le module est actif : exposer l'entrée utilisateur (écran, menu ou API) pour déclarations / exports.
- [x] Task 2 — Export / soumission selon format attendu (AC: #2, #3)
  - [x] Définir ou documenter les formats attendus par éco-organisme (ex. CSV, Excel, schéma spécifique) — au moins un format de référence (ex. générique CSV agrégats) pour la première implémentation.
  - [x] Implémenter un export (téléchargement fichier ou endpoint) basé sur les agrégats `declarative_aggregates` (via service 9.1 ou API GET aggregates).
  - [x] Permettre le choix de la période (year, quarter) et, si applicable, de l'éco-organisme cible.
- [x] Task 3 — Documentation et marquage post-MVP (AC: #1, #3)
  - [x] Documenter le périmètre du module décla post-MVP (formats, éco-organismes supportés, mapping catégories).
  - [x] S'assurer que la story et les livrables sont clairement identifiés comme post-MVP (pas bloquant pour la mise en production MVP).

## Dev Notes

- **Story 9.1** livre : table `declarative_aggregates`, service `compute_and_persist_aggregates`, `GET /v1/declarative/aggregates` (filtres year, quarter, flow_type, category_id), `POST /v1/declarative/aggregates/compute`. S'appuyer sur ces briques ; pas de recalcul des agrégats dans cette story, uniquement **lecture** (GET aggregates ou lecture BDD via service) et mise en forme pour export/soumission.
- **FR23** : Le système peut exposer un module décla éco-organismes (exports, multi-éco-organismes) depuis RecyClique. Post-MVP.
- **Vision** : `references/vision-projet/vision-module-decla-eco-organismes.md` — module(s) agnostiques, plusieurs éco-organismes, mapping catégories boutique → catégories officielles par éco-organisme ; déclarations = calcul et pré-remplissage côté RecyClique, saisie finale sur les plateformes partenaires (pas d'API chez les éco-organismes à ce jour). Donc en post-MVP : export / pré-remplissage selon format attendu ; la « soumission » peut être export fichier pour dépôt manuel.
- **Loader modules** : `api/config/modules.toml`, `api/core/modules/`, slots frontend si besoin ; ne pas recréer une autre convention (architecture Epic 1).

### Architecture Compliance

- Réutiliser les routes ou services existants sous `api/routers/declarative.py`, `api/services/declarative_service.py`. Nouveaux endpoints d'export sous le préfixe cohérent (ex. `GET /v1/declarative/export` ou sous-module).
- **Permissions** : même niveau que Story 9.1 — accès réservé admin (export et entrée utilisateur du module décla) ; pas d'exposition publique.
- BDD : pas de nouvelle table obligatoire pour un premier livrable post-MVP (lecture `declarative_aggregates` suffit) ; si configuration par éco-organisme : tables additives, snake_case, index `idx_*`.
- API : pluriel snake_case, JSON ou fichier binaire (export), erreur `{ "detail": "..." }`, dates ISO 8601.

### Project Structure Notes

- Routes / services : étendre `api/routers/declarative.py` ou `api/services/declarative_service.py` pour l'export ; ou module dédié `api/routers/declarative_export.py` si séparation claire.
- Frontend (si écran décla post-MVP) : sous domaine déclaratif, slots si module activable côté UI ; référence `frontend/src/shared/slots/`, structure par domaine.
- Référence structure : `_bmad-output/planning-artifacts/architecture.md`, `references/artefacts/2026-02-26_03_checklist-v0.1-architecture.md`.

### Previous Story Intelligence (9.1)

- Modèle : `api/models/declarative.py` — table `declarative_aggregates` (year, quarter, category_id, flow_type, weight_kg, quantity).
- Service : `api/services/declarative_service.py` — `compute_and_persist_aggregates(db, year, quarter)` ; lecture des agrégats via repo ou requête.
- API : `GET /v1/declarative/aggregates` (filtres year, quarter, flow_type, category_id) ; permission admin. Schéma `DeclarativeAggregateResponse`, snake_case, ISO 8601.
- Validation 9.1 : `flow_type` = `caisse` | `reception` (422 si invalide) ; `year` borné 1900–2100 sur POST compute. Tests : 403 sans admin, intégration Sale+SaleItem → compute → lignes.
- Doc : `doc/declarative-aggregates-v1.md` — périmètre v1, traçabilité, règles de calcul ; évolution 9.2 indiquée (exports, multi-éco-organismes).

### References

- [Source: _bmad-output/planning-artifacts/epics.md — Epic 9, Story 9.2]
- [Source: _bmad-output/planning-artifacts/prd.md — FR23]
- [Source: doc/declarative-aggregates-v1.md — agrégats, exposition API, évolutions 9.2]
- [Source: references/vision-projet/vision-module-decla-eco-organismes.md — module agnostique, multi-éco-organismes, mapping catégories]
- [Source: _bmad-output/implementation-artifacts/9-1-modele-et-persistance-des-donnees-declaratives.md — modèle, service, API, file list]

## Dev Agent Record

### Agent Model Used

—

### Debug Log References

—

### Completion Notes List

- Task 1 : Critère d'activation = `modules.toml` section `[modules]` enabled inclut `"decla"`. Route export enregistrée dans `main.py` (lecture config) pour ordre avant catch-all. Module DeclaModule dans `api/core/modules/decla_module.py` enregistre aussi l'export (loader) ; l'activation effective utilise la lecture toml dans main pour l'ordre des routes.
- Task 2 : Format de référence CSV (colonnes agrégats) + JSON. GET /v1/declarative/export avec year, quarter obligatoires ; format=csv|json ; flow_type, category_id, eco_organism optionnels. Service `get_aggregates()` ajouté pour réutilisation (router list + export). Permission admin.
- Task 3 : doc/declarative-aggregates-v1.md mis à jour avec section « Module décla post-MVP ». Story et livrables marqués post-MVP (commentaires, doc).

### File List

- api/config/modules.toml (modifié — section [decla], commentaire activation)
- api/config/modules.test.toml (nouveau — enabled stub + decla pour tests)
- api/config/settings.py (modifié — modules_config_path optionnel)
- api/core/modules/base.py (modifié — réintégration typing Any, docstring register)
- api/core/modules/loader.py (modifié — registre decla DeclaModule)
- api/core/modules/decla_module.py (nouveau)
- api/main.py (modifié — inclusion conditionnelle route export décla avant catch-all)
- api/routers/declarative.py (modifié — utilise get_aggregates, suppression import DeclarativeAggregate)
- api/routers/declarative_export.py (nouveau)
- api/services/declarative_service.py (modifié — get_aggregates, import UUID)
- api/tests/conftest.py (modifié — MODULES_CONFIG_PATH vers modules.test.toml en tests)
- api/tests/test_declarative.py (modifié — tests export 200 CSV/JSON, 422 format, 403 sans admin)
- doc/declarative-aggregates-v1.md (modifié — section Module décla post-MVP)
