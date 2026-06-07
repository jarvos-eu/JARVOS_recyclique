# SynthÃ¨se tests automatisÃ©s (bmad-qa-generate-e2e-tests)

**Navigation Epic 28 :** `## Story 28.5` (dernière passe QA e2e). **Epic 26 :** sections `Story 26.5` → `26.2`. Recherche IDE : `## Story 28.` / `## Story 26.` Point d'entrée catalogue : entrée **Synthèse tests (QA / bmad-qa)** dans `references/index.md`.

---

## Story 28.5 — Rétablir l'édition et la navigation sites/postes pour la beta (2026-06-07)

- **Résultat QA (bmad-qa-generate-e2e-tests) :** **PASS**
- **qa_loop :** **0**
- **tests_créés (QA worker) :** **aucun** — évaluation : couverture unit DS suffisante ; e2e optionnel non requis (voir analyse ci-dessous)
- **tests DS (validés QA) :**
  - `peintre-nano/tests/unit/admin-sites-edit-navigation-28-5.test.tsx` (3) — hub sans bandeau gris, modal édition site + PATCH, retour hub + Recharger la liste
  - `peintre-nano/tests/unit/admin-cash-registers-edit-navigation-28-5.test.tsx` (2) — modal édition poste + PATCH, retour hub + Recharger la liste
- **API pytest :** **NA** (aucun changement backend ; gates DS 100/100 cash_register/sites)

### Analyse couverture par `REV-*` / AC

| Item | Fix 28.5 | Couverture | Statut QA |
|------|----------|------------|-----------|
| REV-ADMIN-06 / AC-HUB-SIMPLIFY | Hub sans bandeau gris, boutons titre seul | unit `admin-sites-edit-navigation-28-5` (hub) | **PASS** |
| REV-ADMIN-07 / AC-SITES-EDIT, AC-SITES-BACK, AC-REFRESH-CLARITY | Modal nom/ville, retour hub, Recharger la liste | unit `admin-sites-edit-navigation-28-5` (2 scénarios) | **PASS** |
| REV-ADMIN-08 / AC-REGISTERS-EDIT, AC-REGISTERS-BACK, AC-REFRESH-CLARITY | Modal nom/emplacement/site, retour hub, Recharger la liste | unit `admin-cash-registers-edit-navigation-28-5` (2 scénarios) | **PASS** |
| AC-NON-REGRESSION | Nav CREOS sites/postes/hub | contract `navigation-transverse-served-5-1` ; e2e `navigation-transverse-5-1` (widget sites) | **PASS** (DS) |

### Décision e2e optionnel

Parcours `hub → sites → modifier → retour hub` **non ajouté** en e2e : les 5 tests unit couvrent déjà les AC widget (édition PATCH, `spaNavigateTo` mocké, testid hub). `spaNavigateTo` est un `pushState` + `popstate` trivial ; l'e2e `navigation-transverse-5-1` couvre déjà le rendu `/admin/sites` dans `App`. Un e2e RuntimeDemoApp sur `/admin/sites-and-registers` n'apporterait qu'un signal marginal vs coût de maintenance — aligné note DS et tâche story « optionnel ».

### Commande de validation (cwd `peintre-nano`, exit 0 — QA worker 2026-06-07)

```bash
cd peintre-nano
node ./node_modules/vitest/vitest.mjs run tests/unit/admin-sites-edit-navigation-28-5.test.tsx tests/unit/admin-cash-registers-edit-navigation-28-5.test.tsx
```

**Résultat :** `5 passed` (2 fichiers unit).

### Prochaines étapes

- **HITL** (Strophe) : parcours manuel hub → sites → modifier nom → retour hub → postes → modifier site rattaché — avant marquage `Validé HITL` dans `references/revision/domaines/admin.md`

---

## Story 28.4 — Débruiter les surfaces admin pilotes pour un usage humain (2026-06-07)

- **Résultat QA (bmad-qa-generate-e2e-tests) :** **PASS**
- **qa_loop :** **0**
- **tests_créés (QA worker) :**
  - `peintre-nano/tests/e2e/admin-modules-human-copy-28-4.e2e.test.tsx` — RuntimeDemoApp `/admin/modules` : copie planché, nom site, save sans ETag HTTP, bouton Recharger
  - `peintre-nano/tests/e2e/admin-health-human-copy-28-4.e2e.test.tsx` — RuntimeDemoApp `/admin/health` : « Tester les alertes », badges responsable reco, nom site, POST test-notifications
