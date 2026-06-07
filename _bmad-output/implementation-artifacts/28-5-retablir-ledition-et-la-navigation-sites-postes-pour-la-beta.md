# Story 28.5 : Rétablir l'édition et la navigation `sites` / `postes` pour la beta

Status: done

**Story key :** `28-5-retablir-ledition-et-la-navigation-sites-postes-pour-la-beta`  
**Epic :** 28 — Stabiliser la beta terrain depuis le registre `references/revision/`  
**Implementation artifact :** `_bmad-output/implementation-artifacts/28-5-retablir-ledition-et-la-navigation-sites-postes-pour-la-beta.md`  
**Date CS :** 2026-06-07

Ultimate context engine analysis completed — comprehensive developer guide created.

## Contexte produit

La revue HITL du `2026-06-07` a confirmé que l'administration **sites & postes de caisse** reste incomplète par rapport au legacy brownfield :

1. le **hub** `/admin/sites-and-registers` est fonctionnel mais **bruité** (bandeau gris central, sous-titres redondants sur les boutons) — `REV-ADMIN-06` ;
2. la page **Sites** (`/admin/sites`) permet création / suppression / toggle actif, mais **pas d'édition nom/ville** ni **retour direct** vers le hub — `REV-ADMIN-07` (P1) ;
3. la page **Postes de caisse** (`/admin/cash-registers`) gère les switches inline, mais **pas de modal Modifier** (nom, emplacement, site rattaché) ni retour hub — `REV-ADMIN-08` (P1) ;
4. le bouton **Actualiser** sur les deux listes a un rôle peu explicite (rechargement serveur).

Les stories **28.1**–**28.4** sont `done`. La 28.4 a humanisé modules / santé admin sans toucher sites & postes (explicitement différés). Cette story 28.5 restaure le **minimum d'administration quotidienne** attendu en beta : éditer les champs retenus, revenir au hub `sites & caisses`, clarifier le rafraîchissement — **sans** absorber archivage produit (`REV-ADMIN-09`) ni vision zones (`REV-ADMIN-10`).

## Scope `REV-*`

| ID | Titre | Priorité | Rôle dans 28.5 |
|----|-------|----------|----------------|
| `REV-ADMIN-06` | Hub sites & caisses — mise en page | P2 | Simplifier hub : retirer bandeau gris inutile, alléger libellés boutons |
| `REV-ADMIN-07` | Sites — pas d'édition ni retour | P1 | Modal édition nom/ville + bouton retour hub + clarifier Actualiser |
| `REV-ADMIN-08` | Postes caisse — pas d'édition ni retour | P1 | Modal édition nom/emplacement/site + retour hub + clarifier Actualiser |

**Hors scope direct (différés explicitement) :**

| ID | Raison |
|----|--------|
| `REV-ADMIN-09` | Archiver vs supprimer — décision produit ; le toggle **Actif** et le message d'erreur suppression existants suffisent ; pas de nouveau flux archivage |
| `REV-ADMIN-10` | Vision zones / multi-sites — cadrage long terme, hors slice beta |
| `REV-ADMIN-04` | Dashboard super-admin — polish ultérieur |
| Champs site avancés (`address`, `postal_code`, `country`, `configuration`) | API PATCH les supporte ; **beta = parité legacy** nom + ville uniquement en modal |
| Édition `workflow_options` dans la modal poste | Switches inline (actif / virtuel / différé) restent le chemin retenu |
| Fusion `/admin/site` (singulier) et `/admin/sites` (pluriel) | Décision documentée story 17 / `03-contrats-creos-et-donnees.md` — coexistence inchangée |
| Nettoyage données test terrain (`validationindépendante714e06c-site`) | Hors dev — mention HITL ops si besoin |
| **Validé HITL** | Interdit en DS — seulement Investigé / Corrigé dans `references/revision/` |

## Story (BDD)

