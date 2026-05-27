# BMAD Code Review — Story 9.10 — Liaison Paheko clôture caisse v1

**Date** : 2026-05-27  
**Mode** : AUTO (sans HITL) · `review_mode: full`  
**Story** : `9-10-liaison-paheko-cloture-caisse-v1`  
**Spec** : `_bmad-output/implementation-artifacts/9-10-liaison-paheko-cloture-caisse-v1.md`  
**Contexte QA2** : [2026-05-27_04_qa2-loop-story-9-10-…](2026-05-27_04_qa2-loop-story-9-10-liaison-paheko-cloture-caisse-v1.md) (gate **96 %**, GO)  
**Diff** : 24 fichiers · ~1 824 lignes patch (uncommitted + untracked story 9.10)

---

## Verdict

| Métrique | Valeur |
|----------|--------|
| **Verdict CR** | **APPROVE** |
| **P0** | **0** |
| **P1** | **1** |
| **P2** | **4** |
| **Dismiss** | **3** |

**Synthèse** : Implémentation alignée sur les AC T3 (index 3, 658/758, skip zéro) et D33 (seuil site, 422 dédié, front message backend). Couverture pytest ciblée solide (13 tests 9.10 + extensions 22.7 / arch02). Un risque brownfield révision publiée pré-9.10 reste à traiter côté déploiement (republication révision), non bloquant pour merge dev si gate EC prod respectée.

---

## Couches de revue

| Couche | Statut | Note |
|--------|--------|------|
| Blind Hunter (diff seul) | OK (inline) | Pas de fuite évidente ; erreurs métier nommées |
| Edge Case Hunter | OK (inline) | Bornes D33, skip 0,005 €, écart négatif |
| Acceptance Auditor (spec) | OK (inline) | AC 1–8, 10–11 couverts ; AC 9 hors périmètre diff |

`failed_layers` : *(aucun)*

---

## Findings P0

*(aucun)*

---

## Findings P1

### P1-1 — Révisions comptables publiées avant 9.10 sans clés 658/758 dans le snapshot

| Champ | Détail |
|-------|--------|
| **Sévérité** | P1 (risque prod / sync Paheko) |
| **AC** | AC3, AC7, AC8 |
| **Fichier** | `recyclique/api/src/recyclic_api/services/paheko_close_batch_builder.py` (`_load_revision_payment_accounts`, `_build_cash_variance_planned_write`) |
| **Constat** | Le builder T3 lit `cash_shortage_account` / `cash_surplus_account` **uniquement** depuis le JSON figé de la révision (`global_accounts` du snapshot). Les révisions publiées **avant** migration 9.10 n’ont en général **pas** ces clés → chaînes vides → `variance_accounts_missing` dès que `\|cash_variance\| ≥ 0,005 €`. `build_planned_sub_writes` retourne alors `[], err` (échec de planification globale, pas seulement T3). |
| **Mitigation attendue** | Republication d’une révision comptable après mise à jour des comptes globaux (le widget Peintre l’indique : *« selon la gouvernance des révisions publiées »*). Gate EC prod story inchangée. |
| **Patch optionnel** | Fallback `658`/`758` dans `_load_revision_payment_accounts` **uniquement** si clés absentes du snapshot (distinct des chaînes vides explicites testées en AC3). |

---

## Findings P2

### P2-1 — Pas de test intégration HTTP `POST /cash-sessions/{id}/close` → 422 D33

| Champ | Détail |
|-------|--------|
| **AC** | AC5 |
| **Constat** | `test_story_9_10` couvre `validate_session_close` + mapping `raise_domain_exception_as_http` ; pas de scénario client FastAPI avec seuil site persisté et assertion 422 + corps `detail`. |
| **Impact** | Faible — mapping dédié `CashCloseVarianceExceededError` testé ; risque de régression routing uniquement. |

### P2-2 — Pas d’UI Peintre pour régler le seuil D33 par site