- **tests DS (déjà présents, validés QA) :**
  - `admin-modules-human-copy-28-4.test.tsx`, `admin-system-health-human-copy-28-4.test.tsx`, `admin-modules-widget.test.tsx`, `admin-system-health-widget.test.tsx`
- **API pytest :** **NA** (gates DS déjà passés : 328 pytest admin/module/health)

### Analyse couverture par `REV-*` / AC

| Item | Fix 28.4 | Couverture | Statut QA |
|------|----------|------------|-----------|
| REV-ADMIN-02 / AC-MODULES-COPY | Copie planché modules, sans jargon dev | e2e `admin-modules-human-copy-28-4` ; unit `admin-modules-human-copy-28-4`, `admin-modules-widget` | **PASS** |
| REV-ADMIN-03 / AC-MODULES-SAVE-FIX | Save sans ETag, reload config, messages FR | e2e `admin-modules-human-copy-28-4` (2 scénarios) ; unit `admin-modules-human-copy-28-4` | **PASS** |
| REV-ADMIN-05 / AC-HEALTH-COPY, AC-HEALTH-RECO | Libellé alertes, badges responsable, reco low taguées | e2e `admin-health-human-copy-28-4` ; unit `admin-system-health-human-copy-28-4`, `admin-system-health-widget` | **PASS** |
| REV-TRANSVERSE-04 / AC-MODULES-SITE-NAME | Nom site via `presentationLabels` | e2e modules + health ; unit `admin-modules-human-copy-28-4` | **PASS** |
| REV-TRANSVERSE-05 / AC-CHARTE-TRANSVERSE | 1 phrase surface, détail technique secondaire | e2e modules + health (absence jargon dev en surface) | **PASS** |
| AC-NON-REGRESSION | Flux 28.1–28.3 inchangés | hors scope QA worker (gates DS) | **PASS** (DS) |

### Commande de validation (cwd `peintre-nano`, exit 0 — QA worker 2026-06-07)

```bash
cd peintre-nano
node ./node_modules/vitest/vitest.mjs run tests/e2e/admin-modules-human-copy-28-4.e2e.test.tsx tests/e2e/admin-health-human-copy-28-4.e2e.test.tsx tests/unit/admin-modules-human-copy-28-4.test.tsx tests/unit/admin-system-health-human-copy-28-4.test.tsx tests/unit/admin-modules-widget.test.tsx tests/unit/admin-system-health-widget.test.tsx
```

**Résultat :** `22 passed` (6 fichiers : 2 e2e + 4 unit).

### Prochaines étapes

- **HITL** (Strophe) : relecture humaine Gestion modules + Santé signaux sur poste pilote — avant marquage registre revision

---

## Story 28.3 — Rendre la réception terrain exploitable en hub et poste (2026-06-07)

- **Résultat QA (bmad-qa-generate-e2e-tests) :** **PASS**
- **qa_loop :** **0**
- **tests_créés (QA worker) :**
  - `peintre-nano/tests/e2e/reception-hub-history-28-3.e2e.test.tsx` — RuntimeDemoApp `/reception` : historique hub → masqué cockpit → réapparaît après fermeture poste
  - `peintre-nano/tests/unit/reception-cockpit-resize-28-3.test.tsx` — drag poignée `reception-cockpit-resize-left` + persistance `localStorage`
- **tests DS (déjà présents, validés QA) :**
  - `reception-hub-history-28-3.test.tsx`, `reception-close-state-28-3.test.tsx`, `reception-cockpit-layout-storage-28-3.test.ts`, `reception-exit-stock-hint-28-3.test.tsx`
- **API pytest :** **NA** (aucun changement backend attendu)

### Analyse couverture par `REV-*` / AC