As an admin user managing physical operating contexts,  
I want to edit sites and cash-register posts and return to their hub directly,  
So that the beta supports the minimum day-to-day administration expected from the legacy reference.

## Acceptance criteria

Source normative : `_bmad-output/planning-artifacts/epics.md` — **Story 28.5**.

**Given** the revision register identifies `REV-ADMIN-06`, `07` and `08`  
**When** this story is delivered  
**Then** the retained `sites` and `cash-registers` surfaces expose bounded edit flows for the fields explicitly retained in beta scope  
**And** the user can return directly to the `sites & caisses` hub without an unnecessary detour through the main admin dashboard  
**And** the pages explain or simplify refresh behavior instead of leaving it ambiguous  
**And** the story remains bounded to edit/navigation exploitability rather than broader future "zones" modeling

**Given** Epic 17 provided the first shared admin shell for `sites` and `cash-registers`  
**When** the story is reviewed  
**Then** the retained edit flows reuse the same stable admin patterns and backend authority  
**And** broader product questions such as archive-vs-delete or future zones stay deferred unless explicitly required to keep the retained edit flow coherent

### Critères complémentaires (dérivés registre)

**AC-HUB-SIMPLIFY** — Hub `/admin/sites-and-registers` (`data-testid="admin-sites-and-registers-hub"`) :

- Supprimer le `Paper` gris central *« Choisissez l'option… »* (REV-ADMIN-06).
- Boutons **Gérer les sites** / **Gérer les postes de caisse** : titre principal seul en surface ; sous-titre redondant retiré **ou** déplacé en `Tooltip` ⓘ (pattern charte 28.4).
- Conserver **Retour au tableau de bord** (`data-testid="admin-sites-and-registers-back-dashboard"`) — doublon bandeau Administration acceptable.

**AC-SITES-EDIT** — Page Sites (`data-testid="widget-admin-sites"`) :

- Chaque ligne expose un bouton **Modifier** (`data-testid` indicatif : `admin-sites-edit-{id}` ou bouton unique `admin-sites-edit-open` + modal).
- Modal **« Modifier le site »** : champs **Nom** (requis) et **Ville** (optionnel) — aligné legacy `Sites.tsx` et création existante.
- Soumission : `PATCH` via `updateSiteForAdmin(auth, siteId, { name, city })` — **réutiliser le client existant**, pas de nouvel endpoint.
- Succès : fermer modal, mettre à jour la ligne locale (`setRows` avec `res.site`) ; erreur API : `CashflowClientErrorAlert` inchangé.
- Les switches **Actif** et actions **Supprimer** / **Nouveau site** restent fonctionnels (non-régression).

**AC-SITES-BACK** — En-tête Sites :

- Bouton **« Retour sites et caisses »** (`data-testid="admin-sites-back-to-hub"`) → `spaNavigateTo('/admin/sites-and-registers')`.
- Pattern visuel : `Button variant="subtle"` + `ArrowLeft` — même famille que le hub (`AdminSitesAndRegistersHubWidget.tsx` L16–23).

**AC-REGISTERS-EDIT** — Page Postes (`data-testid="widget-admin-cash-registers"`) :

- Bouton **Modifier** par ligne (à côté de Supprimer).
- Modal **« Modifier le poste »** : **Nom** (requis), **Emplacement** (optionnel, `location`), **Site rattaché** (`Select` — réutiliser `siteSelectData` / `listSitesForAdmin` déjà chargé).
- Soumission : `updateCashRegisterForAdmin(auth, id, { name, location, site_id })`.
- Succès : fermer modal, mettre à jour la ligne locale (`setRows` avec `res.register`) ; erreur API : `CashflowClientErrorAlert` inchangé.
- Switches inline (actif / virtuel / différé) et badge session ouverte/fermée **inchangés** hors modal.

**AC-REGISTERS-BACK** — En-tête Postes :

- Bouton **« Retour sites et caisses »** (`data-testid="admin-cash-registers-back-to-hub"`) → `/admin/sites-and-registers`.

