# Story 27.6 : Lock screen PIN et session opérateur active

Status: review

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

**Story key :** `27-6-pin-lock-operator-session`  
**Epic :** 27 — Postes partagés enrôlés + PIN opérateur + PWA installable non-offline  
**Implementation artifact :** `_bmad-output/implementation-artifacts/27-6-pin-lock-operator-session.md`  
**Date CS :** 2026-05-30

## Dépendances (prérequis)

- **Stories 27.1–27.5 done** : registre `RegisteredDevice`, contexte serveur + garde `shared_workstation_guard`, panel SuperAdmin, enrôlement IndexedDB + credential device, PWA installable non-offline — fichiers `_bmad-output/implementation-artifacts/27-1-registered-device.md` … `27-5-installable-pwa-non-offline.md`.
- **Story 27.2 (socle critique)** : table `device_operator_sessions`, `DeviceOperatorSessionService.start_session` / `end_session`, `require_active_operator_context`, audit `DEVICE_OPERATOR_SESSION_*` — `_bmad-output/implementation-artifacts/27-2-server-context-audit.md`.
- **Story 27.4 (identité poste)** : en-têtes `X-Recyclique-Device-Id` / `X-Recyclique-Device-Credential`, `device-identity-store.ts` (IndexedDB), route `/shared-workstation/enroll` — `_bmad-output/implementation-artifacts/27-4-enrollment-reconnect-replace.md`.
- **Epic 27 — cadrage gelé** : `_bmad-output/planning-artifacts/epics.md` (§ Epic 27, Story 27.6).
- **Mini-ADR Epic 27** : `references/artefacts/2026-05-29_02_mini-adr-postes-partages-pin-non-offline.md` — § Invariants (PIN serveur, rate-limit, audit sans PIN, refus sans opérateur actif).
- **Cadrage produit** : `references/artefacts/2026-05-29_01_cadrage-postes-partages-pin-operateur.md` — §3.2–§3.4 (PIN opérateur vs auth technique, écran verrouillé, accès post-PIN).
- **Runbook orchestration** : `references/artefacts/2026-05-29_04_runbook-orchestration-epic-27-postes-partages-pin.md` — ordre §4, invariants §7, gates sécurité §8.
- **Contrat OpenAPI** : `contracts/openapi/recyclique-api.yaml` — **cette story étend** le contrat (routes PIN poste partagé + schémas lockout / session).
- **ADR brownfield PIN (distinction)** : `_bmad-output/planning-artifacts/architecture/2026-04-19-adr-pin-kiosque-vs-pin-operateur-secret-poste-step-up-lockout-offline.md` — ne pas confondre `POST /v1/auth/pin` (caisse / JWT), `X-Step-Up-Pin` (mutations step-up) et le **PIN poste partagé** Epic 27.
- **Stories suivantes (ne pas implémenter ici)** : 27.7 (intersection serveur modules), 27.8 (brouillons Reception), 27.9 (timeout / passer la main / verrouillage manuel complet), 27.10 (override SuperAdmin).

## Garde-fous ADR / runbook (obligatoires pour le DS)

| Invariant | Application story 27.6 |
|-----------|-------------------------|
| PIN vérifié côté serveur | Hash `User.hashed_pin` via `verify_password` ; **jamais** de comparaison PIN côté front. |
| Rate-limit / lockout | Compteur **5 échecs → lockout 5 min** sur la paire **`device_id + operator_user_id`** (défaut proposé epics.md) ; clés Redis dédiées, **distinctes** de `step_up:pin_*` (step-up = `user_id` seul, 15 min). |
| Aucun PIN en logs/audit | `sanitize_audit_details` + grep revue ; audit avec `outcome` / `operation` uniquement — **pas** de PIN, hash PIN, `step_up_pin`, ni dérivé. |
| Lock screen terrain | Plein écran sans données métier ni navigation métier tant qu’aucune session opérateur active. |
| Session opérateur active | Succès PIN → `DeviceOperatorSessionService.start_session` ; une seule session `active` par `device_id` (règle 27.2). |
| Refus modules sans PIN | Routes protégées `require_active_operator_context` restent en **403** ; le front **masque** le shell métier derrière le lock screen. |
| Pas timeout complet | **Aucun** timer inactivité produit, **aucun** avertissement pré-verrouillage, **aucun** bouton « passer la main » fonctionnel — story **27.9**. Hooks `last_activity_at` / constantes device **documentés seulement** pour branchement futur. |
| Pas intersection modules | **Ne pas** filtrer la navigation par `site × allowlist poste × permissions` — story **27.7**. Post-PIN MVP : état « session active » + accès shell existant (projection non filtrée acceptable temporairement). |
| Appareil personnel admin hors lock screen | Lock screen **uniquement** si identité poste IndexedDB présente **et** device `shared_workstation` actif ; compte SuperAdmin / admin sans enrôlement poste → parcours auth classique inchangé. |
| Pas offline / pas authz front | Endpoints PIN `Cache-Control: no-store` ; le front ne décide jamais seul qu’un opérateur est actif. |
| Pas `localStorage` autoritaire | Ne pas persister PIN, état opérateur actif, ni lockout côté client comme source de vérité ; état session = **vérité serveur** (poll / refresh contexte). |
| Distinction PIN existants | **Ne pas** réutiliser `POST /v1/auth/pin` pour le lock screen poste partagé (retourne JWT caisse — comportement brownfield distinct). **Ne pas** exiger `X-Step-Up-Pin` pour démarrer la session opérateur. |
| `device_id` canonique | Distinct de `cash_register_id` et `reception_post_id`. |

