# Story 3.3: Gestion des PIN opérateur caisse et déverrouillage de session

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->
<!-- HITL (recommandé) : après livraison, valider la politique PIN (longueur min, blocage après X échecs) — voir epics.md HITL-3.3. -->

## Story

En tant qu'**opérateur habilité à la caisse**,
je veux **avoir un code PIN personnel et pouvoir déverrouiller la session caisse en le saisissant**,
afin **que seul un opérateur autorisé puisse sortir du mode caisse**.

## Acceptance Criteria

1. **Étant donné** une personne habilitée à la caisse avec un PIN configuré (Story 3.1)  
   **Quand** le poste est en mode caisse verrouillé et que je saisis mon PIN correct  
   **Alors** la session se déverrouille ; un PIN incorrect ne déverrouille pas (FR5, FR15).

2. **Étant donné** un utilisateur avec permission caisse  
   **Quand** j'accède au flux de déverrouillage (écran ou modal PIN)  
   **Alors** la saisie du PIN appelle `POST /v1/auth/pin` ; en cas de succès, le frontend met à jour l'état « déverrouillé » et l'identité de l'opérateur ; en cas d'échec, un message d'erreur est affiché sans déverrouiller.

3. **Étant donné** l'association PIN / utilisateur  
   **Quand** le système stocke ou vérifie le PIN  
   **Alors** le PIN est géré de façon sécurisée (hash en BDD, pas de PIN en clair dans les logs ni les réponses API) (NFR-S3).

4. **Étant donné** le périmètre v1  
   **Quand** le livrable est livré  
   **Alors** il correspond à la migration/copie 1.4.4 (artefact 08 §2.1, artefact 09 §3.2/3.3, artefact 10 §4.6) ; le déverrouillage par PIN est utilisable depuis l'écran caisse verrouillé (Story 3.5 en dépend).

## Tasks / Subtasks

- [x] Task 1 : Backend — restriction et sécurisation du flux PIN (AC: 1, 3)
  - [x] **Réutiliser** le handler existant `POST /v1/auth/pin` (Story 3.1) ; ne pas créer un nouvel endpoint. Après identification de l'utilisateur par PIN, vérifier qu'il a au moins une permission caisse (`caisse.access`, livré par 3.2 — utiliser la même logique que `require_permissions`) ; retourner 403 si l'utilisateur identifié n'a pas la permission.
  - [x] S'assurer que le PIN est toujours vérifié via hash (déjà en place en 3.1) ; aucun log ni réponse ne contient le PIN en clair.
  - [x] (Optionnel v1) Préparer ou documenter une politique de verrouillage après N échecs (HITL-3.3 à valider après livraison).