**AC-REFRESH-CLARITY** — Sur Sites **et** Postes (REV-ADMIN-07/08) :

- **Décision retenue beta** : conserver l'action manuelle mais la rendre explicite :
  - Renommer le bouton **« Actualiser »** → **« Recharger la liste »** ;
  - Ajouter `title` ou `Tooltip` Mantine : *« Recharge la liste depuis le serveur »* ;
  - `data-testid` conservés ou suffixés (`admin-sites-reload-list`, `admin-cash-registers-reload-list`) — documenter en Completion Notes si renommage testid casse des tests existants (aucun test dédié sites widget repéré au CS).
- **Ne pas** ajouter d'auto-polling — hors scope.

**AC-DELETE-UNCHANGED** — Suppression site/poste :

- Comportement actuel conservé (modal confirmation + message si données liées).
- Si message API bloque la suppression : texte existant suffit — **ne pas** implémenter archivage (REV-ADMIN-09).

**AC-NON-REGRESSION** —

- Navigation CREOS `/admin/sites`, `/admin/cash-registers`, `/admin/sites-and-registers` inchangée (`navigation-transverse-served-5-1.test.ts`, e2e `navigation-transverse-5-1`).
- Stories 28.4 (modules/santé), 28.2 (profil), 28.1 (caisse) : tests `*28-4*`, `*28-2*`, `*28-1*` passent.
- Pas de régression sur toggles switches postes (patches partiels existants).

## Dependencies

- **Epic 17** — shell admin, widgets `AdminSitesWidget`, `AdminCashRegistersWidget`, `AdminSitesAndRegistersHubWidget`, clients `admin-sites-client.ts`, `admin-cash-registers-client.ts`.
- **Story 28.4** (`done`) — charte copie humaine (Tooltip, pas de jargon) ; `useAdminSiteDisplayLabel` disponible mais **non requis** sur ces listes (noms déjà en clair dans les tableaux).
- **OpenAPI** — `SiteV1Update`, `CashRegisterV1Update` (`contracts/openapi/recyclique-api.yaml`) ; types générés `recyclique-api.ts`.
- **Legacy référence** — `recyclique-1.4.4/frontend/src/pages/Admin/Sites.tsx`, `CashRegisters.tsx` (parcours Modifier + retour hub implicite via menu legacy).

## Tasks / Subtasks

- [x] **Hub — simplification mise en page** (AC: AC-HUB-SIMPLIFY, REV-ADMIN-06)
  - [x] `AdminSitesAndRegistersHubWidget.tsx` : retirer/raccourcir bandeau gris central
  - [x] Simplifier libellés des deux boutons navigation (titre seul ou ⓘ tooltip)
  - [x] Vérifier `data-testid` hub inchangés pour e2e existants
- [x] **Sites — modal édition** (AC: AC-SITES-EDIT, REV-ADMIN-07)
  - [x] `AdminSitesWidget.tsx` : état `editTarget`, modal miroir création (nom + ville)
  - [x] Appeler `updateSiteForAdmin` avec body borné ; busy state + désactivation si nom vide
  - [x] Bouton Modifier dans colonne actions (à côté Supprimer)
- [x] **Sites — navigation retour** (AC: AC-SITES-BACK, REV-ADMIN-07)
  - [x] Bouton retour hub en en-tête (`spaNavigateTo('/admin/sites-and-registers')`)
- [x] **Postes — modal édition** (AC: AC-REGISTERS-EDIT, REV-ADMIN-08)
  - [x] `AdminCashRegistersWidget.tsx` : modal Modifier (nom, location, site_id via Select existant)
  - [x] `updateCashRegisterForAdmin` body complet ; conserver switches hors modal
- [x] **Postes — navigation retour** (AC: AC-REGISTERS-BACK, REV-ADMIN-08)
  - [x] Bouton retour hub en en-tête