## Story (BDD)

As a **field operator**,  
I want to **take control of a shared workstation with my PIN**,  
So that **actions are attributed to me and modules remain inaccessible before I am active**.

## Acceptance criteria

Source normative : `_bmad-output/planning-artifacts/epics.md` — **Story 27.6**.

**Given** a workstation is enrolled and server context can include `device_id`  
**When** no operator PIN session is active  
**Then** the workstation shows a locked screen with no business data and no module access  
**And** PIN verification is server-side only  
**And** PIN is never stored locally and never logged  
**And** rate-limit / lockout exists with a documented default proposal of 5 failures → 5 minute lockout on `device_id + operator_user_id`  
**And** UI failure messages are neutral and do not leak whether a PIN or account exists  
**And** a SuperAdmin unblock path is available or explicitly specified  
**And** successful and failed PIN attempts and operator changes are audited  
**And** timeout, warning before lock and handoff behavior are explicitly deferred to Story 27.9

### Interprétation exécutable

#### 1. Modèle mental — trois paliers d’auth (ne pas fusionner)

| Palier | Mécanisme existant | Rôle story 27.6 |
|--------|-------------------|-----------------|
| Auth web technique | JWT (`LiveAuthShell`, `POST /v1/auth/login`) | Peut exister sur poste partagé (compte technique / opérateur connecté) — **ne remplace pas** le PIN opérateur métier. |
| Identité poste | Credential device (27.4) — en-têtes `X-Recyclique-Device-Id` + `X-Recyclique-Device-Credential` | Preuve que le navigateur est un poste enrôlé. |
| Opérateur actif | **Nouveau flux PIN poste partagé** | Vérifie `User.hashed_pin` + démarre `DeviceOperatorSession`. |

Le lock screen s’affiche quand **identité poste valide** + **pas de session opérateur active** (vérité serveur).

#### 2. Backend — service vérification PIN poste partagé

Nouveau module suggéré : `services/shared_workstation_operator_pin_service.py`.

Responsabilités :

1. **`verify_and_start_session(*, device_id, operator_user_id, pin_plain, redis_client, db, request_id)`**
   - Préconditions : device `active` + type `shared_workstation` ; credential device déjà validé par la couche HTTP.
   - Vérifier lockout Redis clé `shared_ws:pin_lockout:{device_id}:{operator_user_id}` — si présente → **429** `SHARED_WORKSTATION_PIN_LOCKED` (message neutre).
   - Charger opérateur ; refus **neutre** si utilisateur absent, inactif, ou sans `hashed_pin` (même code/message que PIN invalide côté client — voir §5).
   - `verify_password(pin_plain, user.hashed_pin)` :
     - **Échec** : incrémenter compteur `shared_ws:pin_fail:{device_id}:{operator_user_id}` (fenêtre glissante **5 min**, TTL clé = 300 s) ; à **5 échecs** → lockout **5 min** ; audit échec ; **403** neutre.
     - **Succès** : effacer compteur échecs ; appeler `DeviceOperatorSessionService.start_session(...)` ; audit succès + changement opérateur si supersession ; retourner contexte session (sans PIN).
2. **`clear_lockout(*, device_id, operator_user_id, redis_client)`** — appelé par route SuperAdmin déblocage.
3. **`end_operator_session(*, device_id, db)`** — fin explicite session active (préparation 27.9 ; **optionnel MVP** si lock screen a bouton « Verrouiller » minimal — voir § hors scope).

Constantes documentées (module-level) :

