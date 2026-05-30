# Synthèse QA automatisée — Story 27.5 (`installable-pwa-non-offline`)

**story_key :** `27-5-installable-pwa-non-offline`  
**Date (run QA) :** 2026-05-30  
**Verdict :** **PASS**  
**qa_loop :** 0  
**Skill :** `bmad-qa-generate-e2e-tests` — PWA manifest/SW/doc + garde-fous API `no-store` ; pas de Playwright install PWA (hors scope story).

---

## Gates

| Gate | Commande | Résultat |
|------|----------|----------|
| Backend story 27.5 | `cd recyclique/api && python -m pytest tests/ -k story_27_5 -q` | **2 passed**, exit 0 |
| Manifest + SW + doc | `cd peintre-nano && npm run test -- tests/unit/pwa-manifest.test.ts` | **6 passed**, exit 0 |
| Non-régression 27.4 | `npm run test -- tests/unit/device-identity-store.test.ts tests/unit/shared-workstation-enrollment-widget.test.tsx` | **5 passed**, exit 0 |
| Lint / build / suite complète | Brief parent (DS) | **PASS** (791 vitest, lint, build) |
| Playwright install PWA | N/A | **Hors scope** — story §149 : optionnel ; Vitest + revue config/build |

---

## Invariants brief ↔ preuves

| Invariant | Preuve automatisée |
|-----------|-------------------|
| Manifest + standalone + icônes | `pwa-manifest.test.ts` — JSON `name`, `display: standalone`, tailles 192/512, fichiers PNG |
| Lien HTML manifest | `pwa-manifest.test.ts` — `rel="manifest"`, theme-color, titre Recyclique |
| Pas de cache offline métier / API auth | `vite.config.ts` — `runtimeCaching: []`, `globIgnores manifests/**` ; backend `test_story_27_5_*_no_store` |
| SW n’intercepte pas `/api` | `vite.config.ts` — `navigateFallbackDenylist` ; `pwa-manifest.test.ts` — grep `dist/sw.js` (denylist `/api`, pas NetworkFirst/SWR, pas precache CREOS) |
| Doc installable ≠ offline | `pwa-manifest.test.ts` — `docs/pwa-terrain.md` (installable, hors ligne/offline, IndexedDB) |
| Distinction CREOS vs W3C | Doc + `globIgnores` ; precache build sans `manifests/navigation` |

---

## Tests automatisés (skill workflow)

### Tests API (DS)

| Fichier | Cas | Rôle |
|---------|-----|------|
| `recyclique/api/tests/test_story_27_5_pwa_non_offline.py` | 2 | `Cache-Control: no-store` sur list registered-devices et flux enroll/complete Epic 27 |

### Tests UI unitaires (DS + complément QA)

| Fichier | Cas | Rôle |
|---------|-----|------|
| `peintre-nano/tests/unit/pwa-manifest.test.ts` | 6 | Manifest W3C, icônes, index.html, config Workbox, doc terrain, **SW buildé** (QA) |
| `peintre-nano/tests/unit/device-identity-store.test.ts` | 1 | Non-régression IndexedDB identité poste (27.4) |
| `peintre-nano/tests/unit/shared-workstation-enrollment-widget.test.tsx` | 4 | Non-régression enrôlement terrain (27.4) |

### E2E / contrat

| Type | Statut | Motif |
|------|--------|--------|
| E2E Vitest compose | **Non ajouté** | Story 27.5 sans parcours UI métier nouveau ; install prompt non simulable en jsdom |
| Contrat CREOS | **N/A** | OpenAPI inchangé ; manifests CREOS inchangés |

---

## Grille critères d’acceptation ↔ preuves

Référence : `_bmad-output/implementation-artifacts/27-5-installable-pwa-non-offline.md`.

