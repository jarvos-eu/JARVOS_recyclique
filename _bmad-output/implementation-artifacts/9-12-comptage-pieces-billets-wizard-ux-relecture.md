# Story 9.12 : Comptage pièces/billets — wizard clôture UX + relecture (v2.0.2)

Status: done

**Story key :** `9-12-comptage-pieces-billets-wizard-ux-relecture`  
**Epic :** 9 — Modules complémentaires v2 (fil **comptage** post-9.10) · hôte UX **Epic 6** story **6.7** (done, extension seulement)  
**Module :** `comptage-pieces-billets` (workflow-step, optionnel par site)  
**Version produit cible :** **v2.0.2** (Peintre / CREOS ; backend = **9.11** ; activation admin = **9.13**)  
**Prérequis :** **9.11** **done** (gate levé 2026-06-06) — endpoints `denomination-count`, référentiel, codes `COMPTAGE_*`, champs `float_target_cents` / `withdraw_cents` / `anomaly_close_sheet` / `close_sheet_pdf_url` livrés ; codegen à jour.

## Story

En tant qu’**opératrice de caisse** (bénévolat terrain),  
je veux **compter le tiroir pièces/billets** dans le wizard de clôture avec une **grille guidée**, une **vérification théorique vs compté**, une **relecture obligatoire** et des **pictos optionnels**,  
afin de **clôturer localement** avec une seule vérité comptée (grille) tout en comprenant que **Recyclique enregistré ≠ Paheko OK** (Story **6.9**).

## Décisions PO Strophe (2026-06-06) — obligatoires (périmètre UX)

| ID | Sujet | Décision | Impact 9.12 |
|----|-------|----------|-------------|
| **D-CPT-01** | Coupures rares | **500 € seul** dans la section « coupures rares » (repliée / masquée par défaut). **200 €** dans la grille principale. | Panel grille § rares |
| **D-CPT-02** | Soirée sans ventes espèces | **Toujours** compter tout le tiroir (fond inclus) — pas de raccourci sans grille. | Pas de skip UI si module actif + `skip_allowed: false` |
| **D-CPT-03** | Historique | Détail comptage consultable après clôture — **pas** de PDF systématique. | Écran succès sans PDF par défaut |
| **D-CPT-04** | PDF | PDF feuille de clôture **uniquement sur anomalie** (écart, seuil D33, coupure rare signalée, etc.). | Bouton / auto-download conditionnel post-close |
| **D-CPT-05** | Relecture | Écran de **relecture obligatoire** avant PIN — **même si tout colle**. | Panel dédié non skippable |
| **D-CPT-06** | Pictos | Images **stylisées** ; option module **`show_images`** : afficher ou masquer. | Assets SVG + lecture config |
| **D-CPT-07** | Pilote | Module actif → **`skip_allowed: false`**, grille complète requise. | Pas de bouton « passer » en pilote |
| **D-CPT-08** | Vérité comptée | **Total grille = seule source de vérité** ; pas de second montant global saisi à la main. | Retirer `NumberInput actual_amount` si module on |
| **D-CPT-09** | Fond de caisse | Tout compter dans la grille (fond inclus) ; fond à laisser / à retirer = **calculs dérivés** affichés au panel vérification. | Panel « Vérifier » |
| **D-CPT-10** | Poids | **Hors V1** — comptage unitaire uniquement. | Hors scope |

Sources : [`references/artefacts/2026-06-06_01_decisions-hitl-comptage-pieces-billets-pilote.md`](../../references/artefacts/2026-06-06_01_decisions-hitl-comptage-pieces-billets-pilote.md) · recherche Perplexity · fiche [`08-MOD`](../../references/protocole-modules-recyclique/08-MOD-exemple-pilote-comptage-pieces-billets.md) §5.

## Contexte chantier

| Bloc | Statut | Référence |
|------|--------|-----------|
| Wizard clôture hôte | **Fait** (6.7) | `CashflowCloseWizard.tsx` — 3 panels (récap / montant manuel / PIN) |
| Défensive sync / local ≠ Paheko | **Fait** (6.9) | `CashflowOperationalSyncNotice`, `RELAY_EPIC8_COPY` |
| Backend comptage + snapshot | **Story 9.11** | `denomination-count`, `COMPTAGE_REQUIRED`, snapshot `denomination_count_v1` |
| Activation module admin | **Story 9.13** | `comptage-pieces-billets.v1.json`, registre `ACTIVE_MODULE_KEYS` |
| CREOS page clôture | **Existant** | `contracts/creos/manifests/page-cashflow-close.json` |
| Batch Paheko T1–T3 + D33 | **Fait** (9.10) | Inchangé — UI consomme seuil / 422 |