```python
SHARED_WS_PIN_MAX_FAILURES = 5
SHARED_WS_PIN_LOCKOUT_SECONDS = 300  # 5 minutes
SHARED_WS_PIN_FAIL_WINDOW_SECONDS = 300
```

**Fail-open Redis** (aligné `step_up.py`) : si Redis indisponible, lockout **non appliqué** ; PIN + permissions restent obligatoires ; logger warning sans PIN.

#### 3. Backend — API HTTP (OpenAPI + implémentation)

Préfixe existant : `/v1/shared-workstation/` (`endpoints/shared_workstation.py`).

| Opération | Méthode | Auth | Comportement |
|-----------|---------|------|--------------|
| Vérifier PIN + démarrer session | `POST …/operator-pin/verify` | Credential device **obligatoire** ; JWT utilisateur **optionnel** (acteur audit si présent) | Body : `{ "operator_user_id": "uuid", "pin": "1234" }` — 4 chiffres, validation Pydantic réutilisant règle `PinSetRequest`. Headers device requis. Succès **200** : `{ "session_id", "device_id", "operator_user_id", "site_id", "started_at" }` + `Cache-Control: no-store`. |
| Statut session opérateur | `GET …/operator-session/status` | Credential device | Retourne `{ "active": bool, "operator_user_id": null \| uuid, "session_id": null \| uuid }` — **sans** données métier ; `no-store`. |
| Déblocage lockout PIN | `POST /v1/registered-devices/{device_id}/clear-operator-pin-lockout` | `SUPER_ADMIN` | Body : `{ "operator_user_id": "uuid" }` — efface clés Redis fail+lockout ; audit `SHARED_WORKSTATION_PIN_LOCKOUT_CLEARED`. |

Codes d’erreur stables (corps `{ "code", "message" }`) :

| Code | HTTP | Quand |
|------|------|-------|
| `SHARED_WORKSTATION_PIN_INVALID` | 403 | PIN incorrect ou opérateur non éligible (message **identique** — pas de fuite existence compte/PIN). |
| `SHARED_WORKSTATION_PIN_LOCKED` | 429 | Lockout actif sur device+opérateur. |
| `SHARED_WORKSTATION_PIN_NOT_CONFIGURED` | 403 | Opérateur sans PIN — **code distinct** en API ; **texte UI identique** à `SHARED_WORKSTATION_PIN_INVALID` (anti-énumération par message, pas par code HTTP). |
| `SHARED_WORKSTATION_OPERATOR_REQUIRED` | 403 | Inchangé (27.2) — routes métier sans session. |
| `DEVICE_CREDENTIAL_REVOKED` | 403 | Inchangé (27.4). |

**Ne pas** modifier le contrat sémantique de `POST /v1/auth/pin` ni brancher le lock screen dessus.

Rate-limit HTTP complémentaire : `@conditional_rate_limit("10/minute")` sur `operator-pin/verify` par IP (en plus du lockout métier device+opérateur).

#### 4. Backend — audit transversal

Étendre `AuditActionType` (`models/audit_log.py`) :

| Valeur enum | Quand |
|-------------|--------|
| `SHARED_WORKSTATION_PIN_SUCCESS` | PIN valide, session démarrée ou opérateur changé. |
| `SHARED_WORKSTATION_PIN_FAILURE` | Échec vérification (sans détail PIN). |
| `SHARED_WORKSTATION_PIN_LOCKOUT` | Seuil échecs atteint, lockout appliqué. |
| `SHARED_WORKSTATION_PIN_LOCKOUT_CLEARED` | Déblocage SuperAdmin. |

Helpers dans `core/audit.py` (pattern `log_device_operator_session_started`) :

- Champs merge : `device_id`, `operator_user_id`, `site_id`, `session_id`, `outcome`, `request_id`.
- **Interdit** : `pin`, `hashed_pin`, `step_up_pin`, secret device.

Sur changement d’opérateur (nouveau PIN alors qu’une session active existe) : audit **succès** + `DEVICE_OPERATOR_SESSION_ENDED` (reason=`superseded`) + `DEVICE_OPERATOR_SESSION_STARTED` — traçabilité « changement d’opérateur actif » exigée par mini-ADR.

#### 5. Frontend — lock screen (Peintre_nano)

Nouveau domaine suggéré : `peintre-nano/src/domains/shared-workstation/SharedWorkstationLockScreen.tsx` (+ provider `SharedWorkstationOperatorSessionProvider.tsx`).

**Déclenchement lock screen** (toutes conditions) :

