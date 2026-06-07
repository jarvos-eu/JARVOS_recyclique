# Révisions terrain — Transverse (bandeau, auth, profil)

**Périmètre :** shell Peintre live — bandeau vert, menu utilisateur, navigation globale, profil / PIN opérateur, dashboard personnel, **chrome PWA** (barre de titre Windows)  
**Dernière passe HITL :** 2026-06-07

**Docs liés :** [cadrage postes partages PIN](../../artefacts/2026-05-29_01_cadrage-postes-partages-pin-operateur.md) · route `/profil` livrée story 28-2 (`contracts/creos/manifests/page-transverse-profile.json`, manifest navigation transverse)

**Legacy référence :** `recyclique-1.4.4/frontend/src/components/Header.jsx` (menu utilisateur) · `recyclique-1.4.4/frontend/src/pages/Profile.tsx` (fiche perso + PIN)

---

## Synthèse

Écarts **navigation globale**, **libellés humains** (UUID partout) et **ton UI** (copie développeur / story visible aux bénévoles). **[Mon profil](#rev-transverse-01--menu-utilisateur-sans-mon-profil) rétabli (story 28-2)** — code livré, HITL terrain en attente. Voir aussi admin modules [REV-ADMIN-02](admin.md#rev-admin-02--gestion-des-modules-copie-dev).

---

## Tableau de bord

| ID | Titre | Type(s) | P | Investigé | Corrigé | HITL |
|----|-------|---------|---|-----------|---------|------|
| [01](#rev-transverse-01--menu-utilisateur-sans-mon-profil) | Menu sans « Mon profil » | UI/UX · parité-legacy · métier | P1 | [x] | [x] | [ ] |
| [02](#rev-transverse-02--barre-de-titre-pwa-bleue) | Barre de titre PWA bleue | UI/UX | P2 | [ ] | [ ] | [ ] |
| [03](#rev-transverse-03--plier-barre-de-titre-pwa) | Plier / déplier barre titre | UI/UX | P2 | [ ] | [ ] | [ ] |
| [04](#rev-transverse-04--uuid-au-lieu-des-noms) | UUID au lieu des noms | UI/UX · métier | P1 | [x] | [x] | [ ] |
| [05](#rev-transverse-05--textes-orientés-dev) | Textes orientés dev | UI/UX · cadrage-produit | P1 | [x] | [x] | [ ] |

---

## D1 — Bandeau / menu utilisateur

### REV-TRANSVERSE-01 — Menu utilisateur sans « Mon profil »

| | |
|---|---|
| **Types** | UI/UX · parité-legacy · métier |
| **Priorité** | P1 |
| **Signalé** | 2026-06-07 |

**Suivi**
- [x] Investigé
- [x] Corrigé
- [ ] Validé HITL

**Observation**  
Depuis le **dashboard** (ou toute page avec bandeau vert) : clic sur le **nom** en haut à droite → menu avec **Dashboard personnel** et **Déconnexion** uniquement. Besoin de renseigner le **code PIN** du compte (non configuré) ; **aucun accès direct** à la fiche personnelle pour le modifier.

**Attendu / legacy**  
Menu legacy (`Header.jsx`) propose **trois** entrées :

1. Dashboard personnel → `/dashboard/benevole`
2. **Mon Profil** → `/profil`
3. Déconnexion

Page legacy `Profile.tsx` : coordonnées, mot de passe, **code PIN** (4 chiffres, `PUT /v1/users/me/pin`), etc.

**État v2 (avant 28-2)**  
- `LiveShellUserMenu.tsx` : seulement `onPersonalDashboard` + `onLogout` — **pas de lien profil**.
- `RuntimeDemoApp.tsx` : passe `onPersonalDashboard` si entrée nav `transverse-dashboard-benevole` ; rien pour profil.
- Doc interne : route **`/profil` non portée** par le `NavigationManifest` — gap connu (`03-contrats-creos-et-donnees.md`).

**Correction story 28-2**  
- `LiveShellUserMenu.tsx` : entrée **Mon profil** (`data-testid="live-shell-user-menu-profile"`) entre Dashboard personnel et Déconnexion quand `onProfile` fourni.
- `RuntimeDemoApp.tsx` : `goProfileFromMenu` → `pushState` `/profil` + `syncSelectionFromPath`.
- Manifeste CREOS `transverse-profile` (`page-transverse-profile.json`, `navigation-transverse-served.json`) + widget `demo.legacy.user.profile` (`UserSelfProfileWidget.tsx`).
- Client API `users-me-client.ts` : `GET /v1/users/me`, `PUT /v1/users/me/pin` avec messages FR.

**État post-28-2**  
- Menu live : **Mon profil** visible ; navigation SPA vers `/profil` opérationnelle.
- Widget self-service : premier PIN et modification (avec `current_password`) via `PUT /v1/users/me/pin` ; erreurs API en français.
- Chaîne admin reset → Mon profil : voir [REV-ADMIN-01](admin.md#rev-admin-01--réinit-pin-sans-parcours-de-création).
- **HITL restant** : retest terrain menu + saisie PIN sur poste installé.

**Impact**  
Était bloquant : impossible de configurer son PIN / ses infos sans admin ([REV-ADMIN-01](admin.md#rev-admin-01--réinit-pin-sans-parcours-de-création)) — freinait **postes partagés + PIN** (Epic 27). **Corrigé code 28-2** ; validation terrain en attente.

**Piste technique**  
~~1. Ajouter `Menu.Item` « Mon profil » dans `LiveShellUserMenu` + callback `onProfile`.~~ **livré 28-2**.  
~~2. Porter page/widget profil self-service (équivalent `Profile.tsx`) + route manifest CREOS (`/profil` ou slug transverse).~~ **livré 28-2**.  
~~3. Réutiliser API `PUT /v1/users/me/pin` (déjà dans OpenAPI legacy).~~ **livré 28-2** (`users-me-client.ts`). Reste : HITL terrain menu + saisie PIN.

**Notes agent**  
Story 28.2 (done 2026-06-07) — `LiveShellUserMenu.tsx`, `RuntimeDemoApp.tsx`, `UserSelfProfileWidget.tsx`, `users-me-client.ts`, manifests CREOS `transverse-profile`. Tests `*28-2*` : `live-shell-user-menu-28-2`, `user-self-profile-widget-28-2`, `runtime-demo-profile-nav-28-2`, `profile-menu-pin-self-service-28-2.e2e`.

---

## D2 — PWA installée (Windows / poste terrain)

### REV-TRANSVERSE-02 — Barre de titre PWA bleue

| | |
|---|---|
| **Types** | UI/UX |
| **Priorité** | P2 |
| **Signalé** | 2026-06-07 |

**Suivi**
- [ ] Investigé
- [ ] Corrigé
- [ ] Validé HITL

**Observation**  
En **web app installée** (barre Windows), la **barre de titre** est d'un **bleu** (même teinte que les boutons Mantine) — visuellement intrusive. Souhait : couleur du **fond de l'app**, barre **discrète / « invisible »**.

**Référence comparative**  
Autre web app du poste : barre de titre harmonisée avec le fond.

**État v2 (confirmé code)**  
- `public/manifest.webmanifest` : `"theme_color": "#228be6"` (bleu Mantine)
- `index.html` : `<meta name="theme-color" content="#228be6" />`
- `background_color` : `#f8f9fa` — **décalage** avec `theme_color`

**Piste technique**  
Aligner `theme_color` sur `background_color` ou blanc ; tester Edge/Chrome PWA Windows ; éventuellement `theme-color` dynamique par page (bandeau vert réception ?) — à cadrer PO.

**Notes agent**  
—

---

### REV-TRANSVERSE-03 — Plier / déplier barre de titre

| | |
|---|---|
| **Types** | UI/UX |
| **Priorité** | P2 |
| **Signalé** | 2026-06-07 |

**Suivi**
- [ ] Investigé
- [ ] Corrigé
- [ ] Validé HITL

**Observation**  
Dans une autre web app : **petite flèche** pour **plier / déplier** la barre de titre — utile pour gagner de la place en kiosk.

**Attendu**  
Évaluer parité confort PWA terrain (pas legacy 1.4.4 navigateur).

**Piste technique**  
API PWA **`display_override": ["window-controls-overlay"]`** + zone `env(titlebar-area-*)` (Chromium / Edge) ; faisabilité Safari / iOS à documenter.

**Notes agent**  
Nice-to-have — après REV-TRANSVERSE-02.

---

## D3 — Libellés et langage utilisateur (transversal)

### REV-TRANSVERSE-04 — UUID au lieu des noms

| | |
|---|---|
| **Types** | UI/UX · métier |
| **Priorité** | P1 |
| **Signalé** | 2026-06-07 |

**Suivi**
- [x] Investigé
- [x] Corrigé
- [ ] Validé HITL

**Observation**  
**Partout** dans l'app (ex. admin **Gestion des modules** : « Site : » + **UUID** en badge bleu), les références métier affichent des **identifiants techniques** — incompréhensibles pour les humains.

**Attendu**  
Nom du site, libellé poste, nom bénévole, etc. — UUID éventuellement en **infobulle** ou mode expert uniquement.

**État v2 (avant 28-4)**  
D'autres écrans admin résolvent déjà (`AdminCashRegistersWidget`, `AdminRegisteredDevicesWidget` — `siteNameById`) ; `AdminModulesWidget` affiche `envelope.siteId` brut.

**État post-28-4**  
Hook `useAdminSiteDisplayLabel` sur modules + santé : `presentation_labels` → `listSitesForAdmin` → troncation UUID (`slice(0,8)…`) ; UUID complet réservé à `title` / infobulle expert.

**Piste technique**  
Pattern transverse : résolution `site_id` → nom via API / enveloppe ; audit grep `siteId` / `Badge` dans `peintre-nano/src/domains/`.

**Notes agent**  
2026-06-07 — story **28-4** DS : hook `useAdminSiteDisplayLabel` (presentation_labels → listSitesForAdmin → troncation) sur modules + santé admin.

---

### REV-TRANSVERSE-05 — Textes orientés dev (pavés vs infobulles)

| | |
|---|---|
| **Types** | UI/UX · cadrage-produit |
| **Priorité** | P1 |
| **Signalé** | 2026-06-07 |

**Suivi**
- [x] Investigé
- [x] Corrigé
- [ ] Validé HITL

**Observation**  
Nombreux **pavés explicatifs** visibles : jargon (`module-config`, `enveloppe`, `getLiveSnapshot`, `traçabilité interne`, `itération ultérieure`). Inutile en surface ; devrait être en **infobulle** (ⓘ) en langage **planché**, non technique.

**Exemple pilote**  
Page **Gestion des modules** — [REV-ADMIN-02](admin.md#rev-admin-02--gestion-des-modules-copie-dev).

**Piste technique**  
Charte rédaction admin : 1 phrase sous le titre max ; détail technique → `Tooltip` / doc admin ; pas de `<code>` en face utilisateur.

**Notes agent**  
2026-06-07 — story **28-4** DS : charte 1 phrase + Tooltip / `<details>` sur `AdminModulesWidget` et `AdminSystemHealthWidget` ; jargon retiré de la surface.

---

## Liens réception (déjà notés)

- **Corrigé (28-2)** — était impossible de quitter le hub réception en PWA sans fermer l'app : [REV-RECEPTION-02](reception.md#rev-reception-02--pwa-sans-retour-menu) (P0). CTA « Retour au menu » sur hub sans poste ouvert.