| Item | Fix 28.3 | Couverture | Statut QA |
|------|----------|------------|-----------|
| REV-RECEPTION-01 / AC-HUB-HISTORY | Slot CREOS `history` + garde `posteOpened` inversée | e2e `reception-hub-history-28-3` ; unit `reception-hub-history-28-3`, `reception-history-7-4` | **PASS** |
| REV-RECEPTION-03 / AC-LAYOUT-READABLE, AC-LAYOUT-RESIZE | Grille 3 colonnes + poignées + `reception-cockpit-layout-v1` | unit `reception-cockpit-layout-storage-28-3`, `reception-cockpit-resize-28-3` ; cockpit visible dans close/exit tests | **PASS** |
| REV-RECEPTION-05 / AC-CLOSE-STATE, AC-CLOSE-CLEAR | Bandeau post-clôture + CTA nouveau ticket | unit `reception-close-state-28-3` (2 scénarios) | **PASS** |
| REV-RECEPTION-06 / AC-EXIT-DISCOVERY | Hint `reception-exit-stock-hint` + raccourci `=` | unit `reception-exit-stock-hint-28-3` | **PASS** |
| AC-NON-REGRESSION | CTA Retour menu 28.2, historique 7.4 | unit `reception-return-to-menu-28-2` ; e2e `reception-pwa-exit-28-2` | **PASS** |

### Commande de validation (cwd `peintre-nano`, exit 0 — QA worker 2026-06-07)

```bash
cd peintre-nano
node ./node_modules/vitest/vitest.mjs run tests/e2e/reception-hub-history-28-3.e2e.test.tsx tests/unit/reception-hub-history-28-3.test.tsx tests/unit/reception-close-state-28-3.test.tsx tests/unit/reception-cockpit-layout-storage-28-3.test.ts tests/unit/reception-cockpit-resize-28-3.test.tsx tests/unit/reception-exit-stock-hint-28-3.test.tsx tests/unit/reception-history-7-4.test.tsx tests/unit/reception-return-to-menu-28-2.test.tsx tests/e2e/reception-pwa-exit-28-2.e2e.test.tsx
```

**Résultat :** `20 passed` (9 fichiers : 2 e2e + 7 unit).

### Prochaines étapes

- **HITL** (Strophe) : hub liste tickets, resize colonnes terrain, clôture → nouveau ticket, hint sortie stock — avant `Validé HITL` dans `references/revision/domaines/reception.md`

---

## Story 28.2 — Rétablir Mon profil, PIN self-service et sortie PWA minimale (2026-06-07)

- **Résultat QA (bmad-qa-generate-e2e-tests) :** **PASS**
- **qa_loop :** **0**
- **tests_créés (e2e) :**
  - `peintre-nano/tests/e2e/profile-menu-pin-self-service-28-2.e2e.test.tsx` — menu live → `/profil` + parcours premier PIN (`PUT /v1/users/me/pin`)
  - `peintre-nano/tests/e2e/reception-pwa-exit-28-2.e2e.test.tsx` — hub réception sans poste : `hideShellNav` + CTA `reception-return-to-menu` → `/dashboard`
- **API pytest :** **NA** (aucun changement backend attendu ; `test_pin_management.py` inchangé)

### Analyse couverture par `REV-*`

| Item | Fix 28.2 | Couverture | Statut QA |
|------|----------|------------|-----------|
| REV-TRANSVERSE-01 | Menu `Mon profil` + route `/profil` | e2e `profile-menu-pin-self-service-28-2` ; unit `live-shell-user-menu-28-2`, `runtime-demo-profile-nav-28-2` | **PASS** |
| REV-ADMIN-01 | PIN self-service `PUT /v1/users/me/pin` | e2e `profile-menu-pin-self-service-28-2` ; unit `user-self-profile-widget-28-2` | **PASS** |
| REV-RECEPTION-02 | Sortie PWA hub réception inactif | e2e `reception-pwa-exit-28-2` ; unit `reception-return-to-menu-28-2` | **PASS** |
| AC-PIN-RESET-CHAIN | Lien admin « Ouvrir mon profil » après reset sur compte courant | unit `admin-users-widget.test.tsx` (hors suffixe 28-2) | **PASS** (unit) |

### Commande de validation (cwd `peintre-nano`, exit 0 — QA worker 2026-06-07)