**Positionnement :** extension **Peintre-only** du wizard existant quand `module-config` signale `enabled: true` ; **parité legacy** préservée quand module **off** (flux 6.7 inchangé : saisie `actual_amount` manuelle).

## Ordre de lecture obligatoire (session dev)

1. [`references/artefacts/2026-06-06_01_decisions-hitl-comptage-pieces-billets-pilote.md`](../../references/artefacts/2026-06-06_01_decisions-hitl-comptage-pieces-billets-pilote.md)
2. [`_bmad-output/implementation-artifacts/9-11-comptage-pieces-billets-contrats-backend-persistance.md`](9-11-comptage-pieces-billets-contrats-backend-persistance.md) — contrats consommés par le front
3. [`references/protocole-modules-recyclique/08-MOD-exemple-pilote-comptage-pieces-billets.md`](../../references/protocole-modules-recyclique/08-MOD-exemple-pilote-comptage-pieces-billets.md) — **§5** insertion wizard, **§9** CREOS / `operation_id`
4. [`references/recherche/2026-06-06_comptage-pieces-billets-fermeture-caisse-ux-terrain_perplexity_reponse.md`](../../references/recherche/2026-06-06_comptage-pieces-billets-fermeture-caisse-ux-terrain_perplexity_reponse.md) — wireframe 7 étapes, 4 règles terrain, pattern hybride
5. [`_bmad-output/implementation-artifacts/6-7-mettre-en-place-la-cloture-locale-exploitable-de-caisse.md`](6-7-mettre-en-place-la-cloture-locale-exploitable-de-caisse.md)
6. [`_bmad-output/implementation-artifacts/6-9-rendre-la-caisse-defensive-face-aux-erreurs-fallbacks-et-sync-differee.md`](6-9-rendre-la-caisse-defensive-face-aux-erreurs-fallbacks-et-sync-differee.md) — copy local / différé / bloqué
7. [`contracts/creos/manifests/page-cashflow-close.json`](../../contracts/creos/manifests/page-cashflow-close.json)
8. [`references/protocole-modules-recyclique/04-MOD-protocole-front-creos.md`](../../references/protocole-modules-recyclique/04-MOD-protocole-front-creos.md) — §8.2 workflow-step, B4 `data_contract`

## Parcours wizard cible (module activé)

Aligné wireframe Perplexity §2 et **08-MOD §5.2**, avec relecture D-CPT-05 explicite :

| # | Panel | Rôle | `operationId` OpenAPI (data_contract) |
|---|-------|------|----------------------------------------|
| 1 | **Récap session** | Fond ouverture, ventes espèces, remboursements, dons caisse, théorique clôture (serveur) | `recyclique_cashSessions_getCurrent` (existant) |
| 2 | **Grille comptage** | Saisie hybride qty (+/− + champ numérique), billets puis pièces, total live ; section repliée **« Coupures rares »** (500 € seul) ; 4 règles affichées ; pictos si `show_images` | `recyclique_cashSessions_upsertDenominationCount` |
| 3 | **Vérifier** | Côte à côte : théorique, compté (grille), écart, **fond cible à laisser**, **montant à retirer** (dérivés serveur) | `recyclique_cashSessions_getDenominationCount` |
| 4 | **Qualifier l’écart** | Si écart = 0 → continuer ; sinon commentaire obligatoire (tolérance 0,05 € + seuil D33 message API) | (lecture totaux serveur — pas de calcul client) |
| 5 | **Relecture obligatoire** | Résumé compact : identité clôturant, heure, totaux, rappel « le total de la grille fera foi » — **non skippable** | `recyclique_cashSessions_getDenominationCount` |
| 6 | **PIN step-up** | PIN métier ; message renforcé si seuil D33 dépassé ou 500 € présent | — |
| 7 | **Clôture + succès** | POST close ; copy **6.9** ; PDF anomalie si flag / endpoint ; **pas** « compta OK » | `recyclique_cashSessions_closeSession` |

**Module désactivé :** conserver le parcours **6.7** actuel (3 panels : récap → `actual_amount` manuel + commentaire → PIN) — Q-HITL-09 parité legacy.

