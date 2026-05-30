# Story 27.2 : Contexte serveur poste partagé et audit transversal

Status: review

**Story key :** `27-2-server-context-audit`  
**Epic :** 27 — Postes partagés enrôlés + PIN opérateur + PWA installable non-offline  
**Implementation artifact :** `_bmad-output/implementation-artifacts/27-2-server-context-audit.md`  
**Date CS :** 2026-05-30

## Dépendances (prérequis)

- **Story 27.1 done** : modèle `RegisteredDevice`, API `/v1/registered-devices/`, `device_id` canonique — `_bmad-output/implementation-artifacts/27-1-registered-device.md`.
- **Epic 27 — cadrage gelé** : `_bmad-output/planning-artifacts/epics.md` (§ Epic 27, Story 27.2).
- **Mini-ADR Epic 27** : `references/artefacts/2026-05-29_02_mini-adr-postes-partages-pin-non-offline.md` — invariants serveur, vocabulaire `device_id`, audit transversal, exclusions offline / front authz.
- **Runbook orchestration** : `references/artefacts/2026-05-29_04_runbook-orchestration-epic-27-postes-partages-pin.md` — ordre stories, gates transverses, règles produit non négociables (§7).
- **Spec multi-contextes v2** : `references/artefacts/2026-04-02_03_spec-multi-contextes-invariants-autorisation-v2.md` — recalcul explicite, zéro fuite, step-up distinct de l’affichage (§3–§6).
- **Registre `module_key`** : `recyclique/api/src/recyclic_api/modules/module_config/registry.py` ; pack normatif `references/config-modules-site-id/index.md`.
- **Socle audit existant** : `recyclique/api/src/recyclic_api/core/audit.py` (`log_audit`, `sanitize_audit_details`, `merge_critical_audit_fields`) ; `recyclique/api/docs/story-2-5-epic8-audit-foundations.md`.
- **ContextEnvelope existant** : `recyclique/api/src/recyclic_api/services/context_envelope_service.py`, `schemas/context_envelope.py`, `contracts/openapi/recyclique-api.yaml` (`ContextEnvelope`, `ExploitationContextIds`).
- **Garde contexte client (pattern)** : `recyclique/api/src/recyclic_api/core/context_binding_guard.py` (Story 25.8 — `CONTEXT_STALE`, en-têtes optionnels).
- **Stories suivantes (ne pas implémenter ici)** : 27.3 (panel SuperAdmin UI), 27.4 (enrôlement / secret local), 27.5 (PWA), 27.6 (lock screen PIN + endpoints PIN), 27.7 (intersection modules), 27.10 (override SuperAdmin complet).

## Garde-fous ADR / runbook (obligatoires pour le DS)

| Invariant | Application story 27.2 |
|-----------|-------------------------|
| Pas d’offline métier | Aucun cache SW, file locale, sync différée ; contexte poste = vérité serveur uniquement. |
| Pas d’authz front | Refus à la frontière API ; le front ne décide jamais seul de l’opérateur actif ni du `module_key` effectif. |
| Invariant serveur documenté | Tuple **`site_id + device_id + operator_user_id + module_key + override`** — source autoritaire pour poste partagé. |
| Refus sans opérateur actif | Aucune donnée métier ni action métier sur routes « poste partagé » sans `operator_user_id` actif côté serveur. |
| Recalcul / refus sur changement | Changement poste, opérateur, site, module, droits ou override → invalidation ou recalcul explicite ; pas de continuation silencieuse. |
| Audit socle existant | Réutiliser `audit_logs` + helpers ; **pas** de second journal. |
| Pas de PIN en audit / logs | `sanitize_audit_details` + revue grep : aucun PIN ni dérivé (`pin`, `step_up_pin`, hash PIN, etc.). |
| `device_id` canonique | Distinct de `cash_register_id` et de `reception_post_id` (poste réception métier). |
| Évolution ContextEnvelope | Alignement / extension champs optionnels — **pas** redéfinition OpenAPI complète hors besoin story. |
| Pas de lock screen UI | Aucun écran Peintre, aucun composant verrouillage — story **27.6**. |
| Pas de vérification PIN publique | Pas d’endpoint `POST /auth/pin` poste partagé ni rate-limit PIN terrain — story **27.6** ; 27.2 pose le **modèle de session opérateur** et les **guards** testables. |
| Pas d’intersection modules | Calcul `site config × allowlist poste × permissions opérateur` — story **27.7**. |
| Pas d’override SuperAdmin UI | Flag serveur `override` préparé ; flux complet — story **27.10**. |

