# QA2 boucle — Story 9.10 — Re-QA2 post-OpenAPI

**Date** : 2026-05-27 (itération **1/3**, gate)  
**Précédent** : [2026-05-27_04_qa2-loop-story-9-10-…](2026-05-27_04_qa2-loop-story-9-10-liaison-paheko-cloture-caisse-v1.md) — 96 %, GO (pré-OpenAPI D33/658/758)  
**Livrable** : story `9-10-liaison-paheko-cloture-caisse-v1` + contrat OpenAPI post-correctifs + périmètre API/Peintre story 9.10

---

## Verdict gate

| Métrique | Valeur |
|----------|--------|
| **Score fusionné** | **96 %** |
| **P0** | **0** |
| **P1 bloquants** | **0** |
| **P1 résiduels (dette)** | **3** (voir § P1 résiduels) |
| **Gate 95 %** | **ATTEINT — GO** |

**Itération** : 1/3 — gate atteint après Lot correctifs OpenAPI + re-QA2 ciblé (pas d’itération 2 nécessaire).

---

## Contexte re-QA2

Travail post [rapport loop 04](2026-05-27_04_qa2-loop-story-9-10-liaison-paheko-cloture-caisse-v1.md) :

- Mise à jour `contracts/openapi/recyclique-api.yaml` (658/758, routes D33 `cash-close-variance-max`)
- `npm run generate` → `contracts/openapi/generated/recyclique-api.ts`
- Correctifs gate précédents maintenus : `CashCloseVarianceExceededError` → HTTP 422, 13 tests `test_story_9_10_*`, migration dupliquée supprimée

---

## Orchestration QA2 (5 passes + re-QA2)

| Passe | ID | Score conf. | P0 | Synthèse |
|-------|-----|-------------|-----|----------|
| Doc story delta | pass-1-doc-story-delta | 95 → **97** | 0 | AC alignés post-OpenAPI ; delta vs loop 04 = statut story **done** |
| Backend + pytest | pass-2-code-backend-pytest | **95** | 0 | **23/23 pytest OK** ; T3/D33/422 runtime validés |
| Triade OpenAPI | pass-3-code-openapi-triad | 94 → **97** | 0 | 658/758 + D33 cohérents ; P1 initial 422 POST close |
| Front Peintre | pass-4-code-front-peintre | 94 → **96** | 0 | AC7/AC10 OK ; message 422 D33 via `detail` |
| Adversarial | pass-5-code-adversarial-backend-contrat | 90 → **95** | 0 | Pas de rupture P0 ; drift contrat close corrigé en Lot |
| Re-QA2 Lot it.1 | reqa2-openapi-lot-iter1 | **97** | 0 | P1 OpenAPI fermés ; triade alignée runtime |

**Score initial fusionné** (5 passes) : **94 %** (< gate)  
**Score final itération 1** (après Lot + re-QA2) : **96 %** (moyenne ajustée des scores passes post-correctifs)

---

## pytest peloton

Exécuté depuis `recyclique/api` (pass-2) :

```text
23 passed in 53.71s
```

- `test_story_9_10_liaison_paheko_cloture_caisse_v1.py` — **13**
- `test_story_22_7_paheko_close_batch_builder.py` — **7**
- `test_cash_session_close_arch02.py` — **3**

---

## Correctifs appliqués (Lot itération 1)

1. **OpenAPI POST `/v1/cash-sessions/{session_id}/close`** — description Story 9.10 D33 + réponse **422** enrichie (`CashCloseVarianceExceededError`, exemple `detail`, distinction tolérance 0,05 €).
2. **OpenAPI PUT `/v1/admin/settings/cash-close-variance-max`** — réponse **422** documentée (validation schéma `maxEur`).
3. **`npm run generate`** — `contracts/openapi/generated/recyclique-api.ts` régénéré (libellés 422 close alignés).
4. **Story Dev Agent Record** — nom migration harmonisé `s9_10_cash_variance_accounts` ; référence QA2 → rapport **04**.

---

## Tableau AC — post-OpenAPI

| AC | Statut | Note |
|----|--------|------|
| 1–2 | OK | T3 658/758 + skip zéro |
| 3 | OK | Codes erreur T3 couverts (9.10) |
| 4 | OK | Ordre 0–3 + clé idempotence index 3 |
| 5–6 | OK | D33 blocage **422** ; contrat POST close documenté post-Lot |
| 7 | OK | Comptes expert 658/758 + OpenAPI |
| 8 | OK | Snapshot figé |
| 9 | Hors gate | Mapping 25.9 — Coordinateur |
| 10 | OK | Front message seuil D33 (≠ 0,05 € seul) |
| 11 | OK | Gate EC prod blocking |

---

## Issues fusionnées

### P0

*(aucune)*

### P1 résiduels (non bloquants gate)

- **[LOC] `recyclique/api/tests/test_story_9_10_*.py`** — Pas de test HTTP intégration `POST …/close` → **422** quand `|écart| > seuil D33` (mapping unitaire + tests service suffisants pour gate dev v1 ; recommandé pour verrouillage contrat).
- **[LOC] `peintre-nano/src/api/admin-accounting-expert-client.ts`** — Types 658/758 manuels vs `components['schemas']['AccountingExpertGlobalAccounts']` généré (dette parité contrat ; AC7 fonctionnel OK).
- **[LOC] `references/artefacts/2026-05-27_04_qa2-loop-…md` L25** — Ligne « statut **review** » obsolète vs story **done** + CR APPROVE (doc process).

### Info

- Scénario adversarial clôture OK → T3 quarantaine si comptes 658/758 absents : design 22.7, couverture partielle 9.10.
- PUT D33 : réponses **400** métier + **422** Pydantic coexistent (chemin 400 service rare via API normale).
- Pattern compte Paheko absent du YAML expert (validation Pydantic seule).

---

## Risques

| Risque | Impact | Mitigation |
|--------|--------|------------|
| Révisions brownfield sans 658/758 | Compta Paheko incomplète prod | Gate EC + CR P1 brownfield (rapport 06) |
| Absence test HTTP D33 close | Régression 400 vs 422 | Mapping dédié + 13 tests unitaires |
| Types front hand-rolled | Dérive post-regen OpenAPI | Dette P1 documentée |

---

## Suite recommandée

- Story **9.10** : statut **done** maintenu (CR APPROVE — voir [rapport 06](2026-05-27_06_bmad-cr-story-9-10-liaison-paheko-cloture-caisse-v1.md)).
- Optionnel : test HTTP E2E D33 ; aligner types Peintre sur schémas générés.
- **C2b** terrain + tag **v2.0.1** : gates Coordinateur (hors story technique seule).

---

## Méta QA2

- **Planner** : 5 passes (doc, backend, OpenAPI triad, front, adversarial)
- **Workers** : 5 + 1 re-QA2 ciblé post-Lot
- **Gate** : 95 % — **GO** itération 1/3