## Acceptance Criteria

1. **Montage conditionnel module** — Étant donné un site avec `GET module-config/comptage-pieces-billets` retournant `enabled: false` (ou module absent), quand l’opératrice ouvre `cashflow-close`, alors le wizard affiche le flux **legacy 6.7** (saisie `actual_amount` manuelle) **sans** panel grille ni étape relecture module. [Source : 08-MOD §4.3 · Q-HITL-09]

2. **Montage module activé** — Étant donné `enabled: true` et backend 9.11 livré, quand l’opératrice ouvre la clôture, alors les **7 panels** ci-dessus sont proposés dans l’ordre ; le panel grille appelle `GET /v1/cash-denominations` (ou référentiel inclus dans `GET denomination-count`) pour ordonner les lignes (billets décroissants puis pièces). [Source : Perplexity §1 tableau · 9.11 AC1]

3. **Grille — saisie hybride** — Étant donné le panel comptage, quand l’opératrice modifie une quantité via **steppers +/−**, **champ numérique**, ou **remise à zéro**, alors le **total compté** affiché est recalculé **à partir des quantités locales** pour feedback immédiat, puis **réconcilié** avec `total_counted_cents` serveur après `PUT denomination-count` ; boutons tactiles ≥ **44 px** ; contraste net **1 € / 2 €**. [Source : Perplexity §B · D-CPT-08]

4. **Coupures rares — 500 € seul** — Étant donné le référentiel 15 lignes, quand le panel grille s’affiche, alors **EUR_50000** est dans une section **« Coupures rares »** repliée par défaut ; **EUR_20000** reste dans la grille principale visible. [Source : D-CPT-01]

5. **Absence saisie montant global manuel** — Étant donné le module activé, quand le panel comptage ou vérification est affiché, alors le champ **`NumberInput` « Montant compté (€) »** (`data-testid="cashflow-close-actual-amount"`) est **absent** ; le total affiché provient **uniquement** de la grille. [Source : D-CPT-08 · Perplexity P0]

6. **Persistance grille avant close** — Étant donné des quantités saisies, quand l’opératrice avance au panel « Vérifier », alors un **`PUT denomination-count`** a été exécuté (debounce ou blur explicite documenté) et les totaux **théorique / compté / écart** proviennent de la **réponse serveur** (`GET denomination-count`), pas d’une formule recalculée côté Peintre. [Source : 08-MOD B4.3 · 9.11 AC3]

7. **Panel vérification — fond et retrait** — Étant donné une réponse `denomination-count` valide, quand le panel « Vérifier » s’affiche, alors l’UI expose : montant théorique espèces, total compté grille, écart, **fond cible à laisser**, **montant à retirer** (champs dérivés fournis par l’API 9.11 ou calculés serveur dans la même réponse — **interdiction** de dériver le fond cible uniquement client). [Source : D-CPT-09 · Perplexity §3]

8. **Commentaire d’écart** — Étant donné |écart| &gt; `CLOSE_VARIANCE_TOLERANCE` (0,05 €) ou règle existante `needsVarianceComment`, quand l’opératrice atteint le panel « Qualifier l’écart », alors le commentaire est **obligatoire** avant relecture ; si l’API renvoie **422** seuil D33, le message affiche le **seuil site** (pattern 9.10 AC10). [Source : 9.10 · 6.7]

9. **Relecture obligatoire** — Étant donné un parcours module activé, quand l’opératrice atteint le panel « Relecture », alors elle **doit** confirmer explicitement (bouton « J’ai relu » / équivalent) avant d’accéder au PIN — **aucun** raccourci même si écart = 0. [Source : D-CPT-05]

10. **4 règles terrain visibles** — Étant donné le panel grille (module on), quand l’écran est affiché, alors les **4 règles** suivantes sont visibles en permanence (bandeau ou encart) : « Comptez tout le tiroir, fond compris » · « Saisissez des quantités, jamais des montants » · « Le total de la grille fait foi » · « Commentez tout écart ou coupure rare ». [Source : Perplexity §D]

11. **Pictos stylisés (`show_images`)** — Étant donné `module-config.payload.show_images: true`, quand la grille s’affiche, alors chaque ligne montre un picto SVG depuis `peintre-nano/public/assets/cash-denominations/` ; si `false` ou absent, affichage **texte + valeur** seulement. Les assets sont **stylisés** (forme générique + libellé) — **pas** de photo réaliste de billets (BCE). Un **`README.md`** dans le dossier assets documente sources / licences (UXWing, Noun Project, etc.). [Source : D-CPT-06 · artefact HITL §Visuels]

