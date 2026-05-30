# Story 27.1 : Contrat `RegisteredDevice` et registre minimal

Status: review

**Story key :** `27-1-registered-device`  
**Epic :** 27 — Postes partagés enrôlés + PIN opérateur + PWA installable non-offline  
**Implementation artifact :** `_bmad-output/implementation-artifacts/27-1-registered-device.md`  
**Date CS :** 2026-05-30

## Dépendances (prérequis)

- **Epic 27 — cadrage gelé** : `_bmad-output/planning-artifacts/epics.md` (§ Epic 27, Story 27.1).
- **Mini-ADR Epic 27** : `references/artefacts/2026-05-29_02_mini-adr-postes-partages-pin-non-offline.md` — invariants serveur, vocabulaire `device_id`, exclusions offline / front authz.
- **Runbook orchestration** : `references/artefacts/2026-05-29_04_runbook-orchestration-epic-27-postes-partages-pin.md` — ordre stories, gates transverses, règles produit non négociables (§7).
- **Registre `module_key`** : `recyclique/api/src/recyclic_api/modules/module_config/registry.py` (`is_active_module_key`, `ACTIVE_MODULE_KEYS`) ; pack normatif `references/config-modules-site-id/index.md`.
- **Configuration modules par site** : modèle `SiteModuleConfig` (`recyclique/api/src/recyclic_api/models/site_module_config.py`) — l’allowlist poste **restreint** le contexte ; elle ne remplace pas la config site/module.
- **Stories suivantes (ne pas implémenter ici)** : 27.2 (ContextEnvelope + audit), 27.3 (panel SuperAdmin UI), 27.4 (enrôlement / secret local).

## Garde-fous ADR / runbook (obligatoires pour le DS)

| Invariant | Application story 27.1 |
|-----------|-------------------------|
| Pas d’offline métier | Aucun cache SW, file locale, sync différée ; champs « last contact » = métadonnée serveur uniquement. |
| Pas d’authz front | CRUD registre : rôles **serveur** (`require_role_strict`) ; aucune décision d’accès côté Peintre dans cette story. |
| `device_id` canonique | Identifiant API **`device_id`** (UUID) ; pas de second identifiant `workstation_id` en base. |
| Distinction identifiants | `device_id` ≠ `cash_registers.id` ≠ `poste_reception.id` ; tests de non-confusion obligatoires. |
| Allowlist `module_key` | Sous-ensemble du registre serveur ; validation via `is_active_module_key()`. |
| Pas de panel SuperAdmin complet | API + modèle + OpenAPI + tests ; **pas** d’écran « Gestion des postes » (story 27.3). |
| Pas d’enrôlement / secret local | Pas de flux code court, QR, WebCrypto, `localStorage` (story 27.4). |
| Pas de PIN / opérateur actif | Pas de session PIN ni extension `ContextEnvelope` (story 27.2). |

## Story (BDD)

As a **platform and security owner**,  
I want a **minimal server-side `RegisteredDevice` contract** for enrolled shared workstations,  
So that **shared posts are identified, revocable and future-proof** without being confused with cash registers or reception posts.

## Acceptance criteria

Source normative : `_bmad-output/planning-artifacts/epics.md` — **Story 27.1**.

**Given** Epic 27 uses `RegisteredDevice` as the canonical model and `device_id` as the stable identifier  
**When** this story is delivered  
**Then** the MVP model covers only `type = shared_workstation` while keeping the name broad enough for a future hardware registry  
**And** the contract includes at minimum name, site, emplacement, administrative status, allowlist `module_key`, timeout, simple last contact, and revocation state  
**And** `device_id` is explicitly distinct from `cash_register_id` and from any future `reception_post_id`  
**And** the story does not implement peripherals, hardware discovery, realtime supervision, or the complete hardware registry

### Interprétation exécutable

#### Modèle persistant (`RegisteredDevice`)

