# Révisions terrain — Admin

**Périmètre :** Peintre v2 — admin config, utilisateurs, **modules**, dashboard, **santé & signaux**, **sites & postes caisse**  
**Dernière passe HITL :** 2026-06-07

**Docs liés :** [cadrage postes partages PIN](../../artefacts/2026-05-29_01_cadrage-postes-partages-pin-operateur.md) · lié [REV-TRANSVERSE-01](transverse.md#rev-transverse-01--menu-utilisateur-sans-mon-profil)

**Legacy référence :** `recyclique-1.4.4/frontend/src/components/business/UserProfileTab.tsx` (fiche admin utilisateur) · `Profile.tsx` (définition PIN par l'utilisateur lui-même, `/profil`)

---

## Synthèse

L'admin legacy ne permettait déjà **pas** de saisir un PIN pour un utilisateur — seulement de le **réinitialiser**. La création / modification du PIN se fait sur **Mon profil** (`PUT /v1/users/me/pin`). **Story 28-2** a rétabli cette chaîne en v2 : page `/profil`, widget self-service, lien admin « Ouvrir mon profil » après reset sur le compte courant ([REV-TRANSVERSE-01](transverse.md#rev-transverse-01--menu-utilisateur-sans-mon-profil)).

---

## Tableau de bord

| ID | Titre | Type(s) | P | Investigé | Corrigé | HITL |
|----|-------|---------|---|-----------|---------|------|
| [01](#rev-admin-01--réinit-pin-sans-parcours-de-création) | Réinit PIN sans création | métier · UI/UX · parité-legacy | P1 | [x] | [x] | [ ] |
| [02](#rev-admin-02--gestion-des-modules-copie-dev) | Gestion modules — copie dev | UI/UX · cadrage-produit | P1 | [x] | [x] | [ ] |
| [03](#rev-admin-03--modules-erreur-enregistrement) | Modules — erreur persistante | tech · UI/UX | P1 | [x] | [x] | [ ] |
| [04](#rev-admin-04--dashboard-super-admin-repliable) | Dashboard super-admin repliable | UI/UX · cadrage-produit | P2 | [ ] | [ ] | [ ] |
| [05](#rev-admin-05--santé-et-signaux-langage-humain) | Santé et signaux — langage humain | UI/UX · cadrage-produit | P1 | [x] | [x] | [ ] |
| [06](#rev-admin-06--hub-sites-caisses-ux) | Hub sites & caisses — mise en page | UI/UX | P2 | [x] | [x] | [ ] |
| [07](#rev-admin-07--sites-sans-édition-ni-retour) | Sites — pas d’édition ni retour | parité-legacy · UI/UX | P1 | [x] | [x] | [ ] |
| [08](#rev-admin-08--postes-caisse-sans-édition-ni-retour) | Postes caisse — pas d’édition ni retour | parité-legacy · UI/UX | P1 | [x] | [x] | [ ] |
| [09](#rev-admin-09--archiver-vs-supprimer-site) | Archiver vs supprimer (site) | métier · cadrage-produit | P2 | [ ] | [ ] | [ ] |
| [10](#rev-admin-10--vision-zones-multi-sites) | Vision zones / multi-sites | cadrage-produit | P2 | [ ] | [ ] | [ ] |

---

## D1 — Gestion des utilisateurs / credentials

### REV-ADMIN-01 — Réinit PIN sans parcours de création

| | |
|---|---|
| **Types** | métier · UI/UX · parité-legacy |
| **Priorité** | P1 *(effectif P0 si Epic 27 PIN — chaîne complète bloquée)* |
| **Signalé** | 2026-06-07 |
| **Lié** | [REV-TRANSVERSE-01](transverse.md#rev-transverse-01--menu-utilisateur-sans-mon-profil) |

**Suivi**
- [x] Investigé
- [x] Corrigé
- [ ] Validé HITL

**Observation**  
Dans **Gestion des utilisateurs**, fiche de l'utilisateur connecté :

1. **Réinitialiser le PIN** → efface le PIN ; toast « PIN réinitialisé avec succès » — **aucune suite** pour en définir un nouveau.
2. **Modifier les coordonnées** → identifiant, prénom, nom, courriel, téléphone, adresse, compétences, disponibilités, notes — **pas de champ PIN**.
3. Pas de bouton pour **forcer / définir un PIN** côté admin (l'utilisateur a peut‑être confondu avec **Forcer un mot de passe**, réservé super-admin).

**Attendu / legacy**  
- **Admin** (`UserProfileTab.tsx`) : mêmes actions — réinit mot de passe, **réinit PIN**, forcer mot de passe (super-admin). **Pas** de saisie PIN admin non plus.
- **Création PIN** : page **Mon profil** (`/profil`, `Profile.tsx`) — formulaire PIN 4 chiffres + confirmation, API `PUT /v1/users/me/pin`.
- Modal v2 de réinit PIN dit : *« la personne devra en définir un nouveau à la prochaine utilisation… »* — **chemin inexistant en v2 avant 28-2** (résolu par `/profil` self-service, story 28-2).

**État v2 (avant 28-2)**  
- `AdminUsersWidget.tsx` : `postAdminUserResetPin` uniquement ; modal édition sans PIN.
- API : `POST /v1/admin/users/{id}/reset-pin` (effacement) ; **pas** d'endpoint admin « forcer PIN » (symétrique de `force-password`).
- Définition PIN : **self-service** `PUT /v1/users/me/pin` — UI absente.

**Correction story 28-2**  
- `UserSelfProfileWidget.tsx` + route `/profil` : parcours self-service `PUT /v1/users/me/pin` (premier PIN ou modification avec `current_password`).
- `AdminUsersWidget.tsx` : après reset-pin sur **compte courant**, message + lien **Ouvrir mon profil** vers `/profil`.
- Pas d'endpoint admin « forcer PIN » (hors parité legacy) — la chaîne reset → Mon profil débloque le flux opérateur.

**État post-28-2**  
- Opérateur : peut poser ou modifier son PIN via **Mon profil** après reset admin (ou sur compte sans PIN).
- Admin : reset-pin inchangé (effacement seul) ; guidage explicite vers `/profil` si reset sur **soi-même**.
- Hors scope : forcer un PIN pour un **autre** utilisateur (arbitrage PO / sécurité).
- **HITL restant** : scénario reset admin → Mon profil → nouveau PIN sur poste terrain.

**Impact**  
Était bloquant : après réinit (ou compte sans PIN), impasse — ni admin ni utilisateur ne pouvait poser un PIN en v2 ; freinait postes partagés / step-up PIN. **Corrigé code 28-2** ; validation terrain en attente.

**Piste technique**  
~~1. **Court terme** : porter page **Mon profil** + entrée menu ([REV-TRANSVERSE-01](transverse.md#rev-transverse-01--menu-utilisateur-sans-mon-profil)) — débloque le flux legacy.~~ **livré 28-2**.  
~~2. **UX admin** : après réinit, message explicite + lien « Ouvrir mon profil » si même utilisateur.~~ **livré 28-2** (`AdminUsersWidget.tsx`).  
3. **Option produit** : endpoint + UI admin **Forcer un PIN** (comme mot de passe) — **hors parité legacy**, à trancher PO / sécurité.

**Notes agent**  
Story 28.2 (done 2026-06-07) — `AdminUsersWidget.tsx`, `UserSelfProfileWidget.tsx`, `users-me-client.ts`. Tests `*28-2*` : `user-self-profile-widget-28-2`, `admin-users-widget`, `profile-menu-pin-self-service-28-2.e2e`.

---

## D2 — Gestion des modules

### REV-ADMIN-02 — Gestion des modules — copie dev

| | |
|---|---|
| **Types** | UI/UX · cadrage-produit |
| **Priorité** | P1 |
| **Signalé** | 2026-06-07 |
| **Lié** | [REV-TRANSVERSE-04](transverse.md#rev-transverse-04--uuid-au-lieu-des-noms) · [REV-TRANSVERSE-05](transverse.md#rev-transverse-05--textes-orientés-dev) |

**Suivi**
- [x] Investigé
- [x] Corrigé
- [ ] Validé HITL

**Observation**  
Page **Gestion des modules** (`AdminModulesWidget`) :

- Sous-titre : `module-config`, stockage navigateur — **jargon**.
- Pavé « Qui peut agir » / « Périmètre » : *enveloppe*, super-admin, effets techniques (`getLiveSnapshot`, poll live).
- **Site = UUID** en badge (pas le nom de la ressourcerie).
- Orange : *« Enregistrement désactivé tant que la configuration serveur n'a pas été rechargée… »* — incompréhensible.
- Champ **Motif** + description *journalisation serveur itération ultérieure* — inutile en surface (ex. placeholder inventaire).
- Accordéons **Bandeau KPI** et **Comptage pièces/billets** : **OK** (contenu métier utile).

**Attendu**  
Titre + réglages ; explications en **ⓘ** ; langage bénévole ; nom de site lisible.

**Fichier**  
`peintre-nano/src/domains/admin-config/AdminModulesWidget.tsx`

**Notes agent**  
2026-06-07 — story **28-4** DS : copie planché, nom site lisible (`useAdminSiteDisplayLabel`), motif repliable, détail technique en Tooltip / `<details>` ; `AdminModulesWidget.tsx`.

---

### REV-ADMIN-03 — Modules — erreur enregistrement persistante

| | |
|---|---|
| **Types** | tech · UI/UX |
| **Priorité** | P1 |
| **Signalé** | 2026-06-07 |

**Suivi**
- [x] Investigé
- [x] Corrigé
- [ ] Validé HITL

**Observation**  
Super-admin connecté : **pavé rouge Erreur** (message type *rechargé avant toute tentative d'enregistrement* / auth — formulation STT approximative). **F5** ne corrige pas ; enregistrement impossible.

**Piste technique**  
`kpi-live-banner-settings-provider.tsx` : échec `getSiteModuleConfig` → `canSave=false` + `saveError` ; vérifier API module-config, ETag, permissions super-admin, payload invalide. Message utilisateur à réécrire en français clair (pas « etag », pas « rechargé » sans action).

**Notes agent**  
2026-06-07 — story **28-4** DS : cause racine `canSave` lié à ETag HTTP absent → repli `doc.version` (`resolveModuleConfigEtag`) ; CORS `expose_headers=["ETag"]` ; bouton « Recharger la configuration » ; messages FR opérateur (`kpi-live-banner-settings-provider.tsx`, `ComptagePiecesBilletsModulePanel.tsx`).

---

## D3 — Dashboard administration (accueil admin)

### REV-ADMIN-04 — Dashboard super-admin repliable

| | |
|---|---|
| **Types** | UI/UX · cadrage-produit |
| **Priorité** | P2 |
| **Signalé** | 2026-06-07 |

**Suivi**
- [ ] Investigé
- [ ] Corrigé
- [ ] Validé HITL

**Observation**  
Sur le **tableau de bord Administration** (`AdminLegacyDashboardHomeWidget`) :

1. **Activité & Logs** est dans la grille **« Navigation principale »** — devrait être dans le pavé **Administration Super-Admin** (outil supervision / audit, pas gestion quotidienne).
2. Le pavé **« Administration Super-Admin »** (santé, paramètres, sites, postes, modules, compta…) est **toujours déplié** — encombre l'écran ; souhait : **repliable par défaut** (accordéon / clic pour déplier), puis accès aux boutons.

**Attendu (PO terrain)**  
- Nav principale : gestion opérationnelle courante (utilisateurs, groupes, catégories, sessions caisse/réception, cockpit compta…).  
- Super-admin : outils sensibles + **Activité & Logs**, masqués jusqu'au dépliage.

**État v2**  
`AdminLegacyDashboardHomeWidget.tsx` L603–612 : `Activité & Logs` en nav principale ; L618–699 : bloc super-admin toujours visible si `isSuperAdmin`.

**Piste technique**  
`Accordion` Mantine ou `Collapse` sur le Paper super-admin ; déplacer le `Grid.Col` audit-log ; état replié persisté optionnel (`localStorage`).

**Notes agent**  
—

---

## D4 — Santé et signaux (super-admin)

### REV-ADMIN-05 — Santé et signaux — langage humain

| | |
|---|---|
| **Types** | UI/UX · cadrage-produit |
| **Priorité** | P1 |
| **Signalé** | 2026-06-07 |
| **Lié** | [REV-TRANSVERSE-04](transverse.md#rev-transverse-04--uuid-au-lieu-des-noms) · [REV-TRANSVERSE-05](transverse.md#rev-transverse-05--textes-orientés-dev) |

**Suivi**
- [x] Investigé
- [x] Corrigé
- [ ] Validé HITL

**Observation**  
Page **Santé et signaux** (`AdminSystemHealthWidget`, super-admin) — **charabia** pour un humain non technicien :

- Longs pavés d’intro (*sonde matérielle*, *monitoring infrastructure*, *agrégats serveur*, *planificateur*…).
- Bloc **« Synthèse santé (super-admin) »** : jargon ; bouton *« Vérifier l’endpoint test notifications »* — incompréhensible.
- Section **Recommandations** — exemples terrain :
  - *Priorité faible — Maintenance préventive de la base de données* : « maintenance régulière pour optimiser les performances » + **pistes d’action** (index, archiver, espace disque…) → **Qui fait quoi ?** L’humain ? Recyclique seul ? Quand ?
  - *Révision de sécurité périodique* : audit, logs, permissions, dépendances, sauvegardes — même flou (**checklist ops**, pas d’action dans l’app).
- Identifiants / corrélation encore trop techniques en surface (lien TRANSVERSE-04).

**Attendu**  
- Langage **planché** : ce que je vois, ce que ça implique pour la ressourcerie, **quoi faire concrètement** (ou « rien — simple rappel »).
- Détail technique → **infobulles ⓘ** uniquement.
- Recommandations : badge **« À faire par l’équipe technique »** vs **« Informatif — rien à faire maintenant »** ; masquer ou regrouper les reco **préventives génériques** si toujours affichées sans anomalie réelle.

**État v2 (avant 28-4, confirmé code)**  
- UI : `peintre-nano/src/domains/admin-config/AdminSystemHealthWidget.tsx` (pavés L519–528, synthèse L710+, recommandations L853–886).
- API : reco préventives **génériques** toujours injectées — `anomaly_detection_service.py` `_generate_preventive_maintenance_recommendations()` (maintenance BDD, audit sécurité, priorité `low`).

**État post-28-4**  
- Intro raccourcie + Tooltip ; bouton « Tester les alertes » ; badges responsable recommandations ; nom site lisible ; breakdown erreurs/IP repliable « Pour le support » ; copy métier (indicateurs du jour, sync Paheko).
- Backend : reco préventives `low` uniquement si anomalie détectée (`anomaly_detection_service.py`).

**Piste technique**  
1. **Front** : charte rédaction + tooltips ; renommer boutons (« Tester les alertes » vs endpoint).  
2. **Back / produit** : ne pas afficher les reco préventives **low** sans anomalie associée, ou les reformuler (*« Bonnes pratiques — hors app »*).  
3. Chaque piste d’action : préfixe **Responsable :** support / admin Recyclique / hébergeur.

**Notes agent**  
2026-06-07 — story **28-4** DS : intro raccourcie + Tooltip ; bouton « Tester les alertes » ; badges responsable recommandations ; nom site lisible ; backend : reco préventives low uniquement si anomalie détectée (`anomaly_detection_service.py`).

---

## D5 — Sites et postes de caisse

### REV-ADMIN-06 — Hub sites & caisses — mise en page

| | |
|---|---|
| **Types** | UI/UX |
| **Priorité** | P2 |
| **Signalé** | 2026-06-07 |

**Suivi**
- [x] Investigé
- [x] Corrigé
- [ ] Validé HITL

**Observation**  
Page intermédiaire **Gestion des sites et caisses** (`AdminSitesAndRegistersHubWidget`) :

- Sous-menu OK + **Retour tableau de bord** ; le bandeau vert **Administration** revient au même endroit (léger doublon — acceptable).
- Texte central *« Choisissez l'option… »* — peu utile.
- Deux gros boutons : sous-titres (*Sites de collecte…*, *Postes de caisse…*) **redondants** avec le titre du bouton ; mise en page des libellés dans le bouton peu lisible.

**Piste technique**  
Simplifier libellés (titre seul ou ⓘ) ; retirer ou raccourcir le bandeau gris central.

**Notes agent**  
Story 28.5 DS : bandeau gris central retiré ; boutons hub titre seul + détail en Tooltip Mantine ; testid hub inchangés.

**État post-28.5**  
Bandeau gris « Choisissez l'option… » supprimé ; boutons hub en titre seul avec détail en Tooltip ; testid hub conservés.

---

### REV-ADMIN-07 — Sites — pas d’édition ni retour

| | |
|---|---|
| **Types** | parité-legacy · UI/UX |
| **Priorité** | P1 |
| **Signalé** | 2026-06-07 |

**Suivi**
- [x] Investigé
- [x] Corrigé
- [ ] Validé HITL

**Observation**  
Page **Sites** (`/admin/sites`) :

- **Création** et **suppression** OK (test « TestNew »).
- **Pas de bouton Modifier** (nom, ville) — legacy `Sites.tsx` a **Modifier** + modal édition.
- **Pas de retour** vers le hub `/admin/sites-and-registers` — obligé de repasser par Administration.
- Bouton **Actualiser** : rôle peu clair (recharge la liste serveur) — libellé ou auto-refresh à cadrer.
- Donnée terrain : site `validationindépendante714e06c-site` (14 avr.) — probable résidu de test QA à nettoyer ou documenter.

**Attendu legacy**  
`recyclique-1.4.4/frontend/src/pages/Admin/Sites.tsx` — actions **Modifier** + **Supprimer**.

**État v2**  
`updateSiteForAdmin` existe mais sert seulement au toggle **Actif** ; pas de modal édition nom/ville.

**Piste technique**  
Modal « Modifier le site » ; bouton « Retour sites et caisses » ; tooltip sur Actualiser.

**Notes agent**  
Story 28.5 DS : modal « Modifier le site » (nom + ville), bouton retour hub, « Recharger la liste » + Tooltip ; tests `admin-sites-edit-navigation-28-5`.

**État post-28.5**  
Modal « Modifier le site » (nom + ville), retour hub, « Recharger la liste » + Tooltip ; switches et suppression inchangés.

---

### REV-ADMIN-08 — Postes caisse — pas d’édition ni retour

| | |
|---|---|
| **Types** | parité-legacy · UI/UX |
| **Priorité** | P1 |
| **Signalé** | 2026-06-07 |

**Suivi**
- [x] Investigé
- [x] Corrigé
- [ ] Validé HITL

**Observation**  
Page **Postes de caisse** (`/admin/cash-registers`) :

- Switches inline (actif, virtuel, différé) OK.
- **Pas de bouton Modifier** pour nom, emplacement, site rattaché — legacy `CashRegisters.tsx` a modal **Modifier**.
- **Pas de retour** vers hub sites & caisses.
- **Actualiser** : même remarque que sites.

**Attendu legacy**  
`CashRegisters.tsx` — **Modifier** + **Supprimer**.

**État v2**  
`updateCashRegisterForAdmin` utilisé pour patches switches uniquement.

**Notes agent**  
Story 28.5 DS : modal « Modifier le poste » (nom, emplacement, site), retour hub, « Recharger la liste » + Tooltip ; switches inline inchangés ; tests `admin-cash-registers-edit-navigation-28-5`.

**État post-28.5**  
Modal « Modifier le poste » (nom, emplacement, site rattaché), retour hub, « Recharger la liste » + Tooltip ; switches inline et badge session inchangés.

---

### REV-ADMIN-09 — Archiver vs supprimer (site)

| | |
|---|---|
| **Types** | métier · cadrage-produit |
| **Priorité** | P2 |
| **Signalé** | 2026-06-07 |

**Suivi**
- [ ] Investigé
- [ ] Corrigé
- [ ] Validé HITL

**Observation**  
Si des **données liées** empêchent la suppression : message actuel seulement. Question PO : proposer **archiver / désactiver** plutôt que supprimer définitivement ?

**Piste**  
Décision produit + API ; le toggle **Actif** existe déjà partiellement.

**Notes agent**  
Réflexion — pas d’impl sans décision PO.

---

### REV-ADMIN-10 — Vision zones / multi-sites

| | |
|---|---|
| **Types** | cadrage-produit |
| **Priorité** | P2 |
| **Signalé** | 2026-06-07 |

**Suivi**
- [ ] Investigé
- [ ] Corrigé
- [ ] Validé HITL

**Observation**  
À terme : pas seulement « sites de collecte » — **zones** (stockage, transit, expo, vente, réparation…), multi-sites / multi-bâtiments. Est-ce que **Sites et caisses** reste le bon écran ou un futur module **Zones** ?

**Piste**  
Croiser `references/idees-kanban/`, epics config-modules, vision flux objets — **hors scope correction beta**.

**Notes agent**  
Item de cadrage — ne pas implémenter dans la vague parité immédiate.

