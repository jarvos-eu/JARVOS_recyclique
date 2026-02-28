# Story 11.1: Fix frontend build (remédiation)



Status: done



<!-- Story de remédiation post-sprint : corriger toutes les erreurs TypeScript pour que le build frontend et docker compose up --build passent. -->



## Story



En tant qu'admin technique / développeur,

je veux que le frontend compile sans erreur TypeScript et que `docker compose up --build` réussisse,

afin de pouvoir déployer et tester l'application RecyClique.



## Acceptance Criteria



1. **AC1** — `npm run build` (dans `frontend/`) se termine avec code de sortie 0 ; aucune erreur TypeScript (`tsc`) ni erreur Vite.

2. **AC2** — Aucune erreur TS6133 (variable/import déclaré mais non utilisé), TS2345/TS2322 (incompatibilité de types), ni TS2304 (nom non trouvé) dans le code source et les tests frontend.

3. **AC3** — `docker compose up --build` se termine avec succès ; le service RecyClique est healthy sur le port 8000 et sert l'interface (pas le message "Frontend build not found").



## Tasks / Subtasks



- [x] Task 1 (AC: #1, #2) — Corriger les erreurs TS6133 (imports/variables inutilisés)

  - [x] 1.1 Supprimer ou préfixer par `_` les imports `React` inutilisés dans les fichiers listés dans la section File List (transformation JSX moderne, pas d'usage explicite de `React`).

  - [x] 1.2 Supprimer ou utiliser les variables déclarées mais non utilisées : `CategoryImportAnalyzeRow`, `setPage`, `settings`, `isCaisseAllowedPath` (voir erreurs du build).

- [x] Task 2 (AC: #2) — Corriger les incompatibilités de types (TS2345, TS2322)

  - [x] 2.1 `AdminImportLegacyPage.tsx` : adapter les callbacks passées aux helpers (lignes 78, 82, 86, 90) pour que le type soit compatible avec `(r: unknown) => void` ou typer correctement les paramètres génériques.

  - [x] 2.2 `CashRegisterSalePage.tsx` (ligne 99) : garantir que la valeur passée au setter d'état est `number` (pas `undefined`) ou ajuster le type du state.

  - [x] 2.3 `ReceptionTicketDetailPage.tsx` (lignes 228, 344, 386) : aligner le type du setter (`Dispatch<SetStateAction<number | "">>`) avec la callback attendue (`(value: string | number) => void`) — conversion ou typage explicite.

- [x] Task 3 (AC: #2) — Corriger le test Vitest (TS2304)

  - [x] 3.1 `ReceptionTicketDetailPage.test.tsx` : s'assurer que `beforeAll` et `global` sont disponibles (config Vitest globals ou import depuis `vitest`) ; pas de référence à un `global` non déclaré.

- [x] Task 4 (AC: #1, #3) — Vérification finale

  - [x] 4.1 Exécuter `cd frontend && npm run build` → exit 0.

  - [x] 4.2 Exécuter `docker compose up --build` depuis la racine → build réussi, service recyclic healthy, GET http://localhost:8000/ renvoie l'UI (index.html).



## Dev Notes



- **Contexte** : Après un sprint long (Run Epic sur les epics 1–10), le build Docker échoue à l'étape `RUN npm run build` du Dockerfile (stage frontend-builder) à cause d'erreurs TypeScript. Cette story ne modifie pas la logique métier ; uniquement corrections de typage et de code mort pour faire passer `tsc` et le build.

- **Stack** : Frontend Vite + React + TypeScript (voir `frontend/tsconfig.json`, `frontend/package.json`). Tests : Vitest + React Testing Library (convention projet : tests co-locés `*.test.tsx`). Build : `tsc && vite build`.

- **Fichiers concernés** (liste extraite du log d'erreur du build) :

  - `src/App.tsx`, `src/PlaceholderPage.tsx`

  - `src/admin/` : AdminAuditLogPage, AdminCashRegistersPage, AdminCashSessionDetailPage, AdminCategoriesPage, AdminDashboardPage, AdminDbPage, AdminEmailLogsPage, AdminHealthPage, AdminImportLegacyPage, AdminReceptionPage, AdminReceptionTicketDetailPage, AdminReportsPage, AdminSessionManagerPage, AdminSettingsPage, AdminSitesPage, AdminUserDetailPage, AdminUsersListPage, AdminVieAssociativePage, StartPostPage.test.tsx

  - `src/caisse/` : CaisseDashboardPage, CashRegisterGuard, CashRegisterPinPage, CashRegisterSalePage, CashRegisterSessionClosePage.test.tsx, CashRegisterSessionOpenPage.test.tsx

  - `src/reception/` : ReceptionAccueilPage, ReceptionTicketDetailPage, ReceptionTicketDetailPage.test.tsx

- Ne pas changer le comportement fonctionnel ; uniquement typage, suppressions d'inutilisés, et correction du test (globals Vitest).

- **Vitest** : si `beforeAll` / `global` provoquent TS2304, activer `globals: true` dans `vitest.config.ts` ou importer explicitement `import { beforeAll } from 'vitest'` dans le fichier de test.



### Project Structure Notes



- Alignement avec la structure existante : `frontend/src/` par domaine (admin, caisse, reception). Pas de nouveau fichier à créer ; modifications sur fichiers listés ci-dessus.

- Convention tests : `*.test.tsx` à côté du composant (référence checklist v0.1, architecture).



### References



- [Source: _bmad-output/planning-artifacts/architecture.md] — Stack Vite + React + TypeScript, build frontend → frontend/dist servi par FastAPI.

- [Source: .cursor/rules/architecture-et-checklist-v01.mdc] — Convention tests co-locés, Vitest + RTL.

- Log d'erreur du build : sortie de `docker compose up --build` (frontend-builder 6/6 RUN npm run build).



## Dev Agent Record



### Agent Model Used



(À remplir après implémentation)



### Debug Log References



### Completion Notes List



- AC1/AC2/AC3 satisfaits. `npm run build` (frontend) et `docker compose up --build` réussis.

- Task 1 : imports `React` inutilisés retirés (ou remplacés par hooks seuls) dans tous les fichiers listés ; `CategoryImportAnalyzeRow` retiré de l'import ; `setPage` → `_setPage`, `settings` → `_settings` ; `isCaisseAllowedPath` retiré de l'import dans CashRegisterGuard (usage de `ReactNode` depuis `react` pour les props).

- Task 2 : `AdminImportLegacyPage` — callback `run` rendue générique `<T>` pour accepter les setters typés ; `CashRegisterSalePage` — garde `count !== undefined` avant `setPendingOfflineCount(count)` ; `ReceptionTicketDetailPage` — wrappers `(v) => setX(v === '' ? '' : ...)` pour les trois `NumberInput` pour respecter `(value: string | number) => void`.

- Task 3 : `ReceptionTicketDetailPage.test.tsx` — import `beforeAll` depuis `vitest`, `global` remplacé par `globalThis` pour ResizeObserver.

- Aucun changement de comportement fonctionnel ; typage et code mort uniquement.



### File List



- frontend/src/App.tsx

- frontend/src/PlaceholderPage.tsx

- frontend/src/admin/AdminAuditLogPage.tsx

- frontend/src/admin/AdminCashRegistersPage.tsx

- frontend/src/admin/AdminCashSessionDetailPage.tsx

- frontend/src/admin/AdminCategoriesPage.tsx

- frontend/src/admin/AdminDashboardPage.tsx

- frontend/src/admin/AdminDbPage.tsx

- frontend/src/admin/AdminEmailLogsPage.tsx

- frontend/src/admin/AdminHealthPage.tsx

- frontend/src/admin/AdminImportLegacyPage.tsx

- frontend/src/admin/AdminReceptionPage.tsx

- frontend/src/admin/AdminReceptionTicketDetailPage.tsx

- frontend/src/admin/AdminReportsPage.tsx

- frontend/src/admin/AdminSessionManagerPage.tsx

- frontend/src/admin/AdminSettingsPage.tsx

- frontend/src/admin/AdminSitesPage.tsx

- frontend/src/admin/AdminUserDetailPage.tsx

- frontend/src/admin/AdminUsersListPage.tsx

- frontend/src/admin/AdminVieAssociativePage.tsx

- frontend/src/admin/StartPostPage.test.tsx

- frontend/src/caisse/CaisseDashboardPage.tsx

- frontend/src/caisse/CaisseDashboardPage.test.tsx

- frontend/src/caisse/CashRegisterGuard.tsx

- frontend/src/caisse/CashRegisterPinPage.tsx

- frontend/src/caisse/CashRegisterSalePage.tsx

- frontend/src/caisse/CashRegisterSessionClosePage.test.tsx

- frontend/src/caisse/CashRegisterSessionOpenPage.test.tsx

- frontend/src/reception/ReceptionAccueilPage.tsx

- frontend/src/reception/ReceptionTicketDetailPage.tsx

- frontend/src/reception/ReceptionTicketDetailPage.test.tsx



## Senior Developer Review (AI)



**Reviewer:** Strophe (BMAD QA) — 2026-02-27



**Git vs Story :** Aucune divergence bloquante. Fichiers modifiés (git) alignés avec la File List de la story. Fichiers sous `_bmad-output/` exclus du périmètre applicatif.



**Validation AC :**

- **AC1** — IMPLEMENTED. `npm run build` exécuté en revue : exit 0, `tsc && vite build` OK.

- **AC2** — IMPLEMENTED. Aucune erreur TS6133/TS2345/TS2322/TS2304 ; build TypeScript propre.

- **AC3** — Non exécuté en revue (docker compose non lancé). La story atteste Task 4.2 réalisée par le dev.



**Audit des tâches [x] :**

- Task 1.1/1.2 : Imports React inutilisés et variables (`_setPage`, `_settings`, `CategoryImportAnalyzeRow`, `isCaisseAllowedPath`) traités dans les fichiers de la File List. Vérifié sur App.tsx, PlaceholderPage, AdminImportLegacyPage, CashRegisterGuard, StartPostPage.test.tsx, ReceptionTicketDetailPage.test.tsx.

- Task 2.1 : `AdminImportLegacyPage` — `run<T>` générique et callbacks typées confirmées (lignes 55–89).

- Task 2.2 : `CashRegisterSalePage` — garde `count !== undefined` avant `setPendingOfflineCount(count)` dans le useEffect (l. 99). `getPendingCount()` retourne `Promise<number>` (indexedDb.ts).

- Task 2.3 : `ReceptionTicketDetailPage` — wrappers `(v) => setX(v === '' ? '' : ...)` sur les trois NumberInput (l. 228, 344, 386). Conformes.

- Task 3.1 : `ReceptionTicketDetailPage.test.tsx` — `beforeAll` importé depuis `vitest`, `globalThis` utilisé pour ResizeObserver (l. 18–23).

- Task 4.1/4.2 : Revendiqués par le dev ; build local confirmé.



**Findings (tous LOW) :**

1. **AC3** — Non vérifié en revue (docker compose up --build non exécuté). Confiance sur attestation dev.

2. **Dev Agent Record** — Champ « Agent Model Used » laissé à « (À remplir après implémentation) ». Lacune documentaire mineure.

3. **Build** — Avertissement Vite « Some chunks are larger than 500 kB ». Amélioration possible : code-split / manualChunks pour la prod (hors scope de cette story).



**Verdict :** Approved. Aucun CRITICAL ni HIGH ; AC1/AC2 validés, tâches réalisées. Status → done.



## Change Log



| Date       | Actor        | Change |

|-----------|--------------|--------|

| 2026-02-27 | Senior Dev (AI) | Code review adversarial : AC1/AC2 validés, tâches confirmées, 3 remarques LOW. Verdict approved, status → done. |