1. `loadDeviceIdentity()` retourne un enregistrement valide (IndexedDB 27.4).
2. `GET /v1/shared-workstation/operator-session/status` (avec en-têtes device) retourne `active: false`.
3. Device status ≠ `revoked` / `identity_lost` (sinon bannière renvoi enrôlement 27.4 — pas lock screen PIN).

**UI lock screen (MVP)** :

- Plein écran (`position: fixed`, z-index au-dessus du shell) — compatible PWA standalone.
- Affiche nom poste / site si disponible via `device-status` (données non sensibles).
- Saisie **identifiant opérateur** : MVP = champ UUID ou sélecteur utilisateur simplifié (liste restreinte **interdite** sans API dédiée — préférer saisie `operator_user_id` UUID ou login username résolu côté API si extension acceptée ; **proposition DS** : body accepte `operator_user_id` UUID ; UI terrain = champ « Identifiant opérateur » + clavier PIN 4 chiffres).
- Clavier numérique PIN 4 chiffres ; **ne pas** persister PIN (ni `sessionStorage` / `localStorage` / IndexedDB).
- Messages d’erreur **neutres** : « Identifiant ou PIN incorrect », « Trop de tentatives — réessayez dans quelques minutes ».
- État lockout : lire code **429** + désactiver saisie jusqu’à expiry (header `Retry-After` optionnel ou durée fixe 5 min documentée).

**Intégration shell** :

- Brancher dans `LiveAuthShell.tsx` **après** auth JWT et **après** détection identité poste — pattern similaire whitelist `/shared-workstation/enroll`.
- Tant que lock screen actif : **ne pas rendre** `children` (navigation / widgets métier) — aucune donnée métier visible.
- Après succès PIN : refresh `GET /v1/users/me/context` (si JWT) + poll session status ; masquer lock screen.

**Appareil personnel admin (hors lock screen)** :

- Si **pas** d’identité IndexedDB → aucun lock screen (parcours admin classique).
- Si SuperAdmin sur laptop sans enrôlement → inchangé.
- Test non-régression : login admin sans device identity ne montre jamais le lock screen.

Client API suggéré : `peintre-nano/src/api/shared-workstation-operator-pin-client.ts` — `fetch` avec `cache: 'no-store'`, en-têtes device depuis `device-identity-store.ts`.

#### 6. Frontend — CREOS / registre (minimal)

- Enregistrer widget `shared-workstation.lock-screen` si pattern widget requis ; **acceptable MVP** : composant shell sans manifeste page dédiée (lock overlay global).
- **Ne pas** ajouter de routes métier accessibles sans session opérateur.
- testids : `shared-workstation-lock-screen`, `shared-workstation-pin-input`, `shared-workstation-operator-id`, `shared-workstation-pin-submit`.

#### 7. ContextEnvelope / refresh

- Après PIN succès : `build_context_envelope` doit refléter `operator_user_id` + `device_id` quand session active (extension 27.2 déjà en place — **vérifier** branchement sur refresh contexte avec en-têtes device).
- Le front envoie `X-Recyclique-Device-Id` (+ credential) sur refresh contexte post-PIN.

#### 8. Tests obligatoires (gates story)

Backend — fichier suggéré : `recyclique/api/tests/test_story_27_6_pin_lock_operator_session.py` (marqueur pytest `story_27_6`).

| # | Cas |
|---|-----|
| 1 | PIN valide + credential device → session `active`, 200, audit `SHARED_WORKSTATION_PIN_SUCCESS`. |
| 2 | PIN invalide → 403 neutre, audit failure, **pas** de PIN dans details audit. |
| 3 | 5 échecs consécutifs → lockout 429, audit lockout. |
| 4 | Pendant lockout → 429 même avec PIN correct. |
| 5 | SuperAdmin clear lockout → retry PIN OK. |
| 6 | Sans session opérateur → `GET /shared-workstation/context` reste 403 (non-régression 27.2). |
| 7 | Changement opérateur (deux PIN successifs users différents) → session superseded + audits changement. |
| 8 | `sanitize_audit_details({"pin": "1234"})` → `[REDACTED]` sur chemins PIN poste partagé. |
| 9 | Credential device invalide → 403 avant toute vérif PIN. |

Frontend :

- `peintre-nano/tests/unit/shared-workstation-lock-screen.test.tsx` — lock screen affiché si device identity mock + session inactive ; masqué après succès mock API.
- `peintre-nano/tests/unit/shared-workstation-operator-pin-client.test.ts` — URLs, headers device, pas de body PIN en log.
- E2E suggéré : `peintre-nano/tests/e2e/shared-workstation-pin-lock-27-6.e2e.test.tsx` — parcours enroll → lock → PIN → shell visible.
- Non-régression : `live-auth-shell-11-2.test.tsx` (admin sans device identity).

