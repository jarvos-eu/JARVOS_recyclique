# Story 9.11 : Comptage pièces/billets — contrats, backend et persistance (v2.0.2)

Status: done

**Story key :** `9-11-comptage-pieces-billets-contrats-backend-persistance`  
**Epic :** 9 — Modules complémentaires v2 (fil **comptage** post-9.10) · hôte UX **Epic 6** story **6.7** (done)  
**Module :** `comptage-pieces-billets` (workflow-step, optionnel par site)  
**Version produit cible :** **v2.0.2** (backend + contrats ; UI wizard = **9.12** ; activation admin = **9.13**)

## Story

En tant qu'**équipe terrain / compta**,  
je veux que le **comptage physique par dénomination** soit **persisté côté Recyclique**, **autoritaire serveur** (totaux, écart, snapshot), et **requis à la clôture** quand le module est actif,  
afin d'aligner la fermeture caisse sur les décisions HITL pilote **sans** modifier la chaîne Paheko 9.10 (agrégats T1–T3 inchangés).

## Décisions PO Strophe (2026-06-06) — obligatoires

| ID | Sujet | Décision |
|----|-------|----------|
| **D-CPT-01** | Coupures rares | **500 € seul** dans « coupures rares » (`display_default: false`). **200 €** visible dans la grille principale. |
| **D-CPT-02** | Soirée sans ventes espèces | **Toujours** compter tout le tiroir (fond inclus) — pas de raccourci sans grille. |
| **D-CPT-03** | Historique | Données de comptage **toujours persistées** en base Recyclique (détail + snapshot) — consultables après clôture. |
| **D-CPT-04** | PDF | PDF feuille de clôture **uniquement sur anomalie** (écart, seuil, coupure rare, etc.) — **pas** à chaque close. *(Génération PDF = story 9.12 ; cette story expose les données.)* |
| **D-CPT-05** | Relecture | Écran de relecture **obligatoire** avant PIN — *(UI 9.12 ; backend expose totaux cohérents pour cet écran.)* |
| **D-CPT-06** | Pictos | Images stylisées optionnelles (`show_images`) — **hors scope 9.11** (assets + config = 9.12 / 9.13). |
| **D-CPT-07** | Pilote | Module actif → **`skip_allowed: false`**, **`require_denomination_grid: true`**. |
| **D-CPT-08** | Vérité comptée | **Total grille = seule source de vérité** ; quand module actif, **ignorer / rejeter** `actual_amount` client si ≠ total serveur ; champ global manuel **déprécié**. |
| **D-CPT-09** | Fond de caisse | Comptage = **tiroir entier** (fond inclus) ; théorique = fond ouverture + mouvements espèces session ; fond à laisser / à retirer = **dérivés** (pas seconde vérité). |
| **D-CPT-10** | Poids / balance | **Hors V1** — comptage **unitaire** d'abord ; poids = phase ultérieure. [Source : artefact HITL D-CPT-10] |
| **D-CPT-11** | Paheko | **Aucune** ligne par dénomination côté Paheko ; **enrichir le snapshot** seulement — chaîne batch **9.10** (T1/T2/T3) **inchangée**. [Source : 08-MOD §8 · Q-HITL-10] |

Sources : [`references/artefacts/2026-06-06_01_decisions-hitl-comptage-pieces-billets-pilote.md`](../../references/artefacts/2026-06-06_01_decisions-hitl-comptage-pieces-billets-pilote.md) · recherche Perplexity · fiche [`08-MOD`](../../references/protocole-modules-recyclique/08-MOD-exemple-pilote-comptage-pieces-billets.md).

## Contexte chantier

