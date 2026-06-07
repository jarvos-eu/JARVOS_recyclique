# Story 28.2 : Rétablir `Mon profil`, PIN self-service et la sortie PWA minimale

Status: done

**Story key :** `28-2-retablir-mon-profil-pin-self-service-et-sortie-pwa-minimale`  
**Epic :** 28 — Stabiliser la beta terrain depuis le registre `references/revision/`  
**Implementation artifact :** `_bmad-output/implementation-artifacts/28-2-retablir-mon-profil-pin-self-service-et-sortie-pwa-minimale.md`  
**Date CS :** 2026-06-07

Ultimate context engine analysis completed — comprehensive developer guide created.

## Contexte produit

La revue HITL du `2026-06-07` a confirmé trois blocages transverses avant tout travail terrain crédible :

1. le menu utilisateur live n’expose pas **Mon profil** (`REV-TRANSVERSE-01`) ;
2. après réinit admin, aucun parcours self-service ne permet de **créer un PIN** (`REV-ADMIN-01`) ;
3. en PWA installée sur `/reception`, l’opérateur est **coincé** sans retour menu (`REV-RECEPTION-02`).

La story 28.1 a stabilisé la caisse P0 sans toucher authz / PIN. Cette story 28.2 rétablit le **chaînage minimal profil → PIN → navigation** requis par la beta et par Epic 27 (postes partagés), sans absorber timeout / handoff / override Epic 27 ni refondre le shell transverse.

## Scope `REV-*`

| ID | Titre | Priorité | Rôle dans 28.2 |
|----|-------|----------|----------------|
| `REV-TRANSVERSE-01` | Menu sans « Mon profil » | P1 | Entrée menu + route manifestée `/profil` |
| `REV-ADMIN-01` | Réinit PIN sans parcours de création | P1 | Surface self-service `PUT /v1/users/me/pin` (débloque la suite après reset admin) |
| `REV-RECEPTION-02` | PWA sans retour menu | P0 | Chemin de sortie borné depuis hub réception inactif |

**Hors scope direct (différés explicitement) :**

| ID | Raison |
|----|--------|
| `REV-TRANSVERSE-02`, `03` | Polish chrome PWA (barre titre bleue, plier/déplier) — post-28.2 ou epic ultérieur |
| `REV-RECEPTION-01`, `03`…`06` | Exploitabilité hub / cockpit — story **28.3** |
| `REV-ADMIN-02`…`10` | Admin pilotes — stories **28.4** / **28.5** |
| Timeout / handoff / override Epic 27 (`27-9`, `27-10`) | Hors slice beta 28.2 |
| Endpoint admin « Forcer un PIN » | Hors parité legacy ; arbitrage PO / sécurité si besoin futur |
| Refonte shell transverse complète | Garde-fou epic |

## Story (BDD)

As a field operator on a shared or installed workstation,  
I want to reach my profile, manage my PIN and leave blocked PWA surfaces safely,  
So that the v2 no longer traps me administratively or operationally before I can work.

## Acceptance criteria

Source normative : `_bmad-output/planning-artifacts/epics.md` — **Story 28.2**.

**Given** the revision register identifies `REV-TRANSVERSE-01`, `REV-ADMIN-01` and `REV-RECEPTION-02`  
**When** this story is delivered  
**Then** the live shell user menu exposes a credible `Mon profil` path in the v2 runtime  
**And** the self-service profile surface lets the user complete the retained PIN-management behavior needed by the beta  
**And** a reception PWA user can always leave the inactive reception surface through a bounded return path instead of closing the whole app  
**And** the fix does not bypass Epic 27 security rules or invent client-side authority around operator activity

**Given** Epic 21 carries the `users` family and Epic 27 the shared-workstation / PWA groundwork  
**When** the story is reviewed  
**Then** the implementation reuses existing contracts and APIs where they already exist  
**And** any truly missing authority is documented rather than hidden in local-only UI state

### Critères complémentaires (dérivés registre)

**AC-PROFIL-ROUTE** — Route retenue : **`/profil`** (parité legacy `Profile.tsx` / `Header.jsx`). Entrée CREOS `transverse-profile` + `page_key` `transverse-profile`. Pas d’alias fantôme hors manifeste.