```bash
cd peintre-nano
node ./node_modules/vitest/vitest.mjs run tests/e2e/profile-menu-pin-self-service-28-2.e2e.test.tsx tests/e2e/reception-pwa-exit-28-2.e2e.test.tsx tests/unit/live-shell-user-menu-28-2.test.tsx tests/unit/runtime-demo-profile-nav-28-2.test.tsx tests/unit/user-self-profile-widget-28-2.test.tsx tests/unit/reception-return-to-menu-28-2.test.tsx
```

**Résultat :** `9 passed` (6 fichiers : 2 e2e + 4 unit `*28-2*`).

### Prochaines étapes

- **HITL** (Strophe) : retest menu profil live, création PIN après reset admin, sortie PWA réception installée — avant `Validé HITL` dans `references/revision/`

---

## Story 28.1 â€” Stabiliser caisse terrain P0 session / finalisation / clÃ´ture (2026-06-07)

- **RÃ©sultat QA (bmad-qa-generate-e2e-tests) :** **NEEDS_HITL**
- **tests_crÃ©Ã©s :** `peintre-nano/tests/e2e/cashflow-close-draft-purge-28-1.e2e.test.tsx` â€” non-rÃ©gression REV-02 (purge brouillon mÃ©moire + sessionStorage aprÃ¨s clÃ´ture rÃ©ussie via `CashflowCloseWizard`)
- **qa_loop :** **2** (itÃ©ration 2 â€” doc rÃ©siduels P1 ; renforcement unitaire `cashflow-finalize-eligibility.test.ts`, `caisse-session-close-reset-draft-28-1.test.tsx`)

### Analyse couverture par `REV-CAISSE-*`

| Item | Fix 28.1 | Couverture | Statut QA |
|------|----------|------------|-----------|
| REV-CAISSE-06 | `evaluateCashflowFinalizeEligibility` â€” held sans `cashSessionIdInput` | `cashflow-finalize-held-without-session-input-28-1.test.tsx`, `cashflow-finalize-eligibility.test.ts` | **PASS** |
| REV-CAISSE-05 | Motifs blocage explicites kiosque | `cashflow-kiosk-finalize-blocked-28-1.test.tsx`, `cashflow-finalize-eligibility.test.ts` | **PASS** |
| REV-CAISSE-10 | Branche held vs encaissement nominal | `cashflow-held-line-add-blocked-28-1.test.tsx` ; e2e `cashflow-held-6-3.e2e.test.tsx` | **RÃ‰GRESSION** â€” 4/4 tests held-6-3 en Ã©chec |
| REV-CAISSE-12 | `firstVirtualRegisterId` / virtuel | `cashflow-register-variants-28-1.test.ts`, `cash-register-variants-13-2.e2e.test.tsx` | **PASS** |
| REV-CAISSE-02 | `resetCashflowDraft()` aprÃ¨s clÃ´ture | `caisse-session-close-reset-draft-28-1.test.tsx`, `cashflow-close-draft-purge-28-1.e2e.test.tsx` | **PASS** |
| REV-CAISSE-01 | Reprise session / sync `cashSessionIdInput` | `caisse-brownfield-ghost-session-28-1.test.tsx`, `cash-register-hub-open-to-sale-13-6.e2e.test.tsx` | **PASS** |

### RÃ©gression bloquante (HITL dev)

`cashflow-held-6-3.e2e.test.tsx` â€” **4 failed** : `Maximum update depth exceeded` entre `KioskFinalizeSaleDock` (`setCashSessionIdInput` depuis enveloppe, L175-180) et `CashflowNominalWizard` (purge `cashSessionIdInput` si GET courant absent, L1723-1737). Conflit introduit par les syncs session 28.1.

### Tests unitaires story 28.1 (QA2 itÃ©ration 2) (vÃ©rifiÃ©s verts â€” QA worker 2026-06-07, passe 2)

```bash
cd peintre-nano
node ./node_modules/vitest/vitest.mjs run tests/unit/cashflow-finalize-eligibility.test.ts tests/unit/cashflow-finalize-held-without-session-input-28-1.test.tsx tests/unit/cashflow-register-variants-28-1.test.ts tests/unit/cashflow-draft-session-persistence.test.ts tests/unit/caisse-session-close-reset-draft-28-1.test.tsx tests/unit/caisse-brownfield-ghost-session-28-1.test.tsx tests/unit/cashflow-kiosk-finalize-blocked-28-1.test.tsx tests/unit/cashflow-held-line-add-blocked-28-1.test.tsx
```