12. **PDF anomalie uniquement** — Étant donné une clôture réussie, quand la réponse `closeSession` (ou champ dédié 9.11) indique **anomalie** (écart non nul, seuil, présence EUR_50000, etc.), alors l’UI propose **téléchargement / génération PDF** (appel endpoint backend documenté OpenAPI ou URL fournie dans la réponse) ; quand **aucune anomalie**, alors **aucun** PDF n’est proposé automatiquement (historique consultable en admin — D-CPT-03). [Source : D-CPT-04]

13. **Copy Story 6.9 — succès local** — Étant donné une clôture **200** locale, quand l’écran succès s’affiche, alors le libellé confirme **« Session close dans Recyclique »** et le relais Epic 8 réutilise / étend le patron **6.9** (`RELAY_EPIC8_COPY`, `CashflowOperationalSyncNotice`) — **jamais** « compta OK » ou « synchronisé Paheko ». [Source : 6.9 AC1 · 08-MOD C.4]

14. **Garde-fous existants préservés** — Étant donné `DATA_STALE`, session absente, `CASH_SESSION_CLOSE_HELD_PENDING`, ou contexte `forbidden` / `degraded`, alors les blocages **6.7 / 6.9** restent effectifs sur la clôture finale (PIN panel). [Source : 6.9 AC4]

15. **CREOS — `data_contract.operation_id`** — Étant donné `page-cashflow-close.json` et le widget `cashflow-close-wizard` étendu, quand les manifests / props documentent les panels critiques, alors chaque panel consommant l’API expose un `data_contract.operation_id` **identique caractère pour caractère** à l’OpenAPI (`recyclique_cashSessions_getDenominationCount`, `recyclique_cashSessions_upsertDenominationCount`, `recyclique_cashSessions_closeSession`, etc.) ; `critical: true` sur totaux et comptage. [Source : 08-MOD §9.1 B4 · 04-MOD §5]

16. **Codes erreur comptage** — Étant donné module actif et grille vide, quand l’opératrice tente de clôturer, alors l’UI affiche le code / message **`COMPTAGE_REQUIRED`** (ou `COMPTAGE_AMOUNT_MISMATCH`) renvoyé par l’API sans le masquer. [Source : 9.11 AC5–6]

17. **Tests Vitest** — Étant donné la story fermée, quand `npm test` / `vitest` s’exécute sur Peintre, alors les suites **unit** et **e2e** cashflow-close couvrent : module off = legacy ; module on = grille + relecture ; absence `actual_amount` ; 500 € section rares ; PDF proposé seulement sur anomalie (mock réponse) ; copy 6.9 sur succès. [Source : pattern 6.7 / 6.9 tests]

## Hors scope (stories adjacentes / futur)

| Périmètre | Story / note |
|----------|----------------|
| Tables SQL, endpoints `denomination-count`, snapshot backend | **9.11** |
| Schéma JSON module, registre, panneau admin activation | **9.13** |
| Comptage par **poids / balance** | D-CPT-10 — phase ultérieure |
| Batch Paheko T3, comptes 658/758, seuil D33 backend | **9.10** (consommation messages seulement) |
| Worker outbox, UI quarantaine complète | Epic **8** |
| Tag **`v2.0.2` prod** | Gates Coordinateur, QA2, CR |

## Tasks / Subtasks

### Prérequis / gate

- [x] Vérifier **9.11 done** : OpenAPI à jour, `npm run generate`, endpoints testés en local
- [x] Fixture test : activer module via API/DB (en attendant **9.13**) pour dev et tests

### Assets pictos (D-CPT-06)

- [x] Créer `peintre-nano/public/assets/cash-denominations/` — 15 SVG stylisés (EUR_001 … EUR_50000)
- [x] Rédiger `peintre-nano/public/assets/cash-denominations/README.md` — sources, licences commerciales, **pas** de reproduction photographique BCE
- [x] Mapping code → fichier asset (convention nommage stable ex. `EUR_2000.svg`)

### Client API Peintre