- [x] Task 2 : Backend — audit du déverrouillage (AC: 1)
  - [x] Enregistrer un événement d'audit à chaque déverrouillage réussi : type « session_unlocked » ou « pin_unlock », user_id, timestamp, contexte (ex. register_id si disponible). Si la table `audit_events` n'existe pas encore, créer une migration minimale (colonnes : id, timestamp, user_id, action, resource_type, resource_id, details) selon architecture.md § Audit log, puis enregistrer l'événement.
  - [x] Ne pas logger les échecs PIN avec détail (éviter fuite d'info) ; un compteur ou un log générique est acceptable pour monitoring.
- [x] Task 3 : Frontend — écran/modal de déverrouillage par PIN (AC: 1, 2, 4)
  - [x] Créer un composant (écran ou modal) « Déverrouillage par PIN » : clavier PIN (4–6 chiffres), champ masqué, bouton valider.
  - [x] Au submit : appeler `POST /v1/auth/pin` avec le body `{ pin: string }` (même contrat que 3.1). En cas de succès : mettre à jour le contexte auth (tokens + user), mettre à jour l'état « session déverrouillée » (state/context caisse) et fermer le modal ou rediriger vers le menu caisse ; en cas d'échec (401/403) : afficher un message d'erreur sans déverrouiller.
  - [x] Aligner sur artefact 10 §4.6 : route dédiée possible (ex. `/cash-register/pin`) ou modal affiché lorsque le mode caisse est actif et verrouillé ; même contrat API que connexion par PIN (POST /v1/auth/pin).
- [x] Task 4 : Intégration état « verrouillé / déverrouillé » (AC: 1, 2)
  - [x] Exposer un état (context ou store) « caisse locked / unlocked » et l'identité de l'opérateur ayant déverrouillé, pour que la Story 3.5 puisse restreindre le menu et afficher le bon écran.
  - [x] Prévoir un moyen de « reverrouiller » (ex. bouton ou timeout) qui remet l'état en verrouillé sans invalider le JWT (le détail du reverrouillage peut être affiné en 3.5).
- [x] Task 5 : Tests et non-régression (AC: 1–4)
  - [x] Tests API (pytest) : POST /v1/auth/pin avec utilisateur sans permission caisse → 403 ; avec permission caisse et bon PIN → 200 + tokens ; mauvais PIN → 401 ; vérifier qu'aucune réponse ne contient de PIN en clair.
  - [x] Tests frontend (Vitest + RTL + jsdom) : composant déverrouillage PIN (affichage, soumission, message d'erreur) ; co-locés `*.test.tsx` selon convention projet.
  - [x] Vérifier que les flows 3.1 (login, profil, PIN) et 3.2 (permissions) ne régressent pas.

### Review Follow-ups (AI)

- [x] [AI-Review][MEDIUM] Aligner PinUnlockModal et LockButton sur Mantine (convention projet, architecture checklist) — frontend/src/caisse/PinUnlockModal.tsx, LockButton.tsx.
- [x] [AI-Review][MEDIUM] Considérer une seule transaction pour session + audit (éviter session créée sans événement audit si commit audit échoue) — api/routers/v1/auth.py.
- [ ] [AI-Review][MEDIUM] Documenter ou committer les fichiers de la story : nombreux fichiers listés en File List sont encore non suivis par git (??) — transparence / traçabilité.
- [x] [AI-Review][LOW] Enrichir l'événement d'audit avec resource_id (ex. register_id) si disponible — api/routers/v1/auth.py.
- [x] [AI-Review][LOW] Ajouter un test unitaire pour LockButton (affichage, appel lock au clic) — frontend/src/caisse/LockButton.test.tsx.
- [x] [AI-Review][LOW] Documenter la dépendance CaisseProvider → AuthProvider (ou garantir le wrapping dans l'app) — frontend/src/caisse/CaisseContext.tsx.

## Senior Developer Review (AI)

**Date :** 2026-02-27  
**Résultat :** Approved (3e passage — corrections MEDIUM/LOW vérifiées)  
**Re-review :** 2026-02-27 — vérification reconduite, même conclusion.

**Vérifications 3e passage :** PinUnlockModal et LockButton alignés Mantine (Modal, Button, TextInput, Alert, SimpleGrid) ; transaction unique session+audit (add_session_no_commit + db.add(evt) + db.commit) dans api/routers/v1/auth.py et api/services/auth.py ; LockButton.test.tsx présent (affichage, libellé, appel lock au clic) ; CaisseContext documente dépendance CaisseProvider → AuthProvider et ordre des providers ; resource_id documenté (null v1, register_id en 3.4) dans auth.py. AC1–AC4 et tasks validés. MEDIUM restant (fichiers non commités) : traçabilité/process, non bloquant.

**Git vs File List :** Plusieurs fichiers du File List sont en état non suivi (??) dans git ; le reste est cohérent. Aucun fichier modifié non listé dans la story pour le périmètre 3.3.

**AC validés :** AC1–AC4 implémentés (déverrouillage par PIN, appel POST /v1/auth/pin, PIN hashé / pas en clair, état locked/unlocked et reverrouillage).

**Tasks :** Toutes les tâches marquées [x] correspondent à du code présent (auth.py restriction caisse + audit, AuditEvent + migration 006, PinUnlockModal, CaisseContext, LockButton, tests API et frontend).

**Problèmes relevés (passes précédentes) :**
- **MEDIUM :** PinUnlockModal et LockButton n'utilisent pas Mantine (convention projet). → **Résolu**
- **MEDIUM :** Audit et session créés en deux commits ; en cas d'échec du second commit, session sans événement d'audit. → **Résolu**
- **MEDIUM :** Fichiers 3.3 non commités (documentation / traçabilité). → Non traité (process, non bloquant)
- **LOW :** register_id non renseigné dans l'audit ; LockButton non testé ; dépendance CaisseProvider → AuthProvider non documentée. → **Résolus**

## Change Log

| Date       | Phase   | Auteur | Commentaire |
|------------|---------|--------|-------------|
| 2026-02-27 | review  | bmad-qa | Code review adversarial : 3 MEDIUM, 3 LOW. Status → in-progress. Follow-ups ajoutés. |
| 2026-02-27 | review  | bmad-qa | Re-review adversarial : même résultat ; follow-ups MEDIUM/LOW non résolus. review.json et statut inchangés. |
| 2026-02-27 | review  | bmad-qa | 3e passage : corrections MEDIUM/LOW vérifiées. review.json → approved. Status → done, sprint-status 3-3 → done. |

## Dev Notes

- **Réutilisation obligatoire** : Ne pas réimplémenter ni dupliquer `POST /v1/auth/pin`. Étendre le handler existant (Story 3.1) dans `api/routers/v1/auth.py` : après résolution de l'utilisateur par PIN, ajouter la vérification de permission caisse ; réutiliser `api/core/deps.py` (require_permissions) ou la même logique.
- **Contexte 3.1 et 3.2** : Story 3.1 livre déjà `POST /v1/auth/pin` (body `pin` → tokens + user), `PUT /v1/users/me/pin` (définir/modifier PIN), et le stockage du PIN en hash. Story 3.2 livre `require_permissions` et les permissions `caisse.access`, etc. Cette story 3.3 ajoute : (1) restriction de POST /v1/auth/pin aux seuls utilisateurs avec permission caisse, (2) flux frontend déverrouillage (écran/modal PIN + mise à jour état déverrouillé), (3) audit des déverrouillages, (4) état « locked/unlocked » pour 3.5.
- **Sécurité (NFR-S3)** : Accès caisse restreint par mode verrouillé et déverrouillage par PIN par opérateur habilité. PIN toujours hashé (passlib/bcrypt) ; pas de PIN en clair dans les réponses ni les logs. [Source: _bmad-output/planning-artifacts/architecture.md § Authentication & Security]
- **Règle brownfield** : Livrable = migration/copie 1.4.4. Références : artefact 08 §2.1 (users/PIN en RecyClique), artefact 09 §3.2/3.3 (auth, users), artefact 10 §4.6 (Connexion par PIN caisse — route `/login` option PIN ou `/cash-register/pin`, POST /v1/auth/pin). [Source: references/artefacts/2026-02-26_10_tracabilite-ecran-donnees-appels-api.md §4.6]
- **FR5, FR15** : Déverrouiller par PIN ; PIN par opérateur caisse. [Source: epics.md FR Coverage Map]
- **HITL-3.3** : Après livraison, Strophe peut trancher la politique PIN (longueur min, blocage après X échecs, durée). Implémenter une base simple (ex. refus 401 sur mauvais PIN) et documenter les options pour HITL.

### Project Structure Notes

- **Backend** : Étendre `api/routers/v1/auth.py` (handler POST /v1/auth/pin) pour vérifier la permission caisse après identification par PIN ; enregistrement dans `audit_events` (créer la table en migration si absente). Réutiliser `api/core/deps.py` (get_current_user, require_permissions) pour la logique permission.
- **Frontend** : Nouveau composant dans `frontend/src/` (ex. `caisse/` ou `auth/`) pour l'écran/modal « Déverrouillage par PIN » ; clavier numérique et appel POST /v1/auth/pin. Contexte ou state partagé pour « caisse locked/unlocked » et « opérateur ayant déverrouillé » (alignement avec 3.5).
- **Tests** : API = `api/tests/routers/test_auth.py` (étendre avec cas PIN + permission caisse) ou fichier dédié ; frontend = tests co-locés `*.test.tsx`.

### References

- [Source: _bmad-output/planning-artifacts/epics.md] Epic 3, Story 3.3, FR4, FR5, FR15, NFR-S3, HITL-3.3
- [Source: _bmad-output/planning-artifacts/architecture.md] Authentication & Security, PIN par opérateur, mode caisse verrouillé
- [Source: references/artefacts/2026-02-26_08_catalogue-qui-stocke-quoi-recyclic-paheko.md] §2.1 Utilisateurs et rôles, PIN en RecyClique
- [Source: references/artefacts/2026-02-26_09_perimetre-api-recyclique-v1.md] §3.2 Authentification, §3.3 Utilisateurs
- [Source: references/artefacts/2026-02-26_10_tracabilite-ecran-donnees-appels-api.md] §4.6 Connexion par PIN (caisse / tablette)
- [Source: references/ancien-repo/checklist-import-1.4.4.md] Copy + consolidate + security
- [Source: references/ancien-repo/v1.4.4-liste-endpoints-api.md] POST /v1/auth/pin, PUT /v1/users/me/pin
- [Source: _bmad-output/implementation-artifacts/3-1-users-jwt-et-gestion-de-compte-terrain.md] POST /v1/auth/pin, PUT /v1/users/me/pin, hash PIN
- [Source: _bmad-output/implementation-artifacts/3-2-groupes-permissions-et-rbac.md] require_permissions, caisse.access, GET /v1/users/me/permissions

## Dev Agent Record

### Agent Model Used

{{agent_model_name_version}}

### Debug Log References

### Completion Notes List

- Task 1 : Handler POST /v1/auth/pin étendu avec vérification get_user_permission_codes_from_user(db, found) ; 403 si caisse.access absent. PIN inchangé (hash, pas en clair).
- Task 2 : Modèle AuditEvent (api/models/audit_event.py), migration 006 audit_events, enregistrement session_unlocked après succès PIN. Pas de log détaillé sur échec PIN.
- Task 3 : PinUnlockModal (frontend/src/caisse/), clavier 4–6 chiffres, POST /v1/auth/pin via api/auth.ts ; AuthContext + CaisseContext pour tokens/user et état déverrouillé.
- Task 4 : CaisseContext (isLocked, unlockedBy, unlockWithPin, lock) ; LockButton pour reverrouiller sans invalider JWT.
- Task 5 : Tests API (test_auth.py) : 403 sans caisse, 200 avec caisse+bon PIN, 401 mauvais PIN, pas de PIN en clair, audit event créé. Tests frontend PinUnlockModal.test.tsx (affichage, erreur API, succès). Non-régression 3.1/3.2 vérifiée (test_put_me_pin_success avec user caisse, test_admin_rbac inchangé).
- Review follow-ups (2026-02-27) : PinUnlockModal et LockButton migrés Mantine (Modal, Button, TextInput, Alert, SimpleGrid) ; session + audit en une transaction (add_session_no_commit + db.commit unique) ; resource_id documenté (null v1, register_id en 3.4) ; LockButton.test.tsx ajouté ; dépendance CaisseProvider → AuthProvider documentée dans CaisseContext. MEDIUM git (fichiers non commités) non traité.

### File List

- api/routers/v1/auth.py (modifié)
- api/services/auth.py (modifié — add_session_no_commit pour transaction unique)
- api/models/audit_event.py (nouveau)
- api/models/__init__.py (modifié)
- api/db/alembic/versions/2026_02_27_006_create_audit_events_table.py (nouveau)
- api/tests/conftest.py (modifié — import AuditEvent)
- api/tests/routers/test_auth.py (modifié — fixtures caisse, tests 3.3)
- frontend/package.json (modifié — @mantine/core, @mantine/hooks, @testing-library/user-event)
- frontend/src/test/setup.ts (modifié — styles Mantine, mock matchMedia)
- frontend/src/api/auth.ts (nouveau)
- frontend/src/api/index.ts (modifié)
- frontend/src/auth/AuthContext.tsx (nouveau)
- frontend/src/auth/index.ts (modifié)
- frontend/src/caisse/CaisseContext.tsx (nouveau — doc dépendance AuthProvider)
- frontend/src/caisse/PinUnlockModal.tsx (nouveau — Mantine Modal, Button, TextInput, Alert)
- frontend/src/caisse/LockButton.tsx (nouveau — Mantine Button)
- frontend/src/caisse/index.ts (modifié)
- frontend/src/caisse/PinUnlockModal.test.tsx (nouveau — MantineProvider, assertion dialog)
- frontend/src/caisse/LockButton.test.tsx (nouveau)
- _bmad-output/implementation-artifacts/sprint-status.yaml (modifié — 3-3 in-progress puis review)
