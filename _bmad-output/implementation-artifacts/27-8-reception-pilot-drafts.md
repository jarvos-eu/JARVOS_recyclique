# Story 27.8 : Pilote Reception — brouillons masqués et reprise autorisée

Status: review

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

**Story key :** `27-8-reception-pilot-drafts`  
**Epic :** 27 — Postes partagés enrôlés + PIN opérateur + PWA installable non-offline  
**Implementation artifact :** `_bmad-output/implementation-artifacts/27-8-reception-pilot-drafts.md`  
**Date CS :** 2026-05-30

## Dépendances (prérequis)

- **Stories 27.1–27.7 done** : registre `RegisteredDevice`, contexte serveur + garde `require_active_operator_context`, panel SuperAdmin, enrôlement credential device, PWA non-offline, lock screen PIN + session opérateur, intersection modules serveur — fichiers `_bmad-output/implementation-artifacts/27-1-registered-device.md` … `27-7-server-module-intersection.md`.
- **Story 27.6 (PIN / lock)** : lock screen sans données métier ; session opérateur ; pattern reset brouillon caisse au verrouillage (`LiveAuthShell` → `resetCashflowDraft`) — `_bmad-output/implementation-artifacts/27-6-pin-lock-operator-session.md`.
- **Story 27.7 (intersection)** : `SharedWorkstationEffectiveModulesService`, `require_effective_module`, `effective_module_keys`, client/provider front `no-store` — `_bmad-output/implementation-artifacts/27-7-server-module-intersection.md`.
- **Epic 7 (réception v2 brownfield)** : parcours nominal `ReceptionNominalWizard`, API `/v1/reception/*`, modèles `PosteReception` + `TicketDepot` — ne pas réécrire le flux métier ; **borner** au contexte poste partagé.
- **Epic 27 — cadrage gelé** : `_bmad-output/planning-artifacts/epics.md` (§ Epic 27, Story 27.8).
- **Mini-ADR Epic 27** : `references/artefacts/2026-05-29_02_mini-adr-postes-partages-pin-non-offline.md` — § Brouillons (serveur-autoritatif, `network-only` / `no-store`, audit reprise/abandon).
- **Cadrage produit** : `references/artefacts/2026-05-29_01_cadrage-postes-partages-pin-operateur.md` — §3.11–§3.12 (masquage sans PIN, reprise inter-opérateur, minimisation métadonnées).
- **Runbook orchestration** : `references/artefacts/2026-05-29_04_runbook-orchestration-epic-27-postes-partages-pin.md` — ordre §4, invariants §7, gates §8 ; **refus** extension 27.8 à la caisse (§6).
- **Pack config modules** : `references/config-modules-site-id/index.md` — config site-scopée ; resolver MVP `reception` pilote (`site.is_active`) documenté comme dette jusqu’à schema JSON dédié.
- **Registre `module_key`** : `references/protocole-modules-recyclique/05-MOD-registre-module-key.md` — clé **`reception`** (domaine-parcours, réservée → **promotion pilote** dans cette story uniquement).
- **Contrat OpenAPI** : `contracts/openapi/recyclique-api.yaml` — **cette story étend** le contrat (routes brouillon poste partagé + garde réception + événements audit).
- **Stories suivantes (ne pas implémenter ici)** : 27.9 (timeout / passer la main), 27.10 (override SuperAdmin complet).

## Garde-fous ADR / runbook (obligatoires pour le DS)

| Invariant | Application story 27.8 |
|-----------|-------------------------|
| Module pilote **Reception uniquement** | Pas de masquage/reprise brouillon caisse (`cashflow-draft-store`), atelier, inventaire — **NEEDS_HITL** si extension demandée. |
| Autorité serveur | Visibilité et actions brouillon **refusées ou filtrées côté API** ; le front masque en projection seulement. |
| Intersection 27.7 | Opérateur post-PIN doit avoir `reception` ∈ `effective_module_keys` **et** `reception.access` via la formule site × allowlist × permissions. |
| Pas de fuite sans PIN | Lock screen et appels sans session opérateur : **aucun** contenu ticket/ligne/poids/bénévole ; pas de métadonnée sensible (compteur, nom, horodatage précis) hors contexte autorisé. |
| `network-only` / `no-store` | Tous endpoints brouillon et lectures réception protégées poste partagé : `Cache-Control: no-store` ; client `fetch(..., { cache: 'no-store' })`. |
| Pas cache offline | Aucun SW / cache persistant des payloads brouillon ; état UI réception **non autoritaire** (réinitialiser au verrouillage). |
| Pas `localStorage` autoritaire | Ne pas persister brouillon réception comme vérité ; `reception-poste-ui-state.ts` reste indicateur UI **réinitialisé** au lock. |
| Reprise inter-opérateur | Un opérateur autorisé **différent** de `opened_by_user_id` peut reprendre **avec confirmation explicite** (cadrage §3.12) — adapter `_assert_poste_operator` **uniquement** en contexte `device_id` poste partagé. |
| Audit | Reprise, abandon, refus accès brouillon : `log_audit` + `merge_critical_audit_fields` ; **pas** de PIN ni contenu ligne en `details_json`. |
| `device_id` canonique | Lier le brouillon au **poste partagé enrôlé** (`RegisteredDevice.id`), pas au `poste_reception.id` métier seul. |
| Distinction identifiants | `device_id` ≠ `poste_reception.id` ≠ `cash_register_id` ≠ futur `reception_post_id`. |
| Pas timeout / handoff | Verrouillage par inactivité, avertissement, bouton « passer la main » — story **27.9**. |
| Pas override SuperAdmin | Activation UX override — story **27.10**. |

