# Story 27.7 : Intersection serveur modules / poste / opérateur

Status: review

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

**Story key :** `27-7-server-module-intersection`  
**Epic :** 27 — Postes partagés enrôlés + PIN opérateur + PWA installable non-offline  
**Implementation artifact :** `_bmad-output/implementation-artifacts/27-7-server-module-intersection.md`  
**Date CS :** 2026-05-30

## Dépendances (prérequis)

- **Stories 27.1–27.6 done** : registre `RegisteredDevice` + `allowed_module_keys`, contexte serveur + garde `require_active_operator_context`, panel SuperAdmin, enrôlement credential device, PWA non-offline, lock screen PIN + session opérateur — fichiers `_bmad-output/implementation-artifacts/27-1-registered-device.md` … `27-6-pin-lock-operator-session.md`.
- **Story 27.1 (allowlist poste)** : `RegisteredDevice.allowed_module_keys` validée via `is_active_module_key()` — `_bmad-output/implementation-artifacts/27-1-registered-device.md`.
- **Story 27.2 (socle contexte)** : `SharedWorkstationContextService`, `DeviceOperatorSessionService`, `require_active_operator_context`, `assert_context_fresh`, extension `ContextEnvelope` — `_bmad-output/implementation-artifacts/27-2-server-context-audit.md`.
- **Story 27.6 (PIN actif)** : session opérateur post-PIN, lock screen, **pas encore** de filtrage navigation — `_bmad-output/implementation-artifacts/27-6-pin-lock-operator-session.md` (§ hors scope « intersection modules »).
- **Epic 27 — cadrage gelé** : `_bmad-output/planning-artifacts/epics.md` (§ Epic 27, Story 27.7).
- **Mini-ADR Epic 27** : `references/artefacts/2026-05-29_02_mini-adr-postes-partages-pin-non-offline.md` — § Modules (intersection `module_key`, allowlist poste ≠ droits parallèles).
- **Cadrage produit** : `references/artefacts/2026-05-29_01_cadrage-postes-partages-pin-operateur.md` — §3.4–§3.5 (accès post-PIN, allowlist générique).
- **Runbook orchestration** : `references/artefacts/2026-05-29_04_runbook-orchestration-epic-27-postes-partages-pin.md` — ordre §4, invariants §7, gates §8.
- **Pack config modules** : `references/config-modules-site-id/index.md` + `livrable-normatif-architecture.md` — config site-scopée, registre `module_key`, matrice rôle × module × site.
- **Registre module_key** : `references/protocole-modules-recyclique/05-MOD-registre-module-key.md` — liste blanche serveur, pas de second vocabulaire.
- **Contrat OpenAPI** : `contracts/openapi/recyclique-api.yaml` — **cette story étend** le contrat (endpoint modules effectifs + champs enveloppe + garde module).
- **Stories suivantes (ne pas implémenter ici)** : 27.8 (brouillons Reception pilote), 27.9 (timeout / passer la main), 27.10 (override SuperAdmin complet).

## Garde-fous ADR / runbook (obligatoires pour le DS)

| Invariant | Application story 27.7 |
|-----------|---------------------------|
| Autorité serveur | L'intersection est **calculée et imposée côté backend** ; le front affiche une **projection** uniquement. |
| Formule intersection | **`config module site active` × `allowlist poste` × `permissions opérateur`** — pas de fourth factor inventé. |
| Pas authz front | Ne jamais filtrer la navigation depuis `device-status.allowed_module_keys` seul ni depuis CREOS manifests seuls sur poste partagé. |
| Réutiliser `module_key` | Étendre le registre `modules/module_config/registry.py` ; **interdit** de créer un vocabulaire parallèle (`workstation_modules`, `poste_rights`, etc.). |
| Contrôles frontière API | Toute action métier protégée poste partagé doit refuser si `module_key` ∉ intersection effective — **même si l'UI affiche encore le module** (cas stale). |
| Recalcul / refus | Changement droits, poste, site, config module site ou flag `override_active` → recalcul ou refus explicite (409 `CONTEXT_STALE` ou 403 module). |
| Pas offline / no-store | Endpoint modules effectifs : `Cache-Control: no-store` ; client front `cache: 'no-store'`. |
| Pas PIN en audit | Refus module audités sans PIN ; réutiliser `merge_critical_audit_fields`. |
| `device_id` canonique | Distinct de `cash_register_id` et `reception_post_id`. |
| Pas module pilote Reception | **Ne pas** implémenter masquage/reprise brouillons Reception — story **27.8**. |
| Pas généralisation caisse | **Ne pas** brancher l'intersection sur routes caisse / cashflow / réception brownfield — slice poste partagé + preuve API dédiée. |
| Override SuperAdmin | Lire `override_active` pour recalcul ; **ne pas** implémenter l'activation UX override — story **27.10**. |
| Post-PIN 27.6 | Compléter le filtrage navigation temporairement absent ; ne pas casser lock screen / PIN. |