| Champ | Détail |
|-------|--------|
| **AC** | AC5 (partiel) |
| **Constat** | Routes `GET/PUT /v1/admin/settings/cash-close-variance-max` + OpenAPI OK ; aucun widget admin Peintre. Réglage via API / outil externe uniquement. |
| **Impact** | Friction terrain ; **hors tasks story** (minimal front = 658/758 + messages clôture). |

### P2-3 — Écart de sémantique skip T3 : AC1 (≥ 0,01 €) vs code (&lt; 0,005 €)

| Champ | Détail |
|-------|--------|
| **AC** | AC1, AC2 |
| **Constat** | Skip `skipped_zero` si `\|variance\| < 0,005` ; zone 0,005–0,009 € génère encore une écriture T3 ADVANCED. Cohérent avec tests `test_t3_variance_at_skip_boundary_not_zero` ; écart mineur avec libellé AC1. |
| **Impact** | Micro-montants Paheko ; acceptable MVP v1. |

### P2-4 — Scénario merge retry T1–T2 livrés, T3 en échec (processor)

| Champ | Détail |
|-------|--------|
| **AC** | AC4 |
| **Constat** | Idempotence index 3 testée ; `merge_state_with_planned` couvert en 22.7 pour index 0, pas de test d’intégration processor « T0–2 delivered, T3 fail → retry ». |
| **Impact** | Design 22.7 supposé ; même constat QA2 boucle (non bloquant gate). |

---

## Dismiss (bruit / déjà traité)

| ID | Raison |
|----|--------|
| D-1 | OpenAPI / `generated/recyclique-api.ts` non régénéré — **corrigé** (QA2 it. 2). |
| D-2 | HTTP 422 D33 mappé sur `validation_status=400` route caisse — **corrigé** (`CashCloseVarianceExceededError` + branche dédiée). |
| D-3 | Migration dupliquée `s9_10_*_story910` — **retirée** (QA2). |

---

## Matrice AC (Acceptance Auditor)

| AC | Statut CR | Commentaire |
|----|-----------|-------------|
| 1 | OK | T3 manque/surplus, ADVANCED, montant `\|variance\|` |
| 2 | OK | `skipped_zero` &lt; 0,005 € |
| 3 | OK | Codes `variance_accounts_missing`, `snapshot_missing_revision`, `revision_not_found` |
| 4 | OK | Ordre 0–3, clé idempotence ; merge retry partiel = P2-4 |
| 5 | OK | Blocage strict `> seuil` ; égalité autorisée (test `test_d33_at_threshold_allowed`) |
| 6 | OK | Clôture 1,50 € sous seuil 2 € |
| 7 | OK | Global accounts + migration + expert API |
| 8 | OK | Snapshot figé `closing.cash_variance` uniquement |
| 9 | N/A | Mapping 25.9 non modifié dans le diff |
| 10 | OK | `cashSessionCloseFailureMessage` + tests Peintre 422 seuil |
| 11 | OK | Hypothèses EC documentées story / test-summary |

---

## Points positifs

- Séparation claire **tolérance commentaire 0,05 €** vs **seuil blocage D33** (backend + doc front).
- Tests 9.10 exhaustifs sur T3 et D33 (bornes, signe, 422, idempotence).
- OpenAPI et types générés alignés (658/758, routes admin seuil).
- Extension chirurgicale du batch builder (index 3) sans refonte Epic 22.

---

## Actions recommandées (post-merge, non bloquantes CR)

1. **Avant prod** : republier une révision comptable incluant `cash_shortage_account` / `cash_surplus_account` (P1-1).
2. *(Optionnel)* Test intégration `POST …/close` 422 D33 (P2-1).
3. *(Backlog)* Widget admin seuil D33 Peintre (P2-2).

---

## Références

- Story : `_bmad-output/implementation-artifacts/9-10-liaison-paheko-cloture-caisse-v1.md`
- QA2 gate : `references/artefacts/2026-05-27_04_qa2-loop-story-9-10-liaison-paheko-cloture-caisse-v1.md`
- Test-summary : `_bmad-output/implementation-artifacts/tests/test-summary-story-9-10-liaison-paheko-cloture-caisse-v1.md`