- [x] **Actualiser / recharger** (AC: AC-REFRESH-CLARITY, REV-ADMIN-07/08)
  - [x] Renommer bouton + Tooltip sur Sites et Postes (décision story ci-dessus)
- [x] **Tests** (AC: gates epic)
  - [x] Nouveaux `*28-5*` unit : ouverture modal edit sites, PATCH mock succès, back hub cliqué
  - [x] Nouveaux `*28-5*` unit : modal edit postes (nom + site), back hub
  - [ ] Optionnel e2e `*28-5*` : parcours hub → sites → modifier → retour hub (si coût acceptable)
  - [x] pytest : **aucun changement backend attendu** ; si gap PATCH découvert, cibler `recyclique/api/tests/test_sites_crud.py` + tests cash-registers existants
- [x] **Registre revision** (post-DS, pas en CS)
  - [x] `references/revision/domaines/admin.md` : Investigé / Corrigé sur REV-06, 07, 08 — **pas Validé HITL**

## Dev Notes

### État code confirmé (2026-06-07)

| Zone | Fichier / constat |
|------|-------------------|
| Hub | `AdminSitesAndRegistersHubWidget.tsx` — bandeau gris L26–30 ; sous-titres boutons L50–52, L68–70 |
| Sites UI | `AdminSitesWidget.tsx` — create/delete/toggle OK ; `updateSiteForAdmin` L73 **uniquement** `is_active` ; pas de Modifier ; pas de retour hub |
| Postes UI | `AdminCashRegistersWidget.tsx` — `patchField` L97–114 switches only ; create/delete OK ; `siteNameById` L52–56 |
| Clients API | `admin-sites-client.ts` — `updateSiteForAdmin` PATCH `/v1/sites/{id}` ; `SiteAdminUpdateBody` = `SiteV1Update` |
| | `admin-cash-registers-client.ts` — `updateCashRegisterForAdmin` PATCH `/v1/cash-registers/{id}` |
| OpenAPI champs edit | `SiteV1Update` : `name`, `city`, `address`, `postal_code`, `country`, `configuration`, `is_active` |
| | `CashRegisterV1Update` : `name`, `location`, `site_id`, `is_active`, `workflow_options`, `enable_virtual`, `enable_deferred` |
| Navigation | `RuntimeDemoApp.tsx` L473–501 — routes `/admin/sites-and-registers`, `/admin/sites`, `/admin/cash-registers` |
| SPA nav | `spa-navigate.ts` — `spaNavigateTo(path)` pour retour hub (pas `window.location` brut) |
| Manifests | `page-transverse-admin-sites.json`, `page-transverse-admin-cash-registers.json`, `page-transverse-admin-sites-and-registers.json` — **pas de changement manifest attendu** (widgets déjà branchés) |
| Tests existants | `navigation-transverse-served-5-1.test.ts`, `navigation-transverse-5-1.e2e.test.tsx` — parcours nav sites/postes ; **aucun** `admin-sites-widget.test.tsx` repéré |
| Backend | `recyclique/api/tests/test_sites_crud.py` — `test_update_site_success` ; PATCH sites/postes déjà couvert côté API |

### Champs éditables retenus (décision beta)

| Entité | Modal « Modifier » | Hors modal (inchangé) |
|--------|-------------------|------------------------|
| **Site** | `name`, `city` | `is_active` (switch), suppression |
| **Poste caisse** | `name`, `location`, `site_id` | `is_active`, `enable_virtual`, `enable_deferred`, session badge, suppression |

**Justification :** parité legacy `Sites.tsx` / `CashRegisters.tsx` + champs déjà présents en création v2. Pas d'édition adresse complète ni configuration JSON en beta.

### Stratégie modals

- **Réutiliser** le pattern Modal Mantine déjà présent (création L196–208 sites, L264–282 postes) — duplication minimale acceptable ; extraire helper partagé **uniquement** si le DS voit >3 modals identiques (non attendu).
- Validation : nom non vide trim ; `city` / `location` → `null` si chaîne vide (aligné `onCreate`).
- `site_id` poste : même `Select` que création ; valeur `''` → `null` pour détacher du site.

