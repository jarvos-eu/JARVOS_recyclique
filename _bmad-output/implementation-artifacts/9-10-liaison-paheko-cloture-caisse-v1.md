# Story 9.10 : Liaison Paheko — clôture caisse MVP v1 (2.0.1)

Status: done

**Story key :** `9-10-liaison-paheko-cloture-caisse-v1`  
**Epic :** 9 — Modules complémentaires v2 (fil **E** liaison Paheko) · s’appuie sur la chaîne comptable **Epic 22** (done)  
**Version produit cible :** **v2.0.1** (un module métier après plancher 9.6)

## Story

En tant qu’**équipe compta / sync Paheko**,  
je veux que la **clôture de session caisse** produise un **lot Paheko complet** (T1 ventes+dons, T2 remboursements, **T3 écart 658/758**) avec **seuil d’écart paramétrable par site**,  
afin d’aligner le terrain et Paheko sur les décisions métier **sans** module comptage pièces (D5) en v1.

## Décisions PO Strophe (2026-05-27) — obligatoires

| Sujet | Décision |
|-------|----------|
| **D33** | Seuil écart espèces/fonds = **paramètre réglable par site** (settings admin), **défaut suggéré 2,00 €** — unifie terrain + règle Paheko. Ne pas figer 0,05 € seul ni 2 € en dur sans setting. |
| **T3 (lot 658/758)** | **Obligatoire** dans le batch builder clôture (sous-écriture index **3**, kind dédié). |
| **Écran paiement** | Hors scope story — garder flux clavier legacy ; backlog **13.8** si écart après C2b. |
| **Gate EC** | Dev **autorisé** (dérogation fil E brief 02) ; comptes + hypothèses EC **documentés** ; validation Corinne/Caro **blocking prod** uniquement. |

Source plan : [`.cursor/plans/post-9.6_plancher_et_compta_3341de2e.plan.md`](../../.cursor/plans/post-9.6_plancher_et_compta_3341de2e.plan.md) § Décisions PO.

## Contexte chantier

| Bloc | Statut | Référence |
|------|--------|-----------|
| T1/T2 batch Paheko (indices 0–2) | **Fait** (22.7, 23.1, 23.4) | `paheko_close_batch_builder.py` |
| Snapshot figé + `closing.cash_variance` | **Fait** (22.6) | `cash_session_close_snapshot.py` |
| Paramétrage expert 7070/7541/53x/5112 | **Fait** (Epic 23) | `/admin/accounting-expert` |
| **T3 658/758** | **Fait** (9.10) | `paheko_close_batch_builder.py` index 3 |
| **D33 seuil site** | **Fait** (9.10) | `cash_close_variance_max_eur` par site, blocage **422** |
| Module comptage D5 | **Phase 2** (hors AC v1) | MVP = saisie manuelle `actual_amount` à clôture |
| Parité gestes / C2b | **Hors story** | Rapport Agent A ; sign-off Strophe plus tard |

**MVP v1 dégradé (plan Agent B) :** pas de module D5 ; à la clôture, écart espèces saisi **manuellement** (`actual_amount` vs théorique) ; écritures Paheko = agrégats T1/T2/T3 depuis snapshot figé + écart.

## Ordre de lecture obligatoire (session dev)

