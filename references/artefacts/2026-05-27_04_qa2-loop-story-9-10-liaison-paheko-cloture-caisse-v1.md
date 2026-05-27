# QA2 boucle — Story 9.10 — Liaison Paheko clôture caisse v1

**Date** : 2026-05-27 (itération 2/3, gate)  
**Précédent** : [2026-05-27_03_qa2-story-9-10-…](2026-05-27_03_qa2-story-9-10-liaison-paheko-cloture-caisse-v1.md) — 92 %, NO-GO  
**Livrable** : story `9-10-liaison-paheko-cloture-caisse-v1` + périmètre API/Peintre story 9.10

---

## Verdict gate

| Métrique | Valeur |
|----------|--------|
| **Score** | **96 %** |
| **P0** | **0** |
| **P1 résiduels** | **2** (OpenAPI non régénéré ; merge retry T3 processor — hors peloton 9.10) |
| **Gate 95 %** | **ATTEINT — GO** |

---

## Correctifs appliqués (itération gate)

1. **AC5 / HTTP 422** : `CashCloseVarianceExceededError` + mapping dédié dans `domain_exception_http.py` (422 même si `validation_status=400` sur la route).
2. **Tests** : `test_story_9_10_*.py` — **13 passed** (seuil à l’égalité, écart négatif, 422 mapping, T3 `snapshot_missing_revision` / `revision_not_found`, `|variance|=0,005`, clé idempotence index 3).
3. **Migration** : suppression doublon `s9_10_cash_variance_accounts_story910.py`.
4. **Story** : sections Contexte chantier + État brownfield alignées ; statut **review** en attente CR.

**pytest peloton** (parent, 2026-05-27) : 23 passed — `test_story_9_10` (13) + `test_story_22_7` (7) + `test_cash_session_close_arch02` (3).

---

## Tableau AC — post-correctifs

| AC | Statut | Note |
|----|--------|------|
| 1–2 | OK | T3 + skip |
| 3 | OK | Codes erreur T3 couverts en 9.10 |
| 4 | OK | Ordre + clé idempotence index 3 |
| 5–6 | OK | D33 blocage 422 + sous seuil |
| 7–8 | OK | Comptes expert + snapshot figé |
| 9–10 | Hors scope QA2 code | Mapping 25.9 / front message seuil — Peintre déjà branché |
| 11 | OK | Hypothèses EC |

---

## P1 résiduels (non bloquants gate)

- ~~OpenAPI `contracts/openapi/recyclique-api.yaml` non régénéré~~ — **corrigé 2026-05-27** : champs 658/758, routes D33, `npm run generate` → `generated/recyclique-api.ts`.
- Scénario adversarial « T1–T2 OK, T3 fail → merge retry » — couvert par design 22.7, test d’intégration processor optionnel.

---

## Suite

- **Code review** BMAD sur le diff story 9.10.
- Passer story + sprint à **done** après CR OK.
- **C2b** terrain Strophe et tag **v2.0.1** : gates Coordinateur (hors story technique seule).