## Story (BDD)

As a **security owner**,  
I want the **shared workstation and active PIN operator represented in the server authorization context and audit trail**,  
So that **every business action is denied or attributed by backend authority, not by UI projection**.

## Acceptance criteria

Source normative : `_bmad-output/planning-artifacts/epics.md` — **Story 27.2**.

**Given** `ContextEnvelope` remains an evolving alignment target, not a fully redefined contract in this story  
**When** this story is delivered  
**Then** the server invariant is documented or implemented around `site_id + device_id + operator_user_id + module_key + override`  
**And** authorization controls are applied at the API boundary, not only in the UI projection  
**And** no active PIN operator means default refusal for business data and business actions  
**And** changes of workstation, operator, site, module, rights or override trigger explicit server-side recalculation or refusal  
**And** audit uses the existing `audit_logs` / audit helpers instead of a second journal  
**And** no PIN or PIN derivative is stored in logs or audit details

### Interprétation exécutable

#### 1. Invariant serveur `SharedWorkstationContext`

Introduire un objet / schéma interne **`SharedWorkstationContext`** (nom suggéré — service dédié) matérialisant le tuple :

| Champ | Source / règle |
|-------|----------------|
| `site_id` | `RegisteredDevice.site_id` (poste enrôlé) — refus si device révoqué / inconnu. |
| `device_id` | UUID canonique `RegisteredDevice.id` — jamais confondu avec caisse ou poste réception métier. |
| `operator_user_id` | Session opérateur active sur ce `device_id` (voir §2) ; **`null` ⇒ refus par défaut** sur routes protégées. |
| `module_key` | Module courant de la session opérateur (string registre `is_active_module_key`) ; peut être `null` si pas de session active. |
| `override` | Booléen état serveur explicite (SuperAdmin override) — **MVP 27.2** : champ + sémantique documentée ; activation produit complète en **27.10**. |

États runtime suggérés (alignés spec 1.3 §4.2, réutiliser ou étendre `ContextRuntimeState` si pertinent) :

- **`ok`** : device actif + opérateur actif + cohérence site/device.
- **`forbidden`** : device révoqué / inconnu, ou route exige opérateur absent.
- **`degraded`** : réservé si contexte partiel documenté (ex. device connu sans `module_key` — éviter si ambigu ; préférer `forbidden` pour données métier).

Documenter l’invariant dans le module service (docstring module-level) **et** en commentaire OpenAPI sur les champs ajoutés.

#### 2. Persistance session opérateur poste (préparation PIN — sans UI)

Créer une table dédiée (nom suggéré : **`device_operator_sessions`**) — **ne pas** réutiliser `user_sessions` web ni `cash_sessions` :

| Champ (concept) | Colonne / type suggéré | Règles |
|-----------------|------------------------|--------|
| Identifiant | `id` UUID PK | |
| Poste | `device_id` UUID FK → `registered_devices.id` NOT NULL | Index ; cohérence type `shared_workstation`. |
| Opérateur | `operator_user_id` UUID FK → `users.id` NOT NULL | Distinct du compte « technique » web si applicable. |
| Site dénormalisé | `site_id` UUID FK → `sites.id` NOT NULL | Doit matcher `RegisteredDevice.site_id` à la création. |
| Module courant | `active_module_key` VARCHAR(64) NULL | Validé via `is_active_module_key()` quand renseigné. |
| Override | `override_active` BOOLEAN NOT NULL default `false` | Préparation 27.10. |
| Statut | `status` VARCHAR(32) NOT NULL | Proposition : `active`, `ended`, `superseded`, `invalidated`. |
| Horodatage | `started_at`, `ended_at`, `last_activity_at` TIMESTAMPTZ | `last_activity_at` mis à jour par le service (timeout complet en **27.9**). |

**Règle MVP 27.2** : au plus **une** session `active` par `device_id` (contrainte applicative + test ; index partiel unique optionnel si migration le permet).

**Création / fin de session en 27.2** :

