# Story 27.3 : Panel SuperAdmin « Gestion des postes »

Status: review

**Story key :** `27-3-superadmin-device-management`  
**Epic :** 27 — Postes partagés enrôlés + PIN opérateur + PWA installable non-offline  
**Implementation artifact :** `_bmad-output/implementation-artifacts/27-3-superadmin-device-management.md`  
**Date CS :** 2026-05-30

## Dépendances (prérequis)

- **Story 27.1 done** : modèle `RegisteredDevice`, API `/v1/registered-devices/`, `device_id` canonique — `_bmad-output/implementation-artifacts/27-1-registered-device.md`.
- **Story 27.2 done** : contexte serveur `SharedWorkstationContext`, invalidation sessions sur révocation / changement site — `_bmad-output/implementation-artifacts/27-2-server-context-audit.md`.
- **Epic 27 — cadrage gelé** : `_bmad-output/planning-artifacts/epics.md` (§ Epic 27, Story 27.3).
- **Mini-ADR Epic 27** : `references/artefacts/2026-05-29_02_mini-adr-postes-partages-pin-non-offline.md` — panel SuperAdmin, audit révocation/config, pas d’authz front, `device_id` distinct.
- **Runbook orchestration** : `references/artefacts/2026-05-29_04_runbook-orchestration-epic-27-postes-partages-pin.md` — ordre stories §4, gates transverses §8, invariants §7.
- **Contrat OpenAPI** : `contracts/openapi/recyclique-api.yaml` — schémas `RegisteredDeviceV1*` et operationIds `recyclique_registeredDevices_*` (implémentés en 27.1).
- **Registre `module_key`** : `recyclique/api/src/recyclic_api/modules/module_config/registry.py` (`ACTIVE_MODULE_KEYS`, `is_active_module_key`) ; pack normatif `references/config-modules-site-id/index.md`.
- **Pattern admin Peintre** : `AdminCashRegistersWidget`, `admin-cash-registers-client.ts`, manifestes CREOS `page-transverse-admin-cash-registers.json` (Story 17.2 / 17.3).
- **Garde SuperAdmin UI** : `peintre-nano/src/domains/admin-config/admin-super-page-guards.ts` (`ADMIN_SUPER_PAGE_MANIFEST_GUARDS` — proxy `caisse.sale_correct` + `transverse.admin.view`).
- **Stories suivantes (ne pas implémenter ici)** : 27.4 (enrôlement / secret local), 27.5 (PWA), 27.6 (lock screen PIN), 27.7 (intersection modules), 27.8+.

## Garde-fous ADR / runbook (obligatoires pour le DS)

| Invariant | Application story 27.3 |
|-----------|-------------------------|
| Pas d’offline métier | Panel = fetch serveur uniquement ; pas de cache local autoritaire ; pas de SW. |
| Pas d’authz front | UI affiche/refuse selon **ContextEnvelope** (proxy SuperAdmin) ; **refus API** reste sur `require_role_strict(SUPER_ADMIN)` — le front ne décide jamais seul qu’un poste est utilisable. |
| `device_id` canonique | Colonne UI « Identifiant poste (`device_id`) » — **jamais** libellé caisse / `cash_register_id`. |
| Distinction identifiants | Ne pas fusionner liste postes partagés et postes de caisse ; lien hub « Sites et caisses » reste séparé. |
| Panel administratif | Liste + CRUD + révocation + statut simple + dernier contact — **pas** dashboard temps réel, pas de cartographie périphériques, pas de discovery réseau. |
| Pas d’enrôlement terrain | Pas de flux code court, QR, WebCrypto, `localStorage`, bouton « enrôler sur ce navigateur » (story **27.4**). |
| Pas de reporting audit avancé | Pas d’écran analytics / export audit dédié — l’audit est **écrit serveur** ; consultation via journal existant (`admin.audit-log.demo`) suffit. |
| Audit config + révocation | Chaque create / update / revoke via API admin doit produire une entrée `audit_logs` (gap 27.1 — voir § Interprétation). |
| Révocation = route dédiée | UI appelle `POST …/revoke` — pas de PATCH `status=revoked` (bloqué Pydantic côté API depuis 27.2). |

## Story (BDD)

