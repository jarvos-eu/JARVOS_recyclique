# Handoff Epic Runner — chaîne comptage pièces/billets (9.11 → 9.13)

**Date :** 2026-06-06  
**Epic :** 9 — Modules complémentaires v2  
**Cible produit :** v2.0.2  
**Orchestrateur :** BMAD Epic Runner (session autonome Strophe absent)  
**Décisions HITL :** [`2026-06-06_01_decisions-hitl-comptage-pieces-billets-pilote.md`](2026-06-06_01_decisions-hitl-comptage-pieces-billets-pilote.md)

---

## Synthèse exécutive

| Story | Statut final | Sprint-status |
|-------|--------------|---------------|
| **9.11** — backend, contrats, persistance | **PASS** | `done` |
| **9.12** — wizard UX, relecture, pictos | **PASS** | `done` |
| **9.13** — schéma module-config, activation admin | **PASS** | `done` |

**Aucun NEEDS_HITL bloquant** sur le code. La recette terrain **Q-HITL-09/11** (activation on/off pilote La Clique) reste **manuelle** — hors scope Story Runner.

---

## Story 9.11 — contrats backend persistance

**Story Runner :** [9.11 backend](c81f0fe8-1532-435c-9ad9-e20e6d8a807b)

| Étape | Résultat |
|-------|----------|
| VS | PASS (`vs_loop=0`) |
| DS | Sauté (déjà en `review`) |
| Gates | PASS — pytest **14/14** ; codegen OpenAPI OK |
| QA | PASS |
| CR | APPROVE (P0=0, P1=0) |

### Gates exécutées

```bash
cd recyclique/api && python -m pytest tests/test_story_9_11_comptage_pieces_billets_backend.py -q   # exit 0
cd contracts/openapi && npm run generate   # exit 0 (brief racine corrigé — pas de package.json racine)
```

### Fichiers principaux

- `recyclique/api/src/recyclic_api/models/cash_denomination.py`
- `recyclique/api/src/recyclic_api/services/cash_denomination_service.py`
- `recyclique/api/src/recyclic_api/api/api_v1/endpoints/cash_sessions.py`
- `recyclique/api/migrations/versions/s9_11_cash_denomination_counts.py`
- `contracts/openapi/recyclique-api.yaml` + `generated/recyclique-api.ts`
- `recyclique/api/tests/test_story_9_11_comptage_pieces_billets_backend.py`

### Follow-up non bloquant (CR)

- **P2** : GET `denomination-count` sur session fermée (D-CPT-03 historique) — partiellement traité en reprise
- **P2** : tests AC13 incomplets (EUR_50000 seul, D33 sans variance)
- **P3** : constante morte, codes dupliqués PUT, N+1 UPSERT

---

## Story 9.12 — wizard UX relecture

**Story Runner :** [9.12 wizard UX](2c7edd68-8801-40a6-a212-74e18b98a1b9)

| Étape | Résultat |
|-------|----------|
| VS | PASS (`vs_loop=0`) |
| DS | PASS |
| Gates | PASS — lint, **13** tests gate, build |
| QA | PASS — 29/29 peloton complet |
| CR | APPROVE_WITH_NOTES (`cr_loop=0` ou `cr_loop=1` selon reprise) |

### Gates exécutées

```bash
cd peintre-nano && npm run lint                                                          # exit 0
cd peintre-nano && npm run test -- --run cashflow-close-6-7.test.tsx cashflow-close-denomination-9-12.test.tsx   # 13/13
cd peintre-nano && npm run build                                                         # exit 0 (warning chunk > 500 kB)
```

### Fichiers principaux

- `peintre-nano/src/domains/cashflow/CashflowCloseWizard.tsx`
- `peintre-nano/src/api/cash-session-client.ts`, `comptage-module-config.ts`
- `peintre-nano/public/assets/cash-denominations/` (15 SVG stylisés + README)
- `contracts/creos/manifests/page-cashflow-close.json`
- Tests : `cashflow-close-denomination-9-12.test.tsx`, e2e/contract 9-12

### Follow-up non bloquant (CR)

1. **`secondary_operation_id` CREOS** — `recyclique_cashSessions_listCashDenominations` vs OpenAPI `recyclique_cashDenominations_list`
2. **`operatorLabel` relecture** — prop exposé mais wizard ne le transmet pas (affiche « Opérateur courant »)

---

## Story 9.13 — activation schéma recette

**Story Runner :** [9.13 activation](1c175c2f-1b98-4587-968c-8a9cbd547dbb)

| Étape | Résultat |
|-------|----------|
| VS | PASS (`vs_loop=0`) |
| DS | PASS |
| Gates | PASS (retry pytest chemin fichier) |
| QA | PASS — 28/28 |
| CR | PASS — 0 bloquant |

### Gates exécutées

```bash
cd recyclique/api && python -m pytest tests/test_module_config_site.py tests/test_story_9_13_comptage_module_config.py -q   # 17/17
cd peintre-nano && npm run test -- --run admin-modules   # 6/6
```

**Note brief :** le brief Epic Runner référençait `test_story_9_13_comptage_pieces_billets_activation.py` (inexistant). Fichier réel : `test_story_9_13_comptage_module_config.py`.

### Fichiers principaux

- `references/config-modules-site-id/comptage-pieces-billets.v1.json`
- Registre `ACTIVE_MODULE_KEYS`, migration seed pilote La Clique
- Admin Peintre modules + procédure ops recette
- `recyclique/api/tests/test_story_9_13_comptage_module_config.py`

### Follow-up non bloquant (CR)

1. Test vitest garde GET comptage en échec (AC15 partiel)
2. Test pytest 422 type incorrect ; doc combinaison `skip_allowed`

---

## NEEDS_HITL — actions humaines pour Strophe

| ID | Sujet | Action |
|----|-------|--------|
| **Q-HITL-09/11** | Recette terrain on/off module | Exécuter procédure ops sur pilote La Clique (activation admin → wizard clôture avec/sans grille) |
| **Commit / push** | Livrable non commité automatiquement | Staging + commit Conventional Commits si souhaité ; déléguer @git-specialist |
| **Brief gates** | Chemins corrigés en session | Futurs briefs : `npm run generate` → `contracts/openapi` ; pytest 9.13 → `test_story_9_13_comptage_module_config.py` |

---

## Prochaines actions recommandées

1. **Recette terrain** Q-HITL-09/11 sur pilote (dernier jalon avant beta comptage).
2. **Commit** de la chaîne 9.11–9.13 (gros diff backend + peintre-nano + contrats).
3. **Story suivante Epic 9** (ordre sprint-status) : `9-7-livrer-les-acl-minimales-de-fonctionnalites-sensibles` (`backlog`) — ou `bmad-sprint-status` pour arbitrage priorité.
4. **Optionnel** : traiter follow-up CR P2 (GET post-close, CREOS operation_id, operatorLabel).
5. **Rétrospective** : `bmad-retrospective` epic-9 quand le fil comptage + stories restantes seront arbitrées.

---

## Références croisées

- QA2 boucle préalable : [`2026-06-06_02_qa2-loop-stories-9-11-9-13-comptage-pieces-billets.md`](2026-06-06_02_qa2-loop-stories-9-11-9-13-comptage-pieces-billets.md) (GO 96 %)
- Sprint-status : `_bmad-output/implementation-artifacts/sprint-status.yaml` (lignes 9-11/12/13 → `done`)
