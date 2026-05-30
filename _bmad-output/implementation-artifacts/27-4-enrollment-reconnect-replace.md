# Story 27.4 : Enrôlement, reconnexion et remplacement

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

**Story key :** `27-4-enrollment-reconnect-replace`  
**Epic :** 27 — Postes partagés enrôlés + PIN opérateur + PWA installable non-offline  
**Implementation artifact :** `_bmad-output/implementation-artifacts/27-4-enrollment-reconnect-replace.md`  
**Date CS :** 2026-05-30

## Dépendances (prérequis)

- **Story 27.1 done** : modèle `RegisteredDevice`, statuts admin (`pending_enrollment`, `active`, `identity_lost`, `conflict`, `revoked`), API `/v1/registered-devices/` — `_bmad-output/implementation-artifacts/27-1-registered-device.md`.
- **Story 27.2 done** : contexte serveur, garde `shared_workstation_guard`, invalidation sessions, audit socle — `_bmad-output/implementation-artifacts/27-2-server-context-audit.md`.
- **Story 27.3 done** : panel SuperAdmin « Gestion des postes », audit mutations admin — `_bmad-output/implementation-artifacts/27-3-superadmin-device-management.md`.
- **Epic 27 — cadrage gelé** : `_bmad-output/planning-artifacts/epics.md` (§ Epic 27, Story 27.4).
- **Mini-ADR Epic 27** : `references/artefacts/2026-05-29_02_mini-adr-postes-partages-pin-non-offline.md` — identité poste enrôlée, secret local revocable, pas `localStorage`, flux reconnexion/conflit.
- **Cadrage produit** : `references/artefacts/2026-05-29_01_cadrage-postes-partages-pin-operateur.md` — §3.8 enrôlement, § flux reconnexion/remplacement.
- **Runbook orchestration** : `references/artefacts/2026-05-29_04_runbook-orchestration-epic-27-postes-partages-pin.md` — ordre §4, invariants §7, gates §8.
- **Contrat OpenAPI** : `contracts/openapi/recyclique-api.yaml` — schémas `RegisteredDeviceV1*` existants ; **cette story étend** le contrat (enrollment + credential).
- **Stories suivantes (ne pas implémenter ici)** : 27.5 (PWA installable), 27.6 (lock screen PIN + endpoints PIN publics), 27.7 (intersection modules), 27.9 (timeout complet).

## Garde-fous ADR / runbook (obligatoires pour le DS)

| Invariant | Application story 27.4 |
|-----------|-------------------------|
| Poste enrôlé, pas deviné | Aucun fingerprinting navigateur, MAC, discovery réseau, agent local. |
| Secret local revocable | Hash serveur uniquement ; jamais secret en clair en DB, logs ou audit. |
| Pas `localStorage` source de vérité | Persistance identité poste via **IndexedDB** (ou WebCrypto key store) — **interdit** `localStorage` / `sessionStorage` pour le secret ou `device_id` autoritaire. |
| WebCrypto cible si raisonnable | MVP = secret serveur émis + IndexedDB ; WebCrypto non exportable = **option** documentée, pas bloquante MVP. |
| Validation SuperAdmin | Code court généré côté SuperAdmin ; consommation = validation implicite (pas de QR MVP). |
| Révocation ancien secret | Remplacement et reconnexion **rotent** le credential ; ancien refusé. |
| Conflit explicite | Ancienne machine → refus + statut `conflict` + choix SuperAdmin audités. |
| Pas d'offline métier | Enrôlement et heartbeat device = réseau obligatoire ; `Cache-Control: no-store`. |
| Pas d'authz front | Le front stocke et envoie le secret ; le **serveur** valide et décide statuts/refus. |
| Pas de PIN | Aucun endpoint PIN opérateur, lock screen, session PIN UI (story **27.6**). |
| `device_id` canonique | Distinct de `cash_register_id` et `reception_post_id`. |
| Audit transversal | Événements enrôlement / reconnexion / remplacement / conflit via socle `audit_logs`. |

## Story (BDD)

As a **SuperAdmin and field operator**,  
I want a **controlled enrollment and replacement flow for shared workstations**,  
So that **a physical workstation is enrolled by the server rather than guessed by browser fingerprinting**.

## Acceptance criteria

Source normative : `_bmad-output/planning-artifacts/epics.md` — **Story 27.4**.

**Given** a SuperAdmin can manage `RegisteredDevice` entries  
**When** a workstation is enrolled  
**Then** the MVP flow uses a short code plus SuperAdmin validation  
**And** QR code remains an optional later improvement, not an MVP requirement  
**And** the workstation stores a local workstation identity/secret associated with the server record  
**And** `localStorage` is not used as the source of truth for the workstation identity/secret if a reasonable alternative exists  
**And** loss of local identity can be reconnected to an existing server workstation through SuperAdmin validation  
**And** replacement revokes the old secret  
**And** if an old machine returns with the old identity, it is refused or marked as conflict  
**And** SuperAdmin conflict choices are explicit: refuse, replace definitively, or create a distinct workstation

### Interprétation exécutable

