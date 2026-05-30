# Story 27.9 : Timeout inactivité, verrouillage et passage de main

Status: ready-for-dev

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->
<!-- Ultimate context engine analysis completed — comprehensive developer guide created (CS 2026-05-30). -->

**Story key :** `27-9-timeout-lock-handoff`  
**Epic :** 27 — Postes partagés enrôlés + PIN opérateur + PWA installable non-offline  
**Implementation artifact :** `_bmad-output/implementation-artifacts/27-9-timeout-lock-handoff.md`  
**Date CS :** 2026-05-30

## Dépendances (prérequis)

- **Stories 27.1–27.8 done** : registre `RegisteredDevice`, contexte serveur + garde `require_active_operator_context`, panel SuperAdmin (timeout configurable), enrôlement credential device, PWA non-offline, lock screen PIN + session opérateur, intersection modules serveur, brouillons Reception pilote — fichiers `_bmad-output/implementation-artifacts/27-1-registered-device.md` … `27-8-reception-pilot-drafts.md`.
- **Story 27.3 (timeout admin)** : champ `inactivity_timeout_seconds` nullable sur device ; défaut serveur **`DEFAULT_INACTIVITY_TIMEOUT_SECONDS = 900`** (15 min) — `recyclique/api/src/recyclic_api/models/registered_device.py` ; exposé via `GET /v1/shared-workstation/device-status`.
- **Story 27.6 (PIN / lock)** : lock screen, `DeviceOperatorSessionService.start_session` / `end_session`, `touch_activity`, hooks `last_activity_at` — `_bmad-output/implementation-artifacts/27-6-pin-lock-operator-session.md`.
- **Story 27.7 (intersection)** : garde modules ; navigation filtrée post-PIN — `_bmad-output/implementation-artifacts/27-7-server-module-intersection.md`.
- **Story 27.8 (brouillons Reception)** : masquage brouillon au lock ; reset UI réception — `_bmad-output/implementation-artifacts/27-8-reception-pilot-drafts.md`.
- **Epic 27 — cadrage gelé** : `_bmad-output/planning-artifacts/epics.md` (§ Epic 27, Story 27.9).
- **Mini-ADR Epic 27** : `references/artefacts/2026-05-29_02_mini-adr-postes-partages-pin-non-offline.md` — § Audit (verrouillage manuel, verrouillage par timeout).
- **Cadrage produit** : `references/artefacts/2026-05-29_01_cadrage-postes-partages-pin-operateur.md` — §3.10 (timeout, avertissement, continuer, verrouiller maintenant, passer la main).
- **Runbook orchestration** : `references/artefacts/2026-05-29_04_runbook-orchestration-epic-27-postes-partages-pin.md` — ordre §4, invariants §7, gates §8.
- **Contrat OpenAPI** : `contracts/openapi/recyclique-api.yaml` — **cette story étend** le contrat (fin session opérateur, heartbeat activité, champs statut inactivité).
- **Stories suivantes (ne pas implémenter ici)** : 27.10 (override SuperAdmin explicite et audite).

## Garde-fous ADR / runbook (obligatoires pour le DS)