**AC-MENU** — `LiveShellUserMenu` affiche **Mon profil** entre « Dashboard personnel » et « Déconnexion », avec `data-testid="live-shell-user-menu-profile"`. Navigation SPA vers `/profil` (même discipline que `goPersonalDashboardFromMenu` → `/dashboard/benevole`).

**AC-PIN-SELF-SERVICE** — Widget profil appelle **`PUT /v1/users/me/pin`** (`PinSetRequest`: `pin` 4 chiffres ; `current_password` requis si PIN déjà défini côté serveur). Messages d’erreur API affichés en français opérateur. Pas de stockage PIN en clair côté client au-delà du formulaire.

**AC-PIN-RESET-CHAIN** — Après `POST /v1/admin/users/{id}/reset-pin`, l’utilisateur concerné peut poser un nouveau PIN via **Mon profil** sans intervention admin supplémentaire. Optionnel et borné : si l’admin réinitialise le PIN d’un **autre** utilisateur, le message admin existant reste ; pas d’endpoint admin « forcer PIN » dans cette story.

**AC-PWA-EXIT** — Sur `/reception` quand **aucun poste n’est ouvert** (`posteId === null`), un CTA visible **« Retour au menu »** (ou libellé équivalent) mène vers `/dashboard` via `spaNavigateTo` — **sans** réactiver `hideShellNav` globalement ni casser le mode certification quand un poste est ouvert. `data-testid` explicite (ex. `reception-return-to-menu`).

**AC-NON-REGRESSION** — Step-up PIN caisse (story 28.1, `CaisseSessionCloseSurface`) et flux poste partagé Epic 27 (`SharedWorkstationLockScreen`, `verifySharedWorkstationOperatorPin`) inchangés sauf bugfix documenté.

## Dependencies

- **Epic 21** — famille `users` (API `GET/PUT /v1/users/me`, `PUT /v1/users/me/pin`).
- **Epic 27** — postes partagés / PWA (`hideShellNav`, `SharedWorkstationLockScreen`, drafts réception) — ne pas absorber timeout / handoff / override.
- **Story 28.1** (`done`) — patterns tests `*28-1*`, `spaNavigateTo`, non-régression caisse step-up PIN.

## Tasks / Subtasks

- [x] **Menu utilisateur — Mon profil** (AC: menu, AC-PROFIL-ROUTE)
  - [x] Étendre `LiveShellUserMenu` : prop `onProfile` + item « Mon profil »
  - [x] Brancher `RuntimeDemoApp` : callback `goProfileFromMenu` → `pushState` `/profil` + `syncSelectionFromPath` (même pattern que `goPersonalDashboardFromMenu` — **pas** `spaNavigateTo`)
- [x] **Manifeste CREOS + bundle** (AC: AC-PROFIL-ROUTE)
  - [x] Créer `contracts/creos/manifests/page-transverse-profile.json` sur le modèle `page-transverse-dashboard-benevole.json` (`page_key`: `transverse-profile`, slot widget profil)
  - [x] Ajouter entrée `transverse-profile` dans `navigation-transverse-served.json` (`path`: `/profil`, `visibility.permission_any`: `["transverse.dashboard.view"]`, `visibility.contexts_any`: `["site"]` — aligné dashboard personnel)
  - [x] Enregistrer page + import dans `runtime-demo-manifest.ts` ; aligner `peintre-nano/public/manifests/navigation.json` si copie reviewable requise
  - [x] Résoudre `resolvedPageKey` / accès page dans `RuntimeDemoApp` si nécessaire
- [x] **Widget Mon profil self-service** (AC: PIN, Epic 21)
  - [x] Créer `peintre-nano/src/api/users-me-client.ts` : `fetchUsersMeProfile` (`GET /v1/users/me` complet) + `putUsersMePin` — **ne pas** réutiliser `fetchUsersMeForAdminDashboard` (retourne seulement `role`)
  - [x] Créer `UserSelfProfileWidget` (ou nom cohérent) : affichage coordonnées lecture seule ou champs self-update via `PUT /v1/users/me` si déjà couvert ; **section PIN** : saisie 4 chiffres + confirmation ; champ mot de passe compte si modification PIN existant
  - [x] Enregistrer widget `demo.legacy.user.profile` dans `register-demo-widgets.ts` (famille `demo.legacy.*` comme `demo.legacy.dashboard.personal`) — **pas** `register-auth-widgets.ts` (réservé login)
  - [x] Validation front : PIN exactement 4 chiffres ; confirmation identique ; messages erreur 400 API (`Current password is required`, etc.)