## Story (BDD)

As a **security and product owner**,  
I want **the effective modules for a shared workstation session computed by the backend**,  
So that **a public workstation and a capable operator do not accidentally grant too much access**.

## Acceptance criteria

Source normative : `_bmad-output/planning-artifacts/epics.md` — **Story 27.7**.

**Given** module configuration by `site_id`, workstation allowlist by `module_key`, and operator permissions all exist  
**When** an operator enters a valid PIN on an enrolled workstation  
**Then** effective modules are calculated server-side as active site module configuration × workstation allowlist × operator permissions  
**And** controls are applied at the API boundary, not only in UI projection  
**And** the frontend only displays a projection of the server decision  
**And** business APIs refuse actions outside the intersection, even if the UI still displays a stale module  
**And** changes of rights, workstation, site, module configuration or override force recalculation or refusal  
**And** the story reuses `module_key` and does not create a competing rights vocabulary

### Interprétation exécutable

#### 1. Modèle mental — trois facteurs × opérateur actif

| Facteur | Source serveur | Rôle dans l'intersection |
|---------|----------------|--------------------------|
| Config module site | `SiteModuleConfig` + helpers `ModuleConfigService` (ex. slice actif `kpi-live-banner`) | Module **activé pour le site** ; défaut registre si pas de ligne PG. |
| Allowlist poste | `RegisteredDevice.allowed_module_keys` | Contrainte contextuelle poste — **ne remplace pas** config site ni permissions opérateur. |
| Permissions opérateur | `get_user_permissions(user, db)` sur le `User` de la session PIN active (`operator_user_id`) | Union additive existante (Story 2.3) — comparée à des **clés requises par `module_key`**. |
| Session opérateur | `device_operator_sessions` (27.2) + PIN (27.6) | Prérequis : **aucun calcul d'intersection sans `operator_user_id` actif**. |
| Override | `DeviceOperatorSession.override_active` | Si `true` (27.10 futur) : recalcul documenté ; MVP 27.7 = **pas d'élargissement implicite** — lire le flag et invalider si changement. |

Formule (ensemble fini de `module_key` actifs du registre) :

```text
effective(module_key) =
  is_site_module_enabled(site_id, module_key)
  AND module_key ∈ device.allowed_module_keys
  AND operator_has_required_permissions(operator_user_id, module_key)
  [AND règles override explicites quand 27.10 actif]
```

#### 2. Backend — registre d'accès module (extension `module_key`)

Nouveau module suggéré : `recyclique/api/src/recyclic_api/modules/module_config/access_registry.py` (ou extension de `registry.py` si petit).

Pour chaque entrée `ACTIVE_MODULE_KEYS`, définir :

| Champ | Description |
|-------|-------------|
| `module_key` | Clé registre existante (`kpi-live-banner` pilote MVP). |
| `required_permission_keys` | Liste **toutes requises** (AND) — aligner CREOS quand existant (ex. `recyclique.exploitation.view-live-band` pour bandeau). |
| `site_enabled_resolver` | Callable / nom de helper : « module actif pour ce site ? » |

**MVP pilote registre (2026-05-30)** — une seule clé active côté code :

| `module_key` | `required_permission_keys` | Site enabled |
|--------------|---------------------------|--------------|
| `kpi-live-banner` | `["recyclique.exploitation.view-live-band"]` | `ModuleConfigService.resolve_bandeau_live_slice_enabled(site)` |

**Règles extension** :

- Toute nouvelle clé dans `ACTIVE_MODULE_KEYS` **doit** avoir une entrée access registry avant d'être intersectable.
- **Ne pas** ajouter `reception` / `cashflow` au registre actif dans 27.7 — HITL Epic Runner si tenté.
- SUPER_ADMIN / ADMIN : permissions opérateur = celles de l'utilisateur PIN actif (pas de JWT web seul sur poste partagé).

Helper site enabled générique suggéré :

```python
def is_site_module_enabled(db: Session, *, site_id: uuid.UUID, module_key: str) -> bool:
    """Délègue au resolver du access_registry ; False si module_key inconnu."""
```

#### 3. Backend — service intersection

Nouveau service : `services/shared_workstation_effective_modules_service.py`.

Responsabilités :

1. **`compute_effective_module_keys(*, db, device_id, operator_user_id) -> EffectiveModulesResult`**
   - Charger device `active` + type `shared_workstation`.
   - Vérifier session opérateur active cohérente (`operator_user_id` match).
   - Pour chaque `module_key` ∈ `ACTIVE_MODULE_KEYS` : appliquer la formule §1.
   - Retourner liste ordonnée stable + métadonnées debug **non sensibles** (`computed_at`, `site_id`, `device_id`, `operator_user_id`).