As a **SuperAdmin**,  
I want an administrative **« Gestion des postes »** panel for enrolled shared workstations,  
So that **I can configure, revoke and monitor basic status without relying on hidden local state**.

## Acceptance criteria

Source normative : `_bmad-output/planning-artifacts/epics.md` — **Story 27.3**.

**Given** `RegisteredDevice` exists for `shared_workstation`  
**When** this story is delivered  
**Then** the SuperAdmin can list, create/name, assign site and emplacement, set device type, configure allowed `module_key` values, set timeout, view simple status and last contact, revoke a workstation, and modify configuration remotely  
**And** access to this panel is reserved to SuperAdmin permissions  
**And** configuration changes and revocations are audited  
**And** the panel does not implement realtime fleet supervision, peripheral mapping, network discovery, or advanced audit reporting

### Interprétation exécutable

#### 1. Slice backend — audit des mutations admin (complète AC « audited »)

**Constat 27.1** : les endpoints `registered_devices.py` n’appellent pas encore `log_audit` sur create / update / revoke. **27.3** comble ce gap (AC epics + mini-ADR § Audit — révocation et config admin).

**Nouveaux `AuditActionType`** (enum `models/audit_log.py`) — proposition minimale :

| Valeur enum | Quand |
|-------------|--------|
| `REGISTERED_DEVICE_CREATED` | `POST /v1/registered-devices/` réussi |
| `REGISTERED_DEVICE_UPDATED` | `PATCH /v1/registered-devices/{device_id}` réussi (champs modifiés dans `details_json`) |
| `REGISTERED_DEVICE_REVOKED` | `POST /v1/registered-devices/{device_id}/revoke` réussi |

Helpers suggérés dans `core/audit.py` (pattern Epic 27.2) :

- `log_registered_device_created(...)`
- `log_registered_device_updated(..., changed_fields: dict)`
- `log_registered_device_revoked(..., reason: Optional[str])`

Règles :

- `target_type="registered_device"`, `target_id=device.id`.
- `merge_critical_audit_fields` avec `device_id`, `site_id`, `module_key` si pertinent (allowlist — stocker la liste ou un résumé, pas de dump excessif).
- `actor` = utilisateur JWT (`current_user`) sur mutations admin.
- **`details_json`** : inclure `operation`, `outcome`, champs changés (ex. `name`, `site_id`, `allowed_module_keys`, `inactivity_timeout_seconds`, `status` hors revoke).
- **Interdit** : PIN, secret device, hash — grep review.
- Appeler les helpers depuis **`registered_devices.py`** (ou service après commit) — pas depuis le front.

**Tests backend obligatoires** (ajouter à la suite Epic 27) :

1. Create → audit `REGISTERED_DEVICE_CREATED` avec `device_id` ≠ id caisse.
2. PATCH name/site/allowlist/timeout → audit `REGISTERED_DEVICE_UPDATED` avec `changed_fields` cohérents.
3. Revoke → audit `REGISTERED_DEVICE_REVOKED` + device `status=revoked`.
4. Non-régression : tests `test_registered_device_epic27.py` et `test_story_27_2_*` — exit 0.

#### 2. Client API Peintre — `admin-registered-devices-client.ts`

Créer un client aligné OpenAPI (pattern `admin-cash-registers-client.ts`) :

| Opération | operationId | URL |
|-----------|-------------|-----|
| Liste | `recyclique_registeredDevices_listRegisteredDevices` | `GET /v1/registered-devices/` |
| Détail | `recyclique_registeredDevices_getRegisteredDeviceById` | `GET /v1/registered-devices/{device_id}` |
| Création | `recyclique_registeredDevices_createRegisteredDevice` | `POST /v1/registered-devices/` |
| Mise à jour | `recyclique_registeredDevices_updateRegisteredDevice` | `PATCH /v1/registered-devices/{device_id}` |
| Révocation | `recyclique_registeredDevices_revokeRegisteredDevice` | `POST /v1/registered-devices/{device_id}/revoke` |

Types : `components['schemas']['RegisteredDeviceV1Response']`, `RegisteredDeviceV1Create`, `RegisteredDeviceV1Update`, `RegisteredDeviceRevokeV1Request`.

Conventions :