**RÃ©sultat :** `20 passed` (8 fichiers unitaires 28-1 ; voir liste ci-dessous).

Fichiers 28-1 : `cashflow-finalize-eligibility.test.ts`, `cashflow-finalize-held-without-session-input-28-1.test.tsx`, `cashflow-register-variants-28-1.test.ts`, `cashflow-draft-session-persistence.test.ts`, `caisse-session-close-reset-draft-28-1.test.tsx`, `caisse-brownfield-ghost-session-28-1.test.tsx`, `cashflow-kiosk-finalize-blocked-28-1.test.tsx`, `cashflow-held-line-add-blocked-28-1.test.tsx`.

### E2E held liÃ© (rÃ©gression â€” Ã  corriger avant PASS global)

```bash
cd peintre-nano
node ./node_modules/vitest/vitest.mjs run tests/e2e/cashflow-held-6-3.e2e.test.tsx
```

**RÃ©sultat :** `4 failed` (boucle infinie React).

### Prochaines Ã©tapes

- **Dev** : corriger la boucle sync session (garder held encaissable sans `cashSessionIdInput` tout en Ã©vitant set/clear alternÃ© enveloppe â†” GET courant)
- Retest `held-6-3` puis HITL terrain (Strophe) avant `ValidÃ©` dans `references/revision/domaines/caisse.md`
- Suivi P1 rÃ©siduel REV-CAISSE-01 : caissier + fond de caisse non affichÃ©s (hors scope fix 28.1)

---

## Story 26.5 â€” P2 outillage : ruff, F1 repository, ADR guide tests, README (2026-04-22)

- **Story Runner (fin) :** CSâ†’VSâ†’DSâ†’GATEâ†’QAâ†’CR **APPROVE** ; story **`done`** ; **`epic-26`** **`done`** ; vs_loop=0 qa_loop=0 cr_loop=0.
- **RÃ©sultat QA :** **PASS** ; **qa_loop** : **inchangÃ©** (pas dâ€™itÃ©ration de correction sur cette passe ; gates dÃ©jÃ  verts cÃ´tÃ© DS).
- **MÃ©triques :** `6 passed` â€” gate `test_infrastructure.py` ; `ruff check src/recyclic_api` **exit 0** ; `compileall` **exit 0**.
- **Nouveaux tests automatisÃ©s :** **aucun requis** â€” pÃ©rimÃ¨tre **outillage + documentation** (pas de feature UI ni de changement de contrat API). Preuves **AC** = artefacts versionnÃ©s + gates Story Runner.
- **E2E UI / Playwright :** **NA** (inutile pour cette story ; pas de parcours utilisateur modifiÃ©).

### Preuves par AC (traces dans le dÃ©pÃ´t)

- **Ruff (ou rejet documentÃ©)** : `recyclique/api/pyproject.toml` â€” `ruff==0.9.10` dans `[project.optional-dependencies].dev`, `[tool.ruff]` (format type Black, lint E9 minimal) ; `recyclique/api/README.md` â€” install `[dev]`, commandes `ruff format` / `ruff check`, note F10 Docker.
- **Double norme repository (F1)** : `_bmad-output/planning-artifacts/architecture/index.md` (Â§ Epic 26, paragraphe repository + ruff) ; lien audit.
- **Guide stabilisation** : `_bmad-output/planning-artifacts/architecture/2026-04-22-adr-tests-stabilization-no-separate-guide-epic-26.md` (ADR Â« pas de guide sÃ©parÃ© Â») ; `recyclique/api/tests/README.md` â€” section stabilisation, lien ADR, plus dâ€™attente dâ€™un `TESTS_STABILIZATION_GUIDE.md` fantÃ´me.
- **F7â€“F11 / trace** : `epic-26-cloture-f7-f11-trace.md` mentionnÃ© dans la story 26.5 (complÃ©ment F10 / ruff).

### Commande de validation (cwd `recyclique/api`, exit 0)

```text
python -m compileall -q src/recyclic_api
python -m pytest tests/test_infrastructure.py --tb=short -q
python -m ruff check src/recyclic_api
```