## Story (BDD)

As a **reception operator**,  
I want **drafts on the Reception module hidden while the workstation is locked and recoverable only by an authorized operator**,  
So that **the shared workstation pattern is proven on a real field flow without expanding to every module**.

## Acceptance criteria

Source normative : `_bmad-output/planning-artifacts/epics.md` — **Story 27.8**.

**Given** Reception is the only pilot module for this story  
**When** the workstation is locked or has no active PIN operator  
**Then** Reception drafts are not visible and sensitive draft metadata does not leak  
**And** Reception draft endpoints and payloads remain authenticated and `network-only` / `no-store`  
**And** after PIN, an operator authorized by the site × workstation × permission intersection can see, resume or abandon the draft with explicit confirmation  
**And** an unauthorized operator sees neither content nor sensitive metadata  
**And** resume and abandon actions are audited  
**And** the story does not generalize to caisse / cash register, atelier, inventaire or other modules

### Interprétation exécutable

#### 1. Définition métier — « brouillon Reception » (MVP Epic 27)

Pour le pilote poste partagé, le **brouillon** désigne une **session réception en cours côté serveur** :

| Élément | Modèle / statut | Rôle |
|---------|-----------------|------|
| Poste réception ouvert | `PosteReception.status = opened` | Conteneur de session terrain |
| Ticket ouvert | `TicketDepot.status = opened` sur ce poste | Saisie en cours (lignes éventuelles) |
| Ancrage poste partagé | **`device_id`** (nouvelle colonne ou table de liaison) | Le brouillon appartient au **poste enrôlé**, pas seulement à l’utilisateur JWT qui l’a ouvert |
| Opérateur d’origine | `PosteReception.opened_by_user_id` + session PIN courante | Attribution audit ; **ne bloque pas** la reprise par un autre opérateur autorisé sur le même `device_id` |

**Hors définition brouillon 27.8** : brouillon UI caisse (`cashflow-draft-store`), champ local `poidsDraft` du wizard (saisie clavier), tickets **fermés**, historique admin `/admin/reception-sessions`.

**Un seul brouillon actif par `device_id`** (MVP) : ouvrir un nouveau poste alors qu’un brouillon existe → **409** `SHARED_WORKSTATION_RECEPTION_DRAFT_ALREADY_ACTIVE` ou politique documentée de remplacement — **préférer refus** sauf HITL.

#### 2. Promotion `module_key` = `reception` (intersection 27.7)

**Cette story** active la clé pilote dans le registre serveur (27.7 l’a explicitement différée).

| Fichier | Action |
|---------|--------|
| `modules/module_config/registry.py` | Ajouter `MODULE_KEY_RECEPTION = "reception"` à `ACTIVE_MODULE_KEYS` ; entrée registre **sans** `schema_relative_path` obligatoire si pas de document JSON site (pilote : resolver site simplifié). |
| `modules/module_config/access_registry.py` | Entrée : `required_permission_keys = ("reception.access",)` ; `site_enabled_resolver` : **MVP pilote** → `True` si site actif existe (documenter dette : futur `SiteModuleConfig` document `reception` quand HITL schema). |
| Panel SuperAdmin 27.3 | Allowlist poste peut déjà contenir `reception` si validé par `is_active_module_key()` après promotion. |

**Mapping CREOS → module_key** (`shared-workstation-nav-module-mapping.ts`) — manifeste `contracts/creos/manifests/navigation-transverse-served.json` (`id` / `route_key` / `page_key` = `reception-nominal`) :

```typescript
'reception-nominal': 'reception', // pageKey et routeKey identiques dans le manifeste
```

**Ne pas** activer `cashflow` ni autres clés réservées.

#### 3. Backend — persistance `device_id` sur le brouillon

**Migration Alembic** suggérée :