- **Slash final** sur `GET/POST /v1/registered-devices/` (éviter 404 proxy — cf. test `admin-cash-registers-client-url.test.ts`).
- Bearer via `authHeaders` ; pas de cache client.
- Query liste : `site_id`, `status`, `include_revoked`, `skip`, `limit` (max 200).

**Pas** de nouvelles routes backend dans cette story (réutilisation stricte 27.1).

#### 3. Widget Peintre — `AdminRegisteredDevicesWidget`

Emplacement : `peintre-nano/src/domains/admin-config/AdminRegisteredDevicesWidget.tsx`  
Enregistrement : `registerWidget('admin.registered-devices.demo', AdminRegisteredDevicesWidget)` dans `register-admin-config-widgets.ts`.

**Garde UI SuperAdmin** :

- Utiliser `ADMIN_SUPER_PAGE_MANIFEST_GUARDS` (même pattern que `AdminAccountingExpertShellWidget`).
- Si permissions insuffisantes : message explicite « Réservé au super-admin » — **ne pas** appeler l’API (éviter 403 bruit).

**Surface fonctionnelle** (calquée sur `AdminCashRegistersWidget`, adaptée au contrat `RegisteredDevice`) :

| Zone | Comportement |
|------|--------------|
| En-tête | Titre **« Gestion des postes »** ; sous-titre rappelant poste partagé enrôlé ≠ poste de caisse. |
| Filtres | Site (select sites admin), statut admin (tous / actif / pending_enrollment / identity_lost / conflict / révoqués via `include_revoked`), bouton actualiser. |
| Table liste | Colonnes : nom, site, emplacement, statut (badge), `device_id` (mono, copiable optionnel), modules autorisés (résumé), timeout (min ou « défaut serveur »), dernier contact (`last_contact_at` ou « — »), actions. |
| Création (modal) | Champs : nom*, site*, emplacement, allowlist `module_key` (multi-select depuis clés actives), timeout secondes (optionnel). `device_type` forcé `shared_workstation` — affiché en lecture seule, non éditable. Statut initial serveur = `pending_enrollment` (pas de choix enrôlement 27.4). |
| Édition (modal ou inline) | PATCH partiel : nom, emplacement, site, allowlist, timeout. **Pas** d’édition directe `status=revoked` — bouton révoquer séparé. Transitions `identity_lost` / `conflict` : lecture seule en 27.3 (logique 27.4) — afficher badge seulement. |
| Révocation | Modal confirmation + motif optionnel (`reason` corps revoke) → `POST …/revoke`. Idempotent côté serveur. |
| Erreurs | `CashflowClientErrorAlert` / pattern erreur API existant ; 403 = message SuperAdmin. |
| Chargement | `aria-busy` / état busy cohérent hub admin. |
| testids | Racine `widget-admin-registered-devices` ; boutons create/revoke/refresh nommés (`admin-registered-devices-*`). |

**Allowlist `module_key` UI** :

- Source : registre serveur — MVP = clés de `ACTIVE_MODULE_KEYS` (`kpi-live-banner` aujourd’hui).
- Proposer constante partagée ou import depuis un module front existant (`KPI_LIVE_BANNER_MODULE_KEY`) + liste extensible quand registre grossit (27.7 / 27.8).
- Validation finale = API 422 si clé inconnue — afficher message serveur.

**Libellés statuts admin** (proposition locale — risque HITL epics ; Story Runner peut affiner) :

| `status` API | Libellé UI proposé |
|--------------|-------------------|
| `pending_enrollment` | En attente d’enrôlement |
| `active` | Actif |
| `identity_lost` | Identité locale perdue |
| `conflict` | Conflit d’identité |
| `revoked` | Révoqué |

**Exclusions UI explicites** :

- Pas de carte « santé flotte » / heartbeat live / websocket.
- Pas de scan réseau / découverte LAN.
- Pas de mapping imprimante / scanner.
- Pas d’onglet « historique audit poste » filtré (journal transverse suffit).
- Pas de bouton enrôlement / QR / code court.

#### 4. Intégration CREOS, navigation, hub admin

**Page manifest** — créer `contracts/creos/manifests/page-transverse-admin-registered-devices.json` :