| Bloc | Statut | Référence |
|------|--------|-----------|
| Clôture locale + wizard hôte | **Fait** (6.7) | `CashflowCloseWizard.tsx`, `closeSession` |
| Snapshot figé + `closing.cash_variance` | **Fait** (22.6) | `cash_session_close_snapshot.py` |
| Batch Paheko T1/T2/T3 + D33 seuil | **Fait** (9.10) | `paheko_close_batch_builder.py` |
| Config admin modules (API) | **Fait** (9.6) | `module-config/{module_key}` |
| Module `comptage-pieces-billets` registre + schéma JSON | **Story 9.13** | `ACTIVE_MODULE_KEYS`, `comptage-pieces-billets.v1.json` |
| Grille dénominations + persistance SQL | **À faire** (9.11) | Cette story |
| Wizard comptage + relecture + PDF anomalie | **Story 9.12** | Peintre / CREOS |

**Positionnement v2.0.2 :** après **v2.0.1** (9.10 Paheko MVP). Le module comptage **remplace** la saisie manuelle `actual_amount` comme vérité terrain quand activé ; la chaîne outbox **consomme** le snapshot enrichi sans nouvelle sous-écriture Paheko.

## Ordre de lecture obligatoire (session dev)

1. [`references/artefacts/2026-06-06_01_decisions-hitl-comptage-pieces-billets-pilote.md`](../../references/artefacts/2026-06-06_01_decisions-hitl-comptage-pieces-billets-pilote.md)
2. [`references/protocole-modules-recyclique/08-MOD-exemple-pilote-comptage-pieces-billets.md`](../../references/protocole-modules-recyclique/08-MOD-exemple-pilote-comptage-pieces-billets.md) — §7 persistance, §6.2 contrats, §8 Paheko
3. [`references/recherche/2026-06-06_comptage-pieces-billets-fermeture-caisse-ux-terrain_perplexity_reponse.md`](../../references/recherche/2026-06-06_comptage-pieces-billets-fermeture-caisse-ux-terrain_perplexity_reponse.md) — référentiel 15 lignes
4. [`_bmad-output/implementation-artifacts/9-10-liaison-paheko-cloture-caisse-v1.md`](9-10-liaison-paheko-cloture-caisse-v1.md) — T3 / D33 / snapshot (ne pas casser)
5. [`_bmad-output/implementation-artifacts/6-7-mettre-en-place-la-cloture-locale-exploitable-de-caisse.md`](6-7-mettre-en-place-la-cloture-locale-exploitable-de-caisse.md) — hôte clôture
6. [`_bmad-output/implementation-artifacts/9-6-config-admin-simple-modules.md`](9-6-config-admin-simple-modules.md) — lecture `module-config`
7. [`references/protocole-modules-recyclique/03-MOD-protocole-backend.md`](../../references/protocole-modules-recyclique/03-MOD-protocole-backend.md) — §13 P2.1–P2.4
8. [`_bmad-output/planning-artifacts/architecture/cash-accounting-paheko-canonical-chain.md`](../../_bmad-output/planning-artifacts/architecture/cash-accounting-paheko-canonical-chain.md)

## Acceptance Criteria

1. **Référentiel 15 dénominations EUR** — Étant donné le déploiement API à jour, quand un client appelle `GET /v1/cash-denominations` (ou lit le référentiel embarqué dans la réponse `denomination-count`), alors la liste contient **exactement 15** codes stables `EUR_001` … `EUR_50000` avec `unit_value_cents`, `kind` (`coin`|`note`), `display_order`, et `display_default: false` **uniquement** pour `EUR_50000`. [Source : D-CPT-01 · Perplexity tableau §1]

2. **Persistance `cash_denomination_counts`** — Étant donné une session caisse **ouverte** et un opérateur autorisé (`caisse.access`), quand il envoie `PUT /v1/cash-sessions/{id}/denomination-count` avec des quantités ≥ 0 par code valide, alors le serveur **UPSERT** les lignes `(cash_session_id, denomination_code)` en base, refuse l'écriture si `status = closed`, et enregistre `recorded_at` / `recorded_by_user_id`. [Source : 08-MOD §7.2 · 03-MOD P2.1]