- Colonne nullable `registered_device_id` (UUID FK → `registered_devices.id`) sur `poste_reception`, **renseignée uniquement** lors d’ouverture poste depuis contexte poste partagé (en-têtes device + session opérateur).
- Index `(registered_device_id)` WHERE status = opened pour lookup rapide.
- Brownfield : postes ouverts **sans** `registered_device_id` restent gérés par les règles Epic 7 classiques (JWT seul) — pas de régression.

Alternative acceptée si plus propre : table `shared_workstation_reception_drafts` (`device_id`, `poste_id`, `ticket_id`, `started_at`, `started_by_operator_user_id`) — **une** ligne active par `device_id`.

#### 4. Backend — service brouillon poste partagé

Nouveau service : `services/shared_workstation_reception_draft_service.py`.

| Méthode | Comportement |
|---------|--------------|
| `get_draft_for_device(*, db, device_id, operator_user_id)` | Prérequis : device actif `shared_workstation` ; session opérateur active ; `assert_module_in_effective_set(..., "reception")` ; opérateur a `reception.access`. Si brouillon absent → `null`. Si opérateur **non** autorisé → lever **403** sans fuite (même forme que « absent » côté client **ou** code distinct documenté — **préférer 403 générique** pour opérateur sans droit module). |
| `build_authorized_summary(draft, viewer)` | Retour **minimal** autorisé : `poste_id`, `ticket_id`, `started_by_display` (prénom/initiales — politique minimisation), `started_at` (ISO), `line_count` (entier), **pas** de lignes ni poids ni `benevole_user_id` brut si politique stricte. |
| `resume_draft(*, ..., confirm: bool)` | Exige `confirm=true` ; attache session opérateur courante ; audit `SHARED_WORKSTATION_RECEPTION_DRAFT_RESUMED` ; retourne ids pour hydrater le wizard. |
| `abandon_draft(*, ..., confirm: bool)` | Exige `confirm=true` ; ferme ticket ouvert puis poste (réutiliser `ReceptionService.close_ticket` / `close_poste` avec garde poste partagé) ; audit `SHARED_WORKSTATION_RECEPTION_DRAFT_ABANDONED`. |

**Règle anti-fuite (sans session PIN)** :

- `get_draft_for_device` et routes réception détail **interdites** sans `require_active_operator_context`.
- Les endpoints **publics** ou JWT-seuls existants (`GET /v1/reception/tickets/{id}`) doivent **refuser ou masquer** les tickets liés à un `registered_device_id` quand l’appelant est un poste partagé verrouillé — stratégie recommandée :

  1. Détecter en-têtes `X-Recyclique-Device-Id` + credential valide **sans** session opérateur → **403** `SHARED_WORKSTATION_OPERATOR_REQUIRED` sur toute lecture/écriture réception nominale.
  2. Ne pas s’appuyer sur le masquage UI seul.

**Scope poste partagé (injection routes réception)** :

- Dataclass `SharedWorkstationReceptionScope(device_id: str)` dans `reception_service.py`.
- Dependency FastAPI `get_optional_shared_workstation_reception_scope` (`shared_workstation_guard.py`) : si en-têtes device présents → credential + session opérateur + `assert_module_in_effective_set(..., "reception")` ; sinon `None` (brownfield web).
- Helper `_is_shared_workstation_actor(poste, user, shared_workstation_scope=...)` : vrai si `poste.registered_device_id == scope.device_id` **et** `assert_nominal_reception_eligible(user)` (permission `RECEPTION_ACCESS_PERMISSION_KEY` = `"reception.access"`).
- Passer `shared_workstation_scope=ws_scope` à **toutes** les méthodes `ReceptionService` concernées depuis `reception.py` (open poste, tickets, lignes, close, GET détail).

**Adapter** `ReceptionService._assert_poste_operator` :

- Si `poste.registered_device_id` est renseigné : autoriser l’acteur via `_is_shared_workstation_actor` — **pas** uniquement `opened_by_user_id == actor.id`.
- Sinon : comportement brownfield inchangé.

**Adapter aussi** `_assert_ticket_write_actor` et `_assert_ticket_readable` (sinon reprise inter-opérateur **bloquée** après hydratation du wizard) :

- Si le ticket appartient à un poste avec `registered_device_id` renseigné : autoriser lecture/écriture si session opérateur active sur **le même** `device_id`, `reception` ∈ intersection effective, et `reception.access` — **sans** exiger `ticket.benevole_user_id == actor.id` ni `poste.opened_by_user_id == actor.id` (le bénévole métier du ticket reste inchangé).
- Brownfield (poste sans `registered_device_id`) : règles Epic 7 inchangées (`opened_by_user_id`, `benevole_user_id`).
- Admin / SuperAdmin : inchangé.

#### 5. Backend — API HTTP + OpenAPI

Préfixe : `/v1/shared-workstation/` (`endpoints/shared_workstation.py`).