- Exposer un **service interne** (`DeviceOperatorSessionService`) : `start_session(...)`, `end_session(...)`, `get_active_for_device(...)`, `invalidate_on_device_or_operator_change(...)`.
- **Pas** d’endpoint public PIN en 27.2 — les tests utilisent le service directement ou une fixture DB (pattern `test_registered_device_epic27.py`).
- Documenter clairement que **27.6** branchera la vérification PIN sur `start_session`.

#### 3. Service de résolution et garde API

Nouveau module suggéré : `services/shared_workstation_context_service.py` (+ éventuellement `core/shared_workstation_guard.py`).

Responsabilités :

1. **`resolve_shared_workstation_context(db, *, device_id, ...) -> SharedWorkstationContextResult`** — lit `RegisteredDevice` + session active ; retourne état + message restriction.
2. **`require_active_operator_context(...)`** — dependency FastAPI : lève **403** (code stable ex. `SHARED_WORKSTATION_OPERATOR_REQUIRED`) si pas d’opérateur actif.
3. **`assert_context_fresh(...)`** — sur changement détecté (device révoqué, session `superseded`, site device ≠ session, etc.) : lève **409** `CONTEXT_STALE` (réutiliser `CONTEXT_STALE_CODE` de `context_binding_guard.py` ou code dédié documenté).
4. **`invalidate_sessions_for_device / operator / site_change`** — recalcul explicite ; fin de session + audit.

En-têtes client (évolution 25.8 — **optionnels en 27.2**, obligatoires à documenter pour stories ultérieures) :

| En-tête | Rôle |
|---------|------|
| `X-Recyclique-Device-Id` | UUID poste partagé annoncé par le client — si présent, comparer à la vérité serveur. |
| `X-Recyclique-Context-Module-Key` | Module annoncé — si présent avec session active, doit matcher `active_module_key`. |

Ne **pas** accepter `operator_user_id` depuis un en-tête client non signé comme vérité — l’opérateur vient de la **session serveur** liée au device (secret device = **27.4** ; en 27.2 tests via service interne).

#### 4. Évolution `ContextEnvelope` (alignement contrat)

Étendre **`ExploitationContextIdsOut`** / schéma OpenAPI **`ExploitationContextIds`** avec champs **optionnels** (rétrocompat) :

```yaml
# Proposition — fusion dans recyclique-api.yaml uniquement
device_id: string | null
operator_user_id: string | null
module_key: string | null
override_active: boolean | null  # ou shared_workstation_override — figer un nom stable OpenAPI
```

Adapter **`build_context_envelope`** :

- Par défaut (utilisateur web classique, pas de device) : nouveaux champs **`null`** / absents — comportement actuel inchangé.
- Si requête inclut contexte poste partagé (param query `device_id` sur refresh **ou** en-tête `X-Recyclique-Device-Id` sur `GET/POST .../context`) : fusionner résolution `SharedWorkstationContext` dans l’enveloppe retournée.
- **`permission_keys`** : ne **pas** recalculer l’intersection module 27.7 — conserver le calcul utilisateur existant ; documenter que le filtrage module poste arrive en **27.7**.

Endpoints existants à aligner (évolution minimale) :

- `GET /v1/users/me/context` (`recyclique_users_getContextEnvelope`)
- `POST /v1/users/me/context/refresh` (`recyclique_users_refreshContextEnvelope`)

Documenter dans OpenAPI : champs poste partagé = **Story 27.2** ; intersection effective = **Story 27.7**.

#### 5. Audit transversal (extension socle)

**Étendre `merge_critical_audit_fields`** (`core/audit.py`) avec paramètres optionnels :

- `device_id: Optional[str] = None`
- `module_key: Optional[str] = None`
- `override_active: Optional[bool] = None`

Conserver la sémantique **`operator_user_id`** vs **`user_id`** (Story 25.13) : sur poste partagé, `operator_user_id` = opérateur PIN actif ; `user_id` = acteur JWT si différent (ex. admin technique — rare en 27.2).

**Nouveaux `AuditActionType`** (enum `models/audit_log.py`) — proposition minimale :