| Invariant | Application story 27.9 |
|-----------|-------------------------|
| Timeout configurable | Seuil effectif = `RegisteredDevice.inactivity_timeout_seconds` ou **`900 s`** si NULL (déjà 27.1/27.3) ; le front **lit** la valeur via `device-status`, ne l'invente pas. |
| Invalidation serveur avant lock | Toute fin de session (timeout ou manuel) passe par **`DeviceOperatorSessionService.end_session`** (ou équivalent avec `reason` explicite) **avant** que le lock screen ne masque l'UI ; routes sensibles restent **403** via `require_active_operator_context`. |
| Même état de sécurité | Timeout et « passer la main » / « verrouiller maintenant » produisent le **même** état : session opérateur **ended**, lock screen affiché, brouillons masqués (27.8), reset UI éphémère (pattern `LiveAuthShell`). |
| Avertissement pré-lock | Afficher une modale **non bloquante de saisie en cours** : l'utilisateur peut « continuer » (repousse le timer) ou verrouiller tout de suite. |
| Activité réelle repousse le timer | Événements clavier / souris / tactile (debounced) côté front **et** heartbeat serveur throttled pour `last_activity_at` — ne pas verrouiller au milieu d'une frappe active. |
| Pas d'autorité front | Le front **ne décide pas** seul du lock définitif : appel API `end` ou détection serveur `last_activity_at` + timeout ; poll session status existant (27.6). |
| Audit transversal | Événements timeout et lock manuel tracés ; **pas** de PIN ni contenu métier en `details_json`. |
| Timers testables | Horloge injectable (front) ; temps figé / paramétrable (back) — **aucun** test e2e ne doit dépendre d'un sleep réel > 100 ms. |
| Pas override SuperAdmin | Aucun état `override_active=true` fonctionnel, aucun bouton override — story **27.10**. |
| Pas timeout par module | Cadrage §3.10 mentionne « par poste / module » — **MVP 27.9 = par poste (`device_id`) uniquement** ; timeout par `module_key` → **NEEDS_HITL** si demandé. |
| `network-only` / `no-store` | Endpoints session end / heartbeat / statut enrichi : `Cache-Control: no-store`. |

## Story (BDD)

As a **field team member**,  
I want **a clear inactivity timeout and handoff flow on shared workstations**,  
So that **one operator can safely leave the post and another can take over without data leakage**.

## Acceptance criteria

Source normative : `_bmad-output/planning-artifacts/epics.md` — **Story 27.9**.

**Given** a PIN operator session is active on an enrolled workstation  
**When** inactivity reaches the configured threshold  
**Then** the default threshold is 15 minutes unless changed by SuperAdmin policy  
**And** a warning appears before lock  
**And** real user activity can postpone the timer  
**And** "continue" keeps the current operator active  
**And** "lock now" or "passer la main" clears the active operator server-side  
**And** server invalidation happens before new sensitive actions can proceed  
**And** timeout and manual lock events are audited  
**And** timers are testable through mocks/injection to avoid flaky tests

### Interprétation exécutable

#### 1. Paramètres timeout (MVP)

| Paramètre | Source | Valeur MVP |
|-----------|--------|------------|
| Timeout effectif | `GET /v1/shared-workstation/device-status` → `inactivity_timeout_seconds` | `900` si NULL côté device |
| Fenêtre avertissement | Constante front documentée | **`WARNING_LEAD_SECONDS = 60`** (modale ~1 min avant lock) |
| Debounce activité UI | Constante front | **`ACTIVITY_DEBOUNCE_MS = 1000`** |
| Throttle heartbeat serveur | Constante front + back | **`HEARTBEAT_MIN_INTERVAL_SECONDS = 30`** (max 1 touch/min par session) |
| Min/max PATCH SuperAdmin | Schéma existant `ge=1` | **Proposer** min **60 s**, max **7200 s** (2 h) — validation Pydantic + widget admin ; **HITL Strophe** si autres bornes |

Le timer front calcule :

```text
idle_seconds = now - max(local_last_activity, server_last_activity_at)
warning_at   = timeout_seconds - WARNING_LEAD_SECONDS
lock_at      = timeout_seconds
```

Si `idle_seconds >= lock_at` → appeler fin session (timeout) puis refresh lock screen.  
Si `idle_seconds >= warning_at` et pas encore lock → afficher modale avertissement.

#### 2. Backend — service fin session / activité

Étendre ou consommer **`DeviceOperatorSessionService`** (`recyclique/api/src/recyclic_api/services/device_operator_session_service.py`) :