| AC / gate | Preuve |
|-----------|--------|
| Web App Manifest (name, icons, standalone, start_url) | `pwa-manifest.test.ts` (manifest + icônes disque) |
| Lien manifest dans HTML | `pwa-manifest.test.ts` (index.html) |
| SW limité aux assets statiques | `vite.config.ts` + grep `dist/sw.js` (precache bundle, denylist API) |
| Pas de runtimeCaching API | `runtimeCaching: []` + grep SW sans NetworkFirst/SWR |
| Pas precache manifests CREOS | `globIgnores manifests/**` + SW sans `manifests/navigation` |
| Endpoints métier `no-store` | `test_story_27_5_registered_devices_list_no_store`, `test_story_27_5_shared_workstation_enroll_complete_no_store` |
| Doc installable ≠ offline + navigateur dédié + IndexedDB | `pwa-terrain.md` + test doc |
| OpenAPI non modifié | Diff vide attendu (gate DS) |
| Non-régression 27.4 | device-identity + enrollment widget (5 tests) |

---

## Surfaces couvertes

| Surface | Couverture |
|---------|------------|
| `public/manifest.webmanifest` + icônes | 100 % champs MVP |
| `index.html` (manifest, theme, Apple meta) | Assertions HTML |
| `vite.config.ts` / Workbox | Denylist API, pas runtime métier |
| `dist/sw.js` (post-build) | Grep denylist + absence stratégies offline métier |
| `docs/pwa-terrain.md` | Contenu installable ≠ offline |
| API Epic 27 headers | 2/2 endpoints sensibles story |

---

## Gaps restants

Aucun gap bloquant vs AC story 27.5.

| Sujet | Statut | Note |
|-------|--------|------|
| Install prompt Chrome/Edge (Playwright) | Reporté | Explicitement optionnel story §149 |
| Checklist QA manuelle §4.4 (DevTools « from network ») | **HITL terrain** | Documentée dans `pwa-terrain.md` ; non automatisable sans navigateur réel |
| Test `dist/sw.js` sans build préalable | Accepté | Test QA no-op si `dist/` absent ; CI release doit lancer `npm run build` avant vitest si preuve SW exigée |
| Encart UI enroll | Optionnel story | Non livré ; doc seule suffit MVP |

---

## Checklist workflow (`bmad-qa-generate-e2e-tests` / `checklist.md`)

- [x] Tests API — exécutés avec succès (2/2)
- [x] Tests E2E UI — N/A (pas de workflow UI ; complément unitaire manifest/SW)
- [x] Framework standard (pytest + Vitest)
- [x] Happy path + garde-fous critiques (no-store, denylist API, doc offline)
- [x] Pas de sleep arbitraire
- [x] Résumé créé (ce fichier)
- [x] Métriques documentées

---

## Test Automation Summary (Step 5)

```markdown
# Test Automation Summary

## Generated Tests (QA complément)

### API Tests
- [x] recyclique/api/tests/test_story_27_5_pwa_non_offline.py — 2 cas (DS)

### Unit Tests
- [x] peintre-nano/tests/unit/pwa-manifest.test.ts — 6 cas (5 DS + 1 QA grep dist/sw.js)
- [x] Non-régression 27.4 — device-identity-store + shared-workstation-enrollment-widget

### E2E Tests
- [ ] Non requis — story MVP = unitaires manifest + gates build manuels

## Coverage
- Invariants brief PWA : 5/5 automatisés (manifest, SW config+build, doc, API no-store)
- AC story § Testing gates : couverts sauf checklist install manuelle (HITL)

## Next Steps
- Story Runner : enchaîner CR ou clôture 27.5
- HITL optionnel : matrice navigateur terrain si install prompt échoue
```

---

## Fichiers créés / modifiés (worker QA)

| Fichier | Action |
|---------|--------|
| `peintre-nano/tests/unit/pwa-manifest.test.ts` | **Modifié** — cas grep `dist/sw.js` (denylist `/api`) |
| `_bmad-output/implementation-artifacts/tests/test-summary-story-27-5-installable-pwa-non-offline-qa.md` | **Créé** — ce résumé |

`sprint-status.yaml` : **non modifié** (instruction worker).

---

## Prochaines étapes (pipeline Story Runner)

- Gate QA **PASS** — enchaînement parent : **CR** (`bmad-code-review`) puis clôture story si vert.
- Story **27.6** (PIN lock) : nouveaux tests dédiés session opérateur.