2. **`assert_module_in_effective_set(..., module_key) -> None`**
   - Lève **403** `SHARED_WORKSTATION_MODULE_FORBIDDEN` si absent.
   - Audit `SHARED_WORKSTATION_ACCESS_REFUSED` avec `module_key`, `outcome=module_not_effective`.
3. **`invalidate_on_context_change(...)`** — hook appelé quand :
   - PATCH `allowed_module_keys` device (27.3),
   - PATCH config module site,
   - changement permissions opérateur (documenter : recalcul à la prochaine requête ; optionnel invalidation session si politique stricte — **MVP : recalcul stateless à chaque appel**, pas de cache Redis).

**Pas de cache autoritaire** côté serveur pour l'intersection (vérité recalculée à chaque requête protégée).

#### 4. Backend — API HTTP + OpenAPI

Préfixe : `/v1/shared-workstation/` (`endpoints/shared_workstation.py`).

| Opération | Méthode | Auth | Comportement |
|-----------|---------|------|--------------|
| Modules effectifs | `GET …/effective-modules` | Credential device + JWT + session opérateur active (`require_active_operator_context`) | 200 : `{ "module_keys": ["kpi-live-banner", ...], "computed_at", "site_id", "device_id", "operator_user_id" }` ; `no-store`. |
| Contexte enrichi (option) | Extension `GET /v1/shared-workstation/context` (`SharedWorkstationContextOut`) | Idem | Ajouter **`effective_module_keys`** (liste) — évite N+1 si le client lit ce tuple plutôt que l'enveloppe. |

Codes d'erreur stables :

| Code | HTTP | Quand |
|------|------|-------|
| `SHARED_WORKSTATION_MODULE_FORBIDDEN` | 403 | Action ou module demandé hors intersection |
| `SHARED_WORKSTATION_OPERATOR_REQUIRED` | 403 | Inchangé (27.2) — pas de session PIN |
| `CONTEXT_STALE` | 409 | Inchangé (27.2) — en-tête module/device désaligné |

**Garde FastAPI réutilisable** — `core/shared_workstation_guard.py` :

```python
def require_effective_module(module_key: str):
    """Dependency factory : require_active_operator_context + assert_module_in_effective_set."""
```

Brancher cette garde sur **au moins une route métier pilote** poste partagé (proposition : endpoint lecture bandeau live ou wrapper existant `GET /v2/exploitation/live-snapshot` **uniquement si** déjà appelé depuis poste partagé — sinon **nouvelle route minimale** `GET /v1/shared-workstation/probe-module/{module_key}` réservée tests + preuve refus 403, `no-store`, sans données métier sensibles).

**Couche 27.2 vs 27.7** : `assert_context_fresh` (409 `CONTEXT_STALE`) compare l'en-tête `X-Recyclique-Context-Module-Key` au **`module_key` de session active** ; `require_effective_module` / `assert_module_in_effective_set` (403 `SHARED_WORKSTATION_MODULE_FORBIDDEN`) vérifie l'**intersection effective**. Les deux gardes peuvent coexister sur une même route.

**Ne pas** modifier en masse les routes caisse/réception.

#### 5. Backend — extension `ContextEnvelope`

Étendre **`ContextEnvelopeResponse`** (OpenAPI + Pydantic) :

```yaml
effective_module_keys:
  type: array
  items: { type: string }
  description: >
    Story 27.7 — intersection serveur site × allowlist poste × permissions opérateur.
    Présent uniquement quand device_id + operator_user_id actifs ; sinon absent ou [].
```

Adapter `build_context_envelope(...)` :

- Quand `device_id` fourni **et** session opérateur active : appeler `SharedWorkstationEffectiveModulesService.compute_effective_module_keys`.
- **`permission_keys`** reste le calcul utilisateur global (Story 2.3) — **ne pas** le remplacer par l'intersection ; documenter que l'UI poste partagé doit utiliser **`effective_module_keys`** pour la navigation modules.
- Non-régression : utilisateur web sans poste → champ absent ou `[]`.

#### 6. Backend — audit

Réutiliser socle existant — **pas** de second journal.

| Événement | Quand |
|-----------|--------|
| `SHARED_WORKSTATION_ACCESS_REFUSED` (existant) | Refus module hors intersection — enrichir `details_json` avec `module_key`, `outcome=module_not_effective`. |
| `SHARED_WORKSTATION_CONTEXT_INVALIDATED` (existant) | Recalcul forcé après changement allowlist / config site / override flag. |

Étendre `merge_critical_audit_fields` si besoin : `effective_module_keys_count` (nombre seulement, pas la liste complète si volumineuse — **MVP : autoriser liste** car ≤ few keys).