- [x] Étendre `peintre-nano/src/api/cash-session-client.ts` : `getCashDenominations`, `getDenominationCount`, `putDenominationCount`
- [x] Lire `module-config/comptage-pieces-billets` (hook ou helper partagé) — `enabled`, `show_images`, `skip_allowed`
- [x] Gérer codes `COMPTAGE_REQUIRED`, `COMPTAGE_AMOUNT_MISMATCH`, 422 D33 (réutiliser `cashSessionCloseFailureMessage`)

### Composants wizard

- [x] Extraire / créer `CashflowDenominationGridPanel.tsx` — grille hybride, total live, section « Coupures rares »
- [x] Créer `CashflowDenominationRulesBanner.tsx` — 4 règles Perplexity
- [x] Créer `CashflowCloseVerifyPanel.tsx` — théorique / compté / écart / fond / retrait
- [x] Créer `CashflowCloseReviewPanel.tsx` — relecture obligatoire D-CPT-05
- [x] Refactor `CashflowCloseWizard.tsx` : branche `moduleEnabled` → 7 panels vs legacy 3 panels
- [x] `closeSession` : envoyer `actual_amount` **dérivé** du total grille (serveur autoritaire) ou omettre si API 9.11 l’infère

### PDF anomalie (D-CPT-04)

- [x] Consommer flag / URL post-close (`anomaly_close_sheet`, `close_sheet_pdf_url` — contrat 9.11 AC13)
- [x] Bouton téléchargement sur écran succès **uniquement** si anomalie ; pas de génération PDF côté navigateur sans contrat

### CREOS / contrats front

- [x] Mettre à jour `contracts/creos/manifests/page-cashflow-close.json` — body header mentionnant module comptage optionnel
- [x] Documenter panels / `data_contract` dans props widget ou manifest extension (pattern Epic 4 / 6.7)
- [x] Tests contrat : `peintre-nano/tests/contract/creos-cashflow-close-*.test.ts` si pattern existant

### Styles / accessibilité

- [x] CSS module ou Mantine : grille tactile, distinction 1 € / 2 €, section repliée rares
- [x] `data-testid` stables pour e2e (grille, rares, relecture, pdf-anomaly)

### Tests

- [x] Étendre `peintre-nano/tests/unit/cashflow-close-6-7.test.tsx` — non-régression legacy
- [x] Nouveau `peintre-nano/tests/unit/cashflow-close-denomination-9-12.test.tsx` — grille, règles, relecture
- [x] Étendre `peintre-nano/tests/e2e/cashflow-close-6-7.e2e.test.tsx` (ou fichier `*-9-12.e2e.test.tsx`) — parcours module on complet (mock API)
- [x] Test-summary : `_bmad-output/implementation-artifacts/tests/test-summary-story-9-12-comptage-pieces-billets-wizard-ux.md`

## Dev Notes

### État brownfield (pré-9.12)

- `CashflowCloseWizard.tsx` : **3 tabs** — récap → `NumberInput actual_amount` + commentaire → PIN → POST close
- Pas de dossier `cash-denominations/` assets
- Pas d’appel `denomination-count` côté Peintre
- `page-cashflow-close.json` : widget `cashflow-close-wizard` sans props module

### Branchement module (signal autoritaire)

Lire **`GET /v1/sites/{site_id}/module-config/comptage-pieces-billets`** (9.6) — **ne pas** se baser sur `localStorage`. Si 9.13 n’est pas livré, tests seedent la config via API admin ou fixture MSW.

Payload UX pertinent :

| Clé | Usage 9.12 |
|-----|------------|
| `enabled` | Monte le parcours 7 panels |
| `show_images` | Affiche pictos SVG |
| `skip_allowed` | Pilote = `false` → pas de bouton passer (D-CPT-07) |

### Pattern saisie hybride (Perplexity)

Pour chaque ligne : libellé (+ picto optionnel), **NumberInput** centré, boutons **−** / **+** larges, action « remettre à 0 » accessible. Debounce **PUT** (ex. 400–600 ms après dernière modification) ou flush explicite à « Continuer » — **documenter le choix** dans le PR ; éviter un PUT par clic stepper.

### Calculs affichés panel « Vérifier »

Attendu côté réponse `GET denomination-count` (9.11) :

- `theoretical_cash_cents`
- `total_counted_cents`
- `variance_cents`
- `float_target_cents` (fond à laisser — nom exact OpenAPI)
- `withdraw_cents` (montant à retirer)

Si les champs dérivés ne sont pas encore dans 9.11, **NEEDS_HITL** avec le dev 9.11 — **interdit** de recalculer le fond cible en front (D-CPT-09, B4.3).