3. **Total serveur autoritaire** — Étant donné une grille enregistrée, quand le client lit `GET /v1/cash-sessions/{id}/denomination-count`, alors la réponse expose `total_counted_cents` = `SUM(quantity × unit_value_cents)` calculé **serveur**, `theoretical_cash_cents` (fond + mouvements espèces session, aligné `get_closing_preview`), `variance_cents`, `float_target_cents` (fond cible à laisser), `withdraw_cents` (montant à retirer), et le détail par ligne — **tous calculés serveur**, jamais dérivés uniquement côté Peintre. [Source : D-CPT-08/09 · 9.12 AC7 · Perplexity §3]

4. **Grille complète pilote** — Étant donné un site avec module actif et `require_denomination_grid: true`, quand le `PUT` omet une dénomination du référentiel, alors le serveur traite la quantité manquante comme **0** ; quand **toutes** les quantités sont à 0 et `theoretical_cash_cents > 0`, alors `closeSession` est refusé avec **`COMPTAGE_REQUIRED`** ; quand `theoretical_cash_cents = 0` et la grille a été enregistrée (PUT effectué) avec total 0, alors la clôture reste **autorisée** (tiroir vide attesté par grille). [Source : D-CPT-02/07 · Perplexity §B]

5. **Précondition `closeSession`** — Étant donné le module **activé** (`enabled: true`) et `skip_allowed: false` pour le `site_id` de la session, quand l'opérateur appelle `POST .../close` **sans** enregistrement de comptage valide (aucun PUT `denomination-count`, ou total 0 avec théorique > 0), alors l'API renvoie **400** avec `code: COMPTAGE_REQUIRED` et la session reste **ouverte**. [Source : 08-MOD §6.3 · 03-MOD P2.2]

6. **Alignement `actual_amount` depuis la grille** — Étant donné le module actif et un comptage enregistré, quand `closeSession` est appelé avec un `actual_amount` dans le corps, alors le serveur **écrase** par le total grille (`total_counted_cents / 100`) ; si le client envoie un montant **différent** (tolérance &lt; 0,005 €), alors **400** `COMPTAGE_AMOUNT_MISMATCH` (ou rejet explicite documenté OpenAPI). [Source : D-CPT-08]

7. **Module désactivé — parité legacy** — Étant donné `enabled: false` (ou absence de config module pour le site), quand la clôture utilise le flux legacy `actual_amount` manuel, alors **aucun** appel `denomination-count` n'est requis et le comportement 9.10 / 6.7 est **inchangé**. [Source : 08-MOD §6.4 · Q-HITL-09]

8. **Extension snapshot comptable** — Étant donné une clôture réussie avec module actif, quand le snapshot figé est persisté, alors il inclut un bloc **`denomination_count_v1`** : `total_counted_cents`, `theoretical_cash_cents`, `variance_cents`, `breakdown` (liste `{code, quantity, unit_value_cents, line_total_cents}`), `recorded_at`, `breakdown_revision` (hash stable ou version). Le builder Paheko **9.10** continue de lire `closing.cash_variance` — **pas** de nouvelle sous-écriture par dénomination. [Source : D-CPT-11 · 08-MOD §7.3 · 9.10 AC8]

9. **D33 et commentaire d'écart inchangés** — Étant donné un comptage aligné sur la grille, quand |écart| &gt; seuil site (D33) ou &gt; `CLOSE_VARIANCE_TOLERANCE` sans commentaire, alors les garde-fous **9.10** / `validate_session_close` s'appliquent **sur le montant issu de la grille**. [Source : story 9.10 AC5–6]

10. **OpenAPI et codegen** — Étant donné `contracts/openapi/recyclique-api.yaml` mis à jour (`recyclique_cashSessions_getDenominationCount`, `recyclique_cashSessions_upsertDenominationCount`, extension `closeSession` + schémas), quand `npm run generate` est exécuté, alors `generated/recyclique-api.ts` compile ; la description `closeSession` documente la précondition comptage et la dépréciation du montant global manuel si module actif. [Source : 03-MOD P2.3 · gouvernance B4]