Commandes gates (Story Runner brief) :

```bash
cd recyclique/api && python -m pytest tests/ -k story_27_6 -q
cd peintre-nano && npm run lint
cd peintre-nano && npm run test -- --run
```

### Hors scope explicite

- Intersection modules `site × allowlist × permissions` (**27.7**).
- Brouillons Reception masqués / reprise (**27.8**).
- Timeout inactivité, avertissement pré-verrouillage, bouton « passer la main » complet, verrouillage manuel terrain (**27.9**).
- Override SuperAdmin contexte (**27.10**).
- Modification sémantique `POST /v1/auth/pin` (caisse / JWT).
- Remplacement du step-up `X-Step-Up-Pin` sur mutations sensibles.
- QR code, sélection opérateur avec liste nominative sans API, offline, cache PIN.
- Filtrage navigation CREOS par allowlist poste (attendre 27.7).
- Nouveau rôle local « responsable de site ».
- Modification `sprint-status.yaml` depuis CS/DS (writer unique Epic Runner).

### Dépendances 27.1–27.5 (réutilisation obligatoire)

| Story | Réutiliser (ne pas réécrire) |
|-------|------------------------------|
| 27.1 | `RegisteredDevice`, statuts, `allowed_module_keys` (lecture seule — pas de filtrage ici). |
| 27.2 | `DeviceOperatorSessionService`, `require_active_operator_context`, `SharedWorkstationContextService`, audit session started/ended. |
| 27.3 | Route SuperAdmin déblocage lockout (auth `SUPER_ADMIN`). |
| 27.4 | `verify_device_credential_or_raise`, `device-identity-store.ts`, en-têtes device, `/shared-workstation/enroll`. |
| 27.5 | Lock screen compatible PWA standalone ; pas de cache SW sur endpoints PIN. |

### Anti-patterns (interdits)

- Stocker PIN ou état « déverrouillé » dans `localStorage` / `sessionStorage` comme autorité.
- Décider côté front qu’un opérateur est actif sans réponse serveur récente.
- Réutiliser `POST /v1/auth/pin` pour le lock screen poste partagé.
- Logger `pin`, `payload.pin`, ou PIN dans messages d’exception.
- Messages d’erreur du type « utilisateur inconnu » vs « PIN incorrect » (énumération).
- Appliquer lockout step-up global (`stepup:pin_lockout:{user_id}`) à la place du lockout device+opérateur.
- Afficher données métier (dashboard, KPI, listes) sous le lock screen.
- Lock screen sur appareil admin sans identité poste IndexedDB.
- Implémenter timer inactivité ou handoff (27.9) « parce que c’est dans le cadrage ».
- Calculer intersection modules ou masquer brouillons Reception (27.7 / 27.8).

### Testing / gates (Story Runner)

| Gate | Commande / critère |
|------|-------------------|
| Tests backend 27.6 | `cd recyclique/api && python -m pytest tests/ -k story_27_6 -q` → exit 0 |
| Non-régression Epic 27 | `pytest tests/test_story_27_2_shared_workstation_context.py tests/test_story_27_4_enrollment_reconnect_replace.py -q` |
| Lint front | `cd peintre-nano && npm run lint` → exit 0 |
| Tests front | `cd peintre-nano && npm run test -- --run` → exit 0 |
| Revue sécurité | grep `pin` dans logs/audit helpers ; aucun PIN clair ; messages UI neutres |
| OpenAPI | Schémas ↔ Pydantic ; operationIds stables `recyclique_sharedWorkstation_*` |
| YAML sprint (parent) | lecture seule — pas de write CS/DS |

`gates_skipped_with_hitl: false` — aucun skip pour authz, PIN, audit, lockout.

### Project Structure Notes