---

## Story 26.4 â€” SchÃ©mas : convention PEP 604, vague 1 (`category`, `context_envelope`, `email_log`, 2026-04-22)

- **RÃ©sultat QA :** **PASS** ; **qa_loop** : **1** (ajustement assertion Pydantic `CategoryUpdate` aprÃ¨s premier run).
- **MÃ©triques :** `9 passed` â€” gate `test_infrastructure.py` (6) + smoke schÃ©mas (3).
- **Nouveaux :** `recyclique/api/tests/test_schemas_pep604_wave1_story_26_4.py` â€” instanciation Pydantic avec `... | None` explicites (`CategoryCreate` / `CategoryUpdate`, `ContextEnvelopeResponse` / `ExploitationContextIdsOut`, `EmailLogFilters` / `EmailLogResponse`). ComplÃ¨te la couverture mÃ©tier dÃ©jÃ  prÃ©sente (`test_category_*`, `test_openapi_validation` / `test_context_envelope`, `test_email_logs_endpoint` / `test_email_log_service`) sans dupliquer les parcours HTTP.
- **E2E UI :** **NA** (refactor typage schÃ©mas uniquement ; pas de changement produit).
- **ContrÃ´le statique :** aucun `Optional[` rÃ©siduel dans les trois fichiers de la vague 1.

### Commande de validation (cwd `recyclique/api`, exit 0)

```text
python -m compileall -q src/recyclic_api
python -m pytest tests/test_infrastructure.py tests/test_schemas_pep604_wave1_story_26_4.py -q --tb=short
```

### Couverture visÃ©e (AC story 26.4)

- MÃªme sÃ©mantique optionnel/requis sur les modÃ¨les touchÃ©s aprÃ¨s migration **`T | None`**.
- Gates parent Story Runner : **compileall** + **`test_infrastructure`** verts ; smoke schÃ©mas verrouille la vague 1 hors rÃ©gression Pydantic silencieuse.

---

## Story 26.3 â€” Normaliser async vs ORM sync (pilote categories, API pytest, 2026-04-22)

- **RÃ©sultat QA :** **PASS** ; `qa_loop` : **0** (peloton + gate vert sans nouveau test requis).
- **MÃ©triques :** `151 passed` (peloton categories + `test_infrastructure.py`, alignÃ© Dev Agent Record).
- **Nouveaux :** **aucun** â€” pas de **gap bloquant** : les chemins critiques `CategoryService` / `CategoryManagementService` / routes `def` restent couverts par `test_category_*` (arch03, b48) et `test_categories_endpoint.py` ; lâ€™exception **Option B** `async def` sur **`POST /v1/categories/import/analyze`** (`await file.read()`) est dÃ©jÃ  exercÃ©e par `test_categories_import.py` et `test_category_import_price_logic.py` (appels `admin_client.post(..., files=...)`).
- **E2E UI :** **NA** (API uniquement).

### Commande de validation (cwd `recyclique/api`, exit 0)

```text
python -m compileall src/recyclic_api -q
python -m pytest tests/api/test_categories_endpoint.py tests/test_category_create_arch03.py tests/test_category_update_arch03.py tests/test_category_soft_delete_arch03.py tests/test_category_soft_delete_b48_p1.py tests/test_category_restore_arch03.py tests/test_category_hard_delete_arch03.py tests/test_category_management_arch03.py tests/test_category_export.py tests/test_category_import_price_logic.py tests/test_categories_import.py tests/test_category_display_name_b48_p5.py tests/test_category_price_removal.py tests/test_integration_category_migration.py tests/test_sales_stats_by_category.py tests/test_infrastructure.py --tb=short -q
```

### Couverture visÃ©e (AC story 26.3)

- MÃªme contrat HTTP / corps sur scÃ©narios couverts â€” **non-rÃ©gression** aprÃ¨s passage routes/services en **`def`** + ORM synchrone.
- Route async documentÃ©e (import analyze) : **comportement API inchangÃ©** vÃ©rifiÃ© par tests import existants.

---

## Story 26.2 â€” Extraire `admin_users_groups` vers un service (API + service pytest, 2026-04-22)