| Valeur enum | Quand |
|-------------|--------|
| `SHARED_WORKSTATION_ACCESS_REFUSED` | Refus API sans opérateur actif ou device invalide. |
| `SHARED_WORKSTATION_CONTEXT_INVALIDATED` | Recalcul / fin session suite changement poste, opérateur, site, module, droits. |
| `DEVICE_OPERATOR_SESSION_STARTED` | Création session via service (tests + futur PIN 27.6). |
| `DEVICE_OPERATOR_SESSION_ENDED` | Fin explicite ou invalidation. |

Chaque événement passe par **`log_audit`** + **`sanitize_audit_details`** sur `details_json`.

Champs `details_json` recommandés (via merge) : `request_id`, `operation`, `outcome`, `site_id`, `device_id`, `operator_user_id`, `module_key`, `override_active`.

**Interdit** : stocker PIN, hash PIN, `step_up_pin`, secret device, ou tout champ dont la clé matche `_SENSITIVE_KEY_SUBSTRINGS`.

#### 6. Preuve sur route(s) de référence (sans généraliser tout le backend)

Brancher la garde **`require_active_operator_context`** sur **au moins une** route authentifiée « métier poste partagé » — proposition :

- Nouveau endpoint minimal **`GET /v1/shared-workstation/context`** (lecture contexte résolu pour le device courant) **ou**
- Extension d’un endpoint existant documenté comme slice pilote (ex. futur reception — **ne pas** activer reception si hors registre ; préférer endpoint dédié Epic 27).

Comportement attendu :

| Cas | HTTP | Audit |
|-----|------|-------|
| Device inconnu / révoqué | 404 / 403 | `SHARED_WORKSTATION_ACCESS_REFUSED` |
| Device OK, pas de session opérateur | 403 `SHARED_WORKSTATION_OPERATOR_REQUIRED` | idem |
| Session active, device OK | 200 + corps contexte | pas de refus |
| En-tête device/module désaligné | 409 `CONTEXT_STALE` | `SHARED_WORKSTATION_CONTEXT_INVALIDATED` ou refus |
| Invalidation après changement device site | 409 / 403 après recalcul | invalidation auditée |

**Ne pas** modifier en masse les routes caisse / réception brownfield dans cette story.

#### 7. Tests obligatoires (gates story)

Depuis `recyclique/api` :

1. **Session opérateur** : start → get_active → end ; une seule session active par device.
2. **Refus sans opérateur** : route de référence retourne 403 ; audit `SHARED_WORKSTATION_ACCESS_REFUSED` avec `device_id`, sans PIN dans details.
3. **Recalcul / refus changement** : révoquer device ou changer `site_id` device invalide session → 409/403 ; audit invalidation.
4. **ContextEnvelope** : GET context avec device en session → champs `device_id` / `operator_user_id` présents ; sans device → champs null (non-régression).
5. **`merge_critical_audit_fields`** : test unitaire champs `device_id`, `module_key`, `override_active`.
6. **Sanitize PIN** : test qu’un detail `{ "pin": "1234" }` est `[REDACTED]` sur log audit poste partagé.
7. **Non-confusion ids** : `device_id` ≠ `cash_register_id` dans assertions audit et enveloppe.

Commande gate minimale :

```bash
cd recyclique/api && python -m pytest tests/ -k "shared_workstation or device_operator or epic27_2" -q
```

(Le DS créera `tests/test_story_27_2_shared_workstation_context.py` ou équivalent — convention BMAD `test_story_{epic}_{story}_*.py`.)

## Definition of Done

- [x] Modèle `DeviceOperatorSession` (ou nom retenu) + migration Alembic réversible.
- [x] Service résolution `SharedWorkstationContext` + garde FastAPI documentée.
- [x] Extension `ExploitationContextIds` / `build_context_envelope` + OpenAPI aligné (champs optionnels, rétrocompat).
- [x] Extension `merge_critical_audit_fields` + nouveaux `AuditActionType` Epic 27.
- [x] Route(s) de référence protégée(s) prouvant refus sans opérateur et recalcul.
- [x] Tests § Interprétation exécutable — **exit 0**.
- [x] Aucun lock screen UI, endpoint PIN public, intersection modules, panel SuperAdmin, enrôlement, PWA, override complet.
- [x] Revue grep : aucun PIN en clair dans logs/audit ; `sanitize_audit_details` appliqué sur chemins audit poste partagé.
- [x] **Hors scope respecté** : pas de modification `sprint-status.yaml` / `epics.md` par le worker DS (writer unique).

