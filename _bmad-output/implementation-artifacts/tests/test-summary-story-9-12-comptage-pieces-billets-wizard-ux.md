# Test Automation Summary — Story 9.12

**Date :** 2026-06-06  
**Story :** `9-12-comptage-pieces-billets-wizard-ux-relecture`  
**Agent :** QA (bmad-qa-generate-e2e-tests) · qa_loop retry (post CR + fix TS)  
**Dernière exécution :** 2026-06-06 17:43 (Vitest 3.2.4, 44.3 s)  
**Périmètre :** Peintre-nano — extension `CashflowCloseWizard` module `comptage-pieces-billets`

## Generated Tests

### Unit Tests
- [x] `peintre-nano/tests/unit/cashflow-close-6-7.test.tsx` — non-régression legacy 6.7 (7 tests)
- [x] `peintre-nano/tests/unit/cashflow-close-denomination-9-12.test.tsx` — grille, règles, navigation séquentielle (saut d'étapes bloqué), relecture D-CPT-05, reset relecture stale (retour grille / qty modifiée), show_images D-CPT-06, alertes PIN D33/500 €, PDF, COMPTAGE_REQUIRED (12 tests)

### E2E Tests
- [x] `peintre-nano/tests/e2e/cashflow-close-6-7.e2e.test.tsx` — parcours legacy step-up + erreurs (3 tests)
- [x] `peintre-nano/tests/e2e/cashflow-close-denomination-9-12.e2e.test.tsx` — parcours module on complet, relecture obligatoire (PIN tab disabled), PDF anomalie, COMPTAGE_REQUIRED (4 tests)

### Contract Tests
- [x] `peintre-nano/tests/contract/creos-cashflow-close-manifests-9-12.test.ts` — operation_id CREOS / OpenAPI (3 tests)

## Commandes exécutées

```bash
cd peintre-nano
npm run test -- tests/unit/cashflow-close-6-7.test.tsx tests/unit/cashflow-close-denomination-9-12.test.tsx tests/e2e/cashflow-close-6-7.e2e.test.tsx tests/e2e/cashflow-close-denomination-9-12.e2e.test.tsx tests/contract/creos-cashflow-close-manifests-9-12.test.ts
```

## Résultat

| Suite | Tests | Statut |
|-------|-------|--------|
| `cashflow-close-6-7.test.tsx` | 7 | PASS |
| `cashflow-close-denomination-9-12.test.tsx` | 12 | PASS |
| `cashflow-close-6-7.e2e.test.tsx` | 3 | PASS |
| `cashflow-close-denomination-9-12.e2e.test.tsx` | 4 | PASS |
| `creos-cashflow-close-manifests-9-12.test.ts` | 3 | PASS |

**Total : 29 tests PASS**

## Coverage (AC 9.12 — AC critiques vérifiés)

| AC | Couvert par | Statut QA |
|----|-------------|-----------|
| 1 Legacy module off | unit 9-12 parité 404 `actual_amount` | PASS |
| 2–7 Grille / vérif / PUT | unit + e2e 9-12 parcours complet | PASS |
| 4 Coupures rares 500 € | unit + e2e 9-12 (main vs rare section) | PASS |
| 5 Pas `actual_amount` module on | unit + e2e 9-12 | PASS |
| 9 Relecture obligatoire D-CPT-05 | unit (PIN tab disabled, reset relecture) + e2e | PASS |
| 11 Pictos `show_images` D-CPT-06 | unit `show_images true/false` (AC11) | PASS |
| 12 PDF anomalie | unit + e2e 9-12 | PASS |
| 13 Copy 6.9 | unit + e2e 9-12 relay Recyclique | PASS |
| 15 CREOS operation_id | contract 9-12 | PASS |
| 16 COMPTAGE_REQUIRED | unit + e2e 9-12 | PASS |
| 17 Tests Vitest | toutes suites ci-dessus | PASS |

### AC critiques brief (vérification explicite)

- **Navigation séquentielle (CR)** : unit `bloque le saut d'étapes` — onglet « 3. Vérifier » disabled sans continuer depuis la grille.
- **Relecture stale (CR)** : unit `réinitialise la relecture confirmée au retour grille après PIN` + `réinitialise la relecture si quantités modifiées après confirmation` — PIN tab re-disabled.
- **D-CPT-05 relecture** : unit + e2e `relecture obligatoire` — onglet PIN désactivé sans « J'ai relu » ; reset si retour grille ou qty modifiée.
- **D-CPT-06 pictos (CR show_images)** : unit `show_images true/false` — `cashflow-denom-picto-*` présent si `show_images: true`, absent si `false`.
- **Legacy module off** : `actual_amount` conservé, pas de grille.
- **Grille module on** : 7 étapes, PUT denomination-count, pas de saisie montant global.

## Checklist Quinn

- [x] E2E tests générés (UI wizard)
- [x] Tests framework Vitest + Testing Library
- [x] Happy path + erreurs critiques (COMPTAGE_REQUIRED, PDF anomalie)
- [x] Tous les tests passent (29/29)
- [x] Locators sémantiques (`data-testid`, roles)
- [x] Pas de sleeps hardcodés
- [x] Tests indépendants
- [x] Test summary à jour

## Next Steps

- Intégrer le peloton 9.12 dans CI Peintre.
- Prérequis backend **9.11** : gate levé (non ré-exécuté en QA).
- Activation admin module (**9.13**) : tests seedent `module-config` via mock fetch.
