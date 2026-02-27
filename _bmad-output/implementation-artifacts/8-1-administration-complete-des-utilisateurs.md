# Story 8.1 — Administration complète des utilisateurs



**Epic :** epic-8 — Administration, compta v1 et vie associative  

**Story key :** 8-1-administration-complete-des-utilisateurs  

**Statut :** done  

**Dernière mise à jour :** 2026-02-27



---



## 1. User story



**En tant qu'** administrateur,  

**je veux** les écrans complets d'administration des utilisateurs (liste, détail, pending, approve/reject, groupes, audit),  

**afin de** gérer les accès à RecyClique.



### Périmètre fonctionnel



- **Liste utilisateurs** : table avec filtres (rôle, statut), pagination, indicateurs en ligne/hors ligne.

- **Détail utilisateur** : profil, rôle, statut, groupes, historique ; actions (modifier rôle/statut, affecter groupes, reset password/PIN).

- **Pending** : liste des inscriptions en attente ; actions approve / reject.

- **Groupes** : consultation et affectation des groupes par utilisateur (liste groupes, liaison user ↔ groupes).

- **Audit** : historique des actions sur l'utilisateur (connexions, modifications admin) affiché ou accessible depuis le détail.



---



## 2. Critères d'acceptation



Alignés sur `_bmad-output/planning-artifacts/epics.md` (Story 8.1).



**Étant donné** les APIs users/groups/permissions existantes (Epic 3)  

**Quand** j'accède à `/admin/users`  

**Alors** les écrans suivants sont opérationnels :



| Écran / flux | Comportement attendu |

|--------------|----------------------|

| Liste | Liste des utilisateurs avec filtres rôle/statut, pagination ; indicateurs en ligne/hors ligne (si `GET /v1/admin/users/statuses`) ; bouton Nouveau (création utilisateur) ; clic ligne → détail. |

| Détail | Profil, rôle, statut, groupes ; modification rôle, statut, profil ; affectation groupes ; reset password, reset PIN. |

| Pending | Liste des inscriptions en attente ; approve / reject par utilisateur (ou par registration_request si body `registration_request_id`). |

| Groupes (dans le détail) | Liste des groupes disponibles ; affectation/désaffectation groupes pour l'utilisateur. |

| Audit / historique | Historique des actions (connexions, modifications) pour l'utilisateur affiché ou accessible. |



**Et** livrable = migration/copie 1.4.4 (référence `references/artefacts/2026-02-26_10_tracabilite-ecran-donnees-appels-api.md` §7.2 / §7.3).



---



## 3. Tâches techniques



### 3.1 Frontend — routes et pages



- [x] **Route `/admin/users`** : page liste utilisateurs (table Mantine, filtres rôle/statut, pagination).

- [x] **Route `/admin/users/:id`** : page détail utilisateur (profil, rôle, statut, groupes, onglet ou section historique/audit).

- [x] **Vue Pending** : onglet ou sous-route « En attente » (ex. `/admin/users?tab=pending` ou `/admin/users/pending`) listant les inscriptions en attente avec actions Approve / Reject.

- [x] **Navigation** : lien depuis le dashboard admin (`/admin`) vers `/admin/users` ; breadcrumb admin → Utilisateurs → [Détail].



### 3.2 Frontend — appels API (alignés artefact 10 §7.2 / §7.3)



- [x] **Chargement liste** : `GET /v1/admin/users` (query : rôle, statut, pagination) ; optionnel `GET /v1/admin/users/statuses` pour indicateurs en ligne.

- [x] **Chargement détail** : `GET /v1/admin/users/{user_id}` ; `GET /v1/admin/users/{user_id}/history` pour l'audit.

- [x] **Chargement pending** : `GET /v1/admin/users/pending`.

- [x] **Chargement groupes** : `GET /v1/admin/groups` pour l'affectation groupes dans le détail.

- [x] **Actions** :

  - Créer utilisateur : `POST /v1/users` (body : champs utilisateur, côté admin).

  - Modifier rôle : `PUT /v1/admin/users/{user_id}/role` (body : `{ role }`).

  - Modifier statut : `PUT /v1/admin/users/{user_id}/status` (body : `{ status }`).

  - Mise à jour profil : `PUT /v1/admin/users/{user_id}`.

  - Affecter groupes : `PUT /v1/admin/users/{user_id}/groups` (body : `{ group_ids }`).

  - Approuver : `POST /v1/admin/users/{user_id}/approve` (ou body `{ registration_request_id }` si depuis liste pending).

  - Rejeter : `POST /v1/admin/users/{user_id}/reject` (ou body `{ registration_request_id }` si depuis liste pending).

  - Reset password : `POST /v1/admin/users/{user_id}/reset-password` ou `POST /v1/admin/users/{user_id}/force-password`.

  - Reset PIN : `POST /v1/admin/users/{user_id}/reset-pin`.



### 3.3 Backend — APIs existantes (Epic 3)



- [x] Vérifier que les endpoints ci-dessus existent et sont documentés (Epic 3 — Stories 3.1, 3.2). Si un endpoint manque, le documenter comme prérequis ou le créer dans le cadre de cette story (selon convention projet).