| Méthode | Comportement |
|---------|--------------|
| `end_active_session_for_device(*, device_id, reason, actor_user_id=None)` | Récupère session `ACTIVE` ; si absente → **204/idempotent** ; sinon `end_session` avec audit `reason` ∈ `manual_lock`, `timeout`, `handoff`. |
| `record_activity(*, device_id, operator_user_id)` | Session active requise ; si `now - last_activity_at < HEARTBEAT_MIN_INTERVAL` → no-op ; sinon `touch_activity`. |

Nouveau helper audit dans `core/audit.py` (pattern 27.6) :

| `AuditActionType` | Quand |
|-------------------|--------|
| `SHARED_WORKSTATION_OPERATOR_LOCKED_MANUAL` | Fin session via action utilisateur « verrouiller » / « passer la main ». |
| `SHARED_WORKSTATION_OPERATOR_LOCKED_TIMEOUT` | Fin session déclenchée par timeout (front ou garde serveur). |
| `SHARED_WORKSTATION_OPERATOR_ACTIVITY_TOUCH` | **Optionnel MVP** — omit si bruit ; préférer audit lock seulement. |

Champs merge audit : `device_id`, `operator_user_id`, `session_id`, `site_id`, `outcome`, `reason`, `request_id` — **interdit** : PIN, contenu brouillon.

**Garde serveur optionnelle (recommandée)** : dans `require_active_operator_context` ou middleware dédié poste partagé, si `now - session.last_activity_at > effective_timeout` → auto-`end_session(reason=timeout)` + **403** `SHARED_WORKSTATION_OPERATOR_SESSION_EXPIRED` — évite qu'une action sensible passe après expiration si le front n'a pas encore pollé. **Tests obligatoires** sur ce chemin.

#### 3. Backend — API HTTP (OpenAPI + implémentation)

Préfixe : `/v1/shared-workstation/` (`endpoints/shared_workstation.py`).

| Opération | Méthode | Auth | Comportement |
|-----------|---------|------|--------------|
| Fin session opérateur (lock / handoff) | `POST …/operator-session/end` | Credential device **obligatoire** ; session active requise | Body : `{ "reason": "manual_lock" \| "handoff" \| "timeout" }` — idempotent si déjà ended. Succès **200** : `{ "ended": true, "session_id" }` + `no-store`. |
| Heartbeat activité | `POST …/operator-session/activity` | Credential device + session active | Met à jour `last_activity_at` (throttled). **204** si throttled. |
| Statut session enrichi | `GET …/operator-session/status` (**étendre**) | Credential device | Ajouter : `last_activity_at` (ISO), `inactivity_timeout_seconds`, `seconds_until_lock` (calcul serveur, nullable si inactive). |

Codes d'erreur stables :

| Code | HTTP | Quand |
|------|------|-------|
| `SHARED_WORKSTATION_OPERATOR_REQUIRED` | 403 | Inchangé — pas de session active. |
| `SHARED_WORKSTATION_OPERATOR_SESSION_EXPIRED` | 403 | Session expirée côté serveur (auto-invalidation). |

Rate-limit : `@conditional_rate_limit("30/minute")` sur `activity` ; `10/minute` sur `end`.

#### 4. Frontend — timer inactivité + modale avertissement

Nouveau module suggéré : `peintre-nano/src/domains/shared-workstation/useSharedWorkstationInactivityTimer.ts` (+ provider optionnel `SharedWorkstationInactivityProvider.tsx`).

**Responsabilités :**

1. Charger `inactivity_timeout_seconds` depuis `device-status` (cache session mémoire, refresh si admin change timeout — poll device-status toutes les 5 min ou au mount).
2. Écouter activité document : `keydown`, `pointerdown`, `touchstart`, `click` sur `window` (debounced) → reset timer local **et** appeler `POST …/operator-session/activity` (throttled).
3. Tick via `setInterval` **injectable** (`clock: { now: () => number, setInterval, clearInterval }`) — défaut `Date.now` / `window.setInterval`.
4. États : `idle` | `warning` | `locking` — exposer à l'UI.
5. Modale avertissement (`SharedWorkstationInactivityWarningModal.tsx`) :
   - Titre : « Inactivité détectée »
   - Compte à rebours visuel (secondes restantes)
   - Bouton **Continuer** → ferme modale, reset activité locale + heartbeat
   - Bouton **Verrouiller maintenant** / **Passer la main** → `POST …/operator-session/end` avec `reason: manual_lock` ou `handoff` (synonymes produit acceptés — **un seul** code API `manual_lock` suffit si libellés UI diffèrent)