## Tasks / Subtasks

- [x] **Modèle & migration session opérateur** : table `device_operator_sessions`, FK device/user/site (AC: persistance session active).
- [x] **Service session** : `DeviceOperatorSessionService` — start/end/get_active/invalidate (AC: une session active par device).
- [x] **Service contexte poste** : `SharedWorkstationContextService` — resolve + états runtime (AC: invariant tuple serveur).
- [x] **Garde API** : dependency `require_active_operator_context` + binding en-têtes device/module (AC: refus frontière API).
- [x] **ContextEnvelope** : étendre schémas Pydantic + `build_context_envelope` + OpenAPI (AC: alignement évolutif).
- [x] **Audit** : étendre `merge_critical_audit_fields`, enum `AuditActionType`, helpers log refus/invalidation (AC: audit socle, pas de PIN).
- [x] **Endpoint référence** : `GET /v1/shared-workstation/context` (ou équivalent documenté) + router v1 (AC: preuve refus/recalcul).
- [x] **Tests** : suite `test_story_27_2_*` / `test_device_operator*` couvrant gates ci-dessus (AC: non-régression + sanitize PIN).
- [x] **Revue périmètre** : grep qu’aucun fichier front / PIN endpoint / intersection modules n’a été ajouté par erreur.

## Dev Notes

### Intelligence story 27.1 (patterns établis)

| Élément 27.1 | Réutilisation 27.2 |
|--------------|-------------------|
| `RegisteredDevice` + `device_id` API | Ancrage `site_id`, statut device, allowlist (lecture seule en 27.2 — intersection en 27.7). |
| `RegisteredDeviceService.get_required` | Valider device avant résolution contexte. |
| Tests SQLite + `conftest.py` tables | Ajouter `device_operator_sessions` à `create_tables_if_not_exist`. |
| OpenAPI fusion `recyclique-api.yaml` | Même règle — pas de YAML standalone. |
| `Cache-Control: no-store` | Sur endpoints poste partagé authentifiés. |
| Statuts device `revoked` | Doit invalider sessions actives + refuser contexte. |

### Ancres code (lire avant modification)

| Sujet | Chemins |
|--------|---------|
| Registre poste 27.1 | `models/registered_device.py`, `services/registered_device_service.py` |
| ContextEnvelope actuel | `services/context_envelope_service.py`, `schemas/context_envelope.py` |
| OpenAPI ContextEnvelope | `contracts/openapi/recyclique-api.yaml` — `ContextEnvelope`, `ExploitationContextIds` |
| Audit socle | `core/audit.py`, `models/audit_log.py`, `tests/test_audit_story_25.py` |
| Garde contexte stale | `core/context_binding_guard.py`, `tests/test_context_stale_story25_8.py` |
| Step-up PIN (distinct) | `core/step_up.py` — step-up mutation **≠** session opérateur poste ; ne pas fusionner les deux mécanismes. |
| Registre module_key | `modules/module_config/registry.py` |
| Router v1 | `api/api_v1/api.py` |
| Enveloppe erreur AR21 | Pattern `detail={"code": "...", "message": "..."}` + `correlation_id` |

### Distinction concepts (anti-confusion LLM)

| Concept | Identifiant | Story |
|---------|-------------|-------|
| Poste partagé enrôlé | `device_id` (`RegisteredDevice`) | 27.1+ |
| Caisse / registre encaissement | `cash_register_id` | brownfield |
| Poste réception métier (flux matière) | `reception_post_id` | brownfield |
| Session opérateur PIN poste | `device_operator_sessions` | 27.2 (persist), 27.6 (PIN UI) |
| Step-up PIN mutation sensible | en-tête `X-Step-Up-Pin` | 2.4 / 25.14 |
| Session web cookies | `user_sessions` | auth web |

### Mapping `operator_user_id` vs `user_id` (risque epics — tranchage local)

- **`operator_user_id`** : personne ayant pris le poste via session PIN active (bénévole terrain).
- **`user_id` / `actor_id` audit** : compte authentifié sur la requête HTTP (JWT) — peut coïncider avec l’opérateur ; si diverge (cas admin futur), les deux champs doivent apparaître dans `details_json`.
- **`merge_critical_audit_fields`** : conserver `resolved_operator = operator_user_id or user_id` pour rétrocompat caisse.

