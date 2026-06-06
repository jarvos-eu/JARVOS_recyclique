# Test summary — Story 9.11 comptage pièces/billets (backend)

**Date :** 2026-06-06  
**Fichier :** `recyclique/api/tests/test_story_9_11_comptage_pieces_billets_backend.py`  
**QA loop :** 0 (bmad-qa-generate-e2e-tests)

## Résultat

| Suite | Statut |
|-------|--------|
| `test_story_9_11_comptage_pieces_billets_backend.py` (14 tests) | **PASS** |
| Non-régression `test_story_9_10_liaison_paheko_cloture_caisse_v1.py` | **PASS** (peloton story) |
| `npm run generate` (contracts/openapi) | **PASS** (gate DS) |

## Couverture AC

| AC | Couverture |
|----|------------|
| AC1 | `test_list_15_denominations` — 15 lignes, `EUR_50000` seul `display_default: false` |
| AC2–3 | `test_put_get_nominal`, `test_put_rejects_closed_session` — UPSERT, totaux serveur, float/withdraw |
| AC4 | `test_resolve_close_raises_on_zero_grid_with_positive_theoretical`, `test_close_zero_theoretical_with_zero_grid` (session vide → clôture autorisée, suppression B44) |
| AC5–6 | `test_comptage_required_without_grid`, `test_comptage_amount_mismatch`, `test_close_aligns_actual_amount_from_grid` |
| AC7 | `test_module_off_legacy_close` — schema_version 2 sans `denomination_count_v1` |
| AC8 | `test_close_aligns_actual_amount_from_grid` — snapshot v3 + bloc `denomination_count_v1` |
| AC9 | `test_d33_blocks_close_with_grid_variance` |
| AC10 | OpenAPI + codegen — gate manuel `npm run generate` (pas de test pytest dédié) |
| AC11 | `test_get_denomination_count_403_other_operator` |
| AC12 | Suite dédiée 14 tests (liste story) |
| AC13 | `test_close_aligns_actual_amount_from_grid` (`anomaly_close_sheet: false`), `test_close_anomaly_flags_on_variance` (`true` + URL stub) |

## Tests ajoutés (QA loop 0)

- `test_get_denomination_count_403_other_operator` — AC11
- `test_close_zero_theoretical_with_zero_grid` — AC4 (tiroir vide attesté)
- `test_close_anomaly_flags_on_variance` — AC13 réponse HTTP
- Assertions `anomaly_close_sheet` / `close_sheet_pdf_url` sur clôture nominale sans écart

## Commandes

```bash
cd recyclique/api
pytest tests/test_story_9_11_comptage_pieces_billets_backend.py -v
pytest tests/test_story_9_10_liaison_paheko_cloture_caisse_v1.py -q
cd ../../contracts/openapi && npm run generate
```
