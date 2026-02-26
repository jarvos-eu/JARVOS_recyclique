# Story 1.4: Squelette du loader de modules (TOML, ModuleBase) et place pour EventBus/slots

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

En tant que **développeur**,
je veux **une base pour le chargement de modules RecyClique (TOML, contrat ModuleBase, place pour EventBus Redis Streams et slots React dans l'arborescence)**,
afin de **pouvoir activer des modules par configuration sans refonte ultérieure**.

## Acceptance Criteria

1. **Loader API et config TOML**  
   **Étant donné** l'arborescence frontend et API existante  
   **Quand** le loader (côté API) lit une config TOML et enregistre des modules respectant un contrat ModuleBase  
   **Alors** au moins un module exemple ou stub peut être chargé au démarrage  
   **Et** la structure est documentée dans l'architecture (FR24, FR25).

2. **Place pour EventBus et slots**  
   **Étant donné** la même arborescence  
   **Quand** l'arborescence prévoit la place pour EventBus (workers, streams) côté API et slots React côté frontend  
   **Alors** les dossiers/points d'entrée sont en place (sans implémentation métier complète)  
   **Et** la documentation indique comment y brancher les workers Redis Streams et les slots (FR24).

3. **Convention tests frontend**  
   **Étant donné** la checklist v0.1 (epics.md)  
   **Quand** la convention de tests frontend est tranchée (co-located `*.test.tsx` vs `__tests__` au niveau module)  
   **Alors** elle est documentée (architecture ou README frontend) et appliquée pour au moins un composant ou module existant.

## Tasks / Subtasks

- [x] Task 1 : Contrat ModuleBase et config TOML côté API (AC: #1)
  - [x] Définir une interface/contrat ModuleBase (ex. `api/core/modules/base.py` ou équivalent) : méthodes minimales (ex. `name`, `register`, `startup`/`shutdown` ou équivalent)
  - [x] Définir le schéma de la config TOML des modules (ex. chemin fichier, liste de modules activés, champs optionnels)
  - [x] Créer un loader (ex. `api/core/modules/loader.py`) qui lit la config TOML au démarrage et enregistre les modules respectant ModuleBase
  - [x] Intégrer l'appel au loader dans le cycle de vie de l'application FastAPI (startup event)
- [x] Task 2 : Module exemple ou stub (AC: #1)
  - [x] Créer au moins un module stub ou exemple (ex. `api/core/modules/stub_module.py` ou module dédié) implémentant ModuleBase
  - [x] Fournir un fichier TOML d'exemple dans `api/config/` (ex. `modules.example.toml`) listant ce module
  - [x] Vérifier qu'au démarrage l'API charge le module (log ou endpoint de diagnostic optionnel)
- [x] Task 3 : Place pour EventBus (workers, streams) côté API (AC: #2)
  - [x] Prévoir/ajouter dans l'arborescence la place pour les workers Redis Streams (ex. `api/workers/` déjà présent dans l'architecture ; s'assurer qu'un point d'entrée ou un module vide existe pour les consumers EventBus)
  - [x] Documenter le nommage des streams et événements (dot.lowercase ou snake_case, ex. `pos.ticket.created`) et le format payload (JSON snake_case ; prévoir `event_type` / `payload_version` si évolution) — aligné architecture.
  - [x] Pas d'implémentation métier complète des workers dans cette story ; uniquement la structure et la doc
- [x] Task 4 : Place pour slots React côté frontend (AC: #2)
  - [x] Prévoir dans `frontend/src/` la place pour les slots (ex. dossier `shared/slots/` ou point d'injection documenté dans un layout/domaine) permettant d'injecter du contenu fourni par les modules
  - [x] Documenter comment les modules frontend pourront enregistrer des slots (référence FR24, FR25 et recherche technique extension points si pertinent)
- [x] Task 5 : Convention tests frontend et documentation (AC: #3)
  - [x] Trancher la convention : co-located `*.test.tsx` à côté des composants vs dossier `__tests__` au niveau module
  - [x] Documenter la décision dans l'architecture (`_bmad-output/planning-artifacts/architecture.md`) ou dans `frontend/README.md`
  - [x] Appliquer la convention pour au moins un composant ou module existant (ex. un test dans `shared/` ou `caisse/`) ; ajouter Vitest + React Testing Library si pas encore en place (Story 1.1/1.2)

## Dev Notes

- **FR24, FR25** (epics.md) : Le système peut charger et activer des modules RecyClique via configuration (TOML, ModuleBase, EventBus Redis Streams, slots React). Coexistence plugins Paheko et modules RecyClique. Cette story pose le squelette uniquement.
- **EventBus** (architecture) : Redis Streams côté serveur uniquement ; le front passe par l'API. Nommage événements : dot.lowercase ou snake_case (ex. `pos.ticket.created`) ; payload JSON snake_case. Idempotence et acks après traitement.
- **Checklist v0.1** (epics.md) : Intégrer loader modules (TOML, ModuleBase) et slots dans les premières stories modulaires ; prévoir la place dans l'arborescence frontend/API dès le début. Trancher convention tests frontend : co-located `*.test.tsx` vs `__tests__` au niveau module.
- **Structure actuelle** : `api/` avec `routers/`, `config/`, `core/`, `workers/` (présent dans l'architecture) ; `frontend/src/` avec domaines (caisse, reception, auth, admin, shared). Ne pas casser la structure des stories 1.1–1.3.

### Project Structure Notes

- **API** : `api/core/modules/` pour ModuleBase, loader, et module stub ; `api/config/` pour le fichier TOML (ex. `modules.toml`, `modules.example.toml`) — aligné architecture. `api/workers/` pour la place EventBus/consumers.
- **Frontend** : `frontend/src/shared/slots/` ou équivalent pour les points d'injection ; à documenter dans l'architecture.
- Alignement avec `_bmad-output/planning-artifacts/architecture.md` : Implementation Patterns (Event System, nommage Redis), Project Structure (workers, frontend par module), Gap Analysis (loader modules et convention tests).

### Previous Story Intelligence (1.1–1.3)

- **1.1** : Frontend `frontend/src/` par domaine (caisse, reception, auth, admin, shared, core, types). Build → `frontend/dist/`.
- **1.2** : API `api/` avec routers, config Pydantic Settings, montage statics + catch-all, `GET /health`. Pas de secrets en dur.
- **1.3** : Docker Compose en place ; RecyClique un container (front build + API). Le loader doit s'exécuter au démarrage dans le même processus (Uvicorn/FastAPI lifespan).

### References

- [Source: _bmad-output/planning-artifacts/epics.md — Epic 1, Story 1.4, critères d'acceptation]
- [Source: _bmad-output/planning-artifacts/epics.md — FR24, FR25, Checklist v0.1 (loader modules, convention tests)]
- [Source: _bmad-output/planning-artifacts/architecture.md — API & Communication Patterns (EventBus Redis Streams côté serveur), Implementation Patterns (Event System, nommage dot.lowercase/snake_case)]
- [Source: _bmad-output/planning-artifacts/architecture.md — Project Structure (api/workers/, frontend par module), Structure Patterns (tests co-located vs __tests__)]
- [Source: _bmad-output/planning-artifacts/architecture.md — Gap Analysis (loader modules, convention tests frontend à trancher)]

## Dev Agent Record

### Agent Model Used

bmad-dev (Story 1.4 implémentée en une session).

### Debug Log References

- TestClient avec lifespan : utilisation de `with TestClient(app) as client:` pour que le lifespan s'exécute et que GET /api/admin/diagnostic/modules retourne les modules chargés.
- Chemin modules.toml : résolution depuis `api/core/modules/loader.py` avec 4 parents pour atteindre la racine du repo.

### Completion Notes List

- **AC1** : ModuleBase (`api/core/modules/base.py`), schéma TOML `[modules] enabled = [...]` + sections optionnelles par module, loader dans `loader.py`, intégration via lifespan FastAPI. Module stub + `modules.toml` / `modules.example.toml`, endpoint GET /api/admin/diagnostic/modules pour vérifier le chargement.
- **AC2** : `api/workers/` avec README (nommage streams, payload, idempotence/acks). `frontend/src/shared/slots/` avec README et index.ts ; référence dans architecture.
- **AC3** : Convention adoptée — tests co-located `*.test.tsx`. Documentée dans `frontend/README.md` et `architecture.md`. Vitest + React Testing Library ajoutés ; `App.test.tsx` applique la convention.

### File List

- api/core/modules/__init__.py
- api/core/modules/base.py
- api/core/modules/loader.py
- api/core/modules/stub_module.py
- api/config/modules.toml
- api/config/modules.example.toml
- api/config/settings.py (modules_config_path)
- api/workers/__init__.py
- api/workers/README.md
- api/main.py (lifespan, loader)
- api/routers/admin/router.py (GET /api/admin/diagnostic/modules)
- api/tests/test_modules_loader.py
- frontend/src/shared/slots/README.md
- frontend/src/shared/slots/index.ts
- frontend/src/test/setup.ts
- frontend/src/App.test.tsx
- frontend/vite.config.ts (test)
- frontend/package.json (scripts test, test:run ; deps vitest, jsdom, @testing-library/react, @testing-library/jest-dom)
- frontend/README.md (convention tests)
- _bmad-output/planning-artifacts/architecture.md (réf. workers README, slots, convention tests tranchée)

## Senior Developer Review (AI)

- **Date** : 2026-02-26
- **Résultat** : Approuvé après corrections automatiques.

**Vérifications effectuées** : Tous les AC implémentés. Toutes les tâches [x] confirmées dans le code. File List cohérente avec les fichiers présents (api/, frontend/).

**Problèmes trouvés et traités** :
- **MEDIUM** — Sécurité : `modules_config_path` pouvait pointer vers un fichier arbitraire (ex. via env). **Corrigé** dans `api/core/modules/loader.py` : restriction du chemin au répertoire du repo et extension `.toml`.
- **MEDIUM** — Robustesse : si le TOML avait `enabled = "stub"` (chaîne au lieu de liste), itération sur les caractères. **Corrigé** : normalisation `if not isinstance(enabled, list): enabled = []`.

**Points LOW (non bloquants)** : Tests edge (fichier TOML absent, TOML invalide) non ajoutés ; endpoint diagnostic non protégé (documenté comme optionnel) ; version Python minimale 3.11 (tomllib) implicite dans Dockerfile 3.12.

## Change Log

| Date       | Événement | Détail |
|------------|-----------|--------|
| 2026-02-26 | Code review (bmad-qa) | Review adversarial ; 2 correctifs MEDIUM appliqués (validation chemin modules_config_path, type enabled) ; statut → done. |