| Opération | Méthode | Auth | Réponse / notes |
|-----------|---------|------|-----------------|
| Résumé brouillon | `GET …/reception-draft` | Credential device + session opérateur + module `reception` effectif | 200 `{ summary }` ou 204 si aucun brouillon ; `no-store`. |
| Reprendre | `POST …/reception-draft/resume` | Idem | Body `{ "confirm": true }` ; 200 `{ poste_id, ticket_id }` ; audit. |
| Abandonner | `POST …/reception-draft/abandon` | Idem | Body `{ "confirm": true }` ; 200 vide ou `{ abandoned: true }` ; audit. |

**Extension optionnelle** (éviter N+1) : enrichir `GET /v1/shared-workstation/context` avec `reception_draft_summary` **uniquement** si module effectif et session active — champ absent sinon.

Codes d’erreur stables :

| Code | HTTP | Quand |
|------|------|-------|
| `SHARED_WORKSTATION_OPERATOR_REQUIRED` | 403 | Inchangé — pas de PIN |
| `SHARED_WORKSTATION_MODULE_FORBIDDEN` | 403 | `reception` ∉ intersection |
| `SHARED_WORKSTATION_RECEPTION_DRAFT_FORBIDDEN` | 403 | Opérateur sans `reception.access` ou refus politique |
| `SHARED_WORKSTATION_RECEPTION_DRAFT_ALREADY_ACTIVE` | 409 | Second brouillon sur même device |
| `SHARED_WORKSTATION_RECEPTION_DRAFT_NOT_FOUND` | 404 | Reprise/abandon sans brouillon |

**Garde sur routes réception existantes** (poste partagé uniquement) :

- Factory `require_shared_workstation_reception_access` dans `shared_workstation_guard.py` : enchaîne credential device → `require_active_operator_context` → `require_effective_module(MODULE_KEY_RECEPTION)`.
- `resolve_shared_workstation_reception_scope_when_device_present` : en-têtes device **sans** session opérateur → **403** `SHARED_WORKSTATION_OPERATOR_REQUIRED` (anti-fuite avant PIN).
- Brancher `Depends(get_optional_shared_workstation_reception_scope)` sur : `POST /v1/reception/postes/open`, `POST /v1/reception/tickets`, `GET /v1/reception/tickets/{id}`, mutations lignes du parcours nominal — **liste minimale** pour gates ; ne pas refactoriser tout `reception.py` hors contexte device.

#### 6. Backend — audit

Étendre `AuditEventType` :

| Événement | Quand |
|-----------|--------|
| `SHARED_WORKSTATION_RECEPTION_DRAFT_RESUMED` | Reprise confirmée |
| `SHARED_WORKSTATION_RECEPTION_DRAFT_ABANDONED` | Abandon confirmé |
| `SHARED_WORKSTATION_RECEPTION_DRAFT_ACCESS_REFUSED` | Lecture/refus sans droit (optionnel si non redondant avec `SHARED_WORKSTATION_ACCESS_REFUSED`) |

`details_json` suggéré : `device_id`, `poste_id`, `ticket_id`, `operator_user_id`, `previous_operator_user_id`, `outcome` — **jamais** lignes, poids, PIN.

#### 7. Frontend — masquage, reprise, abandon (Peintre_nano)

**Pattern caisse (27.6)** : au verrouillage / fin session opérateur, réinitialiser l’état réception **non autoritaire** :

| Fichier | Action |
|---------|--------|
| `reception-poste-ui-state.ts` | Exporter `resetReceptionPosteUiState()` ; appeler depuis le provider lock (même hook que `resetCashflowDraft`). |
| `ReceptionNominalWizard.tsx` | Ne pas afficher poste/ticket/lignes si `useSharedWorkstationLockRequired()` (hook `SharedWorkstationOperatorSessionProvider`, Story 27.6) ; après PIN, si brouillon serveur → écran reprise/abandon avant reprise du wizard. |
| Nouveau composant suggéré | `SharedWorkstationReceptionDraftResumePanel.tsx` — libellé neutre, confirmation Mantine, appels client API `no-store`. |
| `shared-workstation-reception-draft-client.ts` | `GET/POST` vers routes §5 avec en-têtes device. |
| `LiveAuthShell.tsx` / `SharedWorkstationOperatorSessionProvider` | Sur transition vers lock : reset réception + caisse (déjà partiel). |
| `shared-workstation-nav-module-mapping.ts` | Mapper entrées nav réception → `reception`. |
| `filter-navigation-for-context.ts` | Inchangé si provider effective modules déjà branché — vérifier non-régression. |

**Écran PIN** : aucun libellé du type « brouillon en attente », compteur, nom opérateur (cadrage §3.11).

**Après PIN autorisé** :

- Afficher résumé serveur (§4 `build_authorized_summary`) — texte type : « Brouillon commencé par {display} à {heure locale} » (HITL : granularité display — voir § Risques).
- Actions : **Reprendre** (confirm) → hydrate `posteId` / `ticketId` via API ; **Abandonner** (confirm) → reset UI.