- **RÃ©sultat QA :** **PASS** ; **qa_loop** : **0** (premier run vert aprÃ¨s ajout tests service).
- **MÃ©triques :** 34 passed (gate + `test_admin_user_groups_assignment_service` : 5 tests).
- **Nouveaux / renforcÃ© :** `recyclique/api/tests/test_admin_user_groups_assignment_service.py` â€” appels directs Ã  `update_user_groups_assignment` (happy path, `UserNotFoundForAssignment` Ã—2, `InvalidGroupIdForAssignment`, `GroupNotFoundForAssignment`). Lâ€™existant `test_user_groups.py`, `TestAdminUsersGroupsContract`, `test_admin_users_groups_routes.py` couvre dÃ©jÃ  lâ€™API ; les tests service ferment la boucle F4 (rÃ©gression sur le module extrait).
- **E2E UI :** **NA** (API uniquement).

### Commande de validation (cwd `recyclique/api`, exit 0)

```bash
python -m pytest tests/test_infrastructure.py tests/test_user_groups.py tests/api/test_admin_user_management.py tests/test_admin_users_groups_routes.py tests/test_groups_and_permissions.py::TestAdminUsersGroupsContract tests/test_admin_user_groups_assignment_service.py --tb=short -q
```

### Couverture visÃ©e (AC story)

- DÃ©lÃ©gation endpoint â†’ `admin_user_groups_assignment_service` : comportement transactionnel + exceptions mÃ©tiers alignÃ©s sur les rÃ©ponses HTTP existantes.
- Non-rÃ©gression `PUT /v1/admin/users/{id}/groups` (gates listÃ©s + contract).

---

## Story 25.15 â€” Spike faisabilitÃ© IndexedDB / cache local sans PWA (documentaire, 2026-04-20)

- **SynthÃ¨se QA :** [`test-summary-story-25-15-spike-indexeddb-cache-local-sans-pwa.md`](test-summary-story-25-15-spike-indexeddb-cache-local-sans-pwa.md) â€” **PASS** ; gate pytest `test_story_25_15_spike_faisabilite_indexeddb_cache_local_sans_pwa.py` (`14 passed`) ; rapport `_bmad-output/implementation-artifacts/2026-04-20-spike-25-15-indexeddb-cache-local-faisabilite.md`. E2E navigateur / IndexedDB en CI : **SKIP** (spike doc uniquement ; pas dâ€™UI livrÃ©e ; contrainte Â« pas dâ€™IDB navigateur obligatoire en CI Â»).

---

## Story 25.14 â€” Step-up / revalidation aprÃ¨s contexte sensible (API pytest, 2026-04-20)

- **SynthÃ¨se QA :** [`test-summary-story-25-14-step-up-revalidation-contexte-sensible.md`](test-summary-story-25-14-step-up-revalidation-contexte-sensible.md) â€” **PASS** ; `5 passed` sur `test_story_25_14_step_up_revalidation_apres_changement_contexte_sensible.py` ; complÃ©ment **session caisse** stale + PIN ; E2E navigateur **NA** (matrice). **qa_loop** inchangÃ©.
- **Alignement :** matrice `_bmad-output/implementation-artifacts/2026-04-20-matrice-step-up-revalidation-contexte-sensible-25-14.md` ; ADR 25-2 / ordre 25.8 â†’ step-up.

---

## Story 25.13 â€” Journalisation identitÃ© opÃ©rateur vs poste / kiosque (API / logs, 2026-04-20)

- **SynthÃ¨se QA :** [`test-summary-story-25-13-journalisation-identite-operateur-poste-kiosque.md`](test-summary-story-25-13-journalisation-identite-operateur-poste-kiosque.md) â€” **PASS** ; pytest `test_sale_path_distinguishes_operator_from_register_in_logs_and_audit` ; E2E navigateur **NA** (logs structurÃ©s + audit). **RevalidÃ©** `bmad-qa-generate-e2e-tests` (Task), 2026-04-20.
- **Alignement :** spec 25.4 Â§2.4 / ADR 25-2 (distinction champs opÃ©rateur vs caisse).

---

## Story 25.4 â€” Spec socle multisite / permissions / projection Paheko (documentaire, 2026-04-20)

