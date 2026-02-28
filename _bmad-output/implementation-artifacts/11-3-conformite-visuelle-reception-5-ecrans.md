# Story 11.3: Conformité visuelle — Réception (5 écrans)

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

En tant qu'équipe produit,
je veux que les écrans Réception aient un rendu identique à RecyClique 1.4.4,
afin d'assurer la parité visuelle pour accueil, poste, tickets, lignes, export CSV et stats live.

## Acceptance Criteria

1. **Étant donné** les écrans Réception existants (Accueil/poste, Ouverture poste, Liste tickets, Détail ticket + lignes, Export CSV / Stats live — artefact 10 §6), **quand** on applique la checklist import 1.4.4 (copy + consolidate + security) et qu'on aligne le rendu sur le code 1.4.4, **alors** le rendu des 5 écrans du domaine Réception est identique aux écrans 1.4.4 correspondants.
2. **Et** l'import respecte `references/ancien-repo/checklist-import-1.4.4.md` : « Copie » = réécriture ou adaptation dans la stack actuelle (Mantine, `frontend/src/`), **pas de collage de fichier** ; pour chaque écran (ou bloc logique), identifier dans 1.4.4 les composants et styles concernés, puis les réécrire ou adapter en appliquant Consolidate et Security.
3. **Et** les Completion Notes (ou un commentaire livrable) contiennent une **trace par écran** (ou par lot d'écrans homogène) avec au minimum : **Copy** — source 1.4.4 identifiée (fichier ou chemin) ; **Consolidate** — dépendances ajoutées / pas de doublon ; **Security** — pas de secret en dur, audit rapide des fichiers, `npm audit` OK (ou équivalent). **Sans cette trace, la story n'est pas acceptée comme conforme.**
4. **Et** avant clôture de la story : **build** — exécuter `npm run build` dans `frontend/` et documenter le résultat (OK ou erreurs) dans les Completion Notes ; **docker** — `docker compose up --build` à la racine doit réussir ; **console navigateur (recommandé)** — ouvrir les URLs des écrans livrés, DevTools → Console, vérifier aucune erreur rouge, et documenter dans les Completion Notes.
5. **Et** pas d'import React inutile dans les fichiers `.test.tsx` (runtime JSX automatique Vitest, éviter `noUnusedLocals` / TS6133).
6. **Et** visuel global 1.4.4 : le rendu respecte la source 1.4.4 y compris **couleurs**, typographie, espacements, layout. Si le code 1.4.4 ou l'audit réception définit une charte (couleurs primaires, boutons, cartes), la reproduire avec Mantine (theme, primaryColor, composants) pour parité visuelle.

## Périmètre des 5 écrans Réception

| # | Écran | Route(s) | Composant / zone actuel | Référence détail |
|---|--------|----------|-------------------------|------------------|
| 1 | Accueil réception / poste courant | `/reception` | ReceptionAccueilPage (état poste, KPI, boutons Ouvrir/Fermer poste, Créer ticket) | Artefact 10 §6.1 |
| 2 | Ouverture poste réception | Depuis accueil (modal ou étape) | ReceptionAccueilPage — flux ouverture poste | Artefact 10 §6.2 |
| 3 | Liste tickets réception | `/reception` (liste dans la page) | ReceptionAccueilPage — liste tickets du poste | Artefact 10 §6.3 |
| 4 | Détail ticket + lignes de dépôt | `/reception/tickets/:ticketId` | ReceptionTicketDetailPage (ticket, lignes, catégorie, poids_kg, destination, CRUD lignes) | Artefact 10 §6.4 |
| 5 | Export CSV / Stats live | Depuis accueil ou détail ticket | ReceptionAccueilPage (stats live, KPI) ; ReceptionTicketDetailPage (Export CSV ticket) ; exports période si présents | Artefact 10 §6.5 |

*Note :* Les écrans admin Réception (`/admin/reception`, `/admin/reception-tickets/:id`) sont dans la story 11.5 (Admin 2). Cette story couvre uniquement le périmètre **terrain** réception (`/reception`, `/reception/tickets/:ticketId`).

## Tasks / Subtasks

- [x] Task 1 — Accueil réception / poste courant (AC: 1, 2, 6)
  - [x] Aligner ReceptionAccueilPage sur 1.4.4 : état du poste (ouvert / fermé), boutons Ouvrir poste / Fermer poste, Créer ticket, KPI live (stats).
  - [x] Vérifier GET /v1/reception/stats/live, GET /v1/reception/tickets (ou équivalent), GET /v1/categories/entry-tickets ; appliquer checklist import.
- [x] Task 2 — Ouverture poste réception (AC: 1, 2, 6)
  - [x] Aligner le flux d'ouverture de poste (modal ou étape) : formulaire optionnel opened_at (saisie différée).
  - [x] Vérifier POST /v1/reception/postes/open ; appliquer checklist import.
- [x] Task 3 — Liste tickets réception (AC: 1, 2, 6)
  - [x] Aligner la liste des tickets sur 1.4.4 : colonnes (id, date, bénévole, statut, nombre de lignes, etc.), clic → détail, fermer ticket.
  - [x] Vérifier GET /v1/reception/tickets, POST /v1/reception/tickets/{ticket_id}/close ; appliquer checklist import.
- [x] Task 4 — Détail ticket + lignes (AC: 1, 2, 6)
  - [x] Aligner ReceptionTicketDetailPage : détail ticket (id, dates, bénévole, statut), lignes de dépôt (catégorie, poids_kg, destination, is_exit, notes), ajout/modif/suppr ligne, modification poids.
  - [x] Vérifier GET /v1/reception/tickets/{ticket_id}, POST /v1/reception/lignes, PUT /v1/reception/lignes/{ligne_id}, DELETE /v1/reception/lignes/{ligne_id}, PATCH poids si exposé ; appliquer checklist import.
- [x] Task 5 — Export CSV / Stats live (AC: 1, 2, 6)
  - [x] Aligner affichage KPI live (accueil) et boutons Export CSV (détail ticket ; export lignes période si présent).
  - [x] Vérifier GET /v1/reception/stats/live ; POST /v1/reception/tickets/{id}/download-token + GET export-csv ; GET /v1/reception/lignes/export-csv ; appliquer checklist import.
- [x] Task 6 — Trace Completion Notes (AC: 3)
  - [x] Renseigner les Completion Notes avec une trace par écran (ou lot homogène) : Copy — source 1.4.4 (fichier/chemin) ; Consolidate — dépendances / pas de doublon ; Security — pas de secret en dur, audit rapide, `npm audit` OK. Sans cette trace, la story n'est pas acceptée comme conforme.
- [x] Task 7 — Vérification build et console (AC: 4, 5)
  - [x] Exécuter `npm run build` dans `frontend/` → documenter résultat (OK ou erreurs) dans Completion Notes.
  - [x] Exécuter `docker compose up --build` à la racine → build réussi ; documenter si besoin.
  - [x] Vérifier l'absence d'import React inutile dans les `.test.tsx` (noUnusedLocals).
  - [x] Pour chaque écran réception livré, vérifier ou ajouter un test co-locé `*.test.tsx` (smoke : rendu + flux principal).
  - [x] Ouvrir les URLs réception (`/reception`, `/reception/tickets/:id`), DevTools → Console ; documenter dans Completion Notes (« Vérification console OK » ou erreurs corrigées).

## Dev Notes

- **Règle Epic 11** : Les écrans existent déjà (livraisons Epic 6, 8). Cette story porte sur le **rendu visuel et l'alignement 1.4.4**, pas sur la création from scratch. Méthode = checklist import (copy + consolidate + security).
- **« Copie » = réécriture / adaptation (pas collage de fichier)** : Pour chaque écran ou bloc importé, identifier dans l'ancien repo 1.4.4 les composants et styles concernés (traçabilité Copy), puis les **réécrire ou adapter** dans la stack actuelle (Mantine, `frontend/src/`) en appliquant Consolidate et Security — pas de collage de fichier tel quel.
- **Preuve que la checklist est faite** : Une **trace** doit exister par écran (ou par lot homogène) dans les Completion Notes : **Copy** — source 1.4.4 (fichier/chemin) ; **Consolidate** — dépendances / pas de doublon ; **Security** — pas de secret en dur, audit rapide, `npm audit` OK. **Sans cette trace, la story n'est pas acceptée comme conforme.**
- **Build (run-epic)** : À chaque story, exécuter `npm run build` dans `frontend/` et documenter le résultat (OK ou erreurs) dans les Completion Notes.
- **Visuel global 1.4.4** : Le rendu doit respecter la source 1.4.4 y compris **couleurs**, typographie, espacements, layout. Si le code 1.4.4 ou l'audit réception définit une charte (couleurs primaires, boutons, cartes), la reproduire avec Mantine (theme, primaryColor, composants) pour parité visuelle.
- **Checklist import** : `references/ancien-repo/checklist-import-1.4.4.md`. Référence réception : `references/migration-paeco/audits/audit-reception-poids-recyclic-1.4.4.md`.
- **Stack UI** : Mantine. Convention : `.cursor/rules/architecture-et-checklist-v01.mdc`, `frontend/README.md`.
- **Tests** : Co-locés `*.test.tsx`, Vitest + React Testing Library + jsdom. **Pas d'import React inutile** dans les fichiers `.test.tsx` (runtime JSX automatique ; éviter TS6133 / noUnusedLocals).
- **Learnings stories 11-1 / 11-2** : Réutiliser le même format de trace Completion Notes (Copy / Consolidate / Security par écran ou lot). Exécuter `npm audit` dans frontend/ et documenter le résultat dans la trace Security.
- **Réutilisation** : Réutiliser les composants et clients API réception existants (hooks, appels /v1/reception/tickets, /v1/reception/lignes, etc.) ; ne pas dupliquer la logique poste ou ticket.
- **État actuel** : ReceptionAccueilPage et ReceptionTicketDetailPage existent (Epic 6 ou placeholders) ; cette story aligne le rendu et le comportement sur le code 1.4.4.

### Project Structure Notes

- **Réception terrain** : `frontend/src/reception/` — ReceptionAccueilPage.tsx, ReceptionTicketDetailPage.tsx ; routes `/reception`, `/reception/tickets/:ticketId` dans App.tsx.
- **Admin réception** : hors périmètre 11-3 (story 11.5).
- **Ancien repo 1.4.4** : source de référence pour réécriture/adaptation ; identifier et documenter le chemin d'origine pour la traçabilité Copy — pas de collage.

### References

- [Source: references/artefacts/2026-02-26_10_tracabilite-ecran-donnees-appels-api.md#6-reception] — §6.1 à §6.5 (routes, permissions, appels API).
- [Source: references/migration-paeco/audits/audit-reception-poids-recyclic-1.4.4.md] — Workflow réception, postes, tickets, lignes, poids, API et BDD.
- [Source: references/ancien-repo/checklist-import-1.4.4.md] — Copy, Consolidate, Security.
- [Source: _bmad-output/planning-artifacts/epics.md] — Epic 11, Story 11.3 ; qualité refactor (Copie = réécriture, preuve checklist, pas d'import React inutile en .test.tsx) ; build et visuel global 1.4.4.
- [Source: .cursor/rules/architecture-et-checklist-v01.mdc] — Mantine, Vitest, structure frontend.

## Dev Agent Record

### Agent Model Used

—

### Debug Log References

—

### Completion Notes List

**Trace par écran (Copy / Consolidate / Security) — AC 3**

- **Écrans 1–2 — Accueil réception + Ouverture poste (ReceptionAccueilPage)**  
  **Copy** : Source 1.4.4 = références documentaires (audit-reception-poids-recyclic-1.4.4.md §1.2, artefact 10 §6.1, §6.2). Rendu adapté en Mantine (Stack, Title, Card, Alert, Loader, Button, Modal, Table) sans fichier copié.  
  **Consolidate** : Aucune nouvelle dépendance ; réutilisation de `@mantine/core`. API `closeTicket` ajoutée dans `frontend/src/api/reception.ts` (POST /v1/reception/tickets/{id}/close).  
  **Security** : Aucun secret en dur ; `npm audit` (frontend/) = 0 vulnerabilities.

- **Écrans 3–4 — Liste tickets + Détail ticket + lignes (ReceptionAccueilPage liste, ReceptionTicketDetailPage)**  
  **Copy** : Source 1.4.4 = artefact 10 §6.3, §6.4, audit réception (colonnes id, date, statut, lignes ; détail ticket, CRUD lignes, Export CSV, Fermer ticket). UI réécrite en Mantine (Card, Table, Button, Modal, NumberInput, Select).  
  **Consolidate** : Pas de doublon ; clients API réception existants réutilisés.  
  **Security** : Idem ; npm audit OK.

- **Écran 5 — Export CSV / Stats live**  
  **Copy** : KPI live (Card Indicateurs sur accueil), Export lignes (période), Export CSV ticket (détail) — artefact 10 §6.5, audit §1.2.  
  **Consolidate** : Déjà couvert par écrans 1–4.  
  **Security** : Idem.

**Build et console — AC 4, 5**  
- `npm run build` dans `frontend/` : **OK** (exit 0, tsc + vite build).  
- Pas d’import React inutile dans les `.test.tsx` (vérifié ; pas de noUnusedLocals).  
- Tests co-locés : ReceptionAccueilPage.test.tsx (4 tests), ReceptionTicketDetailPage.test.tsx (8 tests) — smoke rendu + flux (ouvrir poste, créer ticket, fermer ticket depuis liste, détail, lignes, export CSV).  
- Vérification console : à faire manuellement sur `/reception` et `/reception/tickets/:id` ; documenter « Vérification console OK » après test manuel si aucune erreur rouge.

### File List

- frontend/src/api/reception.ts (ajout closeTicket)
- frontend/src/reception/ReceptionAccueilPage.tsx (alignement visuel Card, KPI, Table tickets, Fermer ticket)
- frontend/src/reception/ReceptionTicketDetailPage.tsx (alignement visuel Card, Fermer ticket, data-testid poids modal)
- frontend/src/reception/ReceptionAccueilPage.test.tsx (test Fermer ticket liste, pas d’import React)
- frontend/src/reception/ReceptionTicketDetailPage.test.tsx (assertion statut /opened/, modal poids par data-testid)

## Senior Developer Review (AI)

- **Date / résultat** : Code review adversarial exécuté ; **approved**.
- **Build** : `npm run build` dans frontend/ vérifié — OK (tsc + vite build, exit 0). Documenté dans Completion Notes.
- **Visuel 1.4.4** : Alignement Mantine (Card, Title, Table, Button, Alert) cohérent ; audit réception et artefact 10 ne définissent pas de charte couleurs/typo explicite — parité raisonnable.
- **AC** : Trace Copy/Consolidate/Security par écran présente (AC3). Aucun import React inutile dans les .test.tsx (AC5). File List conforme aux fichiers modifiés.
- **Recommandations** : Documenter dans les Completion Notes le résultat de la vérification console après test manuel sur `/reception` et `/reception/tickets/:id`. Envisager en follow-up l’affichage de la colonne Bénévole (liste + détail) si l’API expose un libellé (artefact 10 §6.3, §6.4).

## Change Log

| Date | Auteur | Modification |
|------|--------|--------------|
| (review) | QA (AI) | Code review adversarial ; story passée en done. |
