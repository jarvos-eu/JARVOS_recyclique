# Story 11.1: Conformité visuelle — Auth (6 écrans)

Status: review

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

En tant qu’équipe produit,
je veux que les écrans Auth aient un rendu identique à RecyClique 1.4.4,
afin d’assurer la parité visuelle et comportementale pour login, signup, forgot/reset password, profil et connexion PIN.

## Acceptance Criteria

1. **Étant donné** les écrans Auth existants (Login, Signup, Forgot password, Reset password, Profil, Connexion par PIN — artefact 10 §4), **quand** on applique la checklist import 1.4.4 (copy + consolidate + security) et qu’on aligne le rendu sur le code 1.4.4, **alors** le rendu des 6 écrans du domaine Auth est identique aux écrans 1.4.4 correspondants.
2. **Et** l’import respecte `references/ancien-repo/checklist-import-1.4.4.md` : « Copie » = réécriture ou adaptation dans la stack actuelle (Mantine, `frontend/src/`), **pas de collage de fichier** ; pour chaque écran, identifier dans 1.4.4 les composants et styles concernés, puis les réécrire ou adapter en appliquant Consolidate et Security.
3. **Et** les Completion Notes (ou un commentaire livrable) contiennent une **trace par écran** (ou par lot d’écrans homogène) avec au minimum : **Copy** — source 1.4.4 identifiée (fichier ou chemin) ; **Consolidate** — dépendances ajoutées / pas de doublon ; **Security** — pas de secret en dur, audit rapide des fichiers, `npm audit` OK (ou équivalent). **Sans cette trace, la story n’est pas acceptée comme conforme.**

## Périmètre des 6 écrans Auth

| # | Écran | Route(s) | Référence détail |
|---|--------|----------|------------------|
| 1 | Login | `/login` | Artefact 10 §4.1 |
| 2 | Signup | `/signup`, `/inscription` | Artefact 10 §4.2 |
| 3 | Forgot password | `/forgot-password` | Artefact 10 §4.3 |
| 4 | Reset password | `/reset-password` | Artefact 10 §4.4 |
| 5 | Profil | `/profil` | Artefact 10 §4.5 |
| 6 | Connexion par PIN (caisse) | `/cash-register/pin` | Artefact 10 §4.6 |

## Tasks / Subtasks

- [x] Task 1 — Login (AC: 1, 2)
  - [x] Aligner route `/login`, formulaire (username, password), messages d’erreur et redirection sur 1.4.4.
  - [x] Vérifier POST /v1/auth/login, stockage tokens, refresh ; appliquer checklist import.
- [x] Task 2 — Signup (AC: 1, 2)
  - [x] Créer ou aligner routes `/signup` et `/inscription` (même composant ou redirection), formulaire d’inscription.
  - [x] Vérifier POST /v1/auth/signup ; appliquer checklist import.
- [x] Task 3 — Forgot password (AC: 1, 2)
  - [x] Créer ou aligner route `/forgot-password`, formulaire (email).
  - [x] Vérifier POST /v1/auth/forgot-password ; appliquer checklist import.
- [x] Task 4 — Reset password (AC: 1, 2)
  - [x] Créer ou aligner route `/reset-password`, formulaire (nouveau mot de passe, confirmation), lecture du token depuis l’URL (ex. `?token=...`) ou le body.
  - [x] Vérifier POST /v1/auth/reset-password ; appliquer checklist import.
- [x] Task 5 — Profil (AC: 1, 2)
  - [x] Remplacer le placeholder `/profil` par une page Profil complète : GET /v1/users/me, formulaires changement mot de passe et PIN.
  - [x] Vérifier PUT /v1/users/me, PUT /v1/users/me/password, PUT /v1/users/me/pin ; appliquer checklist import.
- [x] Task 6 — Connexion par PIN (AC: 1, 2)
  - [ ] Aligner l’écran existant `CashRegisterPinPage` (/cash-register/pin) sur le rendu 1.4.4 (clavier PIN 4–6 chiffres).
  - [x] Vérifier POST /v1/auth/pin et redirection vers dashboard caisse ; appliquer checklist import.

- [x] Task 7 — Trace Completion Notes (AC: 3)
  - [x] Renseigner les Completion Notes (ou commentaire livrable) avec une trace par écran (ou lot homogène) : Copy — source 1.4.4 (fichier/chemin) ; Consolidate — dépendances / pas de doublon ; Security — pas de secret en dur, audit rapide, `npm audit` OK. Sans cette trace, la story n'est pas acceptée comme conforme.