**Historique réception** (`ReceptionHistoryPanel`) : masquer ou désactiver sur poste partagé sans module effectif ; pas de liste tickets pendant lock.

#### 8. Tests obligatoires (gates story)

Backend — `recyclique/api/tests/test_story_27_8_reception_pilot_drafts.py` (marqueur `story_27_8`).

**Réutiliser helpers tests Epic 27** : `_device_headers`, `_complete_enrollment`, `_create_pending_device` depuis `test_story_27_4_enrollment_reconnect_replace.py` ; `grant_user_reception_eligibility` depuis `reception_story72_eligibility.py` ; patterns session PIN depuis `test_story_27_6_pin_lock_operator_session.py`.

| # | Cas | AC couvert |
|---|-----|------------|
| 1 | Device verrouillé (pas de session) → `GET reception-draft` → 403 | Masqué sans PIN |
| 2 | Session active + intersection `reception` + droits → résumé brouillon 200 sans lignes | Reprise autorisée |
| 3 | Session active **sans** `reception.access` → 403, corps sans métadonnée sensible | Non autorisé |
| 4 | Session active sans `reception` dans allowlist → 403 module | Intersection |
| 5 | `GET /v1/reception/tickets/{id}` avec device credential **sans** PIN → 403 | Pas de fuite API |
| 6 | Reprise par opérateur B d’un brouillon ouvert par A (même device) + `confirm` → 200 + audit RESUMED | Inter-opérateur |
| 6b | Après reprise par B : mutation ligne ou `GET /v1/reception/tickets/{id}` → 200 (pas 403 périmètre opérateur) | Gardes ticket poste partagé |
| 7 | Abandon + `confirm` → ticket/poste fermés + audit ABANDONED | Abandon |
| 8 | Reprise/abandon sans `confirm: true` → 422 | Confirmation |
| 9 | En-têtes réponse `Cache-Control: no-store` sur routes brouillon | network-only |
| 10 | Utilisateur web **sans** device → parcours réception brownfield inchangé | Non-régression |
| 11 | `reception` absent de effective set → pas de résumé dans context | Intersection |
| 12 | Lock screen e2e : pas de `data-testid` ticket/ligne dans le DOM lock | UI masquée |

Frontend :

- `peintre-nano/tests/unit/shared-workstation-reception-draft.test.tsx`
- `peintre-nano/tests/e2e/shared-workstation-reception-draft-27-8.e2e.test.tsx`
- Non-régression : `shared-workstation-operator-session`, `shared-workstation-effective-modules`, lock screen 27.6.

Commandes gates :

```bash
cd recyclique/api && python -m pytest tests/ -k story_27_8 -q
cd peintre-nano && npm run lint
cd peintre-nano && npm run test -- --run
```

Ajouter marqueur `story_27_8` dans `recyclique/api/pyproject.toml` (même pattern que `story_27_7`).

### Hors scope explicite

- Brouillons **caisse** / `cashflow-draft-store` / held sales.
- Timeout, avertissement pré-lock, « passer la main », verrouillage manuel complet (**27.9**).
- Override SuperAdmin (**27.10**).
- Généralisation atelier, inventaire, autres modules.
- Reporting audit avancé, UI admin liste tickets poste partagé.
- Document JSON `module-config` complet pour `reception` (activation site fine) — sauf resolver MVP §2.
- Modification `sprint-status.yaml` depuis CS/DS (writer unique Epic Runner).
- Service worker / cache offline des drafts.

### Dépendances 27.1–27.7 (réutilisation obligatoire)

| Story | Réutiliser |
|-------|------------|
| 27.1 | `RegisteredDevice`, allowlist `module_key`. |
| 27.2 | `require_active_operator_context`, audit helpers, refus sans opérateur. |
| 27.4 | En-têtes device credential. |
| 27.5 | Clients `no-store`. |
| 27.6 | Lock screen, session PIN, reset pattern caisse. |
| 27.7 | `assert_module_in_effective_set`, effective modules provider, garde 403 module. |
| Epic 7 | `ReceptionService`, endpoints `/v1/reception/*`, wizard — **étendre**, pas dupliquer. |

### Intelligence stories précédentes (27.6 → 27.8)