1. [`references/migration-paheko/2026-05-21_procedure-cloture-liaison-paheko-recyclique.md`](../../references/migration-paheko/2026-05-21_procedure-cloture-liaison-paheko-recyclique.md)
2. [`references/migration-paheko/2026-05-21_decisions-compta-liaison-paheko-recherche-terrain.md`](../../references/migration-paheko/2026-05-21_decisions-compta-liaison-paheko-recherche-terrain.md) — D20, D29, D33, D19
3. [`references/migration-paheko/2026-04-15_prd-recyclique-caisse-compta-paheko.md`](../../references/migration-paheko/2026-04-15_prd-recyclique-caisse-compta-paheko.md) — §9.2 batch
4. [`_bmad-output/planning-artifacts/architecture/cash-accounting-paheko-canonical-chain.md`](../../_bmad-output/planning-artifacts/architecture/cash-accounting-paheko-canonical-chain.md)
5. Story **22.7** + **22.6** (prérequis code)
6. [`references/protocole-modules-recyclique/06-MOD-cookbook-nouveau-module-optionnel.md`](../../references/protocole-modules-recyclique/06-MOD-cookbook-nouveau-module-optionnel.md) — **pas** de compta dans JSON `module-config` (loup de mer #7)

## Acceptance Criteria

1. **T3 — sous-écriture écart caisse (658/758)** — Étant donné une session clôturée avec snapshot figé `closing.cash_variance` non nul (|écart| ≥ 0,01 €), une révision comptable publiée contenant les comptes globaux **658** (manque) et **758** (surplus) et le moyen **cash** mappé sur un compte **53x**, quand le builder planifie le batch Paheko, alors une sous-écriture d’**index 3** (`kind` stable ex. `cash_variance_v1`) est produite en **ADVANCED** : manque → débit **658** / crédit **53x** ; surplus → débit **53x** / crédit **758** ; montant = |`cash_variance`| arrondi 2 décimales. [Source : procédure T3 · D19]

2. **T3 — skip zéro** — Étant donné `closing.cash_variance` nul ou |écart| &lt; 0,005 €, alors l’index 3 est planifié avec `skipped_zero` (aucun POST Paheko pour T3), sans faire échouer T1/T2. [Source : cohérence indices 1–2 existants]

3. **T3 — erreurs explicites** — Étant donné un écart non nul mais révision sans comptes 658/758 ou sans `accounting_config_revision_id`, quand le builder construit le batch, alors le batch **échoue** avec code métier explicite (`variance_accounts_missing`, `snapshot_missing_revision`, …) et **aucune** sous-écriture T3 partielle n’est marquée livrée. [Source : pattern `_build_refund_bucket_per_pm_planned_write`]

4. **Ordre et idempotence batch** — Étant donné le même snapshot et payload enrichi, alors l’ordre des sous-écritures reste **0 = T1**, **1–2 = T2**, **3 = T3** ; la clé `sub_write_idempotency_key(batch, 3, kind)` est stable ; `merge_state_with_planned` conserve les livraisons index 0–2 lors d’un retry ciblé sur index 3. [Source : 22.7 AC5]

5. **D33 — seuil paramétrable par site** — Étant donné un site avec seuil configuré (défaut **2,00 €** si absent), quand un opérateur tente `POST` clôture avec |montant physique − théorique espèces| **strictement supérieur** au seuil, alors l’API renvoie **422** avec détail lisible et la session reste **ouverte**. [Source : décision PO D33 · procédure §2 étape 4]

6. **D33 — clôture sous le seuil** — Étant donné un écart de **1,50 €** (≤ seuil 2 €) et champs clôture valides, quand la clôture réussit, alors le snapshot figé contient `closing.cash_variance` cohérent et l’outbox peut enchaîner T1–T3 selon les montants. [Source : D33 « en deçà → T3 auto » côté Paheko]

7. **Comptes 658/758 en révision expert** — Étant donné un super-admin sur `/admin/accounting-expert/global-accounts`, quand il enregistre les comptes écart avec step-up PIN, alors la **prochaine révision publiée** expose `global_accounts.cash_shortage_account` et `cash_surplus_account` (noms à figer dans OpenAPI) utilisables par le builder T3. [Source : Epic 23 — extension, pas refonte 23-2/23-3 Peintre]

8. **Pas de relecture live post-snapshot** — Le builder T3 consomme **uniquement** `accounting_close_snapshot_frozen` (22.6) ; il ne recalcule pas l’écart depuis l’UI ou le legacy. [Source : 22.7 guardrail]

9. **Mapping Paheko inchangé (25.9)** — Étant donné mapping site absent ou invalide, quand la clôture locale réussit, alors l’outbox reste en échec/quarantaine selon 25.9 ; **aucun** succès Paheko global tant que le mapping n’est pas résolu (régression T3 incluse). [Source : story 25.9]

10. **Front clôture — message seuil** — Étant donné le wizard clôture Peintre, quand l’API renvoie 422 seuil D33, alors le message affiché reflète le seuil backend (ne pas laisser uniquement la constante **0,05 €** comme seule référence utilisateur). [Source : rapport parité 03 § fermeture caisse]

11. **Hypothèses EC documentées** — La story et le fichier story § Dev Agent Record listent : comptes **658/758**, seuil **2 €** par défaut, validation EC **requise avant prod réelle** ; gate brainstorming `EN_ATTENTE_VALIDATION_COMPTABLE` = **waived dev** / **blocking prod**. [Source : plan § Gate EC]

## Hors scope v1 (phase 2 explicite)

- Module comptage pièces/billets (**D5**)
- UX bénévole clôture élaborée / PDF feuille clôture (D6 partiel hors MVP)
- Éco-org **9.1**, HelloAsso, réception Paheko
- Refonte flux paiement clavier (**13.8**)
- Tag **`v2.0.1`** / prod : gates Coordinateur (C2b, QA2 story, CR) — hors DS seul

## Tasks / Subtasks

### Backend — batch T3

- [x] `paheko_close_batch_builder.py` : `SUB_KIND_CASH_VARIANCE_V1`, `_build_cash_variance_planned_write`, indices 0–3
- [x] Compte caisse via `payment_methods[code=cash].paheko_debit_account`
- [x] Tests 22.7 / 23.1 / 9.10

### Backend — comptes globaux 658/758

- [x] `GlobalAccountingSettings` + migration `s9_10_cash_variance_accounts`
- [x] `accounting_expert` schémas + service + endpoints
- [x] Snapshot révision inclut `cash_shortage_account` / `cash_surplus_account`

### Backend — seuil D33 par site

- [x] `AdminSetting` clé `cash_close_variance_max_eur`, défaut **2.0**
- [x] GET/PUT `/admin/settings/cash-close-variance-max`
- [x] `validate_session_close` bloque si |écart| > seuil site
- [x] Tests 9.10 + fix `test_cash_session_close_arch02` (+1 €)

### Front Peintre (minimal)

- [x] `AdminAccountingGlobalAccountsWidget.tsx` : champs 658/758
- [x] `cash-session-client.ts` : doc tolérance 0,05 € vs blocage D33 ; erreur API detail
- [x] `contracts/openapi/recyclique-api.yaml` — 658/758 + routes D33 ; `npm run generate` → `generated/recyclique-api.ts`

### Contrats & doc

- [x] `contracts/openapi/recyclique-api.yaml` (Story 9.10 — comptes 658/758 + seuil D33)
- [x] test-summary + hypothèses EC ci-dessous

## Dev Notes

### État brownfield (post-DS 2026-05-27)

- Batch clôture : indices **0–3** (T1, T2×2, T3) — `SUB_KIND_CASH_VARIANCE_V1`
- **D33** : seuil site via `AdminSettingsService` ; blocage `CashCloseVarianceExceededError` → HTTP **422**
- **0,05 €** : tolérance commentaire obligatoire uniquement (`CLOSE_VARIANCE_TOLERANCE`), distincte du blocage D33
- Comptes **658/758** en révision expert + migration `s9_10_cash_variance_accounts`

### Fichiers d’ancrage (priorité)

| Priorité | Fichier |
|----------|---------|
| 1 | `recyclique/api/src/recyclic_api/services/paheko_close_batch_builder.py` |
| 2 | `recyclique/api/src/recyclic_api/services/cash_session_service.py` |
| 3 | `recyclique/api/src/recyclic_api/models/accounting_config.py` |
| 4 | `recyclique/api/src/recyclic_api/schemas/accounting_expert.py` |
| 5 | `recyclique/api/src/recyclic_api/services/accounting_expert_service.py` |
| 6 | `peintre-nano/src/api/cash-session-client.ts` |
| 7 | `peintre-nano/src/domains/cashflow/CashflowCloseWizard.tsx` |
| 8 | `peintre-nano/src/domains/admin-config/AdminAccountingGlobalAccountsWidget.tsx` |

### Chaîne processor (ne pas réécrire)

`cash_session_service.enqueue_cash_session_close_outbox` → `paheko_outbox_processor` → `build_cash_session_close_batch_from_enriched_payload` — **étendre**, pas remplacer Epic 8.

### Testing / gates Story Runner

- **Pytest obligatoire vert** ; `timeout_sec` **≥ 330** (plan Agent B)
- Peloton minimal suggéré :
  - `pytest recyclique/api/tests/test_story_22_7_paheko_close_batch_builder.py`
  - `pytest recyclique/api/tests/test_story_23_1_paheko_per_method_close_batch.py`
  - `pytest recyclique/api/tests/test_story_25_9_paheko_mapping_before_outbox_success.py`
  - `pytest recyclique/api/tests/test_cash_session_close.py -k variance`
  - `pytest recyclique/api/tests/test_paheko_outbox_hardening_v2.py`
- Créer `recyclique/api/tests/test_story_9_10_liaison_paheko_cloture_caisse_v1.py` pour AC T3 + D33 dédiés
- Test-summary : `_bmad-output/implementation-artifacts/tests/test-summary-story-9-10-liaison-paheko-cloture-caisse-v1.md`

### Stories prérequis (done)

| Clé | Apport |
|-----|--------|
| 22-6 | Snapshot figé, `closing.cash_variance` |
| 22-7 | Batch multi-sous-écritures, état `paheko_close_batch_state_v1` |
| 22-8 | Matrice QA chaîne — **étendre** avec T3 |
| 23-1 / 23-4 | T1/T2 ADVANCED par moyen |
| 25-9 | Mapping obligatoire avant succès outbox |
| 6-7 / 13-3 | UI clôture locale |

### Garde-fous

- Ne pas mettre comptes 658/758/seuil dans JSON `module-config` (cookbook #7)
- Ne pas refaire Epic 23 admin Peintre large — **étendre** global accounts + setting seuil
- Ne pas imposer module D5 en AC v1
- T3 = **transaction batch index 3**, distinct des remboursements indices 1–2 (éviter confusion 672 vs 658)

### References

- [Source: `.cursor/plans/post-9.6_plancher_et_compta_3341de2e.plan.md` — § Agent B]
- [Source: `references/artefacts/2026-05-26_03_rapport-parite-plancher-v2-gestes-terrain.md` — D33 P0 documenté]
- [Source: `_bmad-output/brainstorming/brainstorming-session-2026-05-21-paheko-compta-validation.md`]
- [Source: `_bmad-output/implementation-artifacts/22-7-generer-les-ecritures-avancees-multi-lignes-paheko-et-adapter-la-sync-epic-8.md`]

## Dev Agent Record

### Agent Model Used

Agent B parent + sous-agents Task (DS backend, DS Peintre, QA2, CR).

### Debug Log References

- test-summary : `_bmad-output/implementation-artifacts/tests/test-summary-story-9-10-liaison-paheko-cloture-caisse-v1.md`
- QA2 : `references/artefacts/2026-05-27_04_qa2-loop-story-9-10-liaison-paheko-cloture-caisse-v1.md`

### Completion Notes List

- T3 : sous-écriture index **3** `cash_variance_v1` (658/758 ↔ 53x) dans `paheko_close_batch_builder.py`.
- D33 : seuil site via `AdminSetting` `cash_close_variance_max_eur` (défaut 2 €) ; GET/PUT `/admin/settings/cash-close-variance-max`.
- Comptes globaux : `cash_shortage_account` / `cash_surplus_account` + migration `s9_10_cash_variance_accounts`.
- Peintre : champs 658/758 dans `AdminAccountingGlobalAccountsWidget.tsx`.
- CR : **APPROVE** (P1 OpenAPI + republication révision — non bloquant v1 dev).
- Gate EC prod : inchangé (validation écrite requise avant prod).

### File List

- `recyclique/api/src/recyclic_api/services/paheko_close_batch_builder.py`
- `recyclique/api/src/recyclic_api/services/cash_session_service.py`
- `recyclique/api/src/recyclic_api/models/accounting_config.py`
- `recyclique/api/src/recyclic_api/schemas/accounting_expert.py`
- `recyclique/api/src/recyclic_api/services/accounting_expert_service.py`
- `recyclique/api/src/recyclic_api/api/api_v1/endpoints/admin_accounting_expert.py`
- `recyclique/api/src/recyclic_api/schemas/admin_settings.py`
- `recyclique/api/src/recyclic_api/services/admin_settings_service.py`
- `recyclique/api/src/recyclic_api/api/api_v1/endpoints/admin_settings.py`
- `recyclique/api/migrations/versions/s9_10_cash_variance_accounts.py`
- `recyclique/api/tests/test_story_9_10_liaison_paheko_cloture_caisse_v1.py`
- `recyclique/api/tests/test_story_22_7_paheko_close_batch_builder.py`
- `recyclique/api/tests/test_cash_session_close_arch02.py`
- `peintre-nano/src/domains/admin-config/AdminAccountingGlobalAccountsWidget.tsx`
- `peintre-nano/src/api/cash-session-client.ts` (doc / erreurs)
- `_bmad-output/implementation-artifacts/tests/test-summary-story-9-10-liaison-paheko-cloture-caisse-v1.md`
- `references/artefacts/2026-05-27_03_qa2-story-9-10-liaison-paheko-cloture-caisse-v1.md`

## Change Log

| Date | Auteur | Changement |
|------|--------|------------|
| 2026-05-27 | Agent B (DS+QA2+CR) | Implémentation MVP v1 — T3, D33, 658/758 ; story **done** |
| 2026-05-27 | Agent B (create-story) | Création story MVP v1 — T3 + D33 + décisions PO |