#### 7. Frontend — projection navigation (Peintre_nano)

**Backend first, UI projection second** (note Story Runner epics).

Nouveau client : `peintre-nano/src/api/shared-workstation-effective-modules-client.ts`

- `GET /v1/shared-workstation/effective-modules` avec en-têtes device + Bearer.
- `fetch(..., { cache: 'no-store' })`.

Provider suggéré : `SharedWorkstationEffectiveModulesProvider.tsx` (ou extension `SharedWorkstationOperatorSessionProvider`).

**Déclenchement** :

1. Identité poste IndexedDB présente.
2. Session opérateur active (post-PIN, poll 27.6).
3. Fetch modules effectifs serveur → état `effectiveModuleKeys: string[]`.

**Filtrage UI (projection)** :

- Hook `useSharedWorkstationModuleAccess()` retourne `{ effectiveModuleKeys, isModuleEffective(key) }`.
- Sur poste partagé avec session PIN : masquer entrées navigation / widgets dont le `module_key` associé ∉ liste serveur.
- **Mapping CREOS → module_key** : table locale minimale (ex. widget bandeau-live → `kpi-live-banner`) — **ne décide pas** l'accès ; sert uniquement à filtrer l'affichage selon la liste serveur.
- **Cas stale UI** : si l'utilisateur force une navigation vers module absent (URL directe, manifest stale) : l'API métier doit retourner 403 ; le front affiche message neutre « Accès non autorisé sur ce poste » et propose refresh enveloppe.

**Ne pas** :

- Filtrer depuis `GET /device-status` allowlist seule.
- Persister `effectiveModuleKeys` dans `localStorage` / IndexedDB comme autorité.
- Implémenter brouillons Reception (27.8).

Intégration shell : `LiveAuthShell.tsx` — après lock screen levé, wrapper provider effective modules ; rafraîchir après PIN succès et sur refresh enveloppe périodique.

#### 8. Tests obligatoires (gates story)

Backend — fichier suggéré : `recyclique/api/tests/test_story_27_7_server_module_intersection.py` (marqueur pytest `story_27_7`).

| # | Cas | AC couvert |
|---|-----|------------|
| 1 | Site actif + allowlist contient `kpi-live-banner` + opérateur avec permission → module ∈ effective set | Intersection OK |
| 2 | Allowlist poste **exclut** le module → effective set vide / module absent | Allowlist |
| 3 | Opérateur **sans** permission requise → module absent malgré allowlist | Permissions |
| 4 | Config site désactive slice (`show_on_*` false) → module absent | Config site |
| 5 | Sans session opérateur → `GET effective-modules` → 403 | Prérequis PIN |
| 6 | Route probe protégée `require_effective_module` → 403 si module ∉ intersection | Frontière API |
| 7 | **Stale UI** : client envoie `X-Recyclique-Context-Module-Key` hors intersection avec session active → 403 ou 409 selon garde | Stale action refused |
| 8 | PATCH allowlist device retire module → prochain appel recalcule (module disparu) | Recalcul |
| 9 | `build_context_envelope` avec device+session → `effective_module_keys` présent | Enveloppe |
| 10 | Utilisateur web sans device → `effective_module_keys` absent/`[]` | Non-régression |
| 11 | `module_key` invalide registre → jamais dans effective set | Non-régression registre |
| 12 | Audit refus module : pas de PIN ; contient `device_id`, `module_key` | Audit |

Frontend :

- `peintre-nano/tests/unit/shared-workstation-effective-modules.test.tsx` — provider fetch mock ; navigation filtrée si module absent.
- `peintre-nano/tests/unit/shared-workstation-effective-modules-client.test.ts` — URLs, headers, no-store.
- Non-régression : lock screen 27.6, admin sans device identity inchangé.

Commandes gates (Story Runner brief) :

```bash
cd recyclique/api && python -m pytest tests/ -k story_27_7 -q
cd peintre-nano && npm run lint
cd peintre-nano && npm run test -- --run
```

### Hors scope explicite

- Module pilote **Reception** : brouillons masqués, reprise, abandon (**27.8**).
- Timeout inactivité, passer la main, verrouillage manuel complet (**27.9**).
- Activation / UX override SuperAdmin (**27.10**) — lire `override_active` seulement pour recalcul.
- Généralisation intersection aux routes **caisse**, **cashflow**, **réception**, **atelier**, **inventaire**.
- Ajout de nouveaux `module_key` au registre actif au-delà de ce qui est nécessaire pour prouver l'intersection (rester sur **`kpi-live-banner`** pilote MVP).
- Cache offline / SW métier.
- Modification `sprint-status.yaml` depuis CS/DS (writer unique Epic Runner).
- Nouveau vocabulaire droits poste (`workstation_permissions`, etc.).