| Story | Réutiliser tel quel |
|-------|---------------------|
| **27.6** | `useSharedWorkstationLockRequired()` pour masquer wizard ; `LiveAuthShell` appelle `resetCashflowDraft()` **et** `resetReceptionPosteUiState()` à chaque transition vers lock ; lock screen sans métadonnée brouillon ; session opérateur = vérité serveur (`DeviceOperatorSessionService`). |
| **27.7** | `SharedWorkstationEffectiveModulesService.assert_module_in_effective_set` ; `require_effective_module` ; provider front `SharedWorkstationEffectiveModulesProvider` + `filter-navigation-for-context.ts` ; **`reception` explicitement différé à 27.8** dans le registre — cette story **promouvoit** la clé. |
| **Epic 7** | `ReceptionService.assert_nominal_reception_eligible` + constante `RECEPTION_ACCESS_PERMISSION_KEY` ; wizard `ReceptionNominalWizard` ; permission nav `reception.access` dans `navigation-transverse-served.json`. |

### Brownfield / WIP sur branche

Des fichiers **peuvent déjà exister** (WIP parallèle au CS) : migration `s27_8_*`, `shared_workstation_reception_draft_service.py`, routes draft dans `shared_workstation.py`, gardes `SharedWorkstationReceptionScope` dans `reception_service.py` / `reception.py`, client + panel front, tests `test_story_27_8_*` / `shared-workstation-reception-draft*.test.tsx`. Le **DS ne doit pas** supposer greenfield : vérifier chaque AC, exécuter les gates, compléter les manques (ex. e2e lock sans fuite DOM cas #12), ne pas marquer done sans exit 0.

### Anti-patterns (interdits)

- Afficher ticket/lignes sur l’écran PIN ou dans le titre lock screen.
- Persister brouillon réception dans `localStorage` / `sessionStorage` comme autorité.
- Décider visibilité brouillon depuis `reception-poste-ui-state` seul.
- Réutiliser `cashflow-draft-store` pour la réception.
- Autoriser reprise sans confirmation explicite serveur (`confirm: true`).
- Exposer `opened_by_user_id` UUID brut dans le résumé sans politique de display.
- Brancher masquage sur tous les utilisateurs web non poste partagé (régression Epic 7).
- Ajouter `cashflow` au registre actif dans cette story.
- Implémenter timeout/handoff « pour compléter » le masquage.

### Risques / HITL

| Sujet | Décision proposée MVP | Escalade |
|-------|----------------------|----------|
| Granularité métadonnées résumé (nom auteur, heure) | Display prénom + heure locale après autorisation ; rien avant PIN | Si RGPD / terrain exige anonymisation → Strophe |
| Resolver `site_enabled` pour `reception` | `True` si site actif (pilote) | Quand schema `reception` PG existe → story dédiée config |
| Second brouillon même device | Refus 409 | Si produit veut empiler → HITL |
| Colonne vs table liaison | Colonne `registered_device_id` sur `poste_reception` | Si historique multi-brouillons requis → HITL |

### Testing / gates (Story Runner)

| Gate | Commande / critère |
|------|-------------------|
| Tests backend 27.8 | `cd recyclique/api && python -m pytest tests/ -k story_27_8 -q` → exit 0 |
| Non-régression Epic 27 | `pytest tests/test_story_27_6_pin_lock_operator_session.py tests/test_story_27_7_server_module_intersection.py -q` |
| Non-régression réception | `pytest tests/ -k reception -q` (sous-ensemble raisonnable si long) |
| Lint front | `cd peintre-nano && npm run lint` → exit 0 |
| Tests front | `cd peintre-nano && npm run test -- --run` → exit 0 |
| OpenAPI | Nouvelles opérations `recyclique_sharedWorkstation_*ReceptionDraft*` alignées Pydantic |
| Revue sécurité | grep : pas de fuite ticket dans réponses 403 lock ; pas de PIN en audit |
| YAML sprint (parent) | **lecture seule** — pas de write CS |

`gates_skipped_with_hitl: false`

### Project Structure Notes

| Zone | Fichiers / dossiers |
|------|---------------------|
| Registre module | `recyclique/api/src/recyclic_api/modules/module_config/registry.py`, `access_registry.py` |
| Migration | `recyclique/api/migrations/versions/s27_8_poste_reception_registered_device.py` (colonne `registered_device_id` sur `poste_reception`) |
| Service brouillon | `recyclique/api/src/recyclic_api/services/shared_workstation_reception_draft_service.py` |
| Réception (garde) | `recyclique/api/src/recyclic_api/services/reception_service.py`, `api/api_v1/endpoints/reception.py` |
| Garde | `recyclique/api/src/recyclic_api/core/shared_workstation_guard.py` (`require_shared_workstation_reception_access`, `get_optional_shared_workstation_reception_scope`) |
| Scope réception | `recyclique/api/src/recyclic_api/services/reception_service.py` (`SharedWorkstationReceptionScope`, `_is_shared_workstation_actor`) |
| Endpoints | `recyclique/api/src/recyclic_api/api/api_v1/endpoints/shared_workstation.py` |
| Schémas | `recyclique/api/src/recyclic_api/schemas/shared_workstation_reception_draft.py` (suggéré) |
| Audit | `recyclique/api/src/recyclic_api/models/audit_log.py` |
| Tests back | `recyclique/api/tests/test_story_27_8_reception_pilot_drafts.py` |
| Client API | `peintre-nano/src/api/shared-workstation-reception-draft-client.ts` |
| UI reprise | `peintre-nano/src/domains/shared-workstation/SharedWorkstationReceptionDraftResumePanel.tsx` |
| Wizard | `peintre-nano/src/domains/reception/ReceptionNominalWizard.tsx`, `reception-poste-ui-state.ts` |
| Nav mapping | `peintre-nano/src/domains/shared-workstation/shared-workstation-nav-module-mapping.ts` |
| Shell | `peintre-nano/src/domains/shared-workstation/SharedWorkstationOperatorSessionProvider.tsx`, `LiveAuthShell.tsx` |
| Contrat | `contracts/openapi/recyclique-api.yaml` |

### References

- `_bmad-output/planning-artifacts/epics.md` — Epic 27, Story 27.8
- `_bmad-output/implementation-artifacts/27-6-pin-lock-operator-session.md`
- `_bmad-output/implementation-artifacts/27-7-server-module-intersection.md`
- `references/artefacts/2026-05-29_01_cadrage-postes-partages-pin-operateur.md` — §3.11–§3.12
- `references/artefacts/2026-05-29_02_mini-adr-postes-partages-pin-non-offline.md`
- `references/artefacts/2026-05-29_04_runbook-orchestration-epic-27-postes-partages-pin.md` — §7–§8
- `references/protocole-modules-recyclique/05-MOD-registre-module-key.md` — § `reception`
- `recyclique/api/src/recyclic_api/services/reception_service.py`
- `recyclique/api/src/recyclic_api/models/poste_reception.py`, `ticket_depot.py`
- `peintre-nano/src/domains/reception/ReceptionNominalWizard.tsx`
- `peintre-nano/src/domains/cashflow/cashflow-draft-store.ts` — **anti-modèle** (ne pas copier)
- `contracts/openapi/recyclique-api.yaml`

## Tasks / Subtasks

- [x] **T1 — Registre `reception` + mapping nav** (AC: pilote Reception, intersection)
  - [x] T1.1 Promouvoir `reception` dans `registry.py` + `access_registry.py`
  - [x] T1.2 Étendre `shared-workstation-nav-module-mapping.ts`
  - [x] T1.3 Tests : `reception` intersectable avec allowlist + `reception.access`
- [x] **T2 — Persistance brouillon lié `device_id`** (AC: brouillon sur le poste)
  - [x] T2.1 Migration `registered_device_id` (ou table dédiée)
  - [x] T2.2 Renseigner à `open_poste` en contexte poste partagé
- [x] **T3 — Service + API brouillon** (AC: masquage, reprise, abandon, no-store)
  - [x] T3.1 `SharedWorkstationReceptionDraftService`
  - [x] T3.2 Routes `GET/POST` shared-workstation + OpenAPI
  - [x] T3.3 Gardes sur endpoints réception nominaux (device sans PIN → 403)
  - [x] T3.4 Adapter `_assert_poste_operator`, `_assert_ticket_write_actor`, `_assert_ticket_readable` pour reprise inter-opérateur (poste `registered_device_id`)
- [x] **T4 — Audit** (AC: reprise/abandon tracés)
  - [x] T4.1 Nouveaux `AuditEventType` + tests grep sans PIN
- [x] **T5 — Frontend** (AC: invisible sans PIN, reprise confirmée)
  - [x] T5.1 Client API + panel reprise/abandon
  - [x] T5.2 Reset état réception au lock ; wizard masqué si lock
  - [x] T5.3 E2e lock sans fuite DOM
- [x] **T6 — Gates** (AC: tous)
  - [x] T6.1 `story_27_8` pytest + Vitest + lint

### Review Findings (CR loop 0 — 2026-05-30)

- [x] [Review][Patch] Garde PIN incomplète sur routes réception nominaux — corrigé : `close poste/ticket`, `PUT/DELETE lignes`, `GET /tickets` + tests `TestStory278ReceptionGuardM1`. [`reception.py`, `reception_service.py`, `test_story_27_8_reception_pilot_drafts.py`]
- [x] [Review][Patch] Contournement brownfield JWT seul sur poste `registered_device_id` — corrigé via `_assert_enrolled_poste_requires_device_scope` + `_http_for_authorization_error`. [`reception_service.py`]
- [x] [Review][Patch] Fuite cross-device (scope device B ≠ poste device A, fallback `opened_by_user_id`) — corrigé : vérif `registered_device_id == scope.device_id` pour USER. [`reception_service.py`]
- [x] [Review][Defer] E2E wizard hydraté post-reprise non couvert — accepté MVP (QA gap non bloquant). — deferred, pre-existing QA note
- [x] [Review][Defer] `started_by_display` dérivé du username — dette RGPD documentée § Risques MVP. — deferred, HITL produit si anonymisation requise

**CR loop 0 — MEDIUM / LOW (documentés, non bloquants)**

- [ ] [Review][Medium] Reprise UI en un clic — le serveur exige `confirm: true` (OK) mais le bouton « Reprendre » n'a pas la double confirmation UI comme « Abandonner » (AC §3.12 interprétation UX). [`SharedWorkstationReceptionDraftResumePanel.tsx`]
- [ ] [Review][Low] Paramètre `viewer` inutilisé dans `build_authorized_summary`. [`shared_workstation_reception_draft_service.py`]
- [ ] [Review][Low] Routes draft `/context` sans propagation `X-Request-Id` vers audit draft (routes dédiées OK). [`shared_workstation.py`]

## Dev Agent Record

### Agent Model Used

Composer (DS subagent Story Runner 27-8)

### Debug Log References

- Gates : `pytest -k story_27_8` 10/10 ; `npm run lint` OK ; Vitest 27.8 3/3
- Post-gate DS (régression Epic 7) : `useSharedWorkstationLockRequired` basculé sur `useOptionalSharedWorkstationOperatorSession` — sans provider → `false` (no-op hors poste partagé) ; Vitest 819/819 ; lint OK ; pytest 27.8 10/10

### Completion Notes List

- Module pilote `reception` promu (registre + intersection 27.7).
- Brouillon ancré sur `poste_reception.registered_device_id` ; service + routes `no-store`.
- Gardes réception inter-opérateur sur poste partagé ; reprise/abandon avec `confirm: true` + audit.
- Front : panel reprise, reset UI au lock, wizard masqué sans PIN.
- Fix régression gate 3 : hook lock optionnel hors `SharedWorkstationOperatorSessionProvider` (tests réception Epic 7 sans wrapper).

### File List

- recyclique/api/migrations/versions/s27_8_poste_reception_registered_device.py
- recyclique/api/src/recyclic_api/modules/module_config/registry.py
- recyclique/api/src/recyclic_api/modules/module_config/access_registry.py
- recyclique/api/src/recyclic_api/models/poste_reception.py
- recyclique/api/src/recyclic_api/models/audit_log.py
- recyclique/api/src/recyclic_api/core/audit.py
- recyclique/api/src/recyclic_api/core/shared_workstation_guard.py
- recyclique/api/src/recyclic_api/repositories/reception.py
- recyclique/api/src/recyclic_api/services/reception_service.py
- recyclique/api/src/recyclic_api/services/shared_workstation_reception_draft_service.py
- recyclique/api/src/recyclic_api/schemas/shared_workstation_reception_draft.py
- recyclique/api/src/recyclic_api/schemas/shared_workstation_context.py
- recyclique/api/src/recyclic_api/api/api_v1/endpoints/shared_workstation.py
- recyclique/api/src/recyclic_api/api/api_v1/endpoints/reception.py
- recyclique/api/tests/test_story_27_8_reception_pilot_drafts.py
- recyclique/api/tests/conftest.py
- recyclique/api/pyproject.toml
- peintre-nano/src/api/shared-workstation-reception-draft-client.ts
- peintre-nano/src/domains/shared-workstation/SharedWorkstationOperatorSessionProvider.tsx
- peintre-nano/src/domains/shared-workstation/SharedWorkstationReceptionDraftResumePanel.tsx
- peintre-nano/src/domains/shared-workstation/shared-workstation-nav-module-mapping.ts
- peintre-nano/src/domains/reception/reception-poste-ui-state.ts
- peintre-nano/src/domains/reception/ReceptionNominalWizard.tsx
- peintre-nano/src/app/auth/LiveAuthShell.tsx
- peintre-nano/tests/unit/shared-workstation-reception-draft.test.tsx
- peintre-nano/tests/e2e/shared-workstation-reception-draft-27-8.e2e.test.tsx
- contracts/openapi/recyclique-api.yaml

## Story completion status

- **Statut cible après CS :** `ready-for-dev`
- **Statut fichier :** `ready-for-dev`
- **Date CS :** 2026-05-30 — analyse exhaustive epics 27.8, mini-ADR brouillons, runbook §7, cadrage §3.11–3.12, stories 27.6–27.7 done, brownfield réception Epic 7 ; gardes inter-opérateur (`SharedWorkstationReceptionScope`, `_assert_ticket_*`), mapping nav `reception-nominal` → `reception`, cas test 6b, chemin migrations corrigé.
- **Clé sprint-status :** `27-8-reception-pilot-drafts` — **non modifiée** par ce worker CS (writer unique Epic Runner).
- **Prochaine étape Story Runner :** `VS` puis `DS` ; **ne pas** modifier `sprint-status.yaml` depuis CS.