6. À lock (timeout ou manuel) : `refreshSessionStatus()` du provider 27.6 → `operatorSessionActive=false` → lock screen via `useSharedWorkstationLockRequired()` ; **ne pas** dupliquer la logique lock screen.

**Barre d'actions session active** (toolbar discrète) :

- Composant : `SharedWorkstationHandoffToolbar.tsx` — visible si `hasDevice && operatorSessionActive && !lockRequired`.
- Boutons : « Passer la main » et « Verrouiller » → même endpoint `end` (raison audit distincte si UX le demande).
- testids : `shared-workstation-handoff`, `shared-workstation-lock-now`, `shared-workstation-inactivity-warning`, `shared-workstation-inactivity-continue`.

**Intégration shell** :

- Monter provider/timer dans `LiveAuthShell.tsx` **sous** `SharedWorkstationOperatorSessionProvider`, **au-dessus** du contenu métier.
- Conserver l'effet existant :

```typescript
// LiveAuthShell.tsx — déjà en place (27.6 / 27.8)
useEffect(() => {
  if (lockRequired) {
    resetCashflowDraft();
    resetReceptionPosteUiState();
  }
}, [lockRequired]);
```

- **Ne pas** réimplémenter le reset brouillon Reception (27.8) : le lock screen + API suffisent.

Client API suggéré : étendre `peintre-nano/src/api/shared-workstation-operator-pin-client.ts` ou fichier dédié `shared-workstation-operator-session-client.ts` — `endOperatorSession`, `touchOperatorSessionActivity`, types statut enrichi.

#### 5. Non-régression brouillons / modules (27.7–27.8)

| Scénario | Attendu |
|----------|---------|
| Timeout sur poste avec brouillon Reception | Lock screen sans fuite ; brouillon toujours serveur-side ; reprise possible après nouveau PIN (27.8). |
| « Passer la main » pendant wizard Reception | UI reset (`resetReceptionPosteUiState`) ; pas de lignes visibles sur lock screen. |
| Module non autorisé | Inchangé 27.7 — timeout ne contourne pas intersection. |

#### 6. Tests obligatoires (gates story)

Backend — fichier suggéré : `recyclique/api/tests/test_story_27_9_timeout_lock_handoff.py` (marqueur pytest `story_27_9`).

| # | Cas |
|---|-----|
| 1 | Session active + `last_activity_at` ancien > timeout → garde serveur refuse mutation sensible + session ended + audit timeout. |
| 2 | `POST …/operator-session/end` reason `manual_lock` → session ended, audit manual, `GET status` → `active: false`. |
| 3 | `POST …/operator-session/activity` → met à jour `last_activity_at` ; second appel < 30 s → no-op. |
| 4 | `GET …/operator-session/status` enrichi → champs timeout + `seconds_until_lock` cohérents (temps figé). |
| 5 | End idempotent si déjà ended → 200/204 sans double audit bruyant. |
| 6 | Sans session → `end` → 403 ; `activity` → 403. |
| 7 | Audit : aucun PIN ; `reason` présent pour timeout vs manual. |
| 8 | Non-régression 27.6 : PIN → session → end → lock screen path (status inactive). |
| 9 | Non-régression 27.8 : brouillon masqué après end session (API draft 403 sans opérateur). |

Frontend :