- **SynthÃ¨se QA :** [`test-summary-story-25-4-doc-qa.md`](test-summary-story-25-4-doc-qa.md) â€” **PASS** ; pas de tests API/E2E (NA) ; conformitÃ© statique spec â†” `epics.md` Â§25.4 ; citations Â§1.1 et index architecture vÃ©rifiÃ©s.
- **Spec :** `_bmad-output/planning-artifacts/architecture/2026-04-20-spec-socle-multisite-permissions-invariants-poste-kiosque-projection-recyclique-paheko.md`

---

## Story 25.2 â€” ADR PIN kiosque (documentaire, 2026-04-19)

- **SynthÃ¨se QA :** [`test-summary-story-25-2-doc-qa.md`](test-summary-story-25-2-doc-qa.md) â€” **PASS** ; pas de tests API/E2E (NA) ; conformitÃ© statique ADR â†” `epics.md` Â§25.2.
- **ADR :** `_bmad-output/planning-artifacts/architecture/2026-04-19-adr-pin-kiosque-vs-pin-operateur-secret-poste-step-up-lockout-offline.md`

---

## Tests gÃ©nÃ©rÃ©s / Ã©tendus

### E2E (Vitest + Testing Library)

- [x] `peintre-nano/tests/e2e/cashflow-refund-24-4-prior-year-expert.e2e.test.tsx` â€” Story 24.4 : hub carte expert N-1, visibilitÃ© proactive GET `prior_closed`, permission `accounting.prior_year_refund`, happy path POST `expert_prior_year_refund`.

### Tests unitaires (dÃ©jÃ  livrÃ©s DS)

- `peintre-nano/tests/unit/cashflow-refund-24-4-prior-year-ux.test.tsx` â€” wizard isolÃ© (non relancÃ© dans cette passe si inchangÃ©).

## Commande de validation

```bash
cd peintre-nano
node ./node_modules/vitest/vitest.mjs run tests/e2e/cashflow-refund-24-4-prior-year-expert.e2e.test.tsx
```

## Couverture visÃ©e (AC story)

- VisibilitÃ© parcours expert N-1 avant validation finale (hub + encart wizard).
- Permission : blocage bouton sans droit ; libellÃ© `accounting.prior_year_refund` sur la carte hub.
- Happy path : confirmation case + POST avec flag expert.

## Prochaines Ã©tapes

- IntÃ©grer le fichier dans la CI avec les autres e2e caisse si besoin.

---

## Story 24.10 P3 (session BMAD QA e2e, 2026-04-19)

### E2E (Vitest + Testing Library)

- [x] `peintre-nano/tests/e2e/cashflow-special-ops-hub-24-10-p3.e2e.test.tsx` â€” hub : copy P3 (`operations_specials_p3`, `approval_evidence_ref`, mention journal d'audit / opÃ©rations sensibles) ; navigation vers `/caisse/remboursement-exceptionnel` + wizard ; garde permission sans `refund.exceptional`.

### API (pytest, couverture rÃ¨gles P3 / seuil / preuve)

- [x] `recyclique/api/tests/test_story_24_10_operations_specials_p3.py` â€” manque preuve 422, happy path avec preuve, rejet seuil 150â‚¬ + `ERREUR_SAISIE`, P2 sans flag, validation unitaire service.

### Hors pÃ©rimÃ¨tre e2e (justification)

- **`GET /v1/admin/audit-log?cash_sensitive_operations=true`** : le widget `AdminAuditLogWidget` nâ€™expose pas le filtre `cash_sensitive_operations` dans lâ€™UI (requÃªte sans ce paramÃ¨tre) â€” la preuve filtre sensible reste cÃ´tÃ© API / tests backend si ajoutÃ©s.
- **Champs corps P3 (`approval_evidence_ref`) sur le wizard** : le formulaire `CashflowExceptionalRefundWizard` nâ€™envoie pas encore ce champ ; les rÃ¨gles mÃ©tier P3 sont couvertes par les tests pytest sur `POST .../exceptional-refunds`.

### Commande de validation

```bash
cd peintre-nano
node ./node_modules/vitest/vitest.mjs run tests/e2e/cashflow-special-ops-hub-24-10-p3.e2e.test.tsx
```

```bash
cd recyclique/api
python -m pytest tests/test_story_24_10_operations_specials_p3.py -q
```