| Zone | Fichiers / dossiers |
|------|---------------------|
| Service PIN | `recyclique/api/src/recyclic_api/services/shared_workstation_operator_pin_service.py` |
| Endpoints | `recyclique/api/src/recyclic_api/api/api_v1/endpoints/shared_workstation.py` (+ admin registered_devices pour unblock) |
| Schémas | `recyclique/api/src/recyclic_api/schemas/shared_workstation_operator_pin.py` (suggéré) |
| Audit | `recyclique/api/src/recyclic_api/core/audit.py`, `models/audit_log.py` |
| Tests back | `recyclique/api/tests/test_story_27_6_pin_lock_operator_session.py` |
| Lock screen UI | `peintre-nano/src/domains/shared-workstation/SharedWorkstationLockScreen.tsx` |
| Provider session | `peintre-nano/src/domains/shared-workstation/SharedWorkstationOperatorSessionProvider.tsx` |
| Client API | `peintre-nano/src/api/shared-workstation-operator-pin-client.ts` |
| Shell | `peintre-nano/src/app/auth/LiveAuthShell.tsx` |
| Tests front | `peintre-nano/tests/unit/shared-workstation-lock-screen.test.tsx`, `shared-workstation-operator-pin-client.test.ts` |
| Contrat | `contracts/openapi/recyclique-api.yaml` |

### References

- `_bmad-output/planning-artifacts/epics.md` — Epic 27, Story 27.6
- `_bmad-output/implementation-artifacts/27-2-server-context-audit.md`
- `_bmad-output/implementation-artifacts/27-4-enrollment-reconnect-replace.md`
- `_bmad-output/implementation-artifacts/27-5-installable-pwa-non-offline.md`
- `references/artefacts/2026-05-29_02_mini-adr-postes-partages-pin-non-offline.md`
- `references/artefacts/2026-05-29_01_cadrage-postes-partages-pin-operateur.md` — §3.2–§3.4
- `references/artefacts/2026-05-29_04_runbook-orchestration-epic-27-postes-partages-pin.md` — §7–§8
- `recyclique/api/src/recyclic_api/core/step_up.py` — pattern lockout Redis (à ne pas confondre)
- `recyclique/api/src/recyclic_api/api/api_v1/endpoints/auth.py` — `POST /pin` brownfield (hors scope lock screen)
- `recyclique/api/src/recyclic_api/services/device_operator_session_service.py`
- `contracts/openapi/recyclique-api.yaml`
- `_bmad-output/project-context.md`

## Trace Epic 27 — ADR

| Élément | Valeur |
|--------|--------|
| Nouvelle ADR structurante requise ? | **ADR N/A pour 27.6** — implémentation mini-ADR § Invariants PIN + cadrage §3.3–§3.4. |
| ADR applicables | Mini-ADR 2026-05-29 ; ADR 2026-04-19 (distinction PIN kiosque / opérateur / step-up). |

## Alignement sprint / YAML

- Clé **`27-6-pin-lock-operator-session`** : **non modifiée** par ce worker CS (writer unique Epic Runner — pas de passage `ready-for-dev` dans `sprint-status.yaml` depuis CS).
- **`epic-27`** : inchangé par CS.
- Prochaine story après clôture 27.6 : **`27-7-server-module-intersection`** (ordre runbook §4).

## Risques / HITL

| Sujet | Statut | Action |
|-------|--------|--------|
| Politique lockout finale (5×5 min) | Risque epics | Proposition par défaut documentée ; HITL Strophe si autre seuil exigé avant prod. |
| Saisie `operator_user_id` vs username terrain | **Décision VS (vs_loop=0)** | **MVP 27.6** : body + UI = `operator_user_id` **UUID** uniquement ; pas d’extension `operator_username` ni liste nominative — HITL Strophe seulement si terrain rejette l’UUID avant prod. |
| Compte technique JWT + PIN opérateur | Cadrage §3.2 | Documenter parcours : login web possible puis lock screen ; pas de double JWT. |
| Fail-open Redis lockout | Aligné step_up | Accepté MVP ; mentionner en doc ops. |
| Bouton « Verrouiller » minimal | Hors scope 27.9 | **Ne pas** livrer en 27.6 sauf HITL explicite. |
| Filtrage nav post-PIN sans 27.7 | Connu | Acceptable temporairement ; 27.7 rattrape intersection. |

**NEEDS_STROPHE_HITL** : non requis pour démarrer le DS si le dev suit les propositions ci-dessus (endpoint dédié, lockout device+opérateur 5×5 min, lock screen overlay, déblocage SuperAdmin).

## Checklist VS (validate-create-story)

**Verdict VS :** **PASS** (vs_loop=0) — story prête pour DS.