### Copy 6.9 — références code

Réutiliser :

- `RELAY_EPIC8_COPY` dans `CashflowCloseWizard.tsx`
- `CashflowOperationalSyncNotice` en tête de wizard
- Patron « enregistré dans Recyclique » vs sync Paheko (`cashflow-draft-store`, `cashflow-operational-sync-notice.tsx`)

Ne **pas** afficher d’état FR24 simulé ; message honnête si sync inconnue.

### PDF anomalie

**Préférence :** backend génère le PDF (9.11 expose endpoint ou URL signée) ; Peintre déclenche le download. Critères anomalie alignés D-CPT-04 : écart ≠ 0, |écart| &gt; tolérance, seuil D33, quantité EUR_50000 &gt; 0, etc. — liste exacte figée avec réponse `closeSession` 9.11.

### Fichiers d’ancrage (priorité)

| Priorité | Fichier |
|----------|---------|
| 1 | `peintre-nano/src/domains/cashflow/CashflowCloseWizard.tsx` |
| 2 | `peintre-nano/src/api/cash-session-client.ts` |
| 3 | `peintre-nano/src/domains/cashflow/CashflowClientErrorAlert.tsx` |
| 4 | `peintre-nano/src/domains/cashflow/cashflow-operational-sync-notice.tsx` |
| 5 | `peintre-nano/src/generated/recyclique-api.ts` (post-codegen 9.11) |
| 6 | `contracts/creos/manifests/page-cashflow-close.json` |
| 7 | `peintre-nano/tests/unit/cashflow-close-6-7.test.tsx` |
| 8 | `peintre-nano/tests/e2e/cashflow-close-6-7.e2e.test.tsx` |
| 9 | `peintre-nano/public/assets/cash-denominations/` *(nouveau)* |

### Garde-fous

- **Ne pas** implémenter persistance SQL ni routes API (9.11)
- **Ne pas** ajouter activation admin UI (9.13)
- **Ne pas** recalculer écart / théorique / fond cible uniquement client (B4.3)
- **Ne pas** casser le flux legacy module off (Q-HITL-09)
- **Ne pas** utiliser photos de billets réalistes (BCE / D-CPT-06)
- Conserver step-up PIN et idempotence existants sur `closeSession`

### Testing / gates Story Runner

- **Vitest obligatoire vert** sur fichiers touchés
- Peloton minimal suggéré :
  - `npm run test -- peintre-nano/tests/unit/cashflow-close-6-7.test.tsx`
  - `npm run test -- peintre-nano/tests/unit/cashflow-close-denomination-9-12.test.tsx`
  - `npm run test -- peintre-nano/tests/e2e/cashflow-close-6-7.e2e.test.tsx` (ou suite 9-12)
  - `npm run lint` / `npm run build` dans `peintre-nano`
- Non-régression : `cashflow-stale-close-6-9.test.tsx` si stale touche le wizard
- Test-summary dédié avant passage **review**
- **Prérequis bloquant :** pytest 9.11 vert en CI

### Stories prérequis

| Clé | Apport | Statut attendu |
|-----|--------|----------------|
| **6.7** | Wizard hôte clôture | done |
| **6.9** | Copy local ≠ Paheko, DATA_STALE | done |
| **9.10** | Messages seuil D33 | done |
| **9.11** | API comptage, snapshot, codes erreur | **done** (gate) |
| **9.6** | Lecture module-config | done |

### Stories suivantes

| Clé | Apport |
|-----|--------|
| **9.13** | Activation module site pilote, schéma JSON `show_images` |

### References

- [Source: `references/artefacts/2026-06-06_01_decisions-hitl-comptage-pieces-billets-pilote.md`](../../references/artefacts/2026-06-06_01_decisions-hitl-comptage-pieces-billets-pilote.md)
- [Source: `references/protocole-modules-recyclique/08-MOD-exemple-pilote-comptage-pieces-billets.md`](../../references/protocole-modules-recyclique/08-MOD-exemple-pilote-comptage-pieces-billets.md) — §5, §9
- [Source: `references/recherche/2026-06-06_comptage-pieces-billets-fermeture-caisse-ux-terrain_perplexity_reponse.md`](../../references/recherche/2026-06-06_comptage-pieces-billets-fermeture-caisse-ux-terrain_perplexity_reponse.md)
- [Source: `_bmad-output/implementation-artifacts/9-11-comptage-pieces-billets-contrats-backend-persistance.md`](9-11-comptage-pieces-billets-contrats-backend-persistance.md)
- [Source: `_bmad-output/implementation-artifacts/6-9-rendre-la-caisse-defensive-face-aux-erreurs-fallbacks-et-sync-differee.md`](6-9-rendre-la-caisse-defensive-face-aux-erreurs-fallbacks-et-sync-differee.md)
- [Source: `contracts/creos/manifests/page-cashflow-close.json`](../../contracts/creos/manifests/page-cashflow-close.json)