- `peintre-nano/tests/unit/shared-workstation-inactivity-timer.test.ts` — fake clock : idle → warning → continue repousse ; idle → lock appelle `endOperatorSession`.
- `peintre-nano/tests/unit/shared-workstation-handoff-toolbar.test.tsx` — boutons appellent API mock.
- `peintre-nano/tests/unit/shared-workstation-operator-session-client.test.ts` — URLs, headers device, `cache: 'no-store'`.
- E2E suggéré : `peintre-nano/tests/e2e/shared-workstation-timeout-handoff-27-9.e2e.test.tsx` — session mock active → warning (clock injectée) → continuer / lock → lock screen.

Commandes gates (Story Runner brief) :

```bash
cd recyclique/api && python -m pytest tests/ -k story_27_9 -q
cd peintre-nano && npm run lint
cd peintre-nano && npm run test -- --run
```

Ajouter marqueur `story_27_9` dans `recyclique/api/pyproject.toml` (même pattern que `story_27_8`).

### Hors scope explicite

- Override SuperAdmin contexte (**27.10**).
- Timeout différencié par `module_key` (cadrage long terme).
- Liste nominative opérateurs / QR badge.
- Verrouillage automatique mid-saisie **sans** avertissement (interdit par cadrage §3.10).
- Réécriture lock screen PIN (27.6) ou intersection modules (27.7).
- Brouillons caisse (`cashflow-draft-store`) — reset UI seulement via lock existant.
- Modification sémantique `POST /v1/auth/pin` brownfield.
- Offline / persistance timer côté client comme autorité.
- Modification `sprint-status.yaml` depuis CS/DS (writer unique Epic Runner).

### Dépendances 27.1–27.8 (réutilisation obligatoire)

| Story | Réutiliser (ne pas réécrire) |
|-------|------------------------------|
| 27.1 | `DEFAULT_INACTIVITY_TIMEOUT_SECONDS`, modèle `RegisteredDevice.inactivity_timeout_seconds`. |
| 27.2 | `DeviceOperatorSession`, `last_activity_at`, audit session started/ended. |
| 27.3 | Panel admin timeout ; validation PATCH — **étendre** min/max si HITL accepté. |
| 27.4 | En-têtes device credential sur tous appels. |
| 27.5 | PWA standalone — modale au-dessus du shell (`z-index` cohérent lock screen). |
| 27.6 | Lock screen, `SharedWorkstationOperatorSessionProvider`, `verifySharedWorkstationOperatorPin`, poll 30 s. |
| 27.7 | `useSharedWorkstationModuleAccess` — toolbar visible seulement si session active. |
| 27.8 | Masquage brouillon Reception au lock ; `resetReceptionPosteUiState`. |

### Intelligence stories précédentes (27.6 → 27.8)

| Story | Réutiliser tel quel |
|-------|---------------------|
| **27.6** | `end_session` déjà implémenté ; `touch_activity` prêt — **brancher**, ne pas dupliquer. Pas de timer produit en 27.6 — c'est le cœur de **27.9**. Lockout PIN Redis **distinct** du timeout inactivité. |
| **27.7** | Filtrage navigation — le timer ne doit pas afficher modules hors intersection. |
| **27.8** | Au lock : brouillon Reception reste serveur ; lock screen sans métadonnées ; pattern reset UI dans `LiveAuthShell`. |

### Anti-patterns (interdits)

- Timer purement client sans invalidation serveur (`localStorage` « unlocked until »).
- Verrouiller sans appeler `end_session` (session fantôme active côté API).
- Sleep réel 15 min dans les tests.
- Oublier l'avertissement pré-lock (lock brutal).
- Confondre timeout inactivité et lockout PIN (Redis `shared_ws:pin_lockout:*`).
- Afficher données métier dans la modale avertissement.
- Implémenter override SuperAdmin « en passant » (**27.10**).
- Étendre timeout par module sans HITL.
- Dupliquer `SharedWorkstationLockScreen` pour le handoff.

### Testing / gates (Story Runner)