### Stratégie retour hub

```text
spaNavigateTo('/admin/sites-and-registers')
```

- Libellé : **« Retour sites et caisses »** (cohérent titre hub « Gestion des sites et caisses »).
- Placement : `Group` en-tête à droite ou sous le titre — ne pas masquer sur mobile (`wrap="wrap"`).

### Stratégie Actualiser (REV-ADMIN-07/08)

**Retenu :** renommer + Tooltip (voir AC-REFRESH-CLARITY). Alternative rejetée : suppression du bouton (perd le contrôle explicite après erreur réseau partielle).

### Garde-fous

- **Ne pas** inventer d'autorité côté client — PATCH via clients existants + token auth.
- **Ne pas** élargir vers REV-ADMIN-09 (archiver) : si DELETE 409/422, message API actuel suffit.
- **Ne pas** toucher `AdminModulesWidget` / `AdminSystemHealthWidget` (28.4 done).
- **Ne pas** fusionner hub avec dashboard legacy (`AdminLegacyDashboardHomeWidget`).
- Composant back partagé optionnel (`AdminBackToSitesRegistersHubButton.tsx`) — seulement si duplication >2 fichiers **et** trivial.

### Intelligence story 28.4 (précédente)

- Patterns tests : suffixe `28-N` ; `data-testid` systématiques ; registre revision post-DS seulement.
- Charte copie : 1 phrase sous-titre page max ; Tooltip pour détail.
- Gates : Vitest ciblé + lint/build Peintre ; pytest si backend touché.

### Intelligence story 28.3

- `spaNavigateTo` pour navigation intra-SPA admin.
- e2e navigation transverse déjà couvre rendu widgets — compléter par tests `28-5` sur interactions edit/back.

### Pistes techniques (fichiers probables)

- `peintre-nano/src/domains/admin-config/AdminSitesAndRegistersHubWidget.tsx`
- `peintre-nano/src/domains/admin-config/AdminSitesWidget.tsx`
- `peintre-nano/src/domains/admin-config/AdminCashRegistersWidget.tsx`
- `peintre-nano/src/app/demo/spa-navigate.ts` (import seulement)
- `peintre-nano/src/api/admin-sites-client.ts` (import seulement — types `SiteAdminUpdateBody`)
- `peintre-nano/src/api/admin-cash-registers-client.ts` (import seulement)
- Nouveaux tests :
  - `peintre-nano/tests/unit/admin-sites-edit-navigation-28-5.test.tsx`
  - `peintre-nano/tests/unit/admin-cash-registers-edit-navigation-28-5.test.tsx`
  - Optionnel : `peintre-nano/tests/e2e/admin-sites-registers-hub-28-5.e2e.test.tsx`

### Références

- `references/revision/domaines/admin.md` § D5 — REV-ADMIN-06, 07, 08 (+ 09/10 hors scope)
- `_bmad-output/planning-artifacts/epics.md` § Epic 28 / Story 28.5
- `_bmad-output/implementation-artifacts/28-4-debruiter-les-surfaces-admin-pilotes-pour-un-usage-humain.md`
- `peintre-nano/docs/03-contrats-creos-et-donnees.md` § routes `/admin/sites`, `/admin/cash-registers`, coexistence `/admin/site`
- `contracts/openapi/recyclique-api.yaml` — `SiteV1Update`, `CashRegisterV1Update`
- Legacy : `recyclique-1.4.4/frontend/src/pages/Admin/Sites.tsx`, `CashRegisters.tsx`
- `recyclique/api/tests/test_sites_crud.py`

## Testing / gates recommandés

Brief Story Runner YAML :