```json
{
  "version": "1",
  "page_key": "transverse-admin-registered-devices",
  "required_permission_keys": ["transverse.admin.view", "caisse.sale_correct"],
  "requires_site": true,
  "slots": [
    {
      "slot_id": "admin.transverse-list.main",
      "widget_type": "admin.registered-devices.demo",
      "widget_props": {}
    }
  ]
}
```

**Navigation** — ajouter entrée dans `contracts/creos/manifests/navigation-transverse-served.json` **et** miroir `peintre-nano/public/manifests/navigation.json` :

| Champ | Valeur proposée |
|-------|-----------------|
| `id` / `route_key` | `transverse-admin-registered-devices` |
| `path` | `/admin/registered-devices` |
| `page_key` | `transverse-admin-registered-devices` |
| `label_key` | `nav.transverse.admin.registeredDevices` (libellé FR servi : « Gestion des postes ») |
| `required_permission_keys` | `["transverse.admin.view", "caisse.sale_correct"]` |
| `visibility.permission_any` | `["transverse.admin.view"]` (filtrage effectif via permissions super-admin sur enveloppe) |

**Libellé nav (fallback UI)** — ajouter dans `peintre-nano/src/runtime/nav-label-presentation-fallbacks.ts` :

```ts
'nav.transverse.admin.registeredDevices': 'Gestion des postes',
```

(même pattern que `nav.transverse.admin.cashRegisters` ; présentation uniquement.)

**Runtime demo** : enregistrer le manifeste dans `peintre-nano/src/app/demo/runtime-demo-manifest.ts` ; **obligatoire** (pattern cash-registers) :

- `RuntimeDemoApp.tsx` : branche `pathForMatch === '/admin/registered-devices'` → `setSelectedEntryId('transverse-admin-registered-devices')`.
- `toolbar-selection-for-live-path.ts` : inclure `transverse-admin-registered-devices` dans la liste des entrées admin rattachées à `transverse-admin` (surbrillance topbar live).

**Hub SuperAdmin** : ajouter bouton dans `AdminLegacyDashboardHomeWidget` (section Super-Admin) → `/admin/registered-devices`, icône suggérée `Monitor` ou `Tablet`, `data-testid="admin-legacy-nav-registered-devices"`.

**OpenAPI** : **aucune** modification schéma attendue (contrat 27.1 complet) — regénérer types TS seulement si le pipeline projet l’exige après pull.

#### 5. Tests obligatoires (gates story)

**Backend** (`recyclique/api`) :

```bash
cd recyclique/api && python -m pytest tests/ -k "registered_device or story_27_3" -q
```

Couverture minimale :

- Audit create / update / revoke (§1).
- 403 non-SuperAdmin inchangé (non-régression 27.1).

**Frontend** (`peintre-nano`) :

```bash
cd peintre-nano && npm run test -- --run tests/unit/admin-registered-devices-client-url.test.ts tests/unit/admin-registered-devices-widget.test.tsx
```

Couverture minimale :

- Client : URL `GET /v1/registered-devices/` avec slash final.
- Widget : garde non-super-admin (pas de fetch) ; rendu liste mockée ; modal create appelle POST ; revoke appelle POST revoke (mocks fetch).
- Contract test navigation (optionnel mais recommandé) : entrée manifeste + `page_key` + widget slot — pattern `navigation-transverse-served-5-1.test.ts`.

**E2E ciblé** (recommandé, pattern 17.2) :

- Clic nav ou hub → `/admin/registered-devices` + `widget-admin-registered-devices` visible pour stub super-admin.

**Lint / build** :

```bash
cd peintre-nano && npm run lint && npm run build
```

## Definition of Done

- [x] Audit serveur sur create / update / revoke `RegisteredDevice` + tests dédiés story 27.3.
- [x] Client `admin-registered-devices-client.ts` aligné operationIds OpenAPI.
- [x] Widget `AdminRegisteredDevicesWidget` : liste, create, edit, revoke, filtres, garde SuperAdmin.
- [x] Manifeste page + entrée navigation + hub SuperAdmin branchés.
- [x] Tests backend + frontend listés — **exit 0**.
- [x] Aucun enrôlement, PWA, lock screen, intersection modules, dashboard temps réel, discovery, reporting audit avancé.
- [x] UI distingue clairement poste partagé (`device_id`) et poste de caisse.
- [x] **Hors scope respecté** : pas de modification `sprint-status.yaml` / `epics.md` par le worker DS (writer unique).