Créer une table dédiée (nom suggéré : **`registered_devices`**) et un modèle SQLAlchemy **`RegisteredDevice`** — **ne pas** réutiliser `cash_registers` ni `poste_reception`.

| Champ (concept) | Colonne / type suggéré | Règles |
|-----------------|------------------------|--------|
| Identifiant stable | `id` UUID PK ; exposé API/OpenAPI comme **`device_id`** | Jamais aliasé `cash_register_id` / `reception_post_id`. |
| Type appareil | `device_type` VARCHAR / enum | MVP : seule valeur créable **`shared_workstation`** ; refuser autres types à la validation (422). |
| Nom | `name` VARCHAR(100) NOT NULL | Libellé admin / produit « poste partagé ». |
| Site | `site_id` UUID FK → `sites.id` NOT NULL | Site résolu serveur ; refuser site inconnu (404). |
| Emplacement | `location` VARCHAR(255) NULL | Équivalent sémantique `CashRegister.location`. |
| Statut administratif | `status` VARCHAR(32) NOT NULL | Vocabulaire proposé (arbitrage local Story Runner si besoin) : `active`, `pending_enrollment`, `identity_lost`, `conflict`, `revoked`. |
| Révocation | `revoked_at` TIMESTAMPTZ NULL + cohérence `status == revoked` | Révoquer = `status=revoked` + horodatage ; idempotent si déjà révoqué. |
| Allowlist modules | `allowed_module_keys` `Column(JSON)` NOT NULL default `[]` | Tableau de strings ; chaque entrée doit passer `is_active_module_key()` ; doublons rejetés. **Modèle SQLAlchemy : `JSON` dialect-neutral** (comme `CashRegister.workflow_options` — JSONB en migration Postgres OK, pas de JSONB pur au modèle : tests SQLite). |
| Timeout inactivité | `inactivity_timeout_seconds` INTEGER NULL | Secondes ; NULL = défaut serveur documenté (proposition : **900** = 15 min, alignée cadrage PIN — ajustable en 27.9). |
| Dernier contact | `last_contact_at` TIMESTAMPTZ NULL | Granularité : **horodatage serveur UTC** ; pas de heartbeat automatique obligatoire en 27.1 — champ présent + PATCH/service hook documenté pour stories ultérieures. |

#### API REST minimale (backend-only)

Exposer des routes **`/v1/registered-devices/`** calquées sur le pattern `cash-registers` :

| Opération | Rôle minimum | Comportement |
|-----------|--------------|--------------|
| `GET /v1/registered-devices/` | `SUPER_ADMIN` | Liste paginée ; filtres `site_id`, `status`, `include_revoked`. |
| `POST /v1/registered-devices/` | `SUPER_ADMIN` | Création ; force `device_type=shared_workstation` ; statut initial par défaut **`pending_enrollment`** (admin sans enrôlement terrain — story 27.4). |
| `GET /v1/registered-devices/{device_id}` | `SUPER_ADMIN` | Détail par `device_id`. |
| `PATCH /v1/registered-devices/{device_id}` | `SUPER_ADMIN` | Mise à jour partielle (name, location, site_id, allowlist, timeout, status hors transitions réservées 27.4 si ambigu → documenter). |
| `POST /v1/registered-devices/{device_id}/revoke` | `SUPER_ADMIN` | Révocation explicite (préféré à un simple bool ambigu). |

- **Pas** de routes publiques / poste enrôlé sans auth admin dans cette story.
- Réponses **`Cache-Control: no-store`** (ou équivalent) sur endpoints authentifiés — cohérent ADR non-offline.

#### Contrat OpenAPI

- Ajouter schémas et paths dans **`contracts/openapi/recyclique-api.yaml`** uniquement (YAML standalone `openapi-module-config.yaml` **interdit**).
- Schémas suggérés : `RegisteredDeviceV1Response`, `RegisteredDeviceV1Create`, `RegisteredDeviceV1Update`, `RegisteredDeviceRevokeV1Request` (si corps requis).
- Propriété canonique **`device_id`** (format uuid) dans les réponses — **ne pas** nommer le champ `cash_register_id`.
- Documenter dans la description OpenAPI la distinction avec `CashRegisterV1Response.id` et `PosteReception` (pas de schéma fusionné).