- [x] **Sortie PWA réception minimale** (AC: AC-PWA-EXIT, REV-RECEPTION-02)
  - [x] Dans `ReceptionNominalWizard` (hub principal `!posteId`, hors panneau reprise draft `SharedWorkstationReceptionDraftResumePanel`) : bouton « Retour au menu » → `spaNavigateTo('/dashboard')`
  - [x] Ne pas modifier `isReceptionNominalCertificationPathRoute` pour réafficher toute la barre nav ; solution **locale et bornée** au hub inactif
- [x] **Admin — chaîne reset PIN** (AC: AC-PIN-RESET-CHAIN, optionnel borné)
  - [x] Si l’utilisateur sélectionné dans `AdminUsersWidget` est l’utilisateur courant : après reset réussi, message + lien « Ouvrir mon profil » vers `/profil`
- [x] **Tests** (AC: gates epic)
  - [x] Unit : `LiveShellUserMenu` affiche Mon profil quand `onProfile` fourni
  - [x] Unit / e2e : navigation menu → `/profil` rend le widget profil
  - [x] Unit : formulaire PIN — succès premier PIN ; échec sans mot de passe si changement
  - [x] Unit / e2e : `/reception` hub inactif — CTA retour menu visible et navigue vers `/dashboard` avec `hideShellNav` actif
  - [x] pytest : **aucun changement backend attendu** ; si touché, réutiliser `recyclique/api/tests/test_pin_management.py`
- [x] **Registre revision** (post-DS, pas en CS)
  - [x] Mettre à jour `references/revision/domaines/transverse.md`, `admin.md`, `reception.md` : colonnes **Investigé** / **Corrigé** sur les 3 REV — **pas Validé HITL** (réservé Strophe)

## Dev Notes

### État code confirmé (2026-06-07) — *pré-DS, obsolète*

> Snapshot CS/VS avant implémentation. Voir **Completion Notes** et **File List** pour l'état livré (DS 2026-06-07).

| Zone | Fichier / constat *(pré-DS)* |
|------|-------------------|
| Menu utilisateur | `peintre-nano/src/app/shell/LiveShellUserMenu.tsx` — Dashboard personnel + Déconnexion seulement |
| Wiring menu | `RuntimeDemoApp.tsx` L744–751 — `onPersonalDashboard` conditionnel ; pas de profil |
| Gap documenté | `peintre-nano/docs/03-contrats-creos-et-donnees.md` § Shell admin — `/profil` non manifesté |
| API PIN self-service | `PUT /v1/users/me/pin` — `users.py` `set_user_pin` ; tests `test_pin_management.py` |
| GET profil | `GET /v1/users/me` — nouveau client dédié ; `fetchUsersMeForAdminDashboard` **insuffisant** (role seul) |
| API reset admin | `POST /v1/admin/users/{id}/reset-pin` — `AdminUsersWidget` + `postAdminUserResetPin` |
| PWA réception bloquée | `RuntimeDemoApp.tsx` L176–177, L647 — `hideShellNav` sur `/reception` entier |
| Legacy référence | `recyclique-1.4.4/frontend/src/pages/Profile.tsx`, `Header.jsx` (menu 3 entrées) |

### Décision route et surface profil

- **Route canonique beta :** `/profil` (legacy), pas `/profile` ni slug sans entrée nav.
- **Widget type retenu :** `demo.legacy.user.profile` (aligné `demo.legacy.dashboard.personal` dans `register-demo-widgets.ts`).
- **Permissions page :** tout utilisateur authentifié avec accès shell live ; réutiliser une clé existante du manifeste transverse plutôt qu’inventer une permission client.

### Comportement PIN (contrat API)

```text
Premier PIN (hashed_pin null côté serveur) :
  PUT { "pin": "1234" }

Modification PIN existant :
  PUT { "pin": "5678", "current_password": "<mot de passe compte>" }
```

Le schéma `UserResponse` n’expose pas `hashed_pin`. UI beta retenue :

- formulaire avec PIN + confirmation ;
- champ « Mot de passe du compte » affiché dès qu’on propose de **modifier** un PIN (ou toujours visible avec aide contextuelle) ;
- laisser l’API trancher ; mapper les `detail` 400 en messages français.