#### 1. Modèle persistant — credentials device (serveur)

Créer une table dédiée (nom suggéré : **`registered_device_credentials`**) — **ne pas** stocker le secret en clair :

| Champ (concept) | Colonne / type suggéré | Règles |
|-----------------|------------------------|--------|
| Identifiant | `id` UUID PK | |
| Poste | `device_id` UUID FK → `registered_devices.id` NOT NULL | Index. |
| Empreinte secret | `secret_hash` VARCHAR(255) NOT NULL | bcrypt ou argon2 (pattern `hash_password` existant). |
| Préfixe identification | `secret_prefix` VARCHAR(8) NULL | 4–6 chars du secret pour support admin (jamais le secret complet). |
| Statut | `status` VARCHAR(32) NOT NULL | `active`, `revoked`, `superseded`. |
| Horodatage | `created_at`, `revoked_at` TIMESTAMPTZ | |
| Raison révocation | `revocation_reason` VARCHAR(64) NULL | ex. `replaced`, `reconnect`, `conflict_refused`, `admin_revoke`. |

**Règle MVP** : au plus **un** credential `active` par `device_id` (contrainte applicative + test ; index unique partiel si migration Postgres OK).

Migration Alembic réversible sous `recyclique/api/migrations/versions/`.

#### 2. Modèle persistant — codes d'enrôlement (serveur)

Table suggérée : **`device_enrollment_codes`** :

| Champ | Type | Règles |
|-------|------|--------|
| `id` | UUID PK | |
| `device_id` | UUID FK NOT NULL | Poste cible (`pending_enrollment`, `identity_lost`, `active` selon `purpose`). |
| `code` | VARCHAR(12) NOT NULL | Code court **humain** (ex. 8 chars alphanum uppercase, sans ambiguïté 0/O/1/I) ; **unique** tant que non consommé. |
| `purpose` | VARCHAR(32) NOT NULL | `initial_enrollment`, `reconnect`, `replace`. |
| `expires_at` | TIMESTAMPTZ NOT NULL | TTL proposé : **15 minutes** (constant documentée). |
| `consumed_at` | TIMESTAMPTZ NULL | Rempli à la consommation réussie. |
| `created_by_user_id` | UUID FK → `users.id` NOT NULL | SuperAdmin générateur. |

Génération : `secrets`-style ou `secrets.token_hex` tronqué — **pas** de code prédictible.

#### 3. API backend — génération code (SuperAdmin)

Nouvelles routes sous **`/v1/registered-devices/{device_id}/`** (auth `SUPER_ADMIN`) :

