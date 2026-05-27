# Test summary — Story 9.10 liaison Paheko clôture caisse v1

**Date :** 2026-05-27  
**Story :** `9-10-liaison-paheko-cloture-caisse-v1`

## Gates exécutés

| Commande | Résultat |
|----------|----------|
| `pytest tests/test_story_9_10_liaison_paheko_cloture_caisse_v1.py` | **13 passed** (gate QA2 boucle 04) |
| `pytest tests/test_story_22_7_paheko_close_batch_builder.py` | 7 passed |
| `pytest tests/test_story_23_1_paheko_per_method_close_batch.py` | 14 passed |
| `pytest tests/test_story_25_9_paheko_mapping_before_outbox_success.py` | 2 passed |
| `pytest tests/test_paheko_outbox_hardening_v2.py` | 6 passed |
| `pytest tests/test_cash_session_close_arch02.py` | 3 passed (dont fix écart +1 € vs seuil D33) |
| `npm run test -- tests/unit/cashflow-close-6-7.test.tsx` (Peintre) | 7 passed |

## Couverture AC

- **T3** : manque, surplus, skip zéro, comptes manquants, `snapshot_missing_revision`, `revision_not_found`, frontière 0,005 € — `test_story_9_10_*`
- **D33** : blocage > seuil (422 HTTP mapping), égalité au seuil, écart négatif, acceptation sous seuil — `test_story_9_10_*` + arch02
- **Batch ordre** : indices `[0,1,2,3]` + clé idempotence index 3 — `test_story_9_10_*` + `test_story_22_7`

## Hypothèses EC

Comptes 658/758 et seuil 2 € par défaut — validation Corinne/Caro requise avant prod réelle.