| Gate | Commande / critère |
|------|-------------------|
| Tests backend 27.9 | `cd recyclique/api && python -m pytest tests/ -k story_27_9 -q` → exit 0 |
| Non-régression Epic 27 | `pytest tests/test_story_27_6_pin_lock_operator_session.py tests/test_story_27_8_reception_pilot_drafts.py -q` |
| Lint front | `cd peintre-nano && npm run lint` → exit 0 |
| Tests front | `cd peintre-nano && npm run test -- --run` → exit 0 |
| Revue sécurité | grep audit timeout/manual ; pas de fuite métier sur lock screen après timeout |
| OpenAPI | operationIds stables `recyclique_sharedWorkstation_*` |
| YAML sprint (parent) | lecture seule — pas de write CS/DS |

`gates_skipped_with_hitl: false` — aucun skip pour invalidation serveur, audit, testabilité timers.

### Project Structure Notes

| Zone | Fichiers / dossiers |
|------|---------------------|
| Service session | `recyclique/api/src/recyclic_api/services/device_operator_session_service.py` (étendre) |
| Endpoints | `recyclique/api/src/recyclic_api/api/api_v1/endpoints/shared_workstation.py` |
| Schémas | `recyclique/api/src/recyclic_api/schemas/shared_workstation_operator_session.py` (suggéré) |
| Garde expiration | `recyclique/api/src/recyclic_api/core/shared_workstation_guard.py` (étendre si middleware) |
| Audit | `recyclique/api/src/recyclic_api/core/audit.py`, `models/audit_log.py` |
| Tests back | `recyclique/api/tests/test_story_27_9_timeout_lock_handoff.py` |
| Timer hook | `peintre-nano/src/domains/shared-workstation/useSharedWorkstationInactivityTimer.ts` |
| Modale warning | `peintre-nano/src/domains/shared-workstation/SharedWorkstationInactivityWarningModal.tsx` |
| Toolbar handoff | `peintre-nano/src/domains/shared-workstation/SharedWorkstationHandoffToolbar.tsx` |
| Client API | `peintre-nano/src/api/shared-workstation-operator-session-client.ts` (suggéré) |
| Shell | `peintre-nano/src/app/auth/LiveAuthShell.tsx` |
| Tests front | `peintre-nano/tests/unit/shared-workstation-inactivity-timer.test.ts`, `shared-workstation-handoff-toolbar.test.tsx` |
| Contrat | `contracts/openapi/recyclique-api.yaml` |

### References

- `_bmad-output/planning-artifacts/epics.md` — Epic 27, Story 27.9
- `_bmad-output/implementation-artifacts/27-3-superadmin-device-management.md`
- `_bmad-output/implementation-artifacts/27-6-pin-lock-operator-session.md`
- `_bmad-output/implementation-artifacts/27-7-server-module-intersection.md`
- `_bmad-output/implementation-artifacts/27-8-reception-pilot-drafts.md`
- `references/artefacts/2026-05-29_02_mini-adr-postes-partages-pin-non-offline.md`
- `references/artefacts/2026-05-29_01_cadrage-postes-partages-pin-operateur.md` — §3.10
- `references/artefacts/2026-05-29_04_runbook-orchestration-epic-27-postes-partages-pin.md` — §4, §7–§8
- `recyclique/api/src/recyclic_api/models/registered_device.py` — `DEFAULT_INACTIVITY_TIMEOUT_SECONDS`
- `recyclique/api/src/recyclic_api/services/device_operator_session_service.py`
- `peintre-nano/src/domains/shared-workstation/SharedWorkstationOperatorSessionProvider.tsx`
- `peintre-nano/src/app/auth/LiveAuthShell.tsx`
- `contracts/openapi/recyclique-api.yaml`
- `_bmad-output/project-context.md`

## Trace Epic 27 — ADR

| Élément | Valeur |
|--------|--------|
| Nouvelle ADR structurante requise ? | **ADR N/A pour 27.9** — implémentation mini-ADR § Audit + cadrage §3.10. |
| ADR applicables | Mini-ADR 2026-05-29 ; stories 27.6 (session), 27.3 (timeout admin). |