11. **Membership et session** — Étant donné un `site_id` ou `session_id` hors périmètre de l'utilisateur, quand il tente GET/PUT denomination-count, alors **403/404** selon conventions existantes caisse ; pas d'IDOR cross-site. [Source : ADR-001 · 03-MOD §5]

12. **Tests pytest dédiés** — Étant donné `recyclique/api/tests/test_story_9_11_comptage_pieces_billets_backend.py`, quand la suite story est exécutée, alors elle couvre : référentiel 15 lignes, PUT/GET nominal, refus session fermée, `COMPTAGE_REQUIRED`, alignement `actual_amount`, snapshot enrichi, module off = legacy, non-régression D33 sur total grille. [Source : pattern 9.10 test-summary]

13. **Signaux PDF anomalie (contrat close)** — Étant donné une clôture réussie avec module actif, quand la réponse `closeSession` est émise, alors elle inclut `anomaly_close_sheet: boolean` et, si `true`, `close_sheet_pdf_url` (URL signée ou chemin GET documenté OpenAPI) ; les critères d'anomalie figés sont : `variance_cents ≠ 0`, |écart| > `CLOSE_VARIANCE_TOLERANCE`, seuil D33 dépassé, ou quantité `EUR_50000 > 0`. Si aucune anomalie, `anomaly_close_sheet: false` et pas d'URL. [Source : D-CPT-04 · 9.12 AC12]

## Hors scope (stories suivantes)

| Story | Périmètre exclu de 9.11 |
|-------|-------------------------|
| **9.12** | Wizard Peintre : panel grille, steppers, section « coupures rares », écran relecture, pictos SVG, génération PDF anomalie, CREOS `page-cashflow-close.json` |
| **9.13** | Schéma `comptage-pieces-billets.v1.json`, entrée registre `ACTIVE_MODULE_KEYS`, panneau `/admin/modules`, recette on/off site pilote |
| **9.10** | Refonte batch Paheko, comptes 658/758, seuil D33 (déjà livré) |
| **Epic 8** | Worker outbox, retry Paheko (inchangé) |
| **Balance / poids** | D-CPT-10 — phase ultérieure (aligné artefact HITL) |
| **Tag `v2.0.2` prod** | Gates Coordinateur, QA2 story, validation EC — hors DS seul |

## Tasks / Subtasks

### Backend — référentiel et DDL

- [x] Migration Alembic : table `cash_denominations` (seed 15 lignes) **ou** enum Python + table seed idempotente
- [x] Migration : table `cash_denomination_counts` (FK `cash_session_id`, unicité `(session, code)`, `quantity`, `unit_value_cents`, audit)
- [x] Modèle SQLAlchemy + repository / service dédié (`cash_denomination_service.py`)

### Backend — API

- [x] `GET /v1/cash-denominations` — liste référentiel (public authentifié caisse)
- [x] `GET /v1/cash-sessions/{id}/denomination-count` — lecture grille + totaux calculés
- [x] `PUT /v1/cash-sessions/{id}/denomination-count` — upsert grille (session ouverte)
- [x] Endpoint(s) dans `cash_sessions.py` ; schémas Pydantic `DenominationCount*V1`

### Backend — intégration clôture

- [x] Helper `is_comptage_module_required(db, site_id) -> bool` (lit `module-config` ; défauts pilote : `enabled`, `skip_allowed: false`, `require_denomination_grid: true` — tolérer seed test sans 9.13)
- [x] `validate_session_close` / `close_session_with_amounts` : si module requis → charger total grille, refuser `COMPTAGE_REQUIRED`, forcer `actual_amount`
- [x] `build_accounting_close_snapshot_v1` : paramètre optionnel `denomination_count_v1` ; bump `schema_version` **3** ou extension documentée backward-compatible
- [x] Extension réponse `closeSession` : `anomaly_close_sheet`, `close_sheet_pdf_url` (génération PDF backend ou stub documenté pour 9.12 — AC13)