### Dépendances 27.1–27.6 (réutilisation obligatoire)

| Story | Réutiliser (ne pas réécrire) |
|-------|------------------------------|
| 27.1 | `RegisteredDevice.allowed_module_keys`, `is_active_module_key()`, validation allowlist. |
| 27.2 | `SharedWorkstationContextService`, `require_active_operator_context`, `assert_context_fresh`, audit refus/invalidation. |
| 27.3 | PATCH allowlist via panel SuperAdmin — tests recalcul après changement admin. |
| 27.4 | En-têtes `X-Recyclique-Device-Id` / credential ; `require_valid_device_credential`. |
| 27.5 | Clients API `no-store` ; pas de cache SW sur effective-modules. |
| 27.6 | Session opérateur PIN active ; lock screen ; **compléter** filtrage nav post-PIN documenté comme dette 27.6. |

### Anti-patterns (interdits)

- Décider modules visibles depuis `allowed_module_keys` seul (ignore permissions ou config site).
- Filtrer navigation CREOS via `permission_keys` enveloppe globale **sans** `effective_module_keys` sur poste partagé.
- Créer un endpoint parallèle `/workstation-modules` avec vocabulaire différent de `module_key`.
- Autoriser action métier si le widget est affiché côté client mais le serveur refuse.
- Cacher la liste effective modules en localStorage / sessionStorage comme vérité.
- Implémenter brouillons Reception ou routes réception pilote (27.8).
- Brancher intersection sur `POST /v1/auth/pin` (caisse JWT) ou step-up `X-Step-Up-Pin`.
- Ajouter `reception` au registre actif dans cette story sans HITL.
- Modifier toutes les routes brownfield caisse/réception « pour être sûr ».

### Testing / gates (Story Runner)

| Gate | Commande / critère |
|------|-------------------|
| Tests backend 27.7 | `cd recyclique/api && python -m pytest tests/ -k story_27_7 -q` → exit 0 |
| Non-régression Epic 27 | `pytest tests/test_story_27_2_shared_workstation_context.py tests/test_story_27_6_pin_lock_operator_session.py -q` |
| Lint front | `cd peintre-nano && npm run lint` → exit 0 |
| Tests front | `cd peintre-nano && npm run test -- --run` → exit 0 |
| OpenAPI | Schémas ↔ Pydantic ; operationId `recyclique_sharedWorkstation_getEffectiveModules` |
| Revue sécurité | grep : pas de décision authz pure front sur poste partagé |
| YAML sprint (parent) | lecture seule — pas de write CS/DS |

`gates_skipped_with_hitl: false` — aucun skip pour authz, intersection, audit, contrats.

### Project Structure Notes

| Zone | Fichiers / dossiers |
|------|---------------------|
| Access registry | `recyclique/api/src/recyclic_api/modules/module_config/access_registry.py` |
| Service intersection | `recyclique/api/src/recyclic_api/services/shared_workstation_effective_modules_service.py` |
| Garde module | `recyclique/api/src/recyclic_api/core/shared_workstation_guard.py` (extension) |
| Endpoints | `recyclique/api/src/recyclic_api/api/api_v1/endpoints/shared_workstation.py` |
| Schémas | `recyclique/api/src/recyclic_api/schemas/shared_workstation_effective_modules.py` (suggéré) |
| ContextEnvelope | `recyclique/api/src/recyclic_api/services/context_envelope_service.py`, `schemas/context_envelope.py` |
| Tests back | `recyclique/api/tests/test_story_27_7_server_module_intersection.py` |
| Client API front | `peintre-nano/src/api/shared-workstation-effective-modules-client.ts` |
| Provider UI | `peintre-nano/src/domains/shared-workstation/SharedWorkstationEffectiveModulesProvider.tsx` |
| Hook accès | `peintre-nano/src/domains/shared-workstation/useSharedWorkstationModuleAccess.ts` (suggéré) |
| Shell | `peintre-nano/src/app/auth/LiveAuthShell.tsx` |
| Tests front | `peintre-nano/tests/unit/shared-workstation-effective-modules*.test.ts(x)` |
| Contrat | `contracts/openapi/recyclique-api.yaml` |
| Marqueur pytest | `recyclique/api/pyproject.toml` — ajouter `story_27_7` (pattern `story_27_6`) |

### References