## Alignement sprint / YAML

- Clé **`27-9-timeout-lock-handoff`** : **non modifiée** par ce worker CS (writer unique Epic Runner — pas de passage `ready-for-dev` dans `sprint-status.yaml` depuis CS, conformément au brief story_run).
- **`epic-27`** : inchangé par CS.
- Prochaine story après clôture 27.9 : **`27-10-superadmin-override`**.

## Risques / HITL

| Sujet | Décision proposée MVP | Escalade |
|-------|----------------------|----------|
| Min/max timeout SuperAdmin | Min **60 s**, max **7200 s** (2 h) ; défaut **900 s** | Strophe si bornes métier différentes |
| Durée fenêtre avertissement | **60 s** avant lock (`WARNING_LEAD_SECONDS`) | HITL si trop court/long terrain |
| Timeout par module vs poste | **Poste uniquement** en 27.9 | Story dédiée ou epic ultérieur si exigé |
| Raison API `handoff` vs `manual_lock` | Deux valeurs audit distinctes, même effet sécurité | Fusion en une seule raison acceptable si simplification DS |
| Garde serveur auto-expire sur mutations | **Recommandée** | Omit seulement si perf mesurée problématique — documenter |
| Libellés UI « Passer la main » / « Verrouiller » | Deux boutons, un endpoint | OK MVP |

**NEEDS_STROPHE_HITL** : non requis pour démarrer le DS si le dev suit les propositions ci-dessus (900 s défaut, warning 60 s, invalidation serveur obligatoire, timers injectables).

## Checklist VS (validate-create-story)

**Verdict VS :** **PASS** (vs_loop=0) — story prête pour DS.

- [x] AC BDD alignés `epics.md` §27.9 (seuil 15 min, avertissement, activité repousse, continuer, lock/handoff serveur, invalidation avant mutations, audit, timers injectables).
- [x] Garde-fous mini-ADR § Audit (verrouillage manuel/timeout) + cadrage §3.10 + runbook §4/§7–§8 (invalidation serveur, pas override 27.10, pas authz front).
- [x] Dépendances 27.1–27.8 et réutilisation explicite (`DeviceOperatorSessionService`, `require_active_operator_context`, `LiveAuthShell` reset 27.8, lock 27.6).
- [x] Hors scope 27.10, timeout par module (HITL), lockout PIN Redis vs inactivité session documenté.
- [x] Spécification API/OpenAPI (`operator-session/end|activity|status` enrichi, codes `SHARED_WORKSTATION_OPERATOR_SESSION_EXPIRED`, rate limits, `no-store`).
- [x] Garde serveur auto-expire nommée (`expire_active_session_if_idle` / `_assert_operator_session_not_expired` dans `shared_workstation_guard.py`).
- [x] Front timer/modale/toolbar + intégration `LiveAuthShell` / provider 27.6 ; constantes MVP (`WARNING_LEAD_SECONDS`, debounce, heartbeat).
- [x] Gates § Testing (pytest `story_27_9`, lint, vitest, e2e suggéré, non-régression 27.6/27.8).
- [x] Anti-patterns (timer client seul, sleep 15 min, lock sans `end_session`, fuite métier modale).
- [x] `sprint-status.yaml` non modifié par CS/VS (writer unique Epic Runner).
- [x] Note brownfield WIP : chemins code/tests déjà présents sur branche — DS doit valider AC + gates, pas supposer greenfield.

## Dev Notes

### Brownfield / implémentation partielle (CS 2026-05-30)

Sur la branche courante, des fichiers **peuvent déjà exister** (WIP parallèle) : extensions `device_operator_session_service.py`, routes `operator-session/end|activity` dans `shared_workstation.py`, timer/modale/toolbar front, tests `test_story_27_9_*`, marqueur `story_27_9` dans `pyproject.toml`. Le **DS ne doit pas** supposer greenfield : vérifier chaque AC, exécuter les gates du brief, compléter les manques, et ne pas marquer la story done sans gates exit 0.