- [x] Permissions : accès réservé aux utilisateurs avec permission `admin` (ou rôle équivalent).



### 3.4 Qualité et conformité



- [x] Permissions : les routes `/admin/users` et `/admin/users/:id` (et pending) ne sont accessibles qu'avec la permission admin.

- [x] Gestion d'états : loading / error / empty states sur liste et détail.

- [x] Livrable aligné sur migration/copie 1.4.4 (`references/ancien-repo/checklist-import-1.4.4.md`) pour les écrans et flux concernés.



---



## 4. Dev notes et références



### 4.1 Références obligatoires



| Référence | Usage |

|-----------|--------|

| **Artefact 10 §7.2** | `references/artefacts/2026-02-26_10_tracabilite-ecran-donnees-appels-api.md` — Utilisateurs (liste) : routes `/admin/users`, données affichées, appels API au chargement, actions → endpoints. |

| **Artefact 10 §7.3** | Même artefact — Utilisateurs (détail, pending) : routes `/admin/users/:id` et pending, détail profil, groupes, historique, actions approve/reject, reset password/PIN, affectation groupes. |

| **Epic 3** | APIs users, groups, permissions déjà livrées (Stories 3.1, 3.2) — s'appuyer sur `GET/POST/PUT/DELETE /v1/admin/groups`, etc. |

| **Règle brownfield** | Livrable = migration/copie depuis 1.4.4 selon `references/ancien-repo/checklist-import-1.4.4.md`. |



### 4.2 Conventions projet



- **UI** : Mantine (alignement 1.4.4). Pas de Tailwind ni autre lib UI sans décision.

- **Tests** : composants co-locés `*.test.tsx` ; Vitest + React Testing Library + jsdom.

- **Routes** : cohérence avec l'index des écrans artefact 10 (§3) : Admin Utilisateurs liste = #18, détail/pending = #19.



- **API** : paramètres de requête (query) et corps JSON (body) en **snake_case** (ex. `group_ids`, `page`, `page_size`) — convention projet (epics.md, architecture.md).



### 4.3 Dépendances



- **Epic 3** livrée (users, JWT, groupes, permissions, RBAC).

- Aucune nouvelle table BDD requise pour cette story (modèles users, groups, permissions existants).



---



## 5. Notes optionnelles



- **HITL-8.1** (epics.md) : après livraison, optionnel de valider le niveau de détail des écrans admin avec le PO.

- Si un endpoint listé en §7.2/7.3 n'existe pas encore (ex. `GET /v1/admin/users/{user_id}/history`), le préciser en revue et soit l'ajouter dans un cadre Epic 3 complémentaire, soit le scoper dans cette story avec accord technique.



- Approve/Reject : si l'implémentation utilise `registration_request_id` dans le body (liste pending = registration_requests), documenter le contrat exact ici et aligner la référence artefact 10 §7.3 si besoin.



---



## 6. File List (Story 8.1)



**Créés :** api/schemas/admin_user.py, api/routers/v1/admin/users.py, frontend/src/api/adminUsers.ts, frontend/src/admin/AdminGuard.tsx, frontend/src/admin/AdminGuard.test.tsx, frontend/src/admin/AdminUsersListPage.tsx, frontend/src/admin/AdminUsersListPage.test.tsx, frontend/src/admin/AdminUserDetailPage.tsx, frontend/src/admin/AdminUserDetailPage.test.tsx, frontend/src/admin/AdminUserCreatePage.tsx, frontend/src/admin/AdminUserCreatePage.test.tsx, frontend/src/admin/AdminDashboardPage.tsx



**Modifiés :** api/routers/v1/admin/__init__.py, api/routers/v1/users.py, frontend/src/App.tsx, frontend/src/caisse/AppNav.tsx, frontend/src/test/setup.ts



---



## 7. Change Log



- 2026-02-27 : Corrections post-review : pagination UI (Précédent/Suivant + Page N sur liste), tests co-locés *.test.tsx (AdminGuard, AdminUsersListPage, AdminUserDetailPage, AdminUserCreatePage) — Vitest + RTL + MantineProvider. Story remise en review.

- 2026-02-27 : Revu QA (bmad-qa) : changes-requested — pagination UI et tests co-locés manquants (voir §8).

- 2026-02-27 : Relecture bmad-revisor : AC complétés (liste indicateurs en ligne/hors ligne, pending registration_request_id), actions approve/reject clarifiées, note §5 alignement artefact 10.

- 2026-02-27 : Implémentation complète (backend admin users API, frontend /admin/users liste/détail/pending, guard admin, Mantine, tests Vitest co-locés). Approve/Reject sur registration_request (body registration_request_id).



---



## 8. Follow-ups (code review QA)



- [x] **Pagination liste** : ajouter les contrôles de pagination sur la page liste utilisateurs (page suivante / précédente ou sélecteur de page) pour respecter l'AC « pagination » ; le backend expose déjà `page` et `page_size`.

- [x] **Tests co-locés** : ajouter les fichiers `*.test.tsx` manquants pour AdminGuard, AdminUsersListPage, AdminUserDetailPage, AdminUserCreatePage (Vitest + React Testing Library + jsdom), conformément à la convention §3.4 et au File List §6.