- [x] AC BDD alignés `epics.md` §27.6 (lock screen, PIN serveur, lockout, audit, messages neutres, déblocage SuperAdmin, defer 27.9).
- [x] Garde-fous mini-ADR + runbook §7 (PIN serveur, pas PIN en audit, pas authz front, admin hors lock screen).
- [x] Dépendances 27.2, 27.3, 27.4 explicites ; réutilisation `DeviceOperatorSessionService`.
- [x] Distinction `POST /auth/pin`, `X-Step-Up-Pin`, PIN poste partagé documentée.
- [x] Hors scope 27.7–27.10 explicite.
- [x] Gates § Testing (pytest `story_27_6`, lint, vitest, revue no-PIN-in-log).
- [x] Anti-patterns couvrent localStorage PIN, réutilisation auth/pin, timeout/handoff.
- [x] `sprint-status.yaml` non modifié par CS/VS (writer unique Epic Runner).
- [x] OpenAPI ↔ implémentation (`operator-pin/verify`, `operator-session/status`, `clear-operator-pin-lockout`) ; `Retry-After` sur 429 documenté (recommandé DS ; repli UI 5 min si absent).

## Definition of Done

- [x] Service `SharedWorkstationOperatorPinService` + lockout Redis device+opérateur (5→5 min).
- [x] Routes `POST …/operator-pin/verify`, `GET …/operator-session/status`, SuperAdmin clear lockout.
- [x] OpenAPI aligné ; `Cache-Control: no-store` sur routes PIN/session.
- [x] Audit `SHARED_WORKSTATION_PIN_*` sans PIN ni dérivé.
- [x] Lock screen plein écran Peintre ; aucune donnée métier sans session active.
- [x] Admin sans identité poste : pas de lock screen (test non-régression).
- [x] Tests `test_story_27_6_*` + tests UI lock screen — **exit 0**.
- [x] **Hors scope respecté** : pas timeout/handoff (27.9), pas intersection modules (27.7), pas brouillons Reception (27.8), pas override (27.10).
- [x] Revue grep : aucun PIN en clair logs/audit.
- [x] **Hors scope respecté** : pas de modification `sprint-status.yaml` / `epics.md` par le worker DS.

## Tasks / Subtasks (DS)

- [x] **Service PIN poste partagé** : vérification hash, lockout Redis, branchement `start_session` (AC: PIN serveur + lockout).
- [x] **Endpoints API** : verify, session status, clear lockout SuperAdmin + schémas Pydantic (AC: contrat OpenAPI).
- [x] **Audit** : enum + helpers succès/échec/lockout/clear ; sanitize (AC: audit sans PIN).
- [x] **Client API front** : `shared-workstation-operator-pin-client.ts` avec en-têtes device (AC: network-only).
- [x] **Lock screen UI** : overlay plein écran + intégration `LiveAuthShell` (AC: pas de données métier sans PIN).
- [x] **Provider session** : poll statut serveur, refresh contexte post-PIN (AC: vérité serveur).
- [x] **Tests backend** : suite `test_story_27_6_*` (AC: gates pytest).
- [x] **Tests frontend** : unit lock screen + client ; e2e optionnel (AC: gates vitest).
- [x] **Revue périmètre** : grep PIN logs ; non-régression admin sans device identity.

## Dev Notes

### Contexte brownfield — PIN existants

| Mécanisme | Fichier | Usage 27.6 |
|-----------|---------|------------|
| `POST /v1/auth/pin` | `endpoints/auth.py` | Caisse — retourne JWT ; **ne pas réutiliser** pour lock screen. |
| `X-Step-Up-Pin` | `core/step_up.py` | Mutations sensibles (clôture caisse, etc.) — orthogonal. |
| `PUT /v1/users/me/pin` | `endpoints/users.py` | Configuration PIN utilisateur — prérequis opérateur. |
| `DeviceOperatorSessionService.start_session` | `services/device_operator_session_service.py` | **Brancher ici** après vérif PIN. |

### Previous story intelligence (27.5 → 27.6)

- PWA standalone : lock screen doit couvrir tout le viewport installé.
- IndexedDB identité poste partage l’origine avec PWA — lock screen s’appuie sur `loadDeviceIdentity()`.
- SW ne cache pas les API — les appels PIN passent toujours au réseau.
- `LiveAuthShell` whitelist déjà `/shared-workstation/enroll` — étendre logique **après** login pour lock overlay.

### Brownfield / implémentation partielle (CS 2026-05-30)

Sur la branche courante, des fichiers **peuvent déjà exister** (WIP parallèle) : `shared_workstation_operator_pin_service.py`, routes dans `shared_workstation.py` / `registered_devices.py`, lock screen + provider front, tests `test_story_27_6_*`, marqueur `story_27_6` dans `pyproject.toml`. Le **DS ne doit pas** supposer greenfield : vérifier chaque ligne de la Definition of Done, exécuter les gates du brief, compléter les manques (ex. e2e `shared-workstation-pin-lock-27-6` encore optionnel), et ne pas marquer la story done sans gates exit 0.

