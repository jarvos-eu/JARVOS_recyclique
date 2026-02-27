# Story 4.1: Configuration du canal push (endpoint, secret, résilience)

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

En tant qu'admin technique,
je veux configurer l'endpoint du plugin Paheko, le secret partagé et les paramètres de résilience,
afin que le worker puisse envoyer les tickets de façon sécurisée.

## Contexte epic

**Epic 4 — Canal push Paheko** : configurer et rendre opérationnel le canal RecyClique → Paheko (endpoint sécurisé, worker Redis Streams, retry sans perte). Prérequis : Epic 1 livré (Redis opérationnel, Paheko joignable). Parallèle possible avec Epic 3. FRs : FR19, FR20 (partiel).

**Prérequis story** : instance RecyClique et Paheko déployées (Epic 1).

## Acceptance Criteria

1. **Étant donné** une instance RecyClique et Paheko déployées  
   **Quand** je configure via `.env` l'URL du plugin, le secret et les options de retry  
   **Alors** la config est chargée par `api/config/settings.py` (Pydantic Settings) ; aucun secret en clair dans les requêtes (NFR-S1, NFR-S2)

2. **Étant donné** la config chargée  
   **Alors** la résilience (nb tentatives, backoff) est documentée (FR19) — soit dans le code (docstrings / types), soit dans un fichier doc (ex. `doc/canal-push.md` ou section dans README).

## Tasks / Subtasks

- [x] Task 1 : Module config Pydantic Settings (AC: 1)
  - [x] Créer `api/config/` si absent
  - [x] Ajouter la dépendance `pydantic-settings` au projet (pyproject.toml ou requirements.txt) si absente
  - [x] Créer `api/config/settings.py` avec une classe Settings (pydantic-settings / BaseSettings) chargeant depuis l'environnement
  - [x] Définir les variables : URL du plugin Paheko (ex. `PAHEKO_PLUGIN_URL`), secret partagé (ex. `PAHEKO_PLUGIN_SECRET`), options retry (ex. `PAHEKO_PUSH_MAX_RETRIES`, `PAHEKO_PUSH_BACKOFF_SECONDS` ou équivalent)
  - [x] S'assurer qu'aucun secret n'est loggé ni exposé dans les réponses API
- [x] Task 2 : Fichier .env et documentation (AC: 1, 2)
  - [x] Documenter dans le repo les variables attendues (ex. `.env.example` ou section README / doc) : noms, exemples sans valeurs réelles, obligation (requis pour le worker)
  - [x] Documenter la résilience : nombre de tentatives, stratégie de backoff, comportement en cas d'échec (message reste en file Redis)
- [x] Task 3 : Intégration et vérification (AC: 1)
  - [x] Vérifier que l'app (ou un point d'entrée worker) peut importer `api.config.settings` et lire les valeurs sans erreur quand les variables sont définies
  - [x] Optionnel : test unitaire chargeant les settings avec des env mocks

## Dev Notes

- **NFR-S1** : Les échanges RecyClique ↔ Paheko passent par HTTPS avec un secret partagé ; aucun secret en clair dans les requêtes.
- **NFR-S2** : Les secrets sont gérés via variables d'environnement ou secrets manager, pas en dur dans le code.
- **Architecture** : Config chargée via Pydantic Settings dans `api/config/` ; pas de secrets en dur. Référence : `_bmad-output/planning-artifacts/architecture.md` — sections « Structure Patterns », « Authentication & Security », « Infrastructure & Deployment ».
- **Stack** : Python 3.12, FastAPI. Utiliser `pydantic-settings` (ou `BaseSettings` de Pydantic v2) pour charger depuis `.env` et variables d'environnement.
- **Nommage** : variables d'environnement en UPPER_SNAKE (ex. `PAHEKO_PLUGIN_URL`, `PAHEKO_PLUGIN_SECRET`). Pas de valeur par défaut pour le secret en prod.
- **Résilience** : paramètres typiques à prévoir : nombre max de tentatives (ex. 3 ou 5), délai initial de backoff (ex. 1 s), facteur d'exponentiel si souhaité. La story 4.2 consommera cette config pour le worker Redis Streams (même module `api.config.settings` — pas de config dupliquée).

### Project Structure Notes

- `api/config/settings.py` : fichier unique de settings pour l'API (convention architecture). Si d'autres settings existent déjà (ex. Epic 1), étendre le même module ou regrouper les settings « canal push » dans un sous-module/nested model.
- `.env` à la racine du repo (ne pas versionner — doit être dans `.gitignore`) ; `.env.example` versionné, sans secrets, avec liste des variables et commentaires.

### References

- [Source: _bmad-output/planning-artifacts/epics.md — Epic 4, Story 4.1]
- [Source: _bmad-output/planning-artifacts/architecture.md — Structure Patterns, Authentication & Security, Infrastructure & Deployment]
- [Source: epics.md — NFR-S1, NFR-S2, FR19]

## Dev Agent Record

### Agent Model Used

bmad-dev (Story 4.1 implementation)

### Debug Log References

-

### Completion Notes List

- **Task 1** : `api/config/` existait déjà. `pydantic-settings` déjà dans `api/requirements.txt`. Étendu `api/config/settings.py` avec les champs canal push : `paheko_plugin_url`, `paheko_plugin_secret` (SecretStr pour ne pas exposer en repr/log), `paheko_push_max_retries` (défaut 5), `paheko_push_backoff_seconds` (1.0), `paheko_push_backoff_factor` (2.0). Aucun secret en clair dans les réponses (SecretStr + pas d'exposition dans l'API).
- **Task 2** : Création de `.env.example` à la racine avec toutes les variables (DB, Redis, JWT, Paheko, résilience) et commentaires. Création de `doc/canal-push.md` (config + résilience FR19 : nb tentatives, backoff exponentiel, message reste en file Redis). Mise à jour de `doc/index.md`.
- **Task 3** : Vérification d'import et lecture des settings (script Python). Ajout de `api/tests/test_config_settings.py` : 4 tests (champs présents, valeurs par défaut, chargement depuis env mock, secret absent du repr). Suite complète : 125 tests passent.

### File List

- api/config/settings.py (modifié)
- .env.example (créé)
- doc/canal-push.md (créé)
- doc/index.md (modifié)
- api/tests/test_config_settings.py (créé)

## Senior Developer Review (AI)

- **Date** : 2026-02-27
- **Outcome** : Approved
- **AC Validation** : AC1 — config chargée par api/config/settings.py (Pydantic Settings), SecretStr pour paheko_plugin_secret, aucun secret en clair (repr, réponses API). AC2 — résilience documentée dans doc/canal-push.md (tentatives, backoff exponentiel, message reste en file Redis).
- **Task Audit** : Toutes les tâches [x] vérifiées (settings.py, .env.example, doc, tests).
- **File List** : Conforme ; tous les fichiers listés présents et cohérents avec la story.
- **Tests** : 4 tests (test_config_settings.py) exécutés et passants.
- **Findings** : LOW uniquement — pas de validation HttpUrl pour PAHEKO_PLUGIN_URL (amélioration possible en 4.2+) ; get_settings() en lru_cache (comportement attendu). Aucun HIGH/MEDIUM.

### Change Log

- 2026-02-27 : Story 4.1 implémentée — config canal push (endpoint, secret, résilience), .env.example, doc/canal-push.md, tests unitaires settings.
- 2026-02-27 : Code review (AI) — AC1/AC2 validés, File List conforme, 4 tests passent. Findings LOW uniquement (validation URL optionnelle, lru_cache connu). Review result: approved. Status → done.
