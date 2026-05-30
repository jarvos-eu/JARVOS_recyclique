# Synthèse QA automatisée — Story 27.7 (`server-module-intersection`)

**story_key :** `27-7-server-module-intersection`  
**Date (run QA) :** 2026-05-30  
**Verdict :** **PASS**  
**qa_loop :** 0  
**Skill :** `bmad-qa-generate-e2e-tests` — intersection serveur modules × allowlist poste × permissions opérateur ; E2E Vitest jsdom (pas Playwright).

---

## Gates

| Gate | Commande | Résultat |
|------|----------|----------|
| Gate story backend | `cd recyclique/api && python -m pytest tests/ -k story_27_7 -q` | **14 passed**, exit 0 (~76 s) |
| Suite front story 27.7 (regroupée) | `vitest run` … effective-modules* + e2e 27-7 + non-régression lock 27-6 | **14 passed** (4 fichiers), exit 0 (~21 s) |
| Dont unit provider/client | `shared-workstation-effective-modules*.test.*` | **4 passed** |
| Dont E2E 27.7 | `shared-workstation-module-intersection-27-7.e2e.test.tsx` | **5 passed** |
| Non-régression lock 27.6 | `shared-workstation-pin-lock-27-6.e2e.test.tsx` | **5 passed** |
| Playwright | N/A | **Hors scope** — stack projet = Vitest + jsdom |

---

## Tests automatisés (skill workflow)

### Tests API (DS)

| Fichier | Cas | Rôle |
|---------|-----|------|
| `recyclique/api/tests/test_story_27_7_server_module_intersection.py` | 14 | Intersection OK, allowlist, permissions, config site, 403 sans session, probe 403/200, stale header 409, recalcul PATCH allowlist, enveloppe device/session, web sans device, clé invalide, audit refus sans PIN |

### Tests UI unitaires (DS)

| Fichier | Cas | Rôle |
|---------|-----|------|
| `peintre-nano/tests/unit/shared-workstation-effective-modules.test.tsx` | 3 | Fetch provider post-PIN ; filtrage nav bandeau absent/présent via `filterNavigation` |
| `peintre-nano/tests/unit/shared-workstation-effective-modules-client.test.ts` | 1 | GET effective-modules : URL, Bearer, device headers, `cache: no-store` |

### E2E Vitest — complément QA

| Fichier | Cas | Motif |
|---------|-----|-------|
| `peintre-nano/tests/e2e/shared-workstation-module-intersection-27-7.e2e.test.tsx` | 5 | Compose `App` + `VITE_LIVE_AUTH` : lock → pas de fetch effective-modules ; post-PIN → fetch no-store + device headers ; shell visible ; liste vide sans crash ; admin sans identité poste sans lock ni fetch |

---

## Grille critères d'acceptation ↔ preuves

Référence : `_bmad-output/implementation-artifacts/27-7-server-module-intersection.md` §8.

| AC / gate | Preuve |
|-----------|--------|
| Intersection triple facteur calculée serveur | pytest matrice 1–4 + service unit |
| Contrôles frontière API (probe 403) | pytest cas 6–7 |
| Front projection uniquement (pas authz depuis allowlist seule) | client unit no-store ; provider fetch ; E2E post-PIN fetch serveur |
| Refus action stale (409/403) | pytest stale header + probe |
| Recalcul après PATCH allowlist | pytest cas 8 |
| Enveloppe `effective_module_keys` | pytest cas 9–10 |
| Audit refus module sans PIN | pytest cas 12 |
| Filtrage navigation projection | unit `filterNavigation` + mapping CREOS→module_key |
| Non-régression lock screen 27.6 | E2E 27-6 inchangé PASS ; E2E 27-7 lock avant fetch |
| Admin sans identité poste | E2E 27-7 cas 5 |
| Reception brouillons / override UX / caisse généralisée | Hors scope — non testé (attendu) |

---

## Endpoints / surfaces couverts