### Contrats

- [x] `contracts/openapi/recyclique-api.yaml` — routes + schémas + codes erreur `COMPTAGE_REQUIRED`, `COMPTAGE_AMOUNT_MISMATCH`
- [x] Extension description `recyclique_cashSessions_closeSession` (précondition, dépréciation `actual_amount`)
- [x] `npm run generate` → `peintre-nano/src/generated/recyclique-api.ts` (contrat seul — **pas** de widget UI)

### Tests

- [x] `recyclique/api/tests/test_story_9_11_comptage_pieces_billets_backend.py`
- [x] Non-régression : `test_story_9_10_*`, `test_cash_session_close.py -k variance`
- [x] Test-summary : `_bmad-output/implementation-artifacts/tests/test-summary-story-9-11-comptage-pieces-billets-backend.md`

## Dev Notes

### État brownfield (pré-9.11)

- Clôture : `actual_amount` saisi manuellement dans `CashSessionClose` → `validate_session_close` → snapshot `closing.actual_cash_amount` [22.6]
- Module comptage : **spécifié** en 08-MOD, **non implémenté** en code (pas de table `cash_denomination_counts`)
- Registre modules : `comptage-pieces-billets` **absent** de `ACTIVE_MODULE_KEYS` (story **9.13**) — 9.11 peut lire `site_module_configs` via `ModuleConfigService` avec clé réservée documentée ou fixture test jusqu'à 9.13

### Référentiel dénominations (seed)

| code | libellé | type | unit_value_cents | display_default | display_order |
|------|---------|------|------------------|-----------------|---------------|
| EUR_50000 | 500 € | note | 50000 | **false** | 1 |
| EUR_20000 | 200 € | note | 20000 | true | 2 |
| EUR_10000 | 100 € | note | 10000 | true | 3 |
| EUR_5000 | 50 € | note | 5000 | true | 4 |
| EUR_2000 | 20 € | note | 2000 | true | 5 |
| EUR_1000 | 10 € | note | 1000 | true | 6 |
| EUR_500 | 5 € | note | 500 | true | 7 |
| EUR_200 | 2 € | coin | 200 | true | 8 |
| EUR_100 | 1 € | coin | 100 | true | 9 |
| EUR_050 | 50 c | coin | 50 | true | 10 |
| EUR_020 | 20 c | coin | 20 | true | 11 |
| EUR_010 | 10 c | coin | 10 | true | 12 |
| EUR_005 | 5 c | coin | 5 | true | 13 |
| EUR_002 | 2 c | coin | 2 | true | 14 |
| EUR_001 | 1 c | coin | 1 | true | 15 |

`display_default` sert le front **9.12** ; le backend **accepte** toutes les lignes dont `EUR_50000`.

### Formule théorique espèces (alignement 6.7 / 9.10)

```
theoretical_cash = initial_amount (fond) + total_sales + dons_ticket
```

Réutiliser `get_closing_preview` / `cash_signed_net_from_journal` selon présence journal 22.6 — **ne pas** inventer une seconde formule. Le comptage physique inclut le **fond** dans le tiroir (D-CPT-09) ; l'écart compare **total grille** vs **théorique complet**.

### Extension snapshot (proposition)

```json
"denomination_count_v1": {
  "total_counted_cents": 24730,
  "theoretical_cash_cents": 25000,
  "variance_cents": -270,
  "breakdown_revision": "sha256:…",
  "recorded_at": "2026-06-06T18:30:00Z",
  "breakdown": [
    {"code": "EUR_2000", "quantity": 10, "unit_value_cents": 2000, "line_total_cents": 20000}
  ]
}
```