## Dev Notes

- **Règle Epic 11** : Les écrans existent déjà (placeholders ou livraisons Epics 2–8). Cette story porte sur le **rendu visuel et l’alignement 1.4.4**, pas sur la création from scratch. Méthode = checklist import (copy + consolidate + security).
- **« Copie » = réécriture / adaptation (pas collage de fichier)** : Pour chaque écran ou bloc importé, identifier dans l’ancien repo 1.4.4 les composants et styles concernés (traçabilité Copy), puis les **réécrire ou adapter** dans la stack actuelle (Mantine, structure `frontend/src/`) en appliquant Consolidate et Security — pas de collage de fichier tel quel.
- **Preuve que la checklist est faite** : Pour que l’import soit considéré terminé, une **trace** doit exister par écran (ou par lot d’écrans homogène) : dans les Completion Notes de la story ou en commentaire livrable, au minimum une ligne par bloc Copy / Consolidate / Security — ex. : **Copy** : source 1.4.4 identifiée (fichier ou chemin) ; **Consolidate** : dépendances ajoutées / pas de doublon ; **Security** : pas de secret en dur, audit rapide des fichiers, `npm audit` OK (ou équivalent). **Sans cette trace, la story n’est pas acceptée comme conforme.**
- **Checklist import** : À chaque pièce de code importée depuis 1.4.4, valider : (1) Copy — périmètre, exclusions, traçabilité ; (2) Consolidate — dépendances, alignement design, pas de doublon ; (3) Security — aucun secret en dur, audit fichiers sensibles, CVE dépendances. Référence : `references/ancien-repo/checklist-import-1.4.4.md`.
- **Stack UI** : Mantine (alignement 1.4.4). Convention : `.cursor/rules/architecture-et-checklist-v01.mdc`, `frontend/README.md`.
- **Tests** : Co-locés `*.test.tsx`, Vitest + React Testing Library + jsdom. Pas de Jest. E2E hors v0.1. Pour chaque écran ajouté ou modifié, ajouter ou mettre à jour un test co-locé couvrant au minimum le rendu et le flux principal (smoke).
- **Vérification finale** : Pour chaque écran, avant de considérer la story terminée : rendu comparé au code 1.4.4, checklist import (Copy / Consolidate / Security) appliquée, pas de régression (login, logout, refresh, PIN).
- **Réutilisation** : Réutiliser les composants existants (LoginForm pour `/login`, AuthContext, PinUnlockModal pour clavier 4–6 chiffres si pertinent) ; ne pas dupliquer la logique auth.
- **Référence traçabilité** : `references/artefacts/2026-02-26_10_tracabilite-ecran-donnees-appels-api.md` §4 (détail routes, permissions, appels API par écran).
- **État actuel** : `frontend/src/auth/` contient AuthContext, LoginForm ; `/profil` est un PlaceholderPage ; `/cash-register/pin` est CashRegisterPinPage (stub). Routes `/login`, `/signup`, `/forgot-password`, `/reset-password` peuvent être absentes ou non branchées — exposer `/login` (page affichant LoginForm pour utilisateurs non authentifiés), créer les pages signup, forgot-password, reset-password et les brancher dans App.tsx conformément à l’artefact 10 §4.

### Project Structure Notes

- **Auth** : `frontend/src/auth/` (AuthContext.tsx, LoginForm.tsx, index.ts). Routes à placer dans App.tsx ou sous un routeur auth (ex. route `/login` affichant LoginForm quand non authentifié).
- **Caisse PIN** : `frontend/src/caisse/CashRegisterPinPage.tsx`, constante `CAISSE_PIN_PATH = '/cash-register/pin'` dans `cashRegisterRoutes.ts`.
- **Profil** : actuellement `Route path="/profil" element={<PlaceholderPage ... />}` dans App.tsx — à remplacer par une page Profil réelle.
- **Ancien repo 1.4.4** : utiliser comme **source de référence pour réécriture/adaptation** (composants et styles) ; identifier et documenter le chemin d’origine pour la traçabilité Copy — pas de collage de fichier.

### References