### Proposition codes erreur stables

| Code | HTTP | Usage |
|------|------|-------|
| `SHARED_WORKSTATION_OPERATOR_REQUIRED` | 403 | Device valide mais aucune session opérateur active. |
| `SHARED_WORKSTATION_DEVICE_INVALID` | 403 / 404 | Device révoqué, inconnu ou type incorrect. |
| `CONTEXT_STALE` | 409 | Désalignement en-têtes / contexte invalidé (réutiliser 25.8). |

### Anti-patterns (interdits)

- Décider l’opérateur actif depuis le body JSON client ou `localStorage`.
- Créer une table `audit_logs_shared_workstation` parallèle.
- Logger le PIN ou le hash PIN en clair ou dans `description` audit.
- Réutiliser `cash_registers.id` ou `poste_reception.id` comme `device_id`.
- Implémenter lock screen, PWA, panel SuperAdmin, enrôlement secret, endpoints PIN publics.
- Recâbler toutes les routes caisse/réception — slice de référence uniquement.
- Calculer l’intersection modules effective (27.7) ou activer override SuperAdmin complet (27.10).
- Casser les tests ContextEnvelope existants (champs optionnels null par défaut).

### Testing / gates (Story Runner)

| Gate | Commande / critère |
|------|-------------------|
| Tests ciblés | `cd recyclique/api && python -m pytest tests/test_story_27_2_shared_workstation_context.py -q` → exit 0 ; peloton élargi : `-k "shared_workstation or device_operator or epic27_2"` |
| Audit PIN | `pytest tests/test_audit_story_25.py -q` + tests Epic 27 sanitize |
| OpenAPI cohérent | Schémas `ExploitationContextIds` ↔ Pydantic ; pas de drift operationIds existants |
| Non-régression contexte | `pytest tests/test_context_stale_story25_8.py -q` si garde touchée |
| YAML sprint (parent) | lecture seule — pas de write CS |

`gates_skipped_with_hitl: false` — aucun skip pour authz / audit / migrations / contrats.

### Project Structure Notes

- Backend : `recyclique/api/src/recyclic_api/` — pattern sync SQLAlchemy + FastAPI v1.
- Contrats : `contracts/openapi/recyclique-api.yaml` — source unique.
- Front : **aucun** changement `peintre-nano/` dans cette story.

### References

- `_bmad-output/planning-artifacts/epics.md` — Epic 27, Story 27.2
- `_bmad-output/implementation-artifacts/27-1-registered-device.md` — prérequis done
- `references/artefacts/2026-05-29_02_mini-adr-postes-partages-pin-non-offline.md`
- `references/artefacts/2026-05-29_04_runbook-orchestration-epic-27-postes-partages-pin.md`
- `references/artefacts/2026-04-02_03_spec-multi-contextes-invariants-autorisation-v2.md`
- `references/config-modules-site-id/index.md`
- `recyclique/api/docs/story-2-5-epic8-audit-foundations.md`
- `_bmad-output/project-context.md`

## Trace Epic 27 — ADR

| Élément | Valeur |
|--------|--------|
| Nouvelle ADR structurante requise ? | **ADR N/A pour 27.2** — extension du mini-ADR 2026-05-29 et spec multi-contextes ; pas de rouvrir ADR 25-2 offline/PWA. |
| ADR applicables | Mini-ADR postes partagés (invariants + audit) ; spec 1.3 (recalcul contexte). |

## Alignement sprint / YAML

- Clé **`27-2-server-context-audit`** : reste **`backlog`** dans `sprint-status.yaml` après CS (writer unique — **mise à jour `ready-for-dev` réservée au writer validé**, pas au worker CS).
- **`epic-27`** : statut sprint non modifié par ce worker CS.
- Prochaine story après clôture 27.2 : **`27-3-superadmin-device-management`** (ordre runbook §4).

## Risques / HITL