- `_bmad-output/planning-artifacts/epics.md` — Epic 27, Story 27.7
- `_bmad-output/implementation-artifacts/27-1-registered-device.md`
- `_bmad-output/implementation-artifacts/27-2-server-context-audit.md`
- `_bmad-output/implementation-artifacts/27-6-pin-lock-operator-session.md`
- `references/artefacts/2026-05-29_02_mini-adr-postes-partages-pin-non-offline.md` — § Modules
- `references/artefacts/2026-05-29_04_runbook-orchestration-epic-27-postes-partages-pin.md` — §7–§8
- `references/config-modules-site-id/index.md`
- `references/config-modules-site-id/livrable-normatif-architecture.md` — §3.3 matrice rôle × module × site
- `references/protocole-modules-recyclique/05-MOD-registre-module-key.md`
- `recyclique/api/src/recyclic_api/modules/module_config/registry.py`
- `recyclique/api/src/recyclic_api/modules/module_config/service.py`
- `recyclique/api/src/recyclic_api/core/auth.py` — `get_user_permissions`
- `contracts/openapi/recyclique-api.yaml`
- `contracts/creos/manifests/page-bandeau-live-sandbox.json` — permission bandeau
- `_bmad-output/project-context.md`

## Trace Epic 27 — ADR

| Élément | Valeur |
|--------|--------|
| Nouvelle ADR structurante requise ? | **ADR N/A pour 27.7** — implémentation mini-ADR § Modules + pack config-modules-site-id. |
| ADR applicables | Mini-ADR 2026-05-29 ; ADR-001 config modules JSON par site. |

## Alignement sprint / YAML

- Clé **`27-7-server-module-intersection`** : **non modifiée** par ce worker CS (writer unique Epic Runner — pas de passage `ready-for-dev` dans `sprint-status.yaml` depuis CS).
- **`epic-27`** : inchangé par CS.
- Prochaine story après clôture 27.7 : **`27-8-reception-pilot-drafts`** (ordre runbook §4).

## Risques / HITL

| Sujet | Statut | Action |
|-------|--------|--------|
| Granularité liste `module_key` disponibles | Risque epics | MVP : prouver avec **`kpi-live-banner`** seul ; HITL si extension registre avant prod multi-modules. |
| Mapping permission ↔ module_key | **Décision VS (vs_loop=0)** | MVP : table statique `access_registry.py` alignée CREOS ; pas de table SQL permissions↔module. |
| Route probe vs route métier existante | Proposition DS | Préférer route probe dédiée + un appel front bandeau si déjà présent ; HITL si toucher live-snapshot brownfield. |
| Recalcul permissions mid-session | Accepté MVP | Recalcul stateless ; pas d'invalidation session automatique sauf `CONTEXT_STALE` en-têtes. |
| Override SuperAdmin | Partiel 27.7 | Lire flag ; comportement élargissement = **27.10**. |
| Réception pilote | Hors scope | **NEEDS_HITL** si DS tente brouillons Reception. |

**NEEDS_STROPHE_HITL** : non requis pour démarrer le DS si le dev suit les propositions ci-dessus (service intersection, endpoint effective-modules, garde API, projection front, pilote `kpi-live-banner`).

## Checklist VS (validate-create-story)

**Verdict VS :** **PASS** (vs_loop=0) — story prête pour DS.

- [x] AC BDD alignés `epics.md` §27.7 (intersection triple, front projection, refus API stale, recalcul, module_key).
- [x] Garde-fous mini-ADR + runbook §7 (pas authz front, pas offline, device_id canonique).
- [x] Dépendances 27.1, 27.2, 27.6 explicites ; réutilisation guards/session (`shared_workstation_guard.py` existant).
- [x] Hors scope 27.8–27.10 + pas généralisation caisse/réception.
- [x] Formule intersection documentée avec sources code concrètes (`registry.py`, `ModuleConfigService`, `build_context_envelope`).
- [x] Gates § Testing (pytest `story_27_7`, lint, vitest, non-régression 27.2/27.6).
- [x] Anti-patterns couvrent allowlist seule, localStorage, vocabulaire parallèle.
- [x] `sprint-status.yaml` non modifié par CS/VS (writer unique Epic Runner).
- [x] OpenAPI ↔ implémentation (`effective-modules`, `effective_module_keys` enveloppe) ; distinction 409 session vs 403 intersection documentée.

## Definition of Done

- [x] `access_registry.py` + resolver site enabled pour `kpi-live-banner`.
- [x] `SharedWorkstationEffectiveModulesService` + tests matrice permissions.
- [x] Route `GET /v1/shared-workstation/effective-modules` + garde `require_effective_module`.
- [x] Extension `ContextEnvelope.effective_module_keys` + OpenAPI aligné.
- [x] Audit refus module enrichi ; pas de PIN en logs.
- [x] Client + provider front ; projection navigation post-PIN sur liste serveur.
- [x] Tests `test_story_27_7_*` + tests UI — **exit 0**.
- [x] **Hors scope respecté** : pas Reception brouillons (27.8), pas timeout (27.9), pas override UX (27.10).
- [x] Non-régression lock screen 27.6 + admin sans device identity.
- [x] **Hors scope respecté** : pas de modification `sprint-status.yaml` / `epics.md` par le worker DS.