## Tasks / Subtasks

- [x] **Audit backend** : enum + helpers + branchement endpoints registered-devices (AC: config et révocations auditées).
- [x] **Tests audit** : `tests/test_story_27_3_superadmin_device_management.py` ou extension `test_registered_device*` (AC: gates audit).
- [x] **Client API front** : `admin-registered-devices-client.ts` + test URL (AC: contrat OpenAPI réutilisé).
- [x] **Widget admin** : `AdminRegisteredDevicesWidget.tsx` — liste/CRUD/révocation/filtres (AC: panel SuperAdmin complet MVP).
- [x] **Enregistrement widget** : `register-admin-config-widgets.ts` (AC: slot CREOS).
- [x] **Manifeste + nav** : `page-transverse-admin-registered-devices.json`, `navigation-transverse-served.json`, `public/manifests/navigation.json`, `nav-label-presentation-fallbacks.ts`, `runtime-demo-manifest.ts`, `RuntimeDemoApp.tsx`, `toolbar-selection-for-live-path.ts` (AC: route `/admin/registered-devices` + libellé FR).
- [x] **Hub SuperAdmin** : lien `AdminLegacyDashboardHomeWidget` (AC: découvrabilité).
- [x] **Tests UI** : unit widget + client ; e2e navigation optionnel (AC: SuperAdmin-only UI).
- [x] **Revue périmètre** : grep qu’aucun flux enrôlement / SW / fleet dashboard n’a été ajouté.

## Dev Notes

### Intelligence stories 27.1 / 27.2 (réutilisation)

| Élément antérieur | Réutilisation 27.3 |
|-------------------|-------------------|
| API `/v1/registered-devices/*` | Client + widget — **pas** de duplication backend CRUD. |
| `device_id` vs caisse | Libellés UI + tests non-confusion audit. |
| Statuts admin | Badges UI ; transitions `identity_lost` / `conflict` = affichage seul (27.4). |
| Révocation | `POST …/revoke` ; invalide sessions (27.2) — UI message post-révocation optionnel. |
| Timeout défaut 900 s | Afficher « 15 min (défaut) » si `inactivity_timeout_seconds` null côté API. |
| Allowlist validation | API 422 — UI multi-select registre actif. |
| `Cache-Control: no-store` | Côté API déjà en place ; client sans cache. |

### Ancres code (lire avant modification)

| Sujet | Chemins |
|--------|---------|
| API registre 27.1 | `api/api_v1/endpoints/registered_devices.py`, `services/registered_device_service.py`, `schemas/registered_device.py` |
| OpenAPI RegisteredDevice | `contracts/openapi/recyclique-api.yaml` — `/v1/registered-devices/` |
| Audit socle | `core/audit.py`, `models/audit_log.py`, `tests/test_audit_story_25.py` |
| Pattern admin liste | `domains/admin-config/AdminCashRegistersWidget.tsx`, `api/admin-cash-registers-client.ts` |
| Garde SuperAdmin UI | `admin-super-page-guards.ts`, `AdminAccountingExpertShellWidget.tsx` |
| Sites admin (select) | `api/admin-sites-client.ts`, `AdminSitesWidget.tsx` |
| Registre module_key | `modules/module_config/registry.py` ; front `peintre-nano/src/api/module-config-client.ts` (`KPI_LIVE_BANNER_MODULE_KEY`) |
| Libellés nav CREOS | `peintre-nano/src/runtime/nav-label-presentation-fallbacks.ts` |
| Hub admin | `widgets/admin/AdminLegacyDashboardHomeWidget.tsx` |
| Manifestes CREOS | `contracts/creos/manifests/page-transverse-admin-cash-registers.json`, `navigation-transverse-served.json` |
| Runtime | `app/demo/runtime-demo-manifest.ts`, `RuntimeDemoApp.tsx`, `runtime/toolbar-selection-for-live-path.ts` |
| Journal audit existant | widget `admin.audit-log.demo` — consultation seule |

### Distinction produit (anti-confusion LLM)