| Sujet | Statut | Action |
|-------|--------|--------|
| Mapping `operator_user_id` vs `user_id` audit | Risque epics | Tranchage § Dev Notes ; documenter dans tests audit. |
| Nom OpenAPI champ override | Proposition | `override_active` bool ; figer dans OpenAPI description. |
| Endpoint référence vs réutiliser route existante | Proposition | `GET /v1/shared-workstation/context` dédié — évite toucher caisse/réception. |
| Paramètre `device_id` sur refresh enveloppe vs en-tête seul | Proposition | Les deux documentés ; en-tête prioritaire si présent. |
| Contrainte DB une session active / device | Proposition | Applicative + test ; index unique partiel si Postgres migration OK. |

**NEEDS_STROPHE_HITL** : non requis pour démarrer le DS si le dev suit les propositions ci-dessus.

## Dev Agent Record

### Agent Model Used

Composer (bmad-dev-story worker DS — post-CR1 cr_loop=1)

### Debug Log References

- Import circulaire `registered_device_service` ↔ `shared_workstation_context_service` résolu par imports lazy dans revoke/update.
- Post-CR1 : `RegisteredDeviceUpdate` Pydantic bloque toujours `status=revoked` à la frontière HTTP (422 → POST `/revoke` préféré) ; test invalidation via `model_construct` sur le service.

### Completion Notes List

- Modèle `DeviceOperatorSession` + migration `s27_2_device_operator_sessions`.
- Services `DeviceOperatorSessionService` et `SharedWorkstationContextService` avec invariant tuple documenté.
- Garde `require_active_operator_context` + en-têtes device/module.
- Extension `ExploitationContextIdsOut`, `build_context_envelope(device_id=...)`, endpoints users context/refresh.
- Audit : 4 `AuditActionType` Epic 27, helpers refus/invalidation/session, `merge_critical_audit_fields` étendu.
- Route pilote `GET /v1/shared-workstation/context` avec `Cache-Control: no-store`.
- Invalidation sessions sur révocation device (`revoke`) et changement `site_id`.
- **Post-CR1 (CR-27.2-M1)** : `RegisteredDeviceService.update()` pose `revoked_at` + `invalidate_sessions_for_device(reason="device_revoked")` si `status=revoked`.
- **Post-CR1 (CR-27.2-M2)** : `_require_active_device` et `resolve_shared_workstation_context` exigent `device.status == active`.
- 20 tests `test_story_27_2_shared_workstation_context.py` — gate exit 0.

### File List

- recyclique/api/src/recyclic_api/models/device_operator_session.py
- recyclique/api/migrations/versions/s27_2_device_operator_sessions.py
- recyclique/api/src/recyclic_api/schemas/shared_workstation_context.py
- recyclique/api/src/recyclic_api/schemas/context_envelope.py
- recyclique/api/src/recyclic_api/services/device_operator_session_service.py
- recyclique/api/src/recyclic_api/services/shared_workstation_context_service.py
- recyclique/api/src/recyclic_api/services/context_envelope_service.py
- recyclique/api/src/recyclic_api/services/registered_device_service.py
- recyclique/api/src/recyclic_api/core/shared_workstation_guard.py
- recyclique/api/src/recyclic_api/core/audit.py
- recyclique/api/src/recyclic_api/models/audit_log.py
- recyclique/api/src/recyclic_api/models/__init__.py
- recyclique/api/src/recyclic_api/api/api_v1/endpoints/shared_workstation.py
- recyclique/api/src/recyclic_api/api/api_v1/endpoints/users.py
- recyclique/api/src/recyclic_api/api/api_v1/endpoints/__init__.py
- recyclique/api/src/recyclic_api/api/api_v1/api.py
- recyclique/api/tests/test_story_27_2_shared_workstation_context.py
- recyclique/api/tests/conftest.py
- contracts/openapi/recyclique-api.yaml

## Change Log

- 2026-05-30 — Story 27.2 CS (create, refresh) : contexte serveur poste partagé, session opérateur, audit transversal, évolution ContextEnvelope ; Status `ready-for-dev` ; sprint-status inchangé (writer unique).
- 2026-05-30 — Story 27.2 DS : implémentation backend + tests gate story_27_2 (20 passed).
- 2026-05-30 — Story 27.2 post-CR1 : invalidation sessions sur update(status=revoked), garde device active-only, +1 test.
- 2026-05-30 — Story 27.2 DS reprise : validation gate story_27_2 exit 0 ; Status `review`.