| Opération | Méthode | Comportement |
|-----------|---------|--------------|
| Générer code enrôlement | `POST …/enrollment-codes` | Body : `{ "purpose": "initial_enrollment" \| "reconnect" \| "replace" }`. Crée code TTL ; invalide codes non consommés expirés du même device+purpose ; retourne `{ code, expires_at, purpose }` **une seule fois** (le code en clair n'est pas re-listable). Audit `DEVICE_ENROLLMENT_CODE_ISSUED`. |
| Marquer identité perdue | `POST …/mark-identity-lost` | Transition device → `identity_lost` ; invalide credential `active` (`superseded`, raison `identity_lost`) ; audit `DEVICE_IDENTITY_LOST_MARKED`. Précondition : statut `active` ou `pending_enrollment` (pas `revoked`). |
| Résoudre conflit | `POST …/resolve-conflict` | Body : `{ "action": "refuse" \| "replace_definitively" \| "create_distinct" }` + champs si `create_distinct` (name). Voir §7. |

**Préconditions purpose** :

| `purpose` | Statut device attendu |
|-----------|----------------------|
| `initial_enrollment` | `pending_enrollment` |
| `reconnect` | `identity_lost` (ou `pending_enrollment` si jamais enrôlé — préférer initial) |
| `replace` | `active` ou `conflict` |

Réponse `Cache-Control: no-store`.

#### 4. API backend — complétion enrôlement (poste physique)

Route **semi-publique** (pas de JWT utilisateur requis ; **rate-limit** recommandé via middleware existant ou compteur simple IP) :

| Opération | Méthode | Comportement |
|-----------|---------|--------------|
| Compléter enrôlement | `POST /v1/shared-workstation/enroll/complete` | Body : `{ "code": "XXXXXXXX" }`. Valide code non expiré/non consommé ; génère **secret device** aléatoire (ex. 32 bytes urlsafe) ; retourne `{ device_id, device_secret, device_name, site_id }` **une seule fois** ; stocke hash serveur ; marque code consommé ; transition statut device → `active` (initial/reconnect/replace selon purpose) ; révoque credential `active` précédent en `superseded` si replace/reconnect ; met à jour `last_contact_at` ; audit `DEVICE_ENROLLED` / `DEVICE_RECONNECTED` / `DEVICE_REPLACED`. |

**Interdit** dans réponses et logs : PIN, secret dans audit `details_json` (utiliser `sanitize_audit_details` ; clés `secret`, `device_secret` déjà couvertes).

Codes erreur stables :

| Code | HTTP | Cas |
|------|------|-----|
| `ENROLLMENT_CODE_INVALID` | 400 | Code inconnu ou mal formé. |
| `ENROLLMENT_CODE_EXPIRED` | 410 | TTL dépassé. |
| `ENROLLMENT_CODE_CONSUMED` | 409 | Déjà utilisé. |
| `DEVICE_ENROLLMENT_STATE_INVALID` | 422 | Statut device incompatible avec purpose. |

#### 5. API backend — authentification device (credential)

Étendre la résolution poste pour valider le **secret device** sur les routes poste partagé (préparation 27.6) :

| Mécanisme | Détail |
|-----------|--------|
| En-tête | `X-Recyclique-Device-Credential` : secret émis à l'enrôlement (prioritaire sur device_id seul pour prouver la possession). |
| En-tête existant | `X-Recyclique-Device-Id` : doit matcher le device lié au credential. |
| Validation | Service `RegisteredDeviceCredentialService.verify(...)` : hash match + credential `active` + device `active` ; mise à jour `last_contact_at`. |
| Credential révoqué | 403 `DEVICE_CREDENTIAL_REVOKED` ; si tentative depuis ancienne machine après replace → audit + passage device en `conflict` si pas déjà traité. |
| Désalignement device_id / secret | 403 `DEVICE_IDENTITY_CONFLICT`. |

**Intégration garde 27.2** : étendre `extract_device_id` / `SharedWorkstationContextService.resolve_shared_workstation_context` pour accepter le couple device_id + credential **avant** exiger opérateur PIN (27.6). En 27.4, ajouter au minimum :

- `GET /v1/shared-workstation/device-status` — avec credential valide : retourne statut device, config allowlist, timeout (sans données métier opérateur).
- Mise à jour `GET /v1/shared-workstation/context` : si credential invalide/révoqué → 403 avant résolution opérateur.

**Ne pas** exiger session opérateur sur `enroll/complete` ni sur `device-status`.

#### 6. Flux reconnexion (identité locale perdue)

**Côté client** : si IndexedDB vide au boot app poste → écran « Identité locale perdue » + CTA « Reconnecter ce poste » (pas de crash silencieux).

**Côté serveur** :

1. SuperAdmin voit statut `identity_lost` dans panel (transition manuelle ou automatique — voir §7).
2. SuperAdmin génère code `purpose=reconnect`.
3. Opérateur saisit code sur poste → `enroll/complete` → nouveau secret, ancien credential `superseded`, statut → `active`.

**Détection `identity_lost`** (MVP — choix local Story Runner) :

- **Option A (recommandée)** : endpoint SuperAdmin `POST …/mark-identity-lost` + bouton panel ; **plus** auto-passage si `device-status` appelé avec device_id connu mais sans credential valide pendant X jours (Reporter heartbeat complexe — **non** en 27.4).
- **Option B minimale** : uniquement action SuperAdmin manuelle « Marquer identité perdue ».

Tranchage proposé : **Option B MVP** + endpoint admin ; auto-détection différée si besoin.

#### 7. Flux remplacement et conflit

**Remplacement planifié** (SuperAdmin, device `active`) :

1. `POST …/enrollment-codes` purpose=`replace`.
2. Nouvelle machine consomme code → nouveau secret ; ancien credential → `superseded`.
3. Sessions opérateur invalidées via `DeviceOperatorSessionService.invalidate_sessions_for_device` (pattern 27.2 revoke).

**Ancienne machine revient** :

1. Présente ancien secret → `verify` échoue (`superseded`/`revoked`).
2. Serveur : 403 + audit `DEVICE_IDENTITY_CONFLICT` ; device → `conflict` si credential actif existe ailleurs.
3. SuperAdmin panel — actions `resolve-conflict` :
   - **`refuse`** : maintient nouveau credential ; ancienne machine reste bloquée ; statut → `active` si résolu.
   - **`replace_definitively`** : équivalent rotate forcé — génère code replace, révoque tout credential non actif, statut → `active` après consommation ou immédiat selon implémentation documentée.
   - **`create_distinct`** : crée **nouveau** `RegisteredDevice` (nouveau `device_id`) pour l'ancienne machine ; l'ancien poste logique garde son identité ; audit avec les deux `device_id`.

**QR code** : **hors scope MVP** — ne pas implémenter ; mentionner en commentaire OpenAPI « future improvement ».

#### 8. Persistance client — identité poste (Peintre)

Nouveau module suggéré : `peintre-nano/src/domains/shared-workstation/device-identity-store.ts`

| Exigence | Implémentation |
|----------|----------------|
| Stockage | **IndexedDB** (API `idb` si déjà en deps, sinon wrapper minimal ~50 lignes) — base `recyclique-device-identity`, store `credentials`. |
| Clés stockées | `device_id`, `device_secret`, `enrolled_at` (metadata non autoritaire). |
| Interdit | `localStorage`, `sessionStorage` pour secret / device_id autoritaire. |
| API publique | `loadDeviceIdentity()`, `saveDeviceIdentity(...)`, `clearDeviceIdentity()`, `hasDeviceIdentity()`. |
| Injection requêtes | Helper `sharedWorkstationAuthHeaders()` ajoutant `X-Recyclique-Device-Id` + `X-Recyclique-Device-Credential` — brancher sur client API poste partagé futur ; en 27.4 au minimum sur appels `device-status` / bootstrap. |

**WebCrypto (optionnel, non bloquant)** : si implémenté, documenter dans Dev Notes ; clé non exportable + challenge signé = post-MVP sauf effort < 1 jour validé Story Runner.

#### 9. UI Peintre — enrôlement terrain

| Composant | Chemin / route suggérés |
|-----------|-------------------------|
| Shell enrôlement | `SharedWorkstationEnrollmentWidget.tsx` — route canonique **`/shared-workstation/enroll`** (alias `/poste/setup` optionnel) |
| Enregistrement widget | `registerWidget('shared-workstation.enrollment', …)` + manifeste CREOS page dédiée (voir ci-dessous). |
| États UI | (1) Pas d'identité → formulaire code ; (2) Succès → affiche nom poste + « Enrôlement réussi » ; (3) Erreurs API mappées (expiré, invalide, conflit). |
| testids | `shared-workstation-enrollment-code`, `shared-workstation-enrollment-submit`, `shared-workstation-identity-lost-banner`. |

**Route publique sans JWT utilisateur (obligatoire)** : l'opérateur terrain saisit le code **avant** toute session utilisateur / PIN (27.6). Quand `VITE_LIVE_AUTH` est actif, **`LiveAuthShell` ne doit pas rediriger** `/shared-workstation/enroll` vers `/login` — whitelister cette route aux côtés de `/login` (même pattern que `page-login-public.json`). L'API `enroll/complete` reste semi-publique (sans Bearer).

**Manifeste CREOS enrôlement** (pattern `page-login-public.json`) :

- Créer `contracts/creos/manifests/page-transverse-shared-workstation-enroll.json` avec slot widget `shared-workstation.enrollment`.
- Enregistrer dans `peintre-nano/src/app/demo/runtime-demo-manifest.ts` + `RuntimeDemoApp.tsx` (route hors nav admin).
- **Pas** d'entrée navigation transverse (écran setup ponctuel, pas menu).

**Post-enrôlement MVP** : après succès, rediriger vers `/login` (session opérateur = story 27.6 ; en 27.4, message « identité enregistrée — connectez-vous » suffit).

**Pas** de lock screen, pas de saisie PIN opérateur.

#### 10. UI Peintre — extensions panel SuperAdmin (27.3)

Étendre `AdminRegisteredDevicesWidget` :

| Action | UI |
|--------|-----|
| Générer code enrôlement | Bouton sur ligne `pending_enrollment` → modal affiche code + expiration (copier). |
| Reconnecter | Bouton si `identity_lost` → génère code reconnect. |
| Remplacer poste | Bouton si `active` → confirmation + code replace. |
| Marquer identité perdue | Action manuelle SuperAdmin. |
| Résoudre conflit | Panneau si `conflict` → 3 actions §7 + confirmation forte (texte explicite). |

Client API : étendre `admin-registered-devices-client.ts` avec nouvelles operationIds OpenAPI.

#### 11. OpenAPI — extensions contrat

Fusion dans **`contracts/openapi/recyclique-api.yaml`** uniquement :

**Schémas suggérés** :

- `DeviceEnrollmentCodeV1IssueRequest`, `DeviceEnrollmentCodeV1IssueResponse`
- `SharedWorkstationEnrollCompleteV1Request`, `SharedWorkstationEnrollCompleteV1Response`
- `SharedWorkstationDeviceStatusV1Response`
- `RegisteredDeviceConflictResolveV1Request`, `RegisteredDeviceConflictResolveV1Response`

**Paths / operationIds** (préfixe cohérent) :

- `recyclique_registeredDevices_issueEnrollmentCode`
- `recyclique_registeredDevices_markIdentityLost`
- `recyclique_registeredDevices_resolveConflict`
- `recyclique_sharedWorkstation_completeEnrollment`
- `recyclique_sharedWorkstation_getDeviceStatus`

Documenter en-tête `X-Recyclique-Device-Credential` sur routes poste partagé concernées.

#### 12. Audit — nouveaux événements

Étendre `AuditActionType` + helpers `core/audit.py` :

| Enum | Quand |
|------|--------|
| `DEVICE_ENROLLMENT_CODE_ISSUED` | SuperAdmin génère code |
| `DEVICE_ENROLLED` | Première complétion successful |
| `DEVICE_RECONNECTED` | Reconnect après identity_lost |
| `DEVICE_REPLACED` | Replace successful |
| `DEVICE_IDENTITY_CONFLICT` | Ancien secret refusé / conflit détecté |
| `DEVICE_IDENTITY_LOST_MARKED` | SuperAdmin marque identity_lost |
| `DEVICE_CONFLICT_RESOLVED` | Action resolve-conflict |

`merge_critical_audit_fields` : `device_id` ; jamais secret dans `details_json`.

#### 13. Tests obligatoires (gates story)

**Backend** (`recyclique/api`) :

```bash
cd recyclique/api && python -m pytest tests/ -k "story_27_4 or enrollment or device_credential" -q
```

Couverture minimale :

1. **Enrôlement nominal** : device `pending_enrollment` → code → complete → `active` + credential actif + secret hash ≠ plaintext.
2. **Identité perdue / reconnexion** : mark identity_lost → reconnect code → nouveau secret ; ancien `superseded`.
3. **Remplacement** : replace → ancien secret refusé (403) + audit conflict si re-tentative.
4. **Conflit SuperAdmin** : resolve `refuse`, `replace_definitively`, `create_distinct` (nouveau device_id).
5. **Codes** : expiré, consommé, invalide — HTTP stables.
6. **Garde credential** : `device-status` OK avec credential ; KO sans / révoqué.
7. **Sanitize** : grep / test audit sans secret en clair.
8. **Non-régression** : `test_registered_device_epic27.py`, `test_story_27_2_*`, `test_story_27_3_*` — exit 0.
9. **Non-confusion ids** : `device_id` enrollment ≠ caisse.

**Frontend** (`peintre-nano`) :

```bash
cd peintre-nano && npm run test -- --run tests/unit/device-identity-store.test.ts tests/unit/shared-workstation-enrollment-widget.test.tsx tests/unit/admin-registered-devices-enrollment.test.tsx
```

Couverture minimale :

- Store IndexedDB mocké : save/load/clear ; **assertion** pas d'appel `localStorage` pour identité.
- Widget enrôlement : saisie code → mock API complete → save identity.
- Panel admin : bouton générer code appelle bon endpoint ; resolve conflict mock.

**Lint / build** :

```bash
cd peintre-nano && npm run lint && npm run build
```

## Definition of Done

- [x] Tables `registered_device_credentials` + `device_enrollment_codes` + migrations Alembic.
- [x] Services credential + enrollment + intégration garde poste partagé.
- [x] Endpoints SuperAdmin (codes, mark-identity-lost, resolve-conflict) + `enroll/complete` + `device-status`.
- [x] OpenAPI aligné ; operationIds stables.
- [x] Audit événements §12 branché.
- [x] Module `device-identity-store.ts` (IndexedDB) + widget enrôlement terrain.
- [x] Extensions panel SuperAdmin (codes, reconnect, replace, conflit).
- [x] Tests §13 — **exit 0**.
- [x] Aucun QR, lock screen PIN, PWA, offline, localStorage identité, fingerprinting, agent local.
- [x] **Hors scope respecté** : pas de modification `sprint-status.yaml` / `epics.md` par le worker DS (writer unique).

## Tasks / Subtasks

- [x] **Modèle & migrations** : credentials + enrollment codes (AC: secret hashé, un actif/device).
- [x] **Services backend** : `RegisteredDeviceCredentialService`, `DeviceEnrollmentService` (AC: rotate, verify, conflit).
- [x] **Endpoints SuperAdmin** : issue code, mark-identity-lost, resolve-conflict (AC: validation SuperAdmin).
- [x] **Endpoint enroll/complete** : semi-public + rate-limit (AC: code court MVP).
- [x] **Garde credential** : extension shared_workstation + device-status (AC: ancien secret refusé).
- [x] **Audit** : enum + helpers Epic 27.4 (AC: conflit audité).
- [x] **OpenAPI** : schémas + paths (AC: contrat canonique).
- [x] **device-identity-store** : IndexedDB, headers helper (AC: pas localStorage).
- [x] **UI enrôlement terrain** : widget + route (AC: identité locale associée serveur).
- [x] **UI panel admin** : codes, reconnect, replace, conflit (AC: choix SuperAdmin explicites).
- [x] **Tests** : suites backend + frontend §13 (AC: nominal, perdu, replace, conflit).

## Dev Notes

### Intelligence stories 27.1–27.3 (patterns établis)

| Élément antérieur | Réutilisation 27.4 |
|-------------------|-------------------|
| `RegisteredDevice` + statuts | Transitions `pending_enrollment` → `active`, → `identity_lost`, → `conflict`. |
| `RegisteredDeviceService` | `get_required`, revoke, update site — invalider sessions sur replace (27.2). |
| `shared_workstation_guard` | Étendre avec credential ; conserver `X-Recyclique-Device-Id`. |
| `DeviceOperatorSessionService.invalidate_sessions_for_device` | Appeler sur replace / resolve replace_definitively. |
| Audit helpers 27.2/27.3 | Même pattern `log_*` + `@patch` tests SQLite. |
| `AdminRegisteredDevicesWidget` | Étendre, ne pas dupliquer liste CRUD. |
| `sanitize_audit_details` | Clés `secret` déjà masquées — vérifier `device_secret`, `credential`. |
| OpenAPI fusion | `recyclique-api.yaml` seul. |
| `Cache-Control: no-store` | Tous endpoints enrollment/device. |

### Ancres code (lire avant modification)

| Sujet | Chemins |
|--------|---------|
| Modèle device | `models/registered_device.py`, `services/registered_device_service.py` |
| Endpoints admin device | `api/api_v1/endpoints/registered_devices.py` |
| Garde poste | `core/shared_workstation_guard.py`, `services/shared_workstation_context_service.py` |
| Sessions opérateur | `services/device_operator_session_service.py` |
| Endpoint contexte pilote | `api/api_v1/endpoints/shared_workstation.py` |
| Audit | `core/audit.py`, `models/audit_log.py` |
| Hash mots de passe | `core/security.py` — `hash_password`, `verify_password` (réutiliser pour secret device) |
| Panel admin | `domains/admin-config/AdminRegisteredDevicesWidget.tsx`, `api/admin-registered-devices-client.ts` |
| Auth live pattern | `app/auth/LiveAuthShell.tsx` — sessionStorage **JWT uniquement**, pas modèle identité poste ; **whitelister** `/shared-workstation/enroll` (ne pas forcer redirect `/login`) |
| Manifeste login public (réf.) | `contracts/creos/manifests/page-login-public.json` — modèle page publique sans JWT |
| OpenAPI RegisteredDevice | `contracts/openapi/recyclique-api.yaml` |

### Décision locale — MVP secret vs WebCrypto (tranchage CS)

| Palier | Choix |
|--------|-------|
| **MVP obligatoire** | Secret aléatoire serveur (32+ bytes), stocké client IndexedDB, hash bcrypt serveur, en-tête credential. |
| **Optionnel** | WebCrypto `generateKey` non exportable + challenge — **NEEDS_HITL** si effort > 1 jour ou incompatibilité navigateurs cibles. |

Le DS démarre sur MVP ; WebCrypto uniquement si trivial après gates principales vertes.

### Décision locale — format code court

- **8 caractères** uppercase alphanum (alphabet sans O/0/I/1).
- TTL **15 min**.
- Usage **single-use**.

### Distinction concepts (anti-confusion LLM)

| Concept | Story | Identifiant / mécanisme |
|---------|-------|-------------------------|
| Poste serveur | 27.1 | `device_id` |
| Secret device (preuve possession) | **27.4** | `X-Recyclique-Device-Credential` |
| Code enrôlement (one-time) | **27.4** | `device_enrollment_codes.code` |
| Session opérateur PIN | 27.6 | `device_operator_sessions` |
| JWT utilisateur web | auth existante | Bearer / sessionStorage |
| Poste caisse | brownfield | `cash_register_id` |

### Anti-patterns (interdits)

- Fingerprinting navigateur, MAC, discovery LAN, agent local.
- `localStorage` / `sessionStorage` pour secret device ou device_id autoritaire.
- Secret device en clair en DB, logs, audit, réponses API après complétion initiale.
- QR code scanner MVP.
- Lock screen PIN, endpoints PIN publics, UI opérateur actif (27.6).
- PWA manifest / service worker (27.5).
- Autoriser deux credentials `active` simultanés sur même `device_id`.
- Confondre « complétion enrôlement » avec « session opérateur démarrée ».
- PATCH direct `status=active` sans flux enrollment (transitions via service enrollment).
- Modifier `sprint-status.yaml` depuis DS.
- Exiger JWT utilisateur sur la route enrôlement terrain (doit rester accessible avant login).

### Testing / gates (Story Runner)

| Gate | Commande / critère |
|------|-------------------|
| Tests backend 27.4 | `cd recyclique/api && python -m pytest tests/ -k "story_27_4 or enrollment or device_credential" -q` → exit 0 |
| Non-régression Epic 27 | `pytest tests/test_story_27_2_shared_workstation_context.py tests/test_story_27_3_superadmin_device_management.py tests/test_registered_device_epic27.py -q` |
| Lint/build front | `cd peintre-nano && npm run lint && npm run build` |
| Tests UI ciblés | `npm run test -- --run tests/unit/device-identity-store.test.ts tests/unit/shared-workstation-enrollment*.test.tsx tests/unit/admin-registered-devices-enrollment*.test.tsx` |
| Revue sécurité | grep secret/PIN dans audit ; pas localStorage identité |
| OpenAPI | Schémas ↔ Pydantic ; operationIds stables |
| YAML sprint (parent) | lecture seule — pas de write CS/DS |

`gates_skipped_with_hitl: false` — aucun skip pour authz / audit / migrations / contrats / stockage identité.

### Project Structure Notes

- Backend : `recyclique/api/src/recyclic_api/` — models, services, endpoints, migrations.
- Front identité : `peintre-nano/src/domains/shared-workstation/` (nouveau dossier).
- Front admin : extensions `domains/admin-config/`, `api/admin-registered-devices-client.ts`.
- Contrats : `contracts/openapi/recyclique-api.yaml` ; CREOS page enrôlement si route widget dédiée.
- Tests : `tests/test_story_27_4_enrollment_reconnect_replace.py` (convention BMAD).

### References

- `_bmad-output/planning-artifacts/epics.md` — Epic 27, Story 27.4
- `_bmad-output/implementation-artifacts/27-1-registered-device.md`
- `_bmad-output/implementation-artifacts/27-2-server-context-audit.md`
- `_bmad-output/implementation-artifacts/27-3-superadmin-device-management.md`
- `references/artefacts/2026-05-29_02_mini-adr-postes-partages-pin-non-offline.md`
- `references/artefacts/2026-05-29_01_cadrage-postes-partages-pin-operateur.md` — §3.8
- `references/artefacts/2026-05-29_04_runbook-orchestration-epic-27-postes-partages-pin.md`
- `contracts/openapi/recyclique-api.yaml`
- `_bmad-output/project-context.md`

## Trace Epic 27 — ADR

| Élément | Valeur |
|--------|--------|
| Nouvelle ADR structurante requise ? | **ADR N/A pour 27.4** — implémentation des décisions mini-ADR § Identité du poste et § Audit (enrôlement, reconnexion, conflit). |
| ADR applicables | Mini-ADR 2026-05-29 (secret local revocable, pas localStorage, flux conflit) ; cadrage §3.8. |

## Alignement sprint / YAML

- Clé **`27-4-enrollment-reconnect-replace`** : **non modifiée** par ce worker CS (writer unique Epic Runner — pas de passage `ready-for-dev` dans `sprint-status.yaml`).
- **`epic-27`** : inchangé par CS.
- Prochaine story après clôture 27.4 : **`27-5-installable-pwa-non-offline`** (ordre runbook §4).

## Risques / HITL

| Sujet | Statut | Action |
|-------|--------|--------|
| MVP secret vs WebCrypto | Risque epics | Tranchage § Dev Notes — MVP secret + IndexedDB ; WebCrypto optionnel. |
| Rate-limit endpoint semi-public | Proposition | Middleware simple ou compteur IP ; documenter limite. |
| Auto-détection identity_lost | Proposition | MVP = action SuperAdmin manuelle ; auto différée. |
| Route enrôlement `/poste/setup` vs autre | Proposition | Story Runner tranche localement ; documenter dans manifeste. |
| Libellés UI conflit (refuse / replace / distinct) | Risque epics | Textes explicites §10 ; affinage VS si besoin. |
| Rate-limit vs tests e2e | Connu | Bypass flag test-only ou header test — pattern projet si existant. |

**NEEDS_STROPHE_HITL** : non requis pour démarrer le DS si le dev suit les propositions ci-dessus (MVP secret + code court + IndexedDB).

## Checklist VS (validate-create-story)

- [x] AC BDD alignés `epics.md` §27.4 (code court, pas QR MVP, IndexedDB, reconnexion, replace, conflit SuperAdmin).
- [x] Garde-fous mini-ADR § identité poste + runbook §7 (pas localStorage autoritaire, secret revocable, pas fingerprinting).
- [x] Dépendances 27.1–27.3 référencées ; hors scope 27.5–27.6 explicite.
- [x] OpenAPI : schémas/paths/operationIds §11 documentés ; en-tête `X-Recyclique-Device-Credential`.
- [x] Route publique `/shared-workstation/enroll` + bypass `LiveAuthShell` + manifeste CREOS §9.
- [x] Gates §13 + runbook (nominal enrollment, lost storage, replacement, old secret refused, conflict audited).
- [x] Anti-patterns § Dev Notes couvrent JWT sur enrôlement, double credential actif, PIN/PWA/offline.
- [x] `sprint-status.yaml` non modifié par CS/VS (writer unique Epic Runner).

## Dev Agent Record

### Agent Model Used

Composer 2.5 (worker DS story 27-4)

### Debug Log References

- Reprise implémentation existante (untracked) ; validation gates.
- Fix régression LiveAuthShell : `/login` ne doit pas bypass le formulaire — seul `/shared-workstation/enroll` rend `children` sans JWT.
- **CR1 (cr_loop=1)** : P1-1 `replace_definitively` — **Option A** : conserver credential actif, révoquer uniquement stale, auto-émettre code `replace` dans réponse API + modal admin ; P1-2 test `test_replace_definitively_poste_reste_utilisable` ; P2-2 bannière identité perdue via hint IndexedDB (`hadPriorDeviceEnrollment`) ; P2-4 catch `saveDeviceIdentity`.

### Completion Notes List

- Backend : tables `registered_device_credentials` + `device_enrollment_codes`, migration `s27_4_enrollment_credentials`, services credential/enrollment, endpoints SuperAdmin + `enroll/complete` + `device-status`, garde credential étendue, audit Epic 27.4.
- Frontend : `device-identity-store` (IndexedDB, pas localStorage), widget enrôlement `/shared-workstation/enroll`, whitelist `LiveAuthShell` (enroll only), extensions panel admin (codes, reconnect, replace, conflit).
- OpenAPI + manifeste CREOS `page-transverse-shared-workstation-enroll.json`.
- Gates DS : pytest `-k story_27_4` 7/7 ; `npm run lint` OK ; vitest full 766/766 (159 files).
- **Post-CR1** : `replace_definitively` Option A — credential actif préservé + code replace auto ; pytest story_27_4 **8/8** ; lint OK ; vitest **782/782** (161 files).
- `sprint-status.yaml` non modifié (instruction worker).

### File List

- `recyclique/api/migrations/versions/s27_4_enrollment_credentials.py`
- `recyclique/api/src/recyclic_api/models/device_enrollment_code.py`
- `recyclique/api/src/recyclic_api/models/registered_device_credential.py`
- `recyclique/api/src/recyclic_api/models/__init__.py`
- `recyclique/api/src/recyclic_api/models/audit_log.py`
- `recyclique/api/src/recyclic_api/schemas/device_enrollment.py`
- `recyclique/api/src/recyclic_api/schemas/registered_device.py`
- `recyclique/api/src/recyclic_api/services/device_enrollment_service.py`
- `recyclique/api/src/recyclic_api/services/registered_device_credential_service.py`
- `recyclique/api/src/recyclic_api/services/shared_workstation_context_service.py`
- `recyclique/api/src/recyclic_api/api/api_v1/endpoints/registered_devices.py`
- `recyclique/api/src/recyclic_api/api/api_v1/endpoints/shared_workstation.py`
- `recyclique/api/src/recyclic_api/api/api_v1/api.py`
- `recyclique/api/src/recyclic_api/core/shared_workstation_guard.py`
- `recyclique/api/src/recyclic_api/core/audit.py`
- `recyclique/api/tests/test_story_27_4_enrollment_reconnect_replace.py`
- `contracts/openapi/recyclique-api.yaml`
- `contracts/creos/manifests/page-transverse-shared-workstation-enroll.json`
- `peintre-nano/src/domains/shared-workstation/device-identity-store.ts`
- `peintre-nano/src/domains/shared-workstation/SharedWorkstationEnrollmentWidget.tsx`
- `peintre-nano/src/api/shared-workstation-enrollment-client.ts`
- `peintre-nano/src/api/admin-registered-devices-client.ts`
- `peintre-nano/src/domains/admin-config/AdminRegisteredDevicesWidget.tsx`
- `peintre-nano/src/app/auth/LiveAuthShell.tsx`
- `peintre-nano/src/app/demo/RuntimeDemoApp.tsx`
- `peintre-nano/src/app/demo/runtime-demo-manifest.ts`
- `peintre-nano/src/registry/register-shared-workstation-widgets.ts`
- `peintre-nano/src/registry/index.ts`
- `peintre-nano/tests/unit/device-identity-store.test.ts`
- `peintre-nano/tests/unit/shared-workstation-enrollment-widget.test.tsx`
- `peintre-nano/tests/unit/admin-registered-devices-enrollment.test.tsx`
- `peintre-nano/tests/e2e/shared-workstation-enrollment-27-4.e2e.test.tsx` (QA)
- `peintre-nano/tests/contract/page-transverse-shared-workstation-enroll-27-4.test.ts` (QA)
- `_bmad-output/implementation-artifacts/tests/test-summary-story-27-4-enrollment-reconnect-replace-qa.md` (QA)

### Change Log

- 2026-05-30 — Story 27.4 CS (create, idempotent) : re-validation epics §27.4, mini-ADR, runbook §4/§7, stories 27.1–27.3, OpenAPI cible ; guide dev complet ; Status `ready-for-dev` ; sprint-status non modifié (writer unique).
- 2026-05-30 — Story 27.4 VS (validate, vs_loop=0) : PASS — AC epics §27.4, mini-ADR identité poste, runbook §7/§8, dépendances 27.1–27.3, OpenAPI §11, checklist complète ; prêt DS.
- 2026-05-30 — Story 27.4 DS : implémentation complète + gates verts ; fix LiveAuthShell (login vs enroll) ; Status `review`.
- 2026-05-30 — Story 27.4 QA (qa_loop=0) : **PASS** — E2E Vitest 7 cas + contrat CREOS 3 cas ; résumé `tests/test-summary-story-27-4-enrollment-reconnect-replace-qa.md`.
- 2026-05-30 — Story 27.4 DS post-CR1 (cr_loop=1) : fix `replace_definitively` Option A + test pytest + P2 bannière/saveDeviceIdentity ; gates 8/8 pytest, lint OK, vitest 782/782.

## QA Agent Record

### Agent Model Used

Composer 2.5 (worker QA `bmad-qa-generate-e2e-tests` story 27-4)

### QA Verdict

**PASS** — `qa_loop: 0`

### Tests générés / complétés (QA)

| Fichier | Cas |
|---------|-----|
| `peintre-nano/tests/e2e/shared-workstation-enrollment-27-4.e2e.test.tsx` | 7 |
| `peintre-nano/tests/contract/page-transverse-shared-workstation-enroll-27-4.test.ts` | 3 |

### Exécution

```bash
cd peintre-nano && node ./node_modules/vitest/vitest.mjs run \
  tests/e2e/shared-workstation-enrollment-27-4.e2e.test.tsx \
  tests/contract/page-transverse-shared-workstation-enroll-27-4.test.ts
# → 10 passed, exit 0
```

### Prochaine étape pipeline

**CR** (code review adversarial).
