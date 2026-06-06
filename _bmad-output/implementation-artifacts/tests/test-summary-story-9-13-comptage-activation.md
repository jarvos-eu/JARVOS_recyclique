# Test Automation Summary — Story 9.13 comptage activation

**Date :** 2026-06-06  
**Story :** `9-13-comptage-pieces-billets-activation-schema-recette`  
**QA loop :** 0  
**QA re-vérif. :** 2026-06-06 (worker bmad-qa-generate-e2e-tests) — **PASS**, aucun test ajouté

## Generated Tests

### API Tests (DS — inchangés)
- [x] `recyclique/api/tests/test_story_9_13_comptage_module_config.py` — GET default, PATCH pilote, 404, 403, 422, resolver
- [x] `recyclique/api/tests/test_module_config_site.py` — non-régression kpi-live-banner

### Unit Tests (DS — inchangés)
- [x] `peintre-nano/tests/unit/admin-modules-widget.test.tsx` — carte comptage, PATCH ETag, garde GET

### E2E Tests (QA — ajoutés)
- [x] `peintre-nano/tests/e2e/comptage-module-activation-9-13.e2e.test.tsx` — matrice Q-HITL-09/11 module on/off

| Scénario | Couverture |
|----------|------------|
| Q-HITL-09 module off | Wizard legacy `actual_amount`, pas de grille, pas de PUT `denomination-count` |
| Q-HITL-11 module on (pilote) | Grille obligatoire, pas de bouton « passer », règles terrain |
| `show_images: false` | Pictos masqués, saisie grille conservée (AC13) |
| Admin activation pilote | PATCH 4 toggles → payload pilote AC8 |
| Admin rollback | PATCH `enabled: false` |

### Fixtures étendues
- [x] `peintre-nano/tests/unit/fixtures/cash-denominations-api.ts` — `comptageModuleDisabledJson()`, `comptageModulePilotJson()`

## Exécution

### Pytest (DS)
```powershell
Set-Location "recyclique\api"
$env:TESTING='true'
python -m pytest tests/test_story_9_13_comptage_module_config.py tests/test_module_config_site.py -v --tb=short
```
**Résultat :** 17 passed (~138 s) — re-vérif. QA 2026-06-06

### Vitest unit (DS)
```powershell
Set-Location "peintre-nano"
npm run test -- tests/unit/admin-modules-widget.test.tsx
```
**Résultat :** 6 passed

### Vitest e2e (QA)
```powershell
Set-Location "peintre-nano"
npm run test -- tests/e2e/comptage-module-activation-9-13.e2e.test.tsx
```
**Résultat :** 5 passed (~1.9 s) — re-vérif. QA 2026-06-06

### Vitest peloton QA (unit + e2e)
```powershell
Set-Location "peintre-nano"
npm run test -- tests/unit/admin-modules-widget.test.tsx tests/e2e/comptage-module-activation-9-13.e2e.test.tsx
```
**Résultat :** 11 passed (6 unit + 5 e2e, ~19 s)

## Coverage AC (recette automatisée)

| AC | Vérification |
|----|--------------|
| Schéma JSON 4 booléens | pytest PATCH 422 |
| Registre ACTIVE_MODULE_KEYS | pytest GET/PATCH 200 |
| Defaults safe (module off) | pytest + e2e Q-HITL-09 |
| Admin `/admin/modules` | vitest unit + e2e activation/rollback |
| Config pilote AC8 | e2e Q-HITL-11 + pytest resolver |
| `show_images` toggle | e2e pictos masqués (`false`) ; `true` couvert par `cashflow-close-denomination-9-12.test.tsx` (story 9.12) |
| Recette Q-HITL-09/11 | e2e matrice on/off ; `COMPTAGE_REQUIRED` 400 → pytest 9.11 ; flux complet grille→relecture→close → 9.12 e2e/unit |

## Next Steps
- Passer en **CR** (code review) si gates verts
- Recette HITL terrain manuelle : procédure `references/operations-speciales-recyclique/2026-06-06_procedure-activation-comptage-pieces-billets-pilote.md`