## Tasks / Subtasks (DS)

- [x] **Access registry** : mapping `module_key` → permissions + site enabled (AC: réutiliser vocabulaire registre).
- [x] **Service intersection** : compute + assert + hooks recalcul (AC: formule triple facteur).
- [x] **Endpoint API** : `GET effective-modules` + route probe garde module (AC: refus frontière API).
- [x] **ContextEnvelope** : champ `effective_module_keys` + OpenAPI (AC: projection serveur).
- [x] **Garde FastAPI** : `require_effective_module` factory (AC: stale UI refused).
- [x] **Client API front** : fetch no-store + en-têtes device (AC: pas authz front).
- [x] **Provider + hook UI** : filtrage navigation projection (AC: front non autoritaire).
- [x] **Tests backend** : suite `test_story_27_7_*` matrice + stale (AC: gates pytest).
- [x] **Tests frontend** : unit provider/client (AC: gates vitest).
- [x] **Revue périmètre** : grep authz front ; non-régression 27.6.

### Review Findings (CR 2026-05-30, cr_loop=0)

**Verdict :** merge-ready — **PASS** (1 patch MEDIUM appliqué en CR).

- [x] [Review][Patch] Fenêtre sans filtrage nav post-PIN [`RuntimeDemoApp.tsx`] — corrigé : `navEffectiveModuleKeys` utilise `fetchedModuleKeys` (y compris `[]`) dès `hasDevice && operatorSessionActive`, fail-closed pendant le fetch.
- [x] [Review][Defer] Credential device optionnel sur `require_active_operator_context` si en-tête absent — comportement hérité 27.2/27.4, hors diff 27.7.
- [x] [Review][Defer] Entrées nav sans mapping `module_key` passent le filtre module (restent soumises à `permission_keys`) — MVP pilote `kpi-live-banner` documenté.
- [x] [Review][Defer] Double appel `compute_effective_module_keys` sur `GET /context` — perf seulement.
- [x] [Review][Defer] Message UI neutre sur 403 stale non implémenté dans le provider — refus API couvert ; UX 27.8+.

**Layers :** Acceptance Auditor (spec/ADR/runbook §7) + Edge Case Hunter (exécution locale, pas de sous-agents Task) ; Blind Hunter équivalent via lecture diff ciblée.

**Gates revérifiés CR :** pytest `story_27_7` 14/14 PASS.

## Dev Notes

### Contexte brownfield — permissions vs modules

| Mécanisme | Fichier | Usage 27.7 |
|-----------|---------|------------|
| `get_user_permissions` | `core/auth.py` | Permissions opérateur PIN (via `User` session active). |
| `ModuleConfigService.resolve_bandeau_live_slice_enabled` | `modules/module_config/service.py` | Facteur « site actif » pilote `kpi-live-banner`. |
| `RegisteredDevice.allowed_module_keys` | `models/registered_device.py` | Allowlist poste. |
| CREOS `required_permission_keys` | `contracts/creos/manifests/*.json` | Alignement mapping access registry — **pas** source autorité. |
| `permission_keys` enveloppe | `context_envelope_service.py` | Permissions globales utilisateur — **≠** modules effectifs poste. |

### Previous story intelligence (27.6 → 27.7)

- 27.6 documente explicitement : post-PIN shell visible **sans filtrage intersection** — acceptable temporairement ; **27.7 rattrape**.
- Lock screen reste prioritaire : intersection ne s'applique **qu'après** session opérateur active.
- Poll session 30s (27.6) : ajouter refresh effective modules sur même cycle ou après refresh enveloppe.
- En-têtes device déjà branchés sur clients PIN — réutiliser pattern `shared-workstation-operator-pin-client.ts`.
- `fetchRecycliqueContextEnvelope` (`recyclique-auth-client.ts`) fusionne déjà `sharedWorkstationAuthHeaders()` sur `GET /v1/users/me/context` — le champ `effective_module_keys` de l'enveloppe sera disponible après extension `build_context_envelope` sans nouveau client enveloppe obligatoire (le client dédié `effective-modules` reste la source navigation post-PIN).

### Intelligence stories 27.1–27.5

- Allowlist validée à la création device (`is_active_module_key`) — intersection ne re-valide pas le registre, seulement l'effet runtime.
- `GET /device-status` expose allowlist brute — **interdit** comme source navigation post-PIN.
- PWA + IndexedDB identité : effective modules = **toujours** fetch réseau post-PIN.

### Library / framework

- Backend : FastAPI, SQLAlchemy sync, pattern service 27.2/27.6.
- Front : React + Mantine ; provider pattern 27.6.
- Tests : pytest marqueur `story_27_7` ; vitest co-localisé.

### Architecture compliance