#### Migration Alembic

- Nouvelle révision sous `recyclique/api/migrations/versions/`.
- Enregistrer le modèle dans `recyclic_api/models/__init__.py`.
- Migration réversible (`downgrade`).

#### Tests obligatoires (gates story)

Depuis `recyclique/api` :

1. **Modèle / migration** : table créée ; contraintes FK `site_id`.
2. **CRUD SuperAdmin** : create → get → list → patch → revoke ; 403 pour rôle non SuperAdmin.
3. **Allowlist** : rejet 422 si `module_key` inconnu du registre (`is_active_module_key`).
4. **Type MVP** : rejet 422 si `device_type` ≠ `shared_workstation` à la création.
5. **Non-confusion identifiants** : test explicite prouvant qu’un `device_id` de `RegisteredDevice` n’est **pas** accepté comme `cash_registers.id` sur une route caisse (404/422) et n’est **pas** confondu avec `poste_reception.id` — grep/review assertion documentée dans le test.
6. **Révocation** : après revoke, GET retourne `status=revoked` et `revoked_at` non null.

Commande gate minimale :

```bash
cd recyclique/api && python -m pytest tests/ -k "registered_device" -q
```

(Le DS créera `tests/test_registered_device*.py` ou équivalent ; préfixe URL via `settings.API_V1_STR.rstrip("/")` — pattern `test_cash_register_arch03.py`.)

## Definition of Done

- [x] Modèle `RegisteredDevice` + migration Alembic appliquée en tests SQLite/Postgres selon suite existante.
- [x] Service métier + schémas Pydantic + endpoints `/v1/registered-devices/` branchés dans `recyclic_api/api/api_v1/api.py`.
- [x] Contrat **`contracts/openapi/recyclique-api.yaml`** aligné (schémas + operationIds stables).
- [x] Tests listés en § Interprétation exécutable — **exit 0**.
- [x] Aucun code front Peintre, panel SuperAdmin, enrôlement, PIN, SW, cache offline métier.
- [x] Documentation inline (docstrings / description OpenAPI) rappelant : `device_id` ≠ caisse ≠ poste réception métier.
- [x] **Hors scope respecté** : pas de modification `sprint-status.yaml` / `epics.md` par le worker DS (writer unique).

## Tasks / Subtasks

- [x] **Modèle & migration** : `models/registered_device.py`, Alembic, export `__init__.py` (AC: modèle MVP `shared_workstation`).
- [x] **Schémas Pydantic** : `schemas/registered_device.py` — validation allowlist + device_type (AC: champs contractuels).
- [x] **Service** : `services/registered_device_service.py` — CRUD, revoke, validation site + module_key (AC: registre minimal).
- [x] **Endpoints** : `api/api_v1/endpoints/registered_devices.py` + enregistrement router (AC: API SuperAdmin).
- [x] **OpenAPI** : fusion dans `contracts/openapi/recyclique-api.yaml` (AC: contrat canonique).
- [x] **Tests** : suite `test_registered_device*` couvrant gates ci-dessus (AC: non-confusion + révocation).
- [x] **Revue périmètre** : grep qu’aucun fichier front / SW / enrollment n’a été ajouté par erreur.

## Dev Notes

### Ancres code (lire avant modification)