### Library / framework

- Backend : FastAPI, SQLAlchemy, Redis (lockout — même client que step-up via dependency existante).
- Front : React + Mantine (aligner styles lock screen sur shell existant).
- Hash PIN : `verify_password` / `hash_password` (`core/security.py`) — `User.hashed_pin`.

### Architecture compliance

- Autorité serveur : session opérateur = row `device_operator_sessions` + garde API 27.2.
- Contrat erreur stable : `{ code, message }` (+ `correlation_id` si middleware).
- Tests pytest : ajouter le marqueur `story_27_6` dans `recyclique/api/pyproject.toml` (même pattern que `story_27_5` — obligatoire avant merge).

## Dev Agent Record

### Agent Model Used

Composer (worker bmad-dev-story, resume_at DS)

### Debug Log References

- Correction test `test_invalid_pin_403_neutral_no_pin_in_audit` : assertion sur `kwargs` (éviter faux positif adresse mémoire contenant `0000`).

### Completion Notes List

- Backend : `SharedWorkstationOperatorPinService` (verify + lockout Redis `shared_ws:pin_*`, fail-open si Redis indispo), routes `/operator-pin/verify`, `/operator-session/status`, SuperAdmin `clear-operator-pin-lockout`, audit `SHARED_WORKSTATION_PIN_*`, marqueur pytest `story_27_6`.
- Front : lock screen overlay, provider poll 30s, intégration `LiveAuthShell` (masque `children` si lock requis), client API `no-store` + en-têtes device.
- Gates locaux : pytest `-k story_27_6` 9/9 ; `npm run lint` OK ; vitest 797/797 OK.
- `sprint-status.yaml` non modifié (policy Epic Runner).

### File List

- `recyclique/api/src/recyclic_api/services/shared_workstation_operator_pin_service.py`
- `recyclique/api/src/recyclic_api/schemas/shared_workstation_operator_pin.py`
- `recyclique/api/src/recyclic_api/api/api_v1/endpoints/shared_workstation.py`
- `recyclique/api/src/recyclic_api/api/api_v1/endpoints/registered_devices.py`
- `recyclique/api/src/recyclic_api/core/audit.py`
- `recyclique/api/src/recyclic_api/models/audit_log.py`
- `recyclique/api/src/recyclic_api/services/device_operator_session_service.py`
- `recyclique/api/tests/test_story_27_6_pin_lock_operator_session.py`
- `recyclique/api/pyproject.toml`
- `contracts/openapi/recyclique-api.yaml`
- `peintre-nano/src/api/shared-workstation-operator-pin-client.ts`
- `peintre-nano/src/api/recyclique-auth-client.ts`
- `peintre-nano/src/domains/shared-workstation/SharedWorkstationLockScreen.tsx`
- `peintre-nano/src/domains/shared-workstation/SharedWorkstationOperatorSessionProvider.tsx`
- `peintre-nano/src/app/auth/LiveAuthShell.tsx`
- `peintre-nano/tests/unit/shared-workstation-lock-screen.test.tsx`
- `peintre-nano/tests/unit/shared-workstation-operator-pin-client.test.ts`
- `peintre-nano/tests/unit/live-auth-shell-11-2.test.tsx`

## Change Log

- 2026-05-30 — Story 27.6 CS (create) : guide dev lock screen PIN + session opérateur ; garde-fous ADR/runbook §7 ; endpoints dédiés poste partagé ; lockout device+opérateur 5×5 min ; Status `ready-for-dev` ; sprint-status non modifié (writer unique).
- 2026-05-30 — Story 27.6 CS (re-pass worker) : revalidation epics §27.6 + mini-ADR + runbook §7–§8 ; checklist VS remise à vide pour worker VS ; note brownfield WIP ; dépendance 27.3 (déblocage SuperAdmin) explicite dans checklist VS.
- 2026-05-30 — Story 27.6 VS (validate) : **PASS** (vs_loop=0) — AC epics §27.6 recoupés ; invariants runbook §7 / mini-ADR couverts ; endpoints OpenAPI déjà présents dans le contrat ; décision MVP `operator_user_id` UUID tranchée sans NEEDS_HITL ; `sprint-status.yaml` non modifié.
- 2026-05-30 — Story 27.6 DS : implémentation validée ; gates pytest story_27_6 / lint / vitest exit 0 ; Status `review` ; sprint-status inchangé.