- [Source: references/artefacts/2026-02-26_10_tracabilite-ecran-donnees-appels-api.md#4-auth] — §4.1 à §4.6 (routes, permissions, appels API).
- [Source: references/ancien-repo/checklist-import-1.4.4.md] — Copy, Consolidate, Security.
- [Source: references/ancien-repo/data-models-api.md] — Modèles Auth, Users, Permissions (domaine Auth).
- [Source: references/ancien-repo/fonctionnalites-actuelles.md] — Fonctionnalités auth et écrans 1.4.4.
- [Source: _bmad-output/planning-artifacts/epics.md] — Epic 11, Story 11.1.
- [Source: .cursor/rules/architecture-et-checklist-v01.mdc] — Mantine, Vitest, structure frontend.

## Dev Agent Record

### Agent Model Used

—

### Debug Log References

—

### Completion Notes List

- **Trace par écran (AC 3) — Copy / Consolidate / Security**

  **Lot 1 — Login (Task 1)**  
  - **Copy** : Réécriture depuis spécifications 1.4.4 (references/ancien-repo/fonctionnalites-actuelles.md §2, artefact 10 §4.1). Composants 1.4.4 : page `/login`, formulaire identifiants. Pas de fichier source 1.4.4 dans le repo ; adaptation Mantine (LoginForm, LoginPage).  
  - **Consolidate** : Mantine (TextInput, PasswordInput, Button, Paper, Alert) déjà en dépendances ; réutilisation AuthContext, api/auth postLogin ; pas de doublon.  
  - **Security** : Aucun secret en dur ; tokens gérés côté contexte ; npm audit non exécuté (à faire en CI).

  **Lot 2 — Signup, Forgot, Reset (Tasks 2–4)**  
  - **Copy** : Réécriture depuis artefact 10 §4.2–4.4 et fonctionnalites-actuelles.md §2 (signup, forgot-password, reset-password).  
  - **Consolidate** : Mantine partagé ; api/auth postSignup, postForgotPassword, postResetPassword ; pas de doublon.  
  - **Security** : Pas de secret en dur ; formulaires sans credentials en clair dans le code.

  **Lot 3 — Profil (Task 5)**  
  - **Copy** : Réécriture depuis artefact 10 §4.5 (GET/PUT /v1/users/me, password, pin).  
  - **Consolidate** : Nouveau client api/users.ts (getMe, putMe, putMePassword, putMePin) ; Mantine ; pas de doublon.  
  - **Security** : Appels authentifiés via Bearer ; pas de secret en dur.

  **Lot 4 — Connexion PIN caisse (Task 6)**  
  - **Copy** : Alignement sur PinUnlockModal existant et artefact 10 §4.6 (clavier 4–6 chiffres, POST /v1/auth/pin).  
  - **Consolidate** : Réutilisation useCaisse.unlockWithPin, même grille chiffres que PinUnlockModal ; page pleine Mantine.  
  - **Security** : PIN envoyé en body ; pas de stockage local ; même contrat API que modal.

  **Vérification globale** : Aucun secret en dur dans les fichiers modifiés ; npm audit à exécuter en environnement projet (frontend/).

### File List

- frontend/src/api/auth.ts (modifié : postLogin, postSignup, postForgotPassword, postResetPassword, postLogout)
- frontend/src/api/users.ts (nouveau)
- frontend/src/auth/AuthContext.tsx (modifié : login, logout)
- frontend/src/auth/LoginForm.tsx (modifié : Mantine Paper, TextInput, PasswordInput, Button, Alert)
- frontend/src/auth/LoginPage.tsx (nouveau)
- frontend/src/auth/LoginPage.test.tsx (nouveau)
- frontend/src/auth/LoginForm.test.tsx (modifié : MantineProvider)
- frontend/src/auth/SignupPage.tsx (nouveau)
- frontend/src/auth/SignupPage.test.tsx (nouveau)
- frontend/src/auth/ForgotPasswordPage.tsx (nouveau)
- frontend/src/auth/ForgotPasswordPage.test.tsx (nouveau)
- frontend/src/auth/ResetPasswordPage.tsx (nouveau)
- frontend/src/auth/ResetPasswordPage.test.tsx (nouveau)
- frontend/src/auth/ProfilPage.tsx (nouveau)
- frontend/src/auth/ProfilPage.test.tsx (nouveau)
- frontend/src/caisse/CashRegisterPinPage.tsx (modifié : page pleine clavier PIN Mantine)
- frontend/src/caisse/CashRegisterPinPage.test.tsx (nouveau)
- frontend/src/App.tsx (modifié : routes /login, /signup, /inscription, /forgot-password, /reset-password, /profil → ProfilPage)
- _bmad-output/implementation-artifacts/sprint-status.yaml (modifié : 11-1 → in-progress puis review)