### Sortie PWA — périmètre minimal acceptable

**Retenu :** un seul CTA sur le hub réception **sans poste ouvert**, visible même quand `hideShellNav === true`.

**Non retenu dans 28.2 :**

- réafficher la barre verte complète sur `/reception` ;
- modifier `theme_color` PWA (`REV-TRANSVERSE-02`) ;
- plier/déplier barre titre (`REV-TRANSVERSE-03`) ;
- refonte hub réception (`REV-RECEPTION-01` → 28.3).

### Garde-fous

- Ne pas absorber timeout / handoff / override Epic 27 (`27-9`, `27-10`).
- Ne pas créer d’autorité PIN côté navigateur (pas de bypass `ContextEnvelope` / session opérateur poste partagé).
- Ne pas ajouter d’endpoint admin « forcer PIN » sans arbitrage PO — la story se limite au flux legacy self-service.
- Ne pas marquer **Validé HITL** sur `references/revision/` — seulement Investigé/Corrigé post-merge.
- Ne pas toucher clôture caisse / held / session (28.1 done) sauf régression avérée.

### Intelligence story 28.1 (précédente)

- Patterns tests : suffixe `28-1` dans noms de fichiers ; privilégier fonctions pures + tests RTL ciblés.
- `spaNavigateTo` et `data-testid` systématiques pour parcours opérateur.
- Story 28.1 a explicitement laissé authz / PIN hors scope — **28.2 est le bon véhicule**.

### Pistes techniques

- `LiveShellUserMenu.tsx`, `RuntimeDemoApp.tsx`
- `ReceptionNominalWizard.tsx` (CTA retour hub inactif)
- Nouveau : `peintre-nano/src/domains/transverse/UserSelfProfileWidget.tsx` (emplacement suggéré)
- Nouveau : `peintre-nano/src/api/users-me-client.ts` (`putUsersMePin`, éventuellement `fetchUsersMeProfile`)
- `contracts/creos/manifests/page-transverse-profile.json`
- `contracts/creos/manifests/navigation-transverse-served.json`
- `runtime-demo-manifest.ts`, `register-*-widgets.ts`
- `AdminUsersWidget.tsx` (message post-reset optionnel)

### Références

- `references/revision/domaines/transverse.md` § REV-TRANSVERSE-01
- `references/revision/domaines/admin.md` § REV-ADMIN-01
- `references/revision/domaines/reception.md` § REV-RECEPTION-02
- `references/revision/index.md` (tableau P0)
- `references/artefacts/2026-05-29_01_cadrage-postes-partages-pin-operateur.md`
- `_bmad-output/planning-artifacts/epics.md` § Epic 28 / Story 28.2
- `_bmad-output/implementation-artifacts/28-1-stabiliser-la-caisse-terrain-p0-session-finalisation-et-cloture.md`
- `recyclique/api/tests/test_pin_management.py`

## Testing / gates recommandés

- **Front :** `npm test` ciblé sur nouveaux tests `*28-2*` + non-régression menu shell / réception hub ;
- **Backend :** pytest `test_pin_management.py` si aucun changement API (attendu) ; sinon suite ciblée ;
- **Build :** lint + build Peintre si surfaces UI touchées ;
- **Contrats :** pas de modification OpenAPI attendue ; si ajout permission manifeste uniquement, pas de regen obligatoire ;
- **QA2** ciblé scope 28.2 avant CR ;
- **HITL** : retest menu profil, création PIN après reset admin, sortie PWA réception — Strophe.

## Risques / HITL

| Sujet | Statut |
|-------|--------|
| Libellé exact CTA retour réception (« Retour au menu » vs « Tableau de bord ») | Arbitrage léger possible — défaut `/dashboard` |
| Champ mot de passe obligatoire pour **premier** PIN après reset | API ne l’exige pas ; UX à garder simple |
| Permission manifeste `/profil` | Vérifier clé existante vs nouvelle entrée OpenAPI |
| Chrome PWA minimal en poste ouvert | Hors 28.2 — ne pas élargir `hideShellNav` |

## Alignement sprint / YAML

- `epic-28` : `in-progress`
- `28-1` : `done`
- `28-2-retablir-mon-profil-pin-self-service-et-sortie-pwa-minimale` : `done`
- Stories `28-3` à `28-5` : `backlog`