| Sujet | Chemins |
|--------|---------|
| Analogie registre admin | `models/cash_register.py`, `services/cash_register_service.py`, `schemas/cash_register.py`, `api/api_v1/endpoints/cash_registers.py` |
| OpenAPI caisse (pattern) | `contracts/openapi/recyclique-api.yaml` — `/v1/cash-registers/`, `CashRegisterV1Response` |
| Registre `module_key` | `modules/module_config/registry.py` |
| Config module / site | `models/site_module_config.py`, `modules/module_config/service.py` |
| Poste réception (≠ device) | `models/poste_reception.py` — session métier réception, **pas** identité poste partagé |
| Auth rôles | `core/auth.py` — `require_role_strict`, `UserRole.SUPER_ADMIN` |
| Router v1 | `api/api_v1/api.py` |
| Contexte existant (ne pas étendre ici) | `services/context_envelope_service.py` — story **27.2** |

### Proposition de statuts administratifs (décision locale — risque HITL faible)

Vocabulaire initial pour débloquer le DS ; affinage UX en **27.3** si besoin :

| `status` | Sémantique MVP |
|----------|----------------|
| `active` | Poste enregistré utilisable (sans enrôlement secret — 27.4). |
| `pending_enrollment` | Créé admin, pas encore enrôlé terrain. |
| `identity_lost` | Placeholder statut ADR ; transitions complètes en 27.4. |
| `conflict` | Placeholder conflit identité ; logique en 27.4. |
| `revoked` | Révoqué ; `revoked_at` renseigné. |

Si le DS est bloqué sur une transition interdite en 27.1 → **`NEEDS_HITL`** avec question précise (sinon appliquer le tableau).

### Allowlist vs module pilote Reception

- Le module pilote **Reception** n’est pas forcément présent dans `ACTIVE_MODULE_KEYS` aujourd’hui (registre = `kpi-live-banner`).
- **27.1** exige le **champ** allowlist + validation registre ; les tests peuvent utiliser **`kpi-live-banner`**.
- L’activation du `module_key` **reception** dans le registre est **hors scope 27.1** (story **27.7** / **27.8** ou ticket dédié) — ne pas inventer de clé non registrée sans HITL.

### Anti-patterns (interdits)

- Étendre `CashRegister` ou ajouter `device_id` sur `cash_registers`.
- Réutiliser `poste_reception.id` comme identifiant poste partagé.
- Introduire `workstation_id` comme second UUID technique concurrent.
- CRUD accessible aux rôles USER/ADMIN (réservé SuperAdmin pour le registre global).
- Implémenter le panel UI, l’enrôlement, le PIN, l’audit transversal, ou modifier `ContextEnvelope`.
- Service Worker, cache offline, persistance secret poste.

### Testing / gates (Story Runner)

| Gate | Commande / critère |
|------|-------------------|
| Tests ciblés | `cd recyclique/api && python -m pytest tests/ -k "registered_device" -q` → exit 0 |
| OpenAPI cohérent | Pas de drift manifeste schémas ↔ Pydantic (revue CR) |
| Non-régression | Sous-ensemble auth/admin existant si fichiers auth touchés |
| YAML sprint (parent) | `python -c "import yaml, pathlib; yaml.safe_load(...sprint-status.yaml...)"` — **lecture seule** pour CS ; pas de write CS |

`gates_skipped_with_hitl: false` — aucun skip pour authz / migrations / contrats.

### Project Structure Notes

- Backend : `recyclique/api/src/recyclic_api/` — pattern sync SQLAlchemy + FastAPI v1 (Epic 26 : pas de migration massive implicite vers repository).
- Contrats : `contracts/openapi/recyclique-api.yaml` — source unique fusion T-MOD-3.
- Front : **aucun** changement `peintre-nano/` dans cette story.

### References

- `_bmad-output/planning-artifacts/epics.md` — Epic 27, Story 27.1
- `references/artefacts/2026-05-29_02_mini-adr-postes-partages-pin-non-offline.md`
- `references/artefacts/2026-05-29_04_runbook-orchestration-epic-27-postes-partages-pin.md`
- `references/artefacts/2026-05-29_01_cadrage-postes-partages-pin-operateur.md`
- `references/config-modules-site-id/index.md`
- `references/config-modules-site-id/livrable-normatif-architecture.md`
- `references/protocole-modules-recyclique/18-MOD-config-modules-crosswalk.md`
- `_bmad-output/project-context.md`