- **Backend :** `cd recyclique/api && python -m pytest tests/test_sites_crud.py tests/ -k "cash_register" -q --tb=short` — **attendu vert sans changement** ; n'exécuter élargi que si PATCH modifié.
- **Front :** `cd peintre-nano && npm run test -- --run tests/unit/admin-sites-edit-navigation-28-5 tests/unit/admin-cash-registers-edit-navigation-28-5`

Compléments :

- `npm run test` ciblé `*28-5*` + non-régression `navigation-transverse-served-5-1`, `navigation-transverse-5-1` ;
- `npm run lint` + `npm run build` Peintre (surfaces UI touchées) ;
- **QA2** scope 28.5 avant CR ;
- **HITL** : parcours manuel hub → sites → modifier nom → retour hub → postes → modifier site rattaché — Strophe (hors marquage Validé HITL automatique).

## Risques / HITL

| Sujet | Statut |
|-------|--------|
| Champs site : ville seule vs adresse complète | **Tranché** : nom + ville en beta |
| Actualiser : renommer vs supprimer | **Tranché** : « Recharger la liste » + Tooltip |
| REV-ADMIN-09 : message suppression insuffisant | Si HITL bloque, **clarification texte seule** — pas nouveau flux archivage dans 28.5 |
| Édition `site_id` poste avec session ouverte | PATCH autorisé backend ; si erreur métier, afficher message API — pas de règle front inventée sauf si API documente contrainte |
| Hub : retirer tout le bandeau vs le raccourcir | Préférer suppression bandeau gris ; titre page + boutons suffisent |
| Données test QA sur sites | Nettoyage manuel ops — hors DS |

## Alignement sprint / YAML

- `epic-28` : `in-progress`
- `28-1` … `28-4` : `done`
- `28-5-retablir-ledition-et-la-navigation-sites-postes-pour-la-beta` : `done`

## Dev Agent Record

### Agent Model Used

Composer (DS subagent Story Runner BMAD)

### Debug Log References

- Vitest : labels Mantine « Nom * » → tests edit via `getByDisplayValue` plutôt que `getByLabelText('Nom')`.

### Completion Notes List

- Hub : bandeau gris « Choisissez l'option… » supprimé ; boutons titre seul + Tooltip Mantine pour le détail ; testid hub conservés.
- Sites : modal « Modifier le site » (nom + ville), PATCH `updateSiteForAdmin`, mise à jour locale `setRows` ; bouton retour hub ; « Recharger la liste » (`admin-sites-reload-list`) + Tooltip.
- Postes : modal « Modifier le poste » (nom, emplacement, site_id) ; switches inline inchangés ; retour hub ; `admin-cash-registers-reload-list`.
- Tests `*28-5*` : 5/5 PASS. Gate pytest site/workstation/cash_register : 100/100 PASS. Non-régression nav contract 40/40 + admin 28-4 11/11 PASS.
- e2e `*28-5*` optionnel non ajouté (couverture unit suffisante pour gates).
- Registre `references/revision/domaines/admin.md` : REV-ADMIN-06/07/08 → Investigé + Corrigé (pas Validé HITL).

### File List

- `peintre-nano/src/domains/admin-config/AdminSitesAndRegistersHubWidget.tsx`
- `peintre-nano/src/domains/admin-config/AdminSitesWidget.tsx`
- `peintre-nano/src/domains/admin-config/AdminCashRegistersWidget.tsx`
- `peintre-nano/tests/unit/admin-sites-edit-navigation-28-5.test.tsx`
- `peintre-nano/tests/unit/admin-cash-registers-edit-navigation-28-5.test.tsx`
- `references/revision/domaines/admin.md`
- `_bmad-output/implementation-artifacts/sprint-status.yaml`
- `_bmad-output/implementation-artifacts/28-5-retablir-ledition-et-la-navigation-sites-postes-pour-la-beta.md`

### Change Log

- 2026-06-07 — DS story 28.5 : édition sites/postes, navigation retour hub, hub simplifié, clarification rechargement liste ; tests unitaires 28-5 ; registre revision REV-06/07/08 Investigé+Corrigé.