## Dev Agent Record

### Agent Model Used

Composer (DS Task subagent, story 28.2)

### Debug Log References

- Vitest ciblé `*28-2*` + `admin-users-widget` + contract nav : **18 passed** (aucun changement backend).

### Completion Notes List

- Menu live : entrée **Mon profil** (`data-testid="live-shell-user-menu-profile"`) + navigation SPA `/profil` via `goProfileFromMenu`.
- Manifeste CREOS `transverse-profile` + widget `demo.legacy.user.profile` + client `users-me-client.ts` (GET profil, PUT PIN, messages FR).
- CTA **Retour au menu** sur hub réception sans poste (`reception-return-to-menu`).
- Admin : lien **Ouvrir mon profil** après reset-pin sur compte courant.
- Registre `references/revision/` : REV-TRANSVERSE-01, REV-ADMIN-01, REV-RECEPTION-02 marqués Investigé/Corrigé (pas HITL).

### File List

- `contracts/creos/manifests/page-transverse-profile.json` (new)
- `contracts/creos/manifests/navigation-transverse-served.json`
- `peintre-nano/public/manifests/navigation.json`
- `peintre-nano/src/api/users-me-client.ts` (new)
- `peintre-nano/src/app/demo/RuntimeDemoApp.tsx`
- `peintre-nano/src/app/demo/runtime-demo-manifest.ts`
- `peintre-nano/src/app/shell/LiveShellUserMenu.tsx`
- `peintre-nano/src/domains/admin-config/AdminUsersWidget.tsx`
- `peintre-nano/src/domains/reception/ReceptionNominalWizard.tsx`
- `peintre-nano/src/domains/transverse/UserSelfProfileWidget.tsx` (new)
- `peintre-nano/src/registry/register-demo-widgets.ts`
- `peintre-nano/src/runtime/nav-label-presentation-fallbacks.ts`
- `peintre-nano/tests/unit/live-shell-user-menu-28-2.test.tsx` (new)
- `peintre-nano/tests/unit/user-self-profile-widget-28-2.test.tsx` (new)
- `peintre-nano/tests/unit/runtime-demo-profile-nav-28-2.test.tsx` (new)
- `peintre-nano/tests/unit/reception-return-to-menu-28-2.test.tsx` (new)
- `peintre-nano/tests/e2e/profile-menu-pin-self-service-28-2.e2e.test.tsx` (new)
- `peintre-nano/tests/e2e/reception-pwa-exit-28-2.e2e.test.tsx` (new)
- `peintre-nano/tests/unit/admin-users-widget.test.tsx`
- `peintre-nano/tests/contract/navigation-transverse-served-5-1.test.ts`
- `references/revision/domaines/transverse.md`
- `references/revision/domaines/admin.md`
- `references/revision/domaines/reception.md`
- `references/revision/index.md`
- `references/revision/journal.md`
- `_bmad-output/implementation-artifacts/sprint-status.yaml`

### Change Log

- 2026-06-07 — CS create : story enrichie depuis epics.md Story 28.2 + registre revision transverse/admin/reception.
- 2026-06-07 — VS validate : clarifications client API profil, enregistrement widget, navigation menu/manifeste, placement CTA réception hub ; section Dependencies ajoutée.
- 2026-06-07 — DS bmad-dev-story : implémentation complète story 28.2 ; status **review** ; gates Vitest 18/18 ; pas de changement API backend.
- 2026-06-07 — CR (cr_loop 0) : PASS adversarial ; merge-ready ; 21 tests Vitest ciblés 28-2 + admin + contract nav OK.

### Review Findings (CR cr_loop 0 — 2026-06-07)

- [x] [Review][Defer] PIN saisi en clair (`TextInput` au lieu de `PasswordInput`) — `UserSelfProfileWidget.tsx` — shoulder surfing poste partagé ; hors AC explicite ; amélioration UX sécurité optionnelle post-merge.
- [x] [Review][Defer] Pas de test négatif « CTA retour masqué quand `posteId` ouvert » — lacune couverture ; comportement code correct (`!posteId` guard).
- [x] [Review][Defer] Écran vide transitoire (`return null`) pendant `draftGateChecked` sur poste partagé — `ReceptionNominalWizard.tsx` — pré-existant Epic 27 ; hors slice 28.2.
