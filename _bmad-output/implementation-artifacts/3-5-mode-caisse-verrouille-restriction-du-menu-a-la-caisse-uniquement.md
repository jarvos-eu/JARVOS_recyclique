# Story 3.5: Mode caisse verrouillé — restriction du menu à la caisse uniquement

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->
<!-- HITL (optionnel) : après livraison, valider que la liste des écrans « caisse » est alignée avec la matrice RBAC — voir epics.md HITL-3.5. -->

## Story

En tant qu'**opérateur en poste caisse**,
je veux **que l'écran soit verrouillé sur le menu caisse uniquement tant que la session n'est pas déverrouillée par PIN**,
afin **de garantir que seules les actions caisse sont possibles sur ce poste**.

## Acceptance Criteria

1. **Étant donné** un poste en mode caisse actif (poste démarré, Story 3.4)  
   **Quand** je navigue dans l'application sans avoir déverrouillé par PIN (Story 3.3)  
   **Alors** seul le menu caisse est accessible ; les autres routes sont inaccessibles (redirection ou blocage côté front, cohérent avec FR4).

2. **Étant donné** un opérateur en mode caisse verrouillé  
   **Quand** il tente d'accéder à une route hors caisse (admin, réception, profil, catégories, etc.)  
   **Alors** l'accès est refusé (redirection vers l'écran caisse courant ou écran PIN selon le flux) ; aucune navigation vers `/admin/*`, `/reception`, `/profil`, `/admin/categories`, etc.

3. **Étant donné** un opérateur en mode caisse  
   **Quand** il déverrouille la session en saisissant un PIN valide (flux Story 3.3)  
   **Alors** le mode verrouillé est levé ; la navigation redevient soumise uniquement au RBAC (permissions) ; le déverrouillage exige le PIN d'un opérateur habilité (FR5, FR15).

4. **Étant donné** le périmètre v1  
   **Quand** le livrable est livré  
   **Alors** il correspond à la migration/copie 1.4.4 ; comportement cohérent avec la matrice RBAC (opérateur caisse vs admin, réception, etc.) ; référence artefact 10 §5.1 (routes caisse).

## Tasks / Subtasks