`closing.cash_variance` reste en euros float pour compatibilité 9.10 ; valeurs dérivées cohérentes au centime près.

### Fichiers d'ancrage (priorité)

| Priorité | Fichier |
|----------|---------|
| 1 | `recyclique/api/src/recyclic_api/services/cash_session_service.py` |
| 2 | `recyclique/api/src/recyclic_api/services/cash_session_journal_snapshot.py` |
| 3 | `recyclique/api/src/recyclic_api/schemas/cash_session_close_snapshot.py` |
| 4 | `recyclique/api/src/recyclic_api/api/api_v1/endpoints/cash_sessions.py` |
| 5 | `recyclique/api/src/recyclic_api/services/cash_denomination_service.py` *(nouveau)* |
| 6 | `recyclique/api/src/recyclic_api/models/cash_denomination_count.py` *(nouveau)* |
| 7 | `recyclique/api/migrations/versions/s9_11_cash_denomination_counts.py` *(nouveau)* |
| 8 | `recyclique/api/src/recyclic_api/modules/module_config/service.py` |
| 9 | `contracts/openapi/recyclique-api.yaml` |
| 10 | `recyclique/api/src/recyclic_api/services/paheko_close_batch_builder.py` — **lecture seule** ; vérifier non-régression T3 |

### Chaîne processor (ne pas réécrire)

`close_session_with_amounts` → `build_accounting_close_snapshot_v1` → `enqueue_cash_session_close_outbox` → `paheko_close_batch_builder` — **enrichir** le snapshot, **ne pas** ajouter de POST Paheko par dénomination.

### Garde-fous

