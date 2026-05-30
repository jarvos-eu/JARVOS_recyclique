# Story 27.10 : Override SuperAdmin explicite et audite

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->
<!-- Ultimate context engine analysis completed — comprehensive developer guide created (CS 2026-05-30). -->

**Story key :** `27-10-superadmin-override`  
**Epic :** 27 — Postes partagés enrôlés + PIN opérateur + PWA installable non-offline  
**Implementation artifact :** `_bmad-output/implementation-artifacts/27-10-superadmin-override.md`  
**Date CS :** 2026-05-30

## Dépendances (prérequis)

- **Stories 27.1–27.9 done** : registre `RegisteredDevice`, contexte serveur + garde `require_active_operator_context`, panel SuperAdmin, enrôlement credential device, PWA non-offline, lock screen PIN + session opérateur, intersection modules serveur, brouillons Reception pilote, timeout / passer la main — fichiers `_bmad-output/implementation-artifacts/27-1-registered-device.md` … `27-9-timeout-lock-handoff.md`.
- **Story 27.2 (champ préparé)** : colonne `device_operator_sessions.override_active`, tuple autoritaire `site_id + device_id + operator_user_id + module_key + override_active`, `merge_critical_audit_fields(override_active=…)` — `_bmad-output/implementation-artifacts/27-2-server-context-audit.md`.
- **Story 27.3 (SuperAdmin panel)** : garde `UserRole.SUPER_ADMIN`, pattern admin Peintre — `_bmad-output/implementation-artifacts/27-3-superadmin-device-management.md`.
- **Story 27.6 (PIN / session)** : `verify_and_start_session` appelle `start_session` **sans** `override_active` (défaut `false`) — `_bmad-output/implementation-artifacts/27-6-pin-lock-operator-session.md`.
- **Story 27.7 (intersection)** : formule effective modules ; commentaire « pas d'élargissement implicite » — `_bmad-output/implementation-artifacts/27-7-server-module-intersection.md` ; **27.10 implémente** la règle d'élargissement explicite quand `override_active=true`.
- **Story 27.9 (sortie override)** : `end_active_session_for_device` / timeout / lock terminent la session (et donc l'override) — `_bmad-output/implementation-artifacts/27-9-timeout-lock-handoff.md`.
- **Epic 27 — cadrage gelé** : `_bmad-output/planning-artifacts/epics.md` (§ Epic 27, Story 27.10).
- **Mini-ADR Epic 27** : `references/artefacts/2026-05-29_02_mini-adr-postes-partages-pin-non-offline.md` — § Audit (override SuperAdmin), § Conséquences (état serveur explicite, TTL/sortie claire, jamais implicite après PIN).
- **Cadrage produit** : `references/artefacts/2026-05-29_01_cadrage-postes-partages-pin-operateur.md` — §3.13 (override explicite, confirmation forte, sortie verrouillage/timeout/bouton).
- **Runbook orchestration** : `references/artefacts/2026-05-29_04_runbook-orchestration-epic-27-postes-partages-pin.md` — ordre §4 (27.10 dernière story), invariants §7 (pas d'override implicite), gates §8.
- **Contrat OpenAPI** : `contracts/openapi/recyclique-api.yaml` — champ `override_active` déjà présent sur `ContextEnvelope` / `SharedWorkstationContextV1Response` ; **cette story étend** le contrat (activate/deactivate + statut session enrichi).
- **Dernière story Epic 27** : après clôture 27.10, l'Epic 27 atteint sa DoD globale (`epics.md` § Epic 27).

## Garde-fous ADR / runbook (obligatoires pour le DS)

| Invariant | Application story 27.10 |
|-----------|-------------------------|
| État serveur explicite | `override_active` est persisté sur `DeviceOperatorSession` (PostgreSQL), propagé dans `SharedWorkstationContext`, `ContextEnvelope`, statut session — **jamais** un flag React / `localStorage` / Zustand seul. |
| Jamais automatique après PIN | `SharedWorkstationOperatorPinService.verify_and_start_session` **ne doit pas** passer `override_active=True` ; test de non-régression obligatoire. |
| Action explicite + confirmation forte | Activation via endpoint dédié + **re-saisie PIN** de l'opérateur SuperAdmin actif (step-up terrain) ; pas de toggle silencieux. |
| SuperAdmin identifié | Seul un `User` avec `UserRole.SUPER_ADMIN` **et** session opérateur active sur le poste peut activer l'override. |
| Sortie claire | Trois chemins : bouton « Quitter override », TTL serveur (proposé), timeout/lock/handoff 27.9 (fin session → `override_active` disparaît). |
| Timeout/lock sort de l'override | `end_session` / `end_active_session_for_device` avec raison `timeout|manual_lock|handoff` termine la session entière ; audit de fin inclut `override_active` si actif. |
| Autorité API | Élargissement intersection **uniquement** quand `override_active=true` côté serveur ; refus 403 si action hors périmètre override valide. |
| Pas authz front | Le bandeau UI est une projection ; toute route sensible revalide `override_active` via garde serveur. |
| Visibilité UI override | **Ne pas** déduire SuperAdmin depuis le JWT web / `ContextEnvelope.permission_keys` seul — l'opérateur actif est celui de la **session PIN** (`operator_user_id`). Exposer `can_activate_super_admin_override` (bool) sur `GET …/operator-session/status` ; le front l'utilise uniquement pour afficher/masquer les contrôles (projection serveur, pas décision authz). |
| Audit transversal | Activation, refus d'activation, désactivation (explicite ou TTL), usage (via `merge_critical_audit_fields`) — **pas** de PIN en `details_json`. |
| Pas offline | Endpoints override `Cache-Control: no-store` ; client `cache: 'no-store'`. |
| Distinction poste personnel vs partagé | Override **uniquement** sur poste partagé enrôlé (`shared_workstation`) avec session PIN active — pas sur session web SuperAdmin classique sans poste. |
| `device_id` canonique | Inchangé — distinct de `cash_register_id` / `reception_post_id`. |

## Story (BDD)

As a **SuperAdmin**,  
I want an **explicit audited override on a shared workstation**,  
So that **I can intervene without silently bypassing workstation constraints**.

## Acceptance criteria

Source normative : `_bmad-output/planning-artifacts/epics.md` — **Story 27.10**.

**Given** a SuperAdmin is identified on a shared workstation context  
**When** override is needed  
**Then** override is activated by an explicit action with strong confirmation or revalidation  
**And** override is represented as an explicit server-side context state  
**And** override is never a simple UI flag  
**And** override is never automatic after PIN  
**And** override has a clear exit path  
**And** timeout or lock exits override  
**And** override activation, use and exit are audited  
**And** actions outside valid override are refused by the API boundary

### Interprétation exécutable

#### 1. Sémantique produit — ce que l'override autorise (MVP)

L'override **n'est pas** un bypass total du poste partagé. Il élargit **uniquement** la composante « permissions opérateur » de l'intersection 27.7, tout en conservant :

- la **config module site** (`is_site_module_enabled`) ;
- l'**allowlist poste** (`RegisteredDevice.allowed_module_keys`).

Formule effective quand `override_active=true` **et** `operator.role == SUPER_ADMIN` :

```text
effective(module_key) =
  is_site_module_enabled(site_id, module_key)
  AND module_key ∈ device.allowed_module_keys
  [SKIP operator_has_required_permissions]
```

Quand `override_active=false` : formule 27.7 inchangée.

**Actions « hors override valide »** (refus API 403) :

| Cas | Code stable suggéré |
|-----|---------------------|
| Activation override sans session opérateur active | `SHARED_WORKSTATION_OPERATOR_REQUIRED` |
| Activation par non-SuperAdmin | `SHARED_WORKSTATION_OVERRIDE_FORBIDDEN` |
| Confirmation PIN incorrecte | `SHARED_WORKSTATION_OVERRIDE_CONFIRMATION_FAILED` (message neutre) |
| Mutation sensible nécessitant override mais `override_active=false` | `SHARED_WORKSTATION_OVERRIDE_REQUIRED` |
| Module hors allowlist poste **même en override** | `SHARED_WORKSTATION_MODULE_FORBIDDEN` |
| Override TTL expiré | `SHARED_WORKSTATION_OVERRIDE_EXPIRED` (+ auto-désactivation serveur) |

**Route probe dédiée override (preuve frontière API)** : étendre ou ajouter un endpoint de test (pattern `probe-module/{module_key}` 27.7) acceptant un header/query `require_override=true` pour valider le refus sans override.

#### 2. Persistance — colonne TTL optionnelle

Migration Alembic suggérée : `s27_10_superadmin_override.py`

| Colonne | Type | Règle |
|---------|------|-------|
| `override_started_at` | `TIMESTAMPTZ NULL` | Renseigné à l'activation ; `NULL` quand override inactif. |

Constantes serveur (documenter dans le service) :

| Constante | Valeur MVP proposée |
|-----------|---------------------|
| `DEFAULT_OVERRIDE_TTL_SECONDS` | **1800** (30 min) |
| Rate-limit activate/deactivate | **5/minute** par `device_id` |

Garde TTL : dans `require_active_operator_context` ou helper `assert_override_not_expired`, si `override_active` et `now - override_started_at > TTL` → désactiver override + audit `SHARED_WORKSTATION_OVERRIDE_EXPIRED` + **403** sur mutations nécessitant override ; l'intersection revient au mode normal (override=false).

#### 3. Backend — service override

Nouveau module suggéré : `recyclique/api/src/recyclic_api/services/shared_workstation_override_service.py`.

| Méthode | Comportement |
|---------|--------------|
| `activate_override(*, device_id, operator_user_id, confirmation_pin, actor_user_id, request_id)` | Session active requise ; opérateur = SuperAdmin ; vérifie PIN via même hash que 27.6 (`verify_password`) ; idempotent si déjà actif (refresh `override_started_at` **non** — retourner 409 ou 200 sans double audit bruyant, documenter) ; set `override_active=true`, `override_started_at=now` ; audit activation ; invalide cache intersection (`SharedWorkstationEffectiveModulesService.invalidate_on_context_change`). |
| `deactivate_override(*, device_id, reason, actor_user_id, request_id)` | Session active + override actif ; set `override_active=false`, `override_started_at=null` ; audit désactivation ; recalcul intersection. |
| `expire_override_if_needed(session, now)` | Appelé par garde / status ; retourne bool « expiré traité ». |

Étendre **`DeviceOperatorSessionService.end_session`** : si session avait `override_active=true`, journaliser audit désactivation explicite **en plus** de l'audit lock/session end (reason `session_ended`).

**PIN verify (27.6)** — garde-fou explicite dans le code :

```python
# shared_workstation_operator_pin_service.py — NE PAS MODIFIER pour activer override
session = self._sessions.start_session(
    device_id=device_id,
    operator_user_id=operator_user_id,
    # override_active=False par défaut — INTERDIT True ici
)
```

#### 4. Backend — intersection modules (extension 27.7)

Modifier `SharedWorkstationEffectiveModulesService.compute_effective_module_keys` :

```python
skip_operator_permissions = (
    session is not None
    and session.override_active
    and operator.role == UserRole.SUPER_ADMIN
)
# ...
if not skip_operator_permissions:
    if not all(p in permission_keys for p in entry.required_permission_keys):
        continue
```

Test obligatoire : opérateur SuperAdmin **sans** override → intersection normale ; **avec** override → modules allowlist+site même si permissions opérateur insuffisantes.

#### 5. Backend — API HTTP (OpenAPI + implémentation)

Préfixe : `/v1/shared-workstation/` (`endpoints/shared_workstation.py`).

| Opération | Méthode | Auth | Comportement |
|-----------|---------|------|--------------|
| Activer override | `POST …/override/activate` | Credential device + session opérateur active | Body : `{ "confirmation_pin": string }` — min/max longueur alignées PIN existant. Succès **200** : `{ "override_active": true, "override_started_at": ISO, "override_expires_at": ISO }` + `no-store`. |
| Désactiver override | `POST …/override/deactivate` | Credential device + session active + override actif | Body optionnel `{ "reason": "user_exit" \| "admin_action" }`. Succès **200** : `{ "override_active": false }`. Idempotent si déjà inactif → 200. |
| Statut session enrichi | `GET …/operator-session/status` (**étendre**) | Credential device | Ajouter champs : `override_active`, `override_started_at`, `override_seconds_remaining` (nullable), `can_activate_super_admin_override` (bool, `false` si session inactive). Dérivation serveur : session active **et** `User.role == SUPER_ADMIN` **et** `override_active=false`. |
| Contexte poste | `GET …/context` | Inchangé | Doit refléter `override_active` temps réel. |

Nouveaux schémas OpenAPI suggérés :

- `SharedWorkstationOverrideActivateV1Request`
- `SharedWorkstationOverrideActivateV1Response`
- `SharedWorkstationOverrideDeactivateV1Request`
- `SharedWorkstationOverrideDeactivateV1Response`
- Étendre `SharedWorkstationOperatorSessionStatusV1Response` : `override_active`, `override_started_at`, `override_seconds_remaining`, `can_activate_super_admin_override`

OperationIds stables : `recyclique_sharedWorkstation_activateOverride`, `recyclique_sharedWorkstation_deactivateOverride`.

#### 6. Backend — audit

Nouveaux `AuditActionType` dans `models/audit_log.py` + helpers `core/audit.py` :

| Type | Quand |
|------|--------|
| `SHARED_WORKSTATION_OVERRIDE_ACTIVATED` | Succès activation |
| `SHARED_WORKSTATION_OVERRIDE_DEACTIVATED` | Sortie explicite ou fin session avec override actif |
| `SHARED_WORKSTATION_OVERRIDE_ACTIVATION_REFUSED` | Non-SuperAdmin, PIN confirmation échoué, pas de session |
| `SHARED_WORKSTATION_OVERRIDE_EXPIRED` | TTL dépassé |
| `SHARED_WORKSTATION_OVERRIDE_REQUIRED` | Refus mutation sans override (optionnel si couvert par `SHARED_WORKSTATION_ACCESS_REFUSED`) |

Champs merge : `device_id`, `operator_user_id`, `session_id`, `site_id`, `override_active`, `outcome`, `reason`, `request_id` — **interdit** : PIN, hash PIN.

#### 7. Frontend — UX override explicite

**Principe** : visible, intrusif, auditable — bandeau persistant tant que `override_active=true` (vérité serveur via poll session status 27.6/27.9).

Nouveaux composants suggérés :

| Fichier | Rôle |
|---------|------|
| `SharedWorkstationSuperAdminOverrideBanner.tsx` | Bandeau warning (couleur distincte lock screen) : « Mode override SuperAdmin actif » + compte à rebours TTL + bouton « Quitter override » |
| `SharedWorkstationOverrideActivateControl.tsx` | Entrée menu/toolbar — visible **uniquement** si `operator-session/status` renvoie `can_activate_super_admin_override=true` (vérité serveur sur l'opérateur PIN actif ; **pas** le JWT web / `ContextEnvelope` seul) |
| `SharedWorkstationOverrideActivateModal.tsx` | Modale confirmation : texte explicite des limites (allowlist poste conservée) + champ PIN confirmation + boutons Annuler / Activer |

Intégration shell :

- Monter bandeau + contrôle dans `LiveAuthShell.tsx` sous `SharedWorkstationOperatorSessionProvider`, au-dessus du contenu métier (z-index cohérent modale inactivité 27.9).
- Au lock (`lockRequired=true` via timeout/handoff 27.9) : bandeau disparaît automatiquement (session ended) — **ne pas** persister override côté client.
- Après activation/désactivation : `refreshSessionStatus()` + refresh effective modules (`SharedWorkstationEffectiveModulesProvider`).

Client API suggéré : `peintre-nano/src/api/shared-workstation-override-client.ts` — `activateOverride`, `deactivateOverride` ; headers device ; `cache: 'no-store'`.

Testids : `shared-workstation-override-banner`, `shared-workstation-override-activate`, `shared-workstation-override-confirm`, `shared-workstation-override-exit`.

**Anti-pattern interdit** : `localStorage.setItem('override', 'true')`, toggle sans appel API, activation automatique post-PIN dans `SharedWorkstationLockScreen`.

#### 8. Non-régression 27.6–27.9

| Scénario | Attendu |
|----------|---------|
| PIN opérateur standard (non SuperAdmin) | Pas de contrôle activation ; intersection 27.7 stricte. |
| SuperAdmin PIN sans activation override | Pas d'élargissement intersection. |
| Override actif + timeout inactivité | Session ended → override disparaît ; lock screen ; audit timeout inclut override. |
| Override actif + « Passer la main » | Idem — fin session. |
| Override actif + brouillon Reception | Comportement 27.8 inchangé ; audit trace `override_active`. |
| Révocation device pendant override | Invalidation session (27.2) → override terminé. |

#### 9. Tests obligatoires (gates story)

Backend — fichier suggéré : `recyclique/api/tests/test_story_27_10_superadmin_override.py` (marqueur pytest `story_27_10`).

| # | Cas |
|---|-----|
| 1 | SuperAdmin + session active + PIN confirmation OK → `override_active=true`, audit activation, statut enrichi. |
| 2 | Opérateur non-SuperAdmin tente activate → 403 `SHARED_WORKSTATION_OVERRIDE_FORBIDDEN`, audit refused. |
| 3 | PIN confirmation incorrect → 403 neutre, pas d'activation, audit refused. |
| 4 | PIN verify (27.6) démarre session avec `override_active=false` — non-régression. |
| 5 | Override actif → intersection élargie (module allowlist+site accessible sans permission opérateur). |
| 6 | Override inactif → intersection 27.7 stricte (non-régression). |
| 7 | Module hors allowlist poste → 403 même avec override actif. |
| 8 | `POST …/override/deactivate` → override false, audit, intersection resserrée. |
| 9 | TTL expiré (temps figé) → auto-deactivate + 403 sur route nécessitant override. |
| 10 | `operator-session/end` reason timeout avec override actif → session ended, audit lock + override deactivated. |
| 11 | Route probe / mutation avec `SHARED_WORKSTATION_OVERRIDE_REQUIRED` sans override → 403. |
| 12 | Audit : aucun PIN dans `details_json` ; `override_active` présent sur événements pertinents. |
| 13 | `GET …/operator-session/status` : `can_activate_super_admin_override=true` seulement pour opérateur PIN SuperAdmin sans override actif ; `false` pour opérateur standard. |

Frontend :

- `peintre-nano/tests/unit/shared-workstation-superadmin-override.test.tsx` — bandeau visible si status mock `override_active=true` ; contrôle activation visible si `can_activate_super_admin_override=true` ; modale activation appelle API ; exit appelle deactivate.
- `peintre-nano/tests/unit/shared-workstation-override-client.test.ts` — URLs, headers device, `no-store`.
- E2E suggéré : `peintre-nano/tests/e2e/shared-workstation-superadmin-override-27-10.e2e.test.tsx` — flux activate → bandeau → deactivate.

Commandes gates (Story Runner brief) :

```bash
cd recyclique/api && python -m pytest tests/ -k story_27_10 -q
cd peintre-nano && npm run lint
cd peintre-nano && npm run test -- --run
```

Ajouter marqueur `story_27_10` dans `recyclique/api/pyproject.toml` (même pattern que `story_27_9`).

Validation Vitest ciblée (si CLI npm instable, pattern 27.9) :

```bash
node ./node_modules/vitest/vitest.mjs run tests/unit/shared-workstation-superadmin-override.test.tsx tests/unit/shared-workstation-override-client.test.ts
```

### Hors scope explicite

- Override sur **appareil personnel SuperAdmin** sans poste partagé enrôlé (cadrage §3.14 — epic ultérieur).
- Bypass allowlist poste ou config site (contrevient mini-ADR).
- Override offline / persistance client autoritaire.
- Nouveau rôle local « override operator ».
- Reporting audit avancé / dashboard override.
- Generalisation caisse / cashflow brownfield.
- Modification `sprint-status.yaml` / `epics.md` depuis CS/DS (writer unique Epic Runner).
- Stories post-Epic 27 (kiosque offline PRD, registre matériel complet).

### Dépendances 27.2–27.9 (réutilisation obligatoire)

| Story | Réutiliser (ne pas réécrire) |
|-------|------------------------------|
| 27.2 | `DeviceOperatorSession.override_active`, `SharedWorkstationContextService`, `merge_critical_audit_fields`. |
| 27.3 | `UserRole.SUPER_ADMIN`, pattern garde admin. |
| 27.4 | En-têtes credential device (`require_valid_device_credential`) sur endpoints override — même pattern que PIN / session status. |
| 27.6 | Vérification PIN hash, lock screen, `SharedWorkstationOperatorSessionProvider`, poll status ; opérateur actif = session PIN, distinct du JWT web. |
| 27.7 | `SharedWorkstationEffectiveModulesService`, `assert_module_in_effective_set`, probe-module. |
| 27.9 | `end_active_session_for_device`, timeout → fin session ; bandeau/timer coexistence z-index. |

### Intelligence stories précédentes (27.7 → 27.10)

| Story | Réutiliser tel quel |
|-------|---------------------|
| **27.7** | Formule intersection — **étendre** branche override, ne pas dupliquer service. |
| **27.8** | Brouillons Reception — override ne change pas règles draft ; tracer `override_active` en audit. |
| **27.9** | Fin session = sortie override ; ne pas créer timer override séparé côté front si TTL serveur suffit. |

### Anti-patterns (interdits)

- Activer override dans `verify_and_start_session` ou `start_session` post-PIN.
- Flag UI / Zustand / `localStorage` comme source de vérité override.
- Inférer SuperAdmin depuis JWT web / `ContextEnvelope` pour afficher l'entrée override — utiliser `can_activate_super_admin_override` du statut session PIN.
- Élargir au-delà allowlist poste « parce que SuperAdmin ».
- Oublier audit activation / refus / sortie.
- Bandeau override masqué ou discret (doit être visible — AC « jamais silencieux »).
- Sleep réel 30 min dans tests TTL — utiliser temps injectable.
- Dupliquer logique PIN — réutiliser `verify_password` / service PIN 27.6.

### Testing / gates (Story Runner)

| Gate | Commande / critère |
|------|-------------------|
| Tests backend 27.10 | `cd recyclique/api && python -m pytest tests/ -k story_27_10 -q` → exit 0 |
| Non-régression Epic 27 | `pytest tests/test_story_27_6_pin_lock_operator_session.py tests/test_story_27_7_server_module_intersection.py tests/test_story_27_9_timeout_lock_handoff.py -q` |
| Lint front | `cd peintre-nano && npm run lint` → exit 0 |
| Tests front | `cd peintre-nano && npm run test -- --run` → exit 0 |
| Revue sécurité | grep audit override ; grep absence PIN ; grep `override_active` non set post-PIN |
| OpenAPI | operationIds `recyclique_sharedWorkstation_activateOverride|deactivateOverride` |
| YAML sprint (parent) | lecture seule — pas de write CS/DS |

`gates_skipped_with_hitl: false` — aucun skip pour activation explicite, audit, refus frontière API, sortie timeout/lock.

### Project Structure Notes

| Zone | Fichiers / dossiers |
|------|---------------------|
| Service override | `recyclique/api/src/recyclic_api/services/shared_workstation_override_service.py` (suggéré) |
| Intersection | `recyclique/api/src/recyclic_api/services/shared_workstation_effective_modules_service.py` (étendre) |
| Session | `recyclique/api/src/recyclic_api/services/device_operator_session_service.py` (statut enrichi, end_session audit) |
| Endpoints | `recyclique/api/src/recyclic_api/api/api_v1/endpoints/shared_workstation.py` |
| Schémas | `recyclique/api/src/recyclic_api/schemas/shared_workstation_override.py` (suggéré) |
| Migration | `recyclique/api/migrations/versions/s27_10_superadmin_override.py` (suggéré) |
| Garde | `recyclique/api/src/recyclic_api/core/shared_workstation_guard.py` (TTL override) |
| Audit | `recyclique/api/src/recyclic_api/core/audit.py`, `models/audit_log.py` |
| Tests back | `recyclique/api/tests/test_story_27_10_superadmin_override.py` |
| Bandeau / modale | `peintre-nano/src/domains/shared-workstation/SharedWorkstationSuperAdminOverrideBanner.tsx`, `SharedWorkstationOverrideActivateModal.tsx` |
| Client API | `peintre-nano/src/api/shared-workstation-override-client.ts` |
| Shell | `peintre-nano/src/app/auth/LiveAuthShell.tsx` |
| Tests front | `peintre-nano/tests/unit/shared-workstation-superadmin-override.test.tsx`, `shared-workstation-override-client.test.ts` |
| Contrat | `contracts/openapi/recyclique-api.yaml` |

### References

- `_bmad-output/planning-artifacts/epics.md` — Epic 27, Story 27.10
- `_bmad-output/implementation-artifacts/27-2-server-context-audit.md`
- `_bmad-output/implementation-artifacts/27-3-superadmin-device-management.md`
- `_bmad-output/implementation-artifacts/27-6-pin-lock-operator-session.md`
- `_bmad-output/implementation-artifacts/27-7-server-module-intersection.md`
- `_bmad-output/implementation-artifacts/27-9-timeout-lock-handoff.md`
- `references/artefacts/2026-05-29_02_mini-adr-postes-partages-pin-non-offline.md`
- `references/artefacts/2026-05-29_01_cadrage-postes-partages-pin-operateur.md` — §3.13
- `references/artefacts/2026-05-29_04_runbook-orchestration-epic-27-postes-partages-pin.md` — §4, §7–§8
- `recyclique/api/src/recyclic_api/models/device_operator_session.py` — `override_active`
- `recyclique/api/src/recyclic_api/services/shared_workstation_operator_pin_service.py`
- `recyclique/api/src/recyclic_api/services/shared_workstation_effective_modules_service.py`
- `recyclique/api/src/recyclic_api/core/auth.py` — `require_super_admin_role`, `UserRole.SUPER_ADMIN`
- `contracts/openapi/recyclique-api.yaml`
- `_bmad-output/project-context.md`

## Trace Epic 27 — ADR

| Élément | Valeur |
|--------|--------|
| Nouvelle ADR structurante requise ? | **ADR N/A pour 27.10** — implémentation mini-ADR § Audit + cadrage §3.13. |
| ADR applicables | Mini-ADR 2026-05-29 ; stories 27.2 (champ), 27.7 (intersection), 27.9 (sortie session). |
| Dernière story epic | **Oui** — clôture fonctionnelle Epic 27 après gates + QA + CR. |

## Alignement sprint / YAML

- Clé **`27-10-superadmin-override`** : **non modifiée** par ce worker CS (writer unique Epic Runner — brief story_run interdit modification `sprint-status.yaml`).
- **`epic-27`** : inchangé par CS.
- Story **finale** de la séquence 27.1 → 27.10.

## Risques / HITL

| Sujet | Décision proposée MVP | Escalade |
|-------|----------------------|----------|
| UX confirmation forte | Re-saisie **PIN opérateur** SuperAdmin (aligné cadrage §3.13) | Strophe si mot de passe web / MFA préféré |
| TTL override | **1800 s** (30 min) + auto-expire serveur | Strophe si durée métier différente |
| Idempotence activate | 200 silencieux si déjà actif **sans** refresh TTL | HITL si re-confirmation requise à chaque fois |
| Élargissement intersection | Skip permissions opérateur seulement ; allowlist+site conservés | Strophe si bypass allowlist demandé |
| Bandeau couleur / wording | Warning visible « Override SuperAdmin actif » | UX review Strophe |
| Route « usage » audit explicite | `merge_critical_audit_fields(override_active=True)` sur mutations existantes suffit MVP | Story audit avancée si exigé |

**NEEDS_STROPHE_HITL** : non requis pour démarrer le DS si le dev suit les propositions ci-dessus (PIN confirmation, TTL 1800 s, élargissement borné allowlist+site, sortie via deactivate + 27.9).

## Checklist VS (validate-create-story)

**Verdict VS :** **PASS** (vs_loop=0, validate 2026-05-30) — story prête pour DS.

- [x] AC BDD alignés `epics.md` §27.10 (activation explicite, état serveur, jamais auto PIN, sortie, timeout/lock, audit, refus API).
- [x] Garde-fous mini-ADR + cadrage §3.13 + runbook §7 (pas override implicite, pas authz front, audit sans PIN).
- [x] Dépendances 27.2, 27.3, 27.4, 27.6, 27.7, 27.9 et réutilisation explicite (`override_active`, intersection, end_session, PIN service, credential device).
- [x] Visibilité UI override : `can_activate_super_admin_override` sur statut session (opérateur PIN), pas inférence depuis JWT web seul — corrigé VS.
- [x] Sémantique override bornée (allowlist + site ; pas bypass total poste).
- [x] Spécification API/OpenAPI (activate/deactivate, statut enrichi, codes erreur, rate limits, `no-store`).
- [x] Front bandeau/modale/controls + intégration `LiveAuthShell` ; anti-patterns localStorage/UI flag.
- [x] Gates § Testing (pytest `story_27_10`, vitest `shared-workstation-superadmin-override`, non-régression 27.6/27.7/27.9).
- [x] `sprint-status.yaml` / `epics.md` non modifiés par CS (conformément au brief).
- [x] Dernière story Epic 27 — DoD epic documentée.

## Dev Notes

### Contexte brownfield (CS 2026-05-30)

Le socle **27.2** a déjà préparé `DeviceOperatorSession.override_active`, propagation `ContextEnvelope`, et tests unitaires avec `override_active=True` en fixture directe (`test_story_27_2_shared_workstation_context.py`). Le **DS ne doit pas** supposer greenfield : brancher activation produit, intersection 27.7, endpoints HTTP, UX et tests `story_27_10` — le flag existe mais **n'est pas activable** en produit avant cette story.

### Previous story intelligence (27.9 → 27.10)

- `end_active_session_for_device` et timeout 27.9 terminent la session entière — **réutiliser** comme sortie override sans nouveau mécanisme parallèle.
- `_log_session_end` inclut déjà `override_active=session.override_active` — étendre avec audit override deactivated si `true`.
- Poll `operator-session/status` existant — **étendre** avec champs override plutôt que créer un second poll.

### Library / framework

- Backend : FastAPI, SQLAlchemy — réutiliser `verify_password`, `UserRole.SUPER_ADMIN`, patterns audit 27.6–27.9.
- Front : React + Mantine modale (cohérent 27.9 inactivity warning) ; bandeau warning visible.
- Tests : temps figé pour TTL (`freezegun` ou injection `now` — même pattern que 27.9 `seconds_until_lock`).

## Tasks / Subtasks

- [x] **T1 — Migration + modèle session** (AC: état serveur explicite)
  - [x] T1.1 Colonne `override_started_at` nullable sur `device_operator_sessions`
  - [x] T1.2 Constantes `DEFAULT_OVERRIDE_TTL_SECONDS`
- [x] **T2 — Service override + intersection** (AC: activation, refus, élargissement borné)
  - [x] T2.1 `SharedWorkstationOverrideService.activate/deactivate/expire`
  - [x] T2.2 Extension `compute_effective_module_keys` branche override SuperAdmin
  - [x] T2.3 Garde TTL + codes erreur stables
- [x] **T3 — Backend API HTTP + OpenAPI** (AC: action explicite, statut enrichi)
  - [x] T3.1 `POST …/override/activate` (confirmation PIN)
  - [x] T3.2 `POST …/override/deactivate`
  - [x] T3.3 `GET …/operator-session/status` champs override + `can_activate_super_admin_override`
- [x] **T4 — Audit** (AC: activation, usage, sortie audités)
  - [x] T4.1 Nouveaux `AuditActionType` + helpers sans PIN
  - [x] T4.2 Audit fin session avec override actif (27.9 path)
- [x] **T5 — Frontend UX** (AC: jamais flag UI seul, sortie claire)
  - [x] T5.1 Bandeau override + modale activation PIN
  - [x] T5.2 Client API + refresh session/modules
  - [x] T5.3 Intégration `LiveAuthShell`
- [x] **T6 — Non-régression + gates** (AC: jamais auto PIN, timeout sort override)
  - [x] T6.1 pytest `-k story_27_10` + marqueur `pyproject.toml`
  - [x] T6.2 Vitest `shared-workstation-superadmin-override`
  - [x] T6.3 Non-régression 27.6/27.7/27.9 ; `npm run lint`

## Dev Agent Record

### Agent Model Used

Composer (DS worker story 27-10)

### Debug Log References

- Import circulaire `DeviceOperatorSessionService` ↔ `SharedWorkstationOverrideService` résolu par import lazy dans `get_enriched_session_status`.

### Completion Notes List

- Backend : service override (activate/deactivate/expire TTL 1800s), intersection 27.7 étendue (skip permissions opérateur si override + SuperAdmin), endpoints activate/deactivate, statut session enrichi, probe `/probe-override/{module_key}`, audit 5 types, migration `override_started_at`.
- Frontend : bandeau warning, modale PIN confirmation, client API no-store, shell intégré dans `LiveAuthShell`.
- Gates locaux : pytest `story_27_10` 12/12, lint tsc OK, vitest override 8/8.
- `sprint-status.yaml` non modifié (brief Epic Runner).

### File List

- recyclique/api/migrations/versions/s27_10_superadmin_override.py
- recyclique/api/src/recyclic_api/models/device_operator_session.py
- recyclique/api/src/recyclic_api/models/audit_log.py
- recyclique/api/src/recyclic_api/core/audit.py
- recyclique/api/src/recyclic_api/core/shared_workstation_guard.py
- recyclique/api/src/recyclic_api/services/shared_workstation_override_service.py
- recyclique/api/src/recyclic_api/services/shared_workstation_effective_modules_service.py
- recyclique/api/src/recyclic_api/services/device_operator_session_service.py
- recyclique/api/src/recyclic_api/schemas/shared_workstation_override.py
- recyclique/api/src/recyclic_api/schemas/shared_workstation_operator_session.py
- recyclique/api/src/recyclic_api/api/api_v1/endpoints/shared_workstation.py
- recyclique/api/tests/test_story_27_10_superadmin_override.py
- recyclique/api/pyproject.toml
- contracts/openapi/recyclique-api.yaml
- peintre-nano/src/api/shared-workstation-override-client.ts
- peintre-nano/src/api/shared-workstation-operator-session-client.ts
- peintre-nano/src/domains/shared-workstation/SharedWorkstationOperatorSessionProvider.tsx
- peintre-nano/src/domains/shared-workstation/SharedWorkstationSuperAdminOverrideBanner.tsx
- peintre-nano/src/domains/shared-workstation/SharedWorkstationOverrideActivateControl.tsx
- peintre-nano/src/domains/shared-workstation/SharedWorkstationOverrideActivateModal.tsx
- peintre-nano/src/domains/shared-workstation/SharedWorkstationOverrideShell.tsx
- peintre-nano/src/app/auth/LiveAuthShell.tsx
- peintre-nano/tests/unit/shared-workstation-override-client.test.ts
- peintre-nano/tests/unit/shared-workstation-superadmin-override.test.tsx
- peintre-nano/tests/e2e/shared-workstation-superadmin-override-27-10.e2e.test.tsx

### Change Log

- 2026-05-30 — Story 27.10 CS (create-story worker) : PASS ; story prête DS ; dernière story Epic 27.
- 2026-05-30 — VS validate (vs_loop=0) : PASS après correction visibilité SuperAdmin (`can_activate_super_admin_override` sur statut session PIN, ref 27.4 credential device).
- 2026-05-30 — DS implémentation 27.10 : override SuperAdmin explicite (API + UX + tests gates).