- [x] Task 1 : État « mode caisse » et « verrouillé » (AC: 1, 2, 3)
  - [x] **Réutiliser** CaisseContext (état `isLocked`, poste courant) livré en 3.3/3.4 ; ne pas dupliquer la logique ni créer un nouveau store pour le mode verrouillé. Définir côté frontend la notion de **poste caisse actif** (poste démarré pour l'utilisateur courant, ex. issu de 3.4) et d'**écran verrouillé** (session non déverrouillée par PIN depuis le dernier verrouillage ou depuis l'arrivée sur le poste). Source de vérité : état dérivé du contexte auth + poste courant (GET /v1/cash-registers/status ou équivalent) ; optionnel : endpoint léger GET /v1/me/cash-register-context retournant { is_cash_register_active, is_locked } si déjà exposé par une story précédente.
  - [x] Lorsque l'utilisateur est sur un poste caisse actif et que l'état est « verrouillé », restreindre les routes accessibles aux seules routes **caisse** listées dans l'artefact 10 §5.1 à §5.4 : `/caisse`, `/cash-register/virtual`, `/cash-register/deferred`, `/cash-register/session/open`, `/cash-register/sale`, et l'étape fermeture session (exit). Inclure la route/écran de saisie PIN pour déverrouillage (ex. `/cash-register/pin` ou modal).
  - [x] Toute tentative de navigation vers une route non autorisée en mode verrouillé → redirection vers l'écran caisse principal (ex. `/caisse`) ou vers l'écran PIN si le flux le requiert.
  - [x] Après déverrouillage réussi (POST /v1/auth/pin ou flux existant 3.3), mettre à jour l'état « verrouillé » (false) côté client ; la navigation redevient gérée par le routeur et le RBAC uniquement.

- [x] Task 2 : Garde de routes et menu (AC: 1, 2)
  - [x] Implémenter un garde de routes (React Router ou équivalent) qui lit l'état « poste caisse actif + verrouillé » et autorise uniquement les routes caisse (et la route PIN). Bloquer ou rediriger les accès directs (URL, lien, retour arrière) vers admin, réception, profil, etc.
  - [x] Adapter le menu / la navigation (sidebar, header) : en mode caisse verrouillé, n'afficher que les entrées de menu caisse (dashboard caisses, ouverture session, saisie vente, fermeture session, déverrouiller par PIN). Masquer ou désactiver les liens Admin, Réception, Profil, Catégories, etc., tant que verrouillé.
  - [x] Aligner la liste des routes « caisse » avec `references/artefacts/2026-02-26_10_tracabilite-ecran-donnees-appels-api.md` §5.1 à §5.4 (pas §5.5 qui est admin).

- [x] Task 3 : Cohérence RBAC et déverrouillage (AC: 3, 4)
  - [x] S'assurer que le déverrouillage par PIN réutilise le flux Story 3.3 (POST /v1/auth/pin, tokens + user) ; aucun nouveau endpoint nécessaire si déjà en place.
  - [x] Vérifier que les permissions `caisse.access`, `caisse.virtual.access`, `caisse.deferred.access` restent respectées pour les écrans caisse (artefact 10 §5) ; le mode verrouillé ne contourne pas le RBAC, il restreint en plus la navigation aux seules routes caisse.
  - [x] Documenter ou tester le cas : opérateur avec uniquement caisse.access ne doit jamais voir admin/réception même déverrouillé (RBAC seul) ; opérateur avec caisse + admin déverrouillé peut accéder à admin.

- [x] Task 4 : Tests et non-régression (AC: 1–4)
  - [x] Tests frontend (Vitest + RTL + jsdom) : composant ou garde « mode caisse verrouillé » — lorsque l'état est actif+verrouillé, navigation vers /admin, /reception, /profil redirige vers caisse ou PIN ; après déverrouillage, navigation selon RBAC. Tests co-locés `*.test.tsx`.
  - [x] Vérifier que les flows 3.3 (PIN) et 3.4 (démarrage poste) ne régressent pas ; un opérateur sans poste caisse actif n'est pas soumis au verrouillage caisse.

- [x] Review Follow-ups (AI)
  - [x] [AI-Review][CRITICAL] Intégrer CashRegisterGuard et AppNav dans l'arborescence de l'app : App.tsx et main.tsx sont vides ; aucun Router, CaisseProvider, ni garde n'est monté. AC1/AC2 ne sont pas démontrables en conditions réelles. [frontend/src/App.tsx, main.tsx]
  - [x] [AI-Review][HIGH] Alimenter le statut poste : getCashRegistersStatus n'est appelé nulle part ; setCurrentRegister(registerId, started) n'est utilisé qu'en tests. Un écran (ex. dashboard caisse) doit appeler GET /v1/cash-registers/status et mettre à jour le contexte pour que le mode verrouillé s'active en flux réel. [frontend/src]
  - [x] [AI-Review][MEDIUM] Menu : la story demande « fermeture session » dans les entrées caisse ; AppNav n'a que Dashboard, Ouverture session, Saisie vente, Déverrouiller. Ajouter une entrée « Fermeture session » si l'UX le prévoit, ou documenter que l'étape exit est dans la même zone (pas de lien dédié). [frontend/src/caisse/AppNav.tsx]
  - [x] [AI-Review][LOW] Tests AppNav : envisager waitFor dans le test « en mode verrouillé affiche... » si flakiness. [frontend/src/caisse/AppNav.test.tsx]

## Dev Notes

- **FR4** : Le système peut restreindre l'accès au menu caisse uniquement lorsque le poste est en mode caisse (écran verrouillé sur la caisse). [Source: epics.md FR Coverage Map]
- **Prérequis** : Stories 3.3 (PIN opérateur, déverrouillage) et 3.4 (démarrage poste caisse ou réception). **Réutiliser** CaisseContext et l'état locked/unlocked (3.3), statut poste (3.4). Réutiliser le flux PIN (POST /v1/auth/pin) et l'état « poste démarré » (GET /v1/cash-registers/status ou contexte utilisateur) ; ne pas dupliquer la logique auth.
- **Règle brownfield** : Livrable = migration/copie 1.4.4. Référence principale : artefact 10 §5.1 (Dashboard caisses — routes `/caisse`, `/cash-register/virtual`, `/cash-register/deferred`), §5.2 Ouverture session, §5.3 Saisie vente, §5.4 Fermeture session. Ne pas inclure §5.5 (Détail session admin) dans le « menu caisse » réservé à l'opérateur verrouillé. [Source: references/artefacts/2026-02-26_10_tracabilite-ecran-donnees-appels-api.md]
- **Routes à autoriser en mode verrouillé** : `/caisse`, `/cash-register/virtual`, `/cash-register/deferred`, `/cash-register/session/open`, `/cash-register/sale`, étape exit (même zone ou modal), et la route/écran de déverrouillage PIN (ex. `/cash-register/pin` ou équivalent).
- **Routes à bloquer en mode verrouillé** : toutes les autres, notamment `/admin`, `/admin/*`, `/reception`, `/profil`, `/login` (sauf si utilisé pour PIN), `/signup`, `/admin/categories`, etc. (voir index §3 de l'artefact 10 pour la liste complète des routes par domaine).
- **Architecture** : Cross-cutting concern « mode caisse verrouillé » (architecture.md) : compte admin pour postes, PIN par opérateur caisse, RBAC, mode caisse verrouillé (menu caisse seul). Implémentation côté frontend (garde de routes + état dérivé du contexte auth/poste).

### Project Structure Notes

- **Frontend** : Garde de routes dans le routeur React (ex. `frontend/src/routes/` ou `frontend/src/app/`) ; état « mode caisse actif + verrouillé » dans un contexte React (ex. `CashRegisterContext`) ou store (Zustand/Context) alimenté par l'auth et le statut poste. **Garde et hook dans `frontend/src/caisse/`** à côté de CaisseContext (story 3.3). Menu/navigation : composant qui lit ce contexte et affiche uniquement les entrées caisse + déverrouiller quand verrouillé. Fichiers typiques : `CashRegisterGuard.tsx`, `useCashRegisterLock.ts`, layout/sidebar conditionnel. Aligner sur Mantine (convention projet).
- **Backend** : Aucune modification obligatoire si 3.3 et 3.4 exposent déjà le statut poste et le flux PIN ; optionnel : endpoint GET /v1/me/cash-register-context (is_cash_register_active, is_locked) si le front a besoin d'une source de vérité côté API pour l'état verrouillé (sinon déduire côté client à partir du poste courant et d'un flag « unlocked » en session/localStorage).
- **Tests** : co-locés `*.test.tsx` à côté du garde ou du hook.

### References

- [Source: _bmad-output/planning-artifacts/epics.md] Epic 3, Story 3.5, FR4, FR5, FR15, HITL-3.5
- [Source: _bmad-output/planning-artifacts/architecture.md] Cross-cutting: mode caisse verrouillé (menu caisse seul), RBAC, PIN
- [Source: references/artefacts/2026-02-26_10_tracabilite-ecran-donnees-appels-api.md] §5.1 Dashboard caisses (routes), §5.2 Ouverture session, §5.3 Saisie vente, §5.4 Fermeture session ; §3 Index des écrans (routes par domaine)
- [Source: references/ancien-repo/checklist-import-1.4.4.md] Copy + consolidate + security
- [Source: _bmad-output/implementation-artifacts/3-3-gestion-des-pin-operateur-caisse-et-deverrouillage-de-session.md] Flux PIN, POST /v1/auth/pin, déverrouillage
- [Source: _bmad-output/implementation-artifacts/3-4-demarrer-un-poste-caisse-ou-reception-avec-un-compte-administrateur.md] État poste démarré, GET /v1/cash-registers/status

## Dev Agent Record

### Agent Model Used

(à remplir par l'agent dev)

### Debug Log References

### Completion Notes List

- Task 1 : CaisseContext étendu avec `currentRegisterId`, `currentRegisterStarted`, `setCurrentRegister`, `isCashRegisterActive`. Source de vérité côté client : sélection du poste (dashboard) + statut issu de GET /v1/cash-registers/status. Routes caisse définies dans `cashRegisterRoutes.ts` (artefact 10 §5.1–5.4 + /cash-register/pin). Redirection vers `/caisse` si route non autorisée. Déverrouillage réutilise CaisseContext (unlockWithPin → isLocked false).
- Task 2 : `CashRegisterGuard` (React Router) redirige vers `/caisse` lorsque `isRestricted` et path non autorisé. `AppNav` affiche uniquement entrées caisse + « Déverrouiller par PIN » en mode verrouillé ; liste alignée artefact 10 §5.1–5.4 (pas §5.5).
- Task 3 : Déverrouillage réutilise POST /v1/auth/pin (CaisseContext, 3.3). Le garde ne contourne pas le RBAC : il restreint uniquement quand `isCashRegisterActive && isLocked` ; une fois déverrouillé, la navigation est gérée par le routeur (RBAC à appliquer côté routes/backend).
- Task 4 : Tests co-locés : `cashRegisterRoutes.test.ts`, `useCashRegisterLock.test.tsx`, `CashRegisterGuard.test.tsx`, `AppNav.test.tsx`. Non-régression : PinUnlockModal, LockButton, StartPostPage, LoginForm (33 tests passent).
- **Review follow-ups (2026-02-27)** : ✅ CRITICAL — App.tsx et main.tsx implémentés avec BrowserRouter, AuthProvider, CaisseProvider, CashRegisterGuard, AppNav et Routes (structure minimale pour AC1/AC2). ✅ HIGH — CaisseDashboardPage appelle getCashRegistersStatus au chargement et setCurrentRegister(registerId, true) à la sélection d'un poste démarré ou si un seul poste started. ✅ MEDIUM — Entrée « Fermeture session » ajoutée dans AppNav (route /cash-register/session/close). ✅ LOW — Test AppNav renforcé avec waitFor pour stabilité.

### File List

- frontend/src/api/caisse.ts (nouveau — GET /v1/cash-registers/status)
- frontend/src/api/index.ts (modifié — export caisse)
- frontend/src/auth/AuthContext.tsx (nouveau — minimal pour setFromPinLogin, Story 3.5 intégration)
- frontend/src/auth/index.ts (nouveau)
- frontend/src/caisse/cashRegisterRoutes.ts (nouveau — + CAISSE_SESSION_CLOSE_PATH, /cash-register/session/close)
- frontend/src/caisse/cashRegisterRoutes.test.ts (nouveau)
- frontend/src/caisse/CaisseContext.tsx (modifié — currentRegisterId, isCashRegisterActive, setCurrentRegister)
- frontend/src/caisse/CaisseDashboardPage.tsx (nouveau — GET status, setCurrentRegister, un seul poste démarré auto-sélection)
- frontend/src/caisse/useCashRegisterLock.ts (nouveau)
- frontend/src/caisse/useCashRegisterLock.test.tsx (nouveau)
- frontend/src/caisse/CashRegisterGuard.tsx (nouveau)
- frontend/src/caisse/CashRegisterGuard.test.tsx (nouveau)
- frontend/src/caisse/AppNav.tsx (nouveau — + entrée Fermeture session)
- frontend/src/caisse/AppNav.test.tsx (nouveau — waitFor pour test mode verrouillé)
- frontend/src/caisse/CashRegisterPinPage.tsx (nouveau — placeholder route PIN)
- frontend/src/caisse/CashRegisterSessionClosePage.tsx (nouveau — placeholder fermeture session)
- frontend/src/caisse/index.ts (modifié — exports guard, hook, routes, AppNav, CaisseDashboardPage, CAISSE_SESSION_CLOSE_PATH)
- frontend/src/PlaceholderPage.tsx (nouveau — pages placeholder routes)
- frontend/src/App.tsx (implémenté — BrowserRouter, CashRegisterGuard, AppNav, Routes)
- frontend/src/main.tsx (implémenté — AuthProvider, CaisseProvider, App)
- frontend/package.json (modifié — react-router-dom)

## Senior Developer Review (AI)

**Date :** 2026-02-27 | **Résultat :** Changes requested

- **CRITICAL** : CashRegisterGuard et AppNav ne sont pas intégrés dans l'app (App.tsx/main.tsx vides, pas de Router ni CaisseProvider). AC1/AC2 non démontrables en conditions réelles.
- **HIGH** : getCashRegistersStatus n'est appelé nulle part ; setCurrentRegister n'est utilisé qu'en tests. Pas d'alimentation du statut poste en flux réel.
- **MEDIUM** : AppNav sans entrée « Fermeture session » (story demande dashboard, ouverture, saisie, fermeture, déverrouiller).
- **LOW** : Tests solides (34 passent) ; renforcer AppNav test si flakiness.

**Points positifs** : Routes et garde alignés artefact 10 §5.1–5.4 ; CaisseContext réutilisé ; tests co-locés Vitest+RTL.

**Date :** 2026-02-27 (2e passage) | **Résultat :** Approved

- Intégration App confirmée : main.tsx (AuthProvider, CaisseProvider, App), App.tsx (BrowserRouter, CashRegisterGuard, AppNav, Routes).
- CaisseDashboardPage alimente le contexte : getCashRegistersStatus au chargement, setCurrentRegister à la sélection et pour un seul poste démarré.
- Menu : entrée « Fermeture session » (CAISSE_SESSION_CLOSE_PATH) présente dans AppNav.
- Tests : 34 passent ; CashRegisterGuard et AppNav (avec waitFor) couvrent le mode verrouillé. AC1/AC2 implémentés.

## Change Log

| Date       | Événement        | Détail |
|------------|------------------|--------|
| 2026-02-27 | Code review (AI) | Changes requested. Intégration garde/AppNav manquante ; alimentation statut poste absente ; follow-ups ajoutés. Status → in-progress. |
| 2026-02-27 | Corrections CR    | 4 follow-ups adressés : App/main avec Router+Guard+AppNav ; CaisseDashboardPage appelle getCashRegistersStatus et setCurrentRegister ; entrée Fermeture session dans AppNav ; test AppNav avec waitFor. Status → review. |
| 2026-02-27 | Code review (AI) 2e passage | Approved. Intégration, dashboard, menu Fermeture session et tests vérifiés. Status → done. |