## Trace Epic 27 — ADR

| Élément | Valeur |
|--------|--------|
| Nouvelle ADR structurante requise ? | **ADR N/A pour 27.1** — implémentation du modèle **`RegisteredDevice`** déjà tranché par mini-ADR 2026-05-29 et Epic 27. |
| ADR applicables | `references/artefacts/2026-05-29_02_mini-adr-postes-partages-pin-non-offline.md` (invariants) ; ne pas rouvrir ADR 25-2 offline/PWA. |

## Alignement sprint / YAML

- Clé **`27-1-registered-device`** : reste **`backlog`** dans `sprint-status.yaml` après CS (writer unique — **mise à jour `ready-for-dev` réservée au writer validé**, pas au worker CS).
- **`epic-27`** : statut sprint non modifié par ce worker CS.
- Prochaine story après clôture 27.1 : **`27-2-server-context-audit`** (ordre runbook §4).

## Risques / HITL

| Sujet | Statut | Action |
|-------|--------|--------|
| Vocabulaire exact des statuts admin | Risque epics | Proposition § Dev Notes ; Story Runner peut trancher localement. |
| Granularité « last contact » | Risque epics | `last_contact_at` TIMESTAMPTZ ; heartbeat différé stories ultérieures. |
| Timeout défaut (900 s) | Proposition | Ajustable en 27.9 ; documenter constante serveur. |
| Ajout `reception` au registre `module_key` | Hors 27.1 | Ne pas bloquer ; tests avec clé active existante. |

**NEEDS_STROPHE_HITL** : non requis pour démarrer le DS si le dev suit les propositions ci-dessus.

## Dev Agent Record

### Agent Model Used

Composer (worker bmad-dev-story DS)

### Debug Log References

- Gate : `pytest tests/ -k registered_device -q` → 12 passed, exit 0 (~200s)
- SQLite tests : table `registered_devices` ajoutée à `conftest.py` (`create_tables_if_not_exist`)

### Completion Notes List

- Modèle `RegisteredDevice` (table `registered_devices`), champs contractuels dont `device_id` exposé API (colonne `id`).
- CRUD SuperAdmin sur `/v1/registered-devices/` + `POST …/revoke` ; `Cache-Control: no-store`.
- Validation Pydantic : `device_type=shared_workstation` seul, allowlist via `is_active_module_key()`, statut `revoked` via revoke uniquement.
- Timeout défaut 900 s à la création si non fourni ; statut initial `pending_enrollment`.
- OpenAPI : schémas `RegisteredDeviceV1*` + 5 operationIds ; distinction documentée vs caisse / PosteReception.
- Tests `test_registered_device_epic27.py` : modèle/FK, CRUD, 403 non-SuperAdmin, allowlist, type MVP, non-confusion ids, révocation.

### File List

- `recyclique/api/src/recyclic_api/models/registered_device.py`
- `recyclique/api/src/recyclic_api/models/__init__.py`
- `recyclique/api/src/recyclic_api/schemas/registered_device.py`
- `recyclique/api/src/recyclic_api/services/registered_device_service.py`
- `recyclique/api/src/recyclic_api/api/api_v1/endpoints/registered_devices.py`
- `recyclique/api/src/recyclic_api/api/api_v1/endpoints/__init__.py`
- `recyclique/api/src/recyclic_api/api/api_v1/api.py`
- `recyclique/api/migrations/versions/s27_1_registered_devices.py`
- `recyclique/api/tests/test_registered_device_epic27.py`
- `recyclique/api/tests/conftest.py`
- `contracts/openapi/recyclique-api.yaml`
- `_bmad-output/implementation-artifacts/27-1-registered-device.md`

## Change Log

- 2026-05-30 — Story 27.1 DS : registre `RegisteredDevice`, API SuperAdmin, OpenAPI, tests gate.