### Previous story intelligence (27.8 → 27.9)

- Au lock (`lockRequired=true`), `LiveAuthShell` appelle déjà `resetCashflowDraft()` et `resetReceptionPosteUiState()` — le timeout/handoff **réutilise** ce chemin via fin session + lock screen 27.6.
- Brouillon Reception reste serveur-side après timeout ; lock screen sans métadonnées sensibles (27.8).
- Intersection modules (27.7) : toolbar handoff visible seulement si session active ; timeout ne contourne pas la garde module.

### Library / framework

- Backend : FastAPI, SQLAlchemy — réutiliser `DeviceOperatorSessionService`, `require_active_operator_context`, patterns audit 27.6.
- Front : React + hooks injectables (`clock` fake pour tests) ; modale Mantine cohérente lock screen 27.6.
- Distinction **lockout PIN Redis** (`shared_ws:pin_*`, story 27.6) vs **timeout inactivité** (session `last_activity_at`) — ne pas mélanger.

## Tasks / Subtasks

- [ ] **T1 — Backend service fin session / activité** (AC: invalidation serveur, audit timeout/manual)
  - [ ] T1.1 `end_active_session_for_device`, `record_activity` (throttle 30 s)
  - [ ] T1.2 Audit `SHARED_WORKSTATION_OPERATOR_LOCKED_MANUAL|TIMEOUT` sans PIN
  - [ ] T1.3 Auto-expire dans `require_active_operator_context` + code `SHARED_WORKSTATION_OPERATOR_SESSION_EXPIRED`
- [ ] **T2 — Backend API HTTP + OpenAPI** (AC: lock/handoff, heartbeat, statut enrichi)
  - [ ] T2.1 `POST …/operator-session/end` (reason manual_lock|handoff|timeout)
  - [ ] T2.2 `POST …/operator-session/activity` + rate limits
  - [ ] T2.3 `GET …/operator-session/status` enrichi (`last_activity_at`, `seconds_until_lock`)
  - [ ] T2.4 Validation timeout admin min 60 s / max 7200 s (27.3)
- [ ] **T3 — Frontend timer inactivité + modale avertissement** (AC: warning, continue, activité repousse)
  - [ ] T3.1 `useSharedWorkstationInactivityTimer` (clock injectable, debounce 1 s)
  - [ ] T3.2 `SharedWorkstationInactivityWarningModal` (60 s lead, testids)
  - [ ] T3.3 `SharedWorkstationInactivityProvider` monté dans `LiveAuthShell`
- [ ] **T4 — Frontend handoff / verrouiller** (AC: passer la main, même état sécurité)
  - [ ] T4.1 `SharedWorkstationHandoffToolbar` (boutons handoff + lock now)
  - [ ] T4.2 Client `shared-workstation-operator-session-client.ts` (`no-store`, headers device)
- [ ] **T5 — Non-régression 27.7–27.8** (AC: pas de fuite métier après lock)
  - [ ] T5.1 Timeout avec brouillon Reception → lock sans fuite ; draft API 403 sans opérateur
  - [ ] T5.2 « Passer la main » pendant wizard → reset UI réception
- [ ] **T6 — Gates** (AC: testabilité mocks/injection)
  - [ ] T6.1 pytest `-k story_27_9` + marqueur `pyproject.toml`
  - [ ] T6.2 Vitest timer/toolbar/client + e2e timeout-handoff
  - [ ] T6.3 `npm run lint` ; non-régression 27.6/27.8

## Dev Agent Record

### Agent Model Used

_(à remplir par DS)_

### Debug Log References

### Completion Notes List

### File List

### Change Log

- 2026-05-30 — Story 27.9 VS (validate, vs_loop=0) : PASS ; checklist VS ; alignement epics/ADR/runbook/27.6–27.8 ; prêt DS.