| Concept | UI 27.3 | Autre écran |
|---------|---------|-------------|
| Poste partagé enrôlé | **Gestion des postes** `/admin/registered-devices` | — |
| Poste de caisse | — | `/admin/cash-registers` |
| Site | Select partagé | `/admin/sites` |
| Enrôlement terrain | **Hors scope** | Story 27.4 |
| Opérateur PIN actif | **Hors scope** | Story 27.6 |

### Anti-patterns (interdits)

- Appeler `PATCH` avec `status=revoked` depuis l’UI.
- Stocker config poste en `localStorage` / sessionStorage comme vérité.
- Décider côté front qu’un poste est « actif métier » sans relire l’API.
- Fusionner ou renommer `device_id` en `cash_register_id`.
- Implémenter enrôlement, QR, code court, lock screen, PWA, override SuperAdmin.
- Dashboard temps réel (websocket, polling agressif last_contact).
- Cartographie périphériques ou discovery réseau.
- Écran reporting audit avancé filtré par poste.
- Nouveau rôle permission inventé — réutiliser proxy SuperAdmin existant.
- Modifier OpenAPI RegisteredDevice sans HITL (contrat gelé 27.1).

### Testing / gates (Story Runner)

| Gate | Commande / critère |
|------|-------------------|
| Audit backend | `cd recyclique/api && python -m pytest tests/ -k "story_27_3 or registered_device" -q` → exit 0 |
| Lint/build front | `cd peintre-nano && npm run lint && npm run build` |
| Tests UI ciblés | `npm run test -- --run tests/unit/admin-registered-devices-*` |
| Non-régression Epic 27 | `pytest tests/test_story_27_2_shared_workstation_context.py -q` |
| OpenAPI | Pas de drift schémas RegisteredDevice (revue CR) |
| YAML sprint (parent) | lecture seule — **pas de write CS/DS** |

`gates_skipped_with_hitl: false` — aucun skip pour authz / audit / contrats.

### Project Structure Notes

- Backend : modifications **minimales** — audit uniquement sur endpoints existants (pas de migration).
- Front : `peintre-nano/src/domains/admin-config/` + `peintre-nano/src/api/` + manifestes `contracts/creos/manifests/`.
- Contrats : pas de nouveau YAML OpenAPI métier ; CREOS navigation/page uniquement.

### References

- `_bmad-output/planning-artifacts/epics.md` — Epic 27, Story 27.3
- `_bmad-output/implementation-artifacts/27-1-registered-device.md`
- `_bmad-output/implementation-artifacts/27-2-server-context-audit.md`
- `references/artefacts/2026-05-29_02_mini-adr-postes-partages-pin-non-offline.md`
- `references/artefacts/2026-05-29_04_runbook-orchestration-epic-27-postes-partages-pin.md`
- `references/config-modules-site-id/index.md`
- `peintre-nano/docs/03-contrats-creos-et-donnees.md` — § admin cash-registers / sites (pattern 17.2)
- `_bmad-output/project-context.md`

## Trace Epic 27 — ADR

| Élément | Valeur |
|--------|--------|
| Nouvelle ADR structurante requise ? | **ADR N/A pour 27.3** — écran SuperAdmin prévu mini-ADR § Conséquences ; implémentation UI du registre `RegisteredDevice`. |
| ADR applicables | Mini-ADR postes partagés (panel admin, audit révocation, pas d’authz front). |

## Alignement sprint / YAML

- Clé **`27-3-superadmin-device-management`** : statut sprint **non modifié** par ce worker CS (writer unique — Epic Runner / orchestrateur).
- **`epic-27`** : inchangé par CS.
- Prochaine story après clôture 27.3 : **`27-4-enrollment-reconnect-replace`** (ordre runbook §4).

## Risques / HITL

| Sujet | Statut | Action |
|-------|--------|--------|
| Libellés exacts statuts (`identity_lost`, `conflict`, etc.) | Risque epics | Proposition § Interprétation ; Story Runner tranche localement. |
| Chemin URL `/admin/registered-devices` vs libellé « Gestion des postes » | Proposition | Path anglais aligné API ; titre FR UI. |
| Visibilité nav SuperAdmin vs ADMIN | Proposé | `required_permission_keys` + proxy `caisse.sale_correct` — même pattern compta expert. |
| Audit absent en 27.1 | Écart documenté | Slice backend explicite en 27.3 — ne pas reporter à 27.4. |
| Peu de `module_key` actifs | Connu | UI avec `kpi-live-banner` ; pas d’invention clé `reception` sans 27.7/27.8. |