| Surface | Couverture |
|---------|------------|
| `GET /v1/shared-workstation/effective-modules` | pytest 5 cas + client unit + E2E fetch mock |
| `GET /v1/shared-workstation/probe-module/{module_key}` | pytest 403/200 |
| `build_context_envelope` → `effective_module_keys` | pytest enveloppe device/web |
| `SharedWorkstationEffectiveModulesProvider` | unit 1 + E2E compose |
| `filterNavigation` + mapping nav | unit 2 |
| Garde `require_effective_module` | pytest probe |
| Non-régression PIN lock 27.6 | E2E 27-6 (5) |

---

## Gaps restants

Aucun gap bloquant vs AC story 27.7.

| Sujet | Statut | Note |
|-------|--------|------|
| Playwright navigateur réel | Reporté | Projet n'utilise pas Playwright |
| Masquage nav bandeau-live dans toolbar auth live | Accepté MVP | `pruneNavigationEntriesForLiveToolbar` exclut `bandeau-live-sandbox` du bandeau legacy ; filtrage module couvert en unit `filterNavigation` + pilote `kpi-live-banner` |
| `resolvePageAccess` sans check `effective_module_keys` | Accepté story | Stale UI : refus API métier (pytest probe) ; page access reste permission-based |
| Liste effective vide via fetch seul (sans champ enveloppe) | Risque documenté | `RuntimeDemoApp` n'applique le filtre module que si `envelope.effectiveModuleKeys != null` ou `fetchedModuleKeys.length > 0` — production alimentée par enveloppe + endpoint ; E2E mock enveloppe sans clé + fetch vide : shell stable, pas de crash |
| Reception pilote / override SuperAdmin | Hors scope 27.8 / 27.10 | Attendu |

---

## Checklist workflow (`bmad-qa-generate-e2e-tests` / `checklist.md`)

- [x] Tests API — exécutés avec succès (14/14 DS)
- [x] Tests E2E UI — Vitest jsdom (fetch effective-modules, lock, no-store, non-régression)
- [x] Framework standard (pytest + Vitest + Testing Library)
- [x] Happy path + erreurs critiques (403 sans session, liste vide)
- [x] Locators sémantiques / `data-testid` stables
- [x] Pas de sleep arbitraire
- [x] Résumé créé (ce fichier)
- [x] Métriques documentées

---

## Test Automation Summary (Step 5)

```markdown
# Test Automation Summary

## Generated Tests (QA worker 27.7)

### API Tests
- [x] recyclique/api/tests/test_story_27_7_server_module_intersection.py — 14 cas (DS)

### E2E Tests (Vitest jsdom)
- [x] peintre-nano/tests/e2e/shared-workstation-module-intersection-27-7.e2e.test.tsx — 5 cas (QA)

### Unit (DS)
- [x] shared-workstation-effective-modules.test.tsx — 3
- [x] shared-workstation-effective-modules-client.test.ts — 1

## Coverage
- API scénarios §8 story 27.7 : 14/14
- Surfaces UI projection + fetch serveur : 9/9 (unit + e2e)
- Non-régression lock screen 27.6 : 5/5

## Next Steps
- Story Runner parent : clôture 27.7 si CR OK
- Story 27.8 : brouillons Reception pilote
```

---

## Fichiers créés / modifiés (worker QA)

| Fichier | Action |
|---------|--------|
| `peintre-nano/tests/e2e/shared-workstation-module-intersection-27-7.e2e.test.tsx` | **Créé** — 5 cas E2E intersection modules |
| `_bmad-output/implementation-artifacts/tests/test-summary-story-27-7-server-module-intersection-qa.md` | **Créé** — synthèse QA |

`sprint-status.yaml` : **non modifié** (instruction worker).

---

## Prochaines étapes (pipeline Story Runner)

- Gate QA **PASS** (qa_loop 0) — prêt pour étape CR.
- Aucun retry DS requis.