- Autorité serveur : intersection recalculée serveur ; API refuse hors ensemble.
- Contrat erreur stable : `{ code, message }`.
- OpenAPI fusion unique `recyclique-api.yaml`.
- Sync ORM : services en `def` si pas d'await.

## Dev Agent Record

### Agent Model Used

Composer (DS sub-agent Story Runner)

### Debug Log References

- Correction UUID opérateur dans `compute_effective_module_keys` (`db.get(User, uuid.UUID(...))`).
- Garde probe : `require_effective_module_from_path` pour paramètre chemin dynamique.

### Completion Notes List

- Backend : `access_registry.py` (pilote `kpi-live-banner`), `SharedWorkstationEffectiveModulesService`, endpoints `GET /effective-modules` + `GET /probe-module/{module_key}`, gardes `require_effective_module` / `require_effective_module_from_path`, extension `ContextEnvelope.effective_module_keys` + contexte partagé enrichi, hook invalidation allowlist.
- Front : client `shared-workstation-effective-modules-client.ts`, provider + hook, filtrage nav via `filterNavigation` + mapping CREOS→module_key, intégration `LiveAuthShell` / `RuntimeDemoApp`.
- OpenAPI : opérations `recyclique_sharedWorkstation_getEffectiveModules`, `recyclique_sharedWorkstation_probeModule`, schémas alignés.
- Tests locaux : pytest `-k story_27_7` **14/14 PASS** ; vitest **811/811 PASS** ; lint tsc **PASS**.

### File List

- `recyclique/api/src/recyclic_api/modules/module_config/access_registry.py` (new)
- `recyclique/api/src/recyclic_api/services/shared_workstation_effective_modules_service.py` (new)
- `recyclique/api/src/recyclic_api/schemas/shared_workstation_effective_modules.py` (new)
- `recyclique/api/src/recyclic_api/core/shared_workstation_guard.py`
- `recyclique/api/src/recyclic_api/api/api_v1/endpoints/shared_workstation.py`
- `recyclique/api/src/recyclic_api/schemas/context_envelope.py`
- `recyclique/api/src/recyclic_api/schemas/shared_workstation_context.py`
- `recyclique/api/src/recyclic_api/services/context_envelope_service.py`
- `recyclique/api/src/recyclic_api/services/registered_device_service.py`
- `recyclique/api/tests/test_story_27_7_server_module_intersection.py` (new)
- `recyclique/api/pyproject.toml`
- `contracts/openapi/recyclique-api.yaml`
- `peintre-nano/src/api/shared-workstation-effective-modules-client.ts` (new)
- `peintre-nano/src/domains/shared-workstation/SharedWorkstationEffectiveModulesProvider.tsx` (new)
- `peintre-nano/src/domains/shared-workstation/useSharedWorkstationModuleAccess.ts` (new)
- `peintre-nano/src/domains/shared-workstation/shared-workstation-nav-module-mapping.ts` (new)
- `peintre-nano/src/runtime/filter-navigation-for-context.ts`
- `peintre-nano/src/types/context-envelope.ts`
- `peintre-nano/src/api/context-envelope-from-api.ts`
- `peintre-nano/src/app/auth/LiveAuthShell.tsx`
- `peintre-nano/src/app/demo/RuntimeDemoApp.tsx`
- `peintre-nano/tests/unit/shared-workstation-effective-modules-client.test.ts` (new)
- `peintre-nano/tests/unit/shared-workstation-effective-modules.test.tsx` (new)
- `peintre-nano/tests/e2e/shared-workstation-module-intersection-27-7.e2e.test.tsx` (new)
- `peintre-nano/src/domains/shared-workstation/SharedWorkstationOperatorSessionProvider.tsx` (CR)
- `peintre-nano/src/app/demo/RuntimeDemoApp.tsx` (CR)
- `_bmad-output/implementation-artifacts/27-7-server-module-intersection.md`

## Change Log

- 2026-05-30 — Story 27.7 CS (create) : guide dev intersection serveur modules × allowlist poste × permissions opérateur ; endpoint effective-modules ; extension ContextEnvelope ; projection front ; pilote `kpi-live-banner` ; Status `ready-for-dev` ; sprint-status non modifié (writer unique).
- 2026-05-30 — Story 27.7 VS (validate, vs_loop=0) : PASS ; précisions signature `get_user_permissions`, dualité gardes 409/403, chemins contexte partagé vs enveloppe, en-têtes device déjà sur `fetchRecycliqueContextEnvelope`.
- 2026-05-30 — Story 27.7 DS : implémentation intersection serveur + projection front ; tests gates PASS ; Status `review`.
- 2026-05-30 — Story 27.7 CR (cr_loop=0) : PASS merge-ready ; patch fail-closed nav post-PIN ; pytest 14/14 revérifié.