**NEEDS_STROPHE_HITL** : non requis pour démarrer le DS si le dev suit les propositions ci-dessus.

## Dev Agent Record

### Agent Model Used

Composer (worker bmad-dev-story DS)

### Debug Log References

- Tests audit SQLite : `audit_logs` absent en CI — assertions via `@patch("recyclic_api.core.audit.log_audit")` (pattern 27.2).
- Types OpenAPI générés Peintre sans `RegisteredDeviceV1*` — types locaux dans `admin-registered-devices-client.ts` jusqu’à regén pipeline.

### Completion Notes List

- Backend : `REGISTERED_DEVICE_{CREATED,UPDATED,REVOKED}` + helpers `log_registered_device_*` branchés sur endpoints 27.1 ; `changed_fields` sur PATCH.
- Front : panel `/admin/registered-devices`, garde `ADMIN_SUPER_PAGE_MANIFEST_GUARDS`, CRUD + révocation POST, filtres site/statut/révoqués.
- CREOS + hub legacy SuperAdmin ; tests unit client/widget + contract nav ; lint + build OK.
- Gate vitest (2026-05-30) : modal edit via `data-testid` ; hub SuperAdmin tuile postes hors garde `isAccountingExpertShell` seule ; 59 vitest ciblés + 17 pytest OK.
- Gate DS fix : testids modal edit (`admin-registered-devices-edit-name`, `admin-registered-devices-edit-submit`) ; test unit edit via `waitFor` + value assert ; e2e hub 27.3 — mock fetch élargi (`/v1/users/`, cash-sessions, reception/tickets) pour éviter timeout CI sur `admin-legacy-nav-registered-devices`.

### File List

- recyclique/api/src/recyclic_api/models/audit_log.py
- recyclique/api/src/recyclic_api/core/audit.py
- recyclique/api/src/recyclic_api/api/api_v1/endpoints/registered_devices.py
- recyclique/api/tests/test_story_27_3_superadmin_device_management.py
- peintre-nano/src/api/admin-registered-devices-client.ts
- peintre-nano/src/domains/admin-config/AdminRegisteredDevicesWidget.tsx
- peintre-nano/src/registry/register-admin-config-widgets.ts
- peintre-nano/src/widgets/admin/AdminLegacyDashboardHomeWidget.tsx
- peintre-nano/src/runtime/nav-label-presentation-fallbacks.ts
- peintre-nano/src/runtime/toolbar-selection-for-live-path.ts
- peintre-nano/src/app/demo/runtime-demo-manifest.ts
- peintre-nano/src/app/demo/RuntimeDemoApp.tsx
- peintre-nano/tests/unit/admin-registered-devices-client-url.test.ts
- peintre-nano/tests/unit/admin-registered-devices-widget.test.tsx
- peintre-nano/tests/contract/navigation-transverse-served-5-1.test.ts
- peintre-nano/public/manifests/navigation.json
- contracts/creos/manifests/page-transverse-admin-registered-devices.json
- contracts/creos/manifests/navigation-transverse-served.json

### Change Log

- 2026-05-30 — DS gate fix : testids modal edit widget, test unit edit robuste, mock fetch e2e hub 27.3 ; vitest ciblé 59/59 + pytest 17/17.
- 2026-05-30 — CS (create, idempotent) : re-validation epics §27.3, mini-ADR, runbook §4/§7/§8, OpenAPI `recyclique_registeredDevices_*`, stories 27.1/27.2 ; aucun écart bloquant ; Status `review` conservé (DS déjà livré) ; sprint-status non modifié (writer unique).
- 2026-05-30 — Story 27.3 CS (create) : panel SuperAdmin « Gestion des postes », client/widget Peintre, audit mutations admin, gates UI + backend ; Status `ready-for-dev` ; sprint-status inchangé (writer unique).
- 2026-05-30 — VS (validate) : compléments nav `nav-label-presentation-fallbacks.ts`, branchements runtime demo obligatoires, ancre `module-config-client.ts`.
- 2026-05-30 — DS : implémentation complète (audit backend, panel Peintre, CREOS/nav/hub, tests) ; Status `review` ; sprint-status non modifié.