## Dev Agent Record

### Agent Model Used

Composer (DS subagent Story Runner BMAD)

### Debug Log References

- Debounce PUT denomination-count : **500 ms** (`DENOMINATION_PUT_DEBOUNCE_MS`) + flush explicite au clic « Continuer vers la vérification ».
- Tests module on : mock fetch avec `headers.get` pour compatibilité `parseEtagFromResponse`.

### Completion Notes List

- Extension Peintre `CashflowCloseWizard` : branche `moduleEnabled` (6 panels) vs legacy 3 panels ; totaux dérivés serveur uniquement.
- 15 SVG stylisés + README ; hook `useComptageModuleConfig` ; panels grille / vérif / relecture / PDF anomalie.
- **19 tests PASS** (unit 6.7 + 9.12, e2e 6.7, contract CREOS) ; `tsc -b` vert.
- DS re-vérification Story Runner : **23 tests PASS** (incl. `cashflow-close-denomination-9-12.e2e.test.tsx`) ; AC D-CPT-05/06, 7 étapes wizard, legacy off OK.

### File List

- `peintre-nano/src/api/cash-session-client.ts`
- `peintre-nano/src/api/comptage-module-config.ts`
- `peintre-nano/src/domains/cashflow/CashflowCloseWizard.tsx`
- `peintre-nano/src/domains/cashflow/CashflowCloseWizard.module.css`
- `peintre-nano/src/domains/cashflow/CashflowDenominationGridPanel.tsx`
- `peintre-nano/src/domains/cashflow/CashflowDenominationRulesBanner.tsx`
- `peintre-nano/src/domains/cashflow/CashflowCloseVerifyPanel.tsx`
- `peintre-nano/src/domains/cashflow/CashflowCloseReviewPanel.tsx`
- `peintre-nano/src/domains/cashflow/cash-denomination-asset.ts`
- `peintre-nano/public/assets/cash-denominations/` (15 SVG + README.md)
- `peintre-nano/scripts/gen-cash-denomination-svgs.mjs`
- `peintre-nano/tests/unit/cashflow-close-denomination-9-12.test.tsx`
- `peintre-nano/tests/e2e/cashflow-close-denomination-9-12.e2e.test.tsx`
- `peintre-nano/tests/unit/fixtures/cash-denominations-api.ts`
- `peintre-nano/tests/contract/creos-cashflow-close-manifests-9-12.test.ts`
- `contracts/creos/manifests/page-cashflow-close.json`
- `contracts/creos/manifests/widgets-catalog-cashflow-close.json`
- `_bmad-output/implementation-artifacts/tests/test-summary-story-9-12-comptage-pieces-billets-wizard-ux.md`

## Change Log

| Date | Auteur | Changement |
|------|--------|------------|
| 2026-06-06 | create-story (BMAD) | Création story **9.12** — wizard Peintre comptage, relecture, pictos, PDF anomalie ; statut **backlog** (bloqué par **9.11**) ; décisions HITL D-CPT-01 à D-CPT-10 intégrées |
| 2026-06-06 | validate-story (VS) | **PASS** — alignement epics §9.12, HITL D-CPT-05/06, dépendance **9.11 done** ; statut **ready-for-dev** ; correction nommage `anomaly_close_sheet` |
| 2026-06-06 | dev-story (DS) | Implémentation Peintre wizard comptage 6 panels + legacy ; assets SVG ; tests 19 PASS ; statut **review** |
| 2026-06-06 | Story Runner (VS→DS→gates→QA→CR) | **done** — gates lint/13 tests/build PASS ; QA 29 tests ; CR APPROVE_WITH_NOTES (should_fix non bloquants : CREOS operation_id, operatorLabel relecture) |
| 2026-06-06 | dev-story (DS re-vérif) | Re-vérification tasks/AC vs code : **PASS** ; 23 tests Vitest locaux verts ; statut **review** inchangé |