- Ne pas stocker les lignes de comptage dans JSON `module-config` (cookbook #7, 08-MOD §7.1)
- Ne pas modifier les indices batch 0–3 (9.10)
- Ne pas implémenter le wizard Peintre (9.12)
- Ne pas activer le module en prod sans 9.13 — tests seedent la config via API/DB
- Centimes en **integer** côté persistance ; conversion float uniquement aux frontières legacy `actual_amount`

### Testing / gates Story Runner

- **Pytest obligatoire vert** ; `timeout_sec` **≥ 330** (hérité plan post-9.6)
- Peloton minimal suggéré :
  - `pytest recyclique/api/tests/test_story_9_11_comptage_pieces_billets_backend.py`
  - `pytest recyclique/api/tests/test_story_9_10_liaison_paheko_cloture_caisse_v1.py`
  - `pytest recyclique/api/tests/test_cash_session_close.py -k variance`
  - `pytest recyclique/api/tests/test_story_22_7_paheko_close_batch_builder.py`
  - `pytest recyclique/api/tests/test_cash_session_close_arch02.py`
- OpenAPI : `npm run generate` sans erreur TypeScript
- Test-summary dédié avant passage **review**

### Stories prérequis (done)

| Clé | Apport |
|-----|--------|
| **6.7** | Clôture locale, wizard hôte, `closeSession` |
| **9.6** | API `module-config` par site |
| **9.10** | T3 658/758, D33 seuil, snapshot `closing.*` |
| **22.6** | Snapshot figé immutable |
| **22.7** | Batch Paheko multi-indices |

### Stories suivantes (non bloquantes pour dev 9.11)

| Clé | Apport |
|-----|--------|
| **9.12** | UI grille, relecture, PDF anomalie |
| **9.13** | Registre module + schéma JSON + admin activation |

### References

- [Source: `references/artefacts/2026-06-06_01_decisions-hitl-comptage-pieces-billets-pilote.md`](../../references/artefacts/2026-06-06_01_decisions-hitl-comptage-pieces-billets-pilote.md)
- [Source: `references/protocole-modules-recyclique/08-MOD-exemple-pilote-comptage-pieces-billets.md`](../../references/protocole-modules-recyclique/08-MOD-exemple-pilote-comptage-pieces-billets.md)
- [Source: `references/recherche/2026-06-06_comptage-pieces-billets-fermeture-caisse-ux-terrain_perplexity_reponse.md`](../../references/recherche/2026-06-06_comptage-pieces-billets-fermeture-caisse-ux-terrain_perplexity_reponse.md)
- [Source: `_bmad-output/implementation-artifacts/9-10-liaison-paheko-cloture-caisse-v1.md`](9-10-liaison-paheko-cloture-caisse-v1.md)
- [Source: `_bmad-output/implementation-artifacts/6-7-mettre-en-place-la-cloture-locale-exploitable-de-caisse.md`](6-7-mettre-en-place-la-cloture-locale-exploitable-de-caisse.md)
- [Source: `_bmad-output/implementation-artifacts/9-6-config-admin-simple-modules.md`](9-6-config-admin-simple-modules.md)
- [Source: `references/protocole-modules-recyclique/05-MOD-registre-module-key.md`](../../references/protocole-modules-recyclique/05-MOD-registre-module-key.md) §5.4

## Dev Agent Record

### Agent Model Used

Composer (DS sous-agent Story Runner)

### Debug Log References

- Pytest SQLite : `db_session.expire_all()` requis après POST close (session ORM stale).
- `npm run generate` : `contracts/openapi/generated/recyclique-api.ts` OK.

### Completion Notes List

- Migration `s9_11_cash_denomination_counts` : tables + seed 15 dénominations (D-CPT-01).
- Service `CashDenominationService` : UPSERT grille, totaux serveur, intégration clôture, snapshot `schema_version` 3.
- Codes erreur `COMPTAGE_REQUIRED` / `COMPTAGE_AMOUNT_MISMATCH` via `ConflictError` → enveloppe AR21.
- Peloton pytest 9.11 (11) + 9.10 (13) vert ; OpenAPI codegen OK.

### File List

- `recyclique/api/migrations/versions/s9_11_cash_denomination_counts.py`
- `recyclique/api/src/recyclic_api/models/cash_denomination.py`
- `recyclique/api/src/recyclic_api/schemas/cash_denomination.py`
- `recyclique/api/src/recyclic_api/services/cash_denomination_service.py`
- `recyclique/api/src/recyclic_api/schemas/cash_session_close_snapshot.py`
- `recyclique/api/src/recyclic_api/services/cash_session_journal_snapshot.py`
- `recyclique/api/src/recyclic_api/services/cash_session_service.py`
- `recyclique/api/src/recyclic_api/application/cash_session_closing.py`
- `recyclique/api/src/recyclic_api/application/cash_session_close_presentation.py`
- `recyclique/api/src/recyclic_api/schemas/cash_session.py`
- `recyclique/api/src/recyclic_api/api/api_v1/endpoints/cash_sessions.py`
- `recyclique/api/src/recyclic_api/api/api_v1/api.py`
- `recyclique/api/src/recyclic_api/api/api_v1/endpoints/__init__.py`
- `recyclique/api/src/recyclic_api/models/__init__.py`
- `recyclique/api/src/recyclic_api/services/paheko_close_batch_builder.py`
- `recyclique/api/tests/conftest.py`
- `recyclique/api/tests/test_story_9_11_comptage_pieces_billets_backend.py`
- `contracts/openapi/recyclique-api.yaml`
- `contracts/openapi/generated/recyclique-api.ts`
- `_bmad-output/implementation-artifacts/tests/test-summary-story-9-11-comptage-pieces-billets-backend.md`

## Change Log

| Date | Auteur | Changement |
|------|--------|------------|
| 2026-06-06 | DS (BMAD) | Implémentation backend 9.11 — endpoints, persistance, snapshot v3, tests ; statut **review** |
| 2026-06-06 | create-story (BMAD) | Création story **9.11** — backend + contrats + persistance comptage ; statut **ready-for-dev** ; décisions HITL PO 2026-06-06 intégrées |
