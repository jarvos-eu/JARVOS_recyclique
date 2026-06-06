# Story 9.13 : Comptage pièces/billets — schéma module-config, activation admin et recette (v2.0.2)

Status: done

**Story key :** `9-13-comptage-pieces-billets-activation-schema-recette`  
**Epic :** 9 — Modules complémentaires v2 (fil **comptage** post-9.10) · hôte UX **Epic 6** story **6.7** (done)  
**Module :** `comptage-pieces-billets` (workflow-step, optionnel par site)  
**Version produit cible :** **v2.0.2** (activation + recette ; backend métier = **9.11** ; wizard = **9.12**)

## Story

En tant que **super-admin / responsable site (La Clique pilote)**,  
je veux **activer et paramétrer** le module `comptage-pieces-billets` via le **registre modules** et le panneau **`/admin/modules`**, avec une **recette documentée** module on/off,  
afin de **basculer** le site pilote sur le flux grille complet **sans** casser la **parité legacy** pour les sites où le module reste désactivé.

## Décisions PO Strophe (2026-06-06) — obligatoires

| ID | Sujet | Décision | Impact story 9.13 |
|----|-------|----------|-------------------|
| **D-CPT-06** | Images pièces/billets | **Oui en V1** — pictos **stylisés** ; option module **`show_images`** (afficher / masquer). **Plus tard** : personnalisation visuels par dénomination. | Champ `show_images` dans schéma JSON + toggle admin ; **pas** d’UI upload custom (hors scope). |
| **D-CPT-07** | Comptage obligatoire pilote | Module activé → **`skip_allowed: false`**, grille complète requise (`require_denomination_grid: true`). | Valeurs **figées** pour seed site pilote La Clique ; admin peut les lire mais **ne doit pas** proposer skip en prod pilote sans décision PO. |

Sources : [`references/artefacts/2026-06-06_01_decisions-hitl-comptage-pieces-billets-pilote.md`](../../references/artefacts/2026-06-06_01_decisions-hitl-comptage-pieces-billets-pilote.md) · fiche [`08-MOD`](../../references/protocole-modules-recyclique/08-MOD-exemple-pilote-comptage-pieces-billets.md) §4.2 · recette HITL **Q-HITL-09** / **Q-HITL-11**.

## Contexte chantier

| Bloc | Statut | Référence |
|------|--------|-----------|
| API `module-config` + shell `/admin/modules` | **Fait** (9.6) | `ModuleConfigService`, `AdminModulesWidget` |
| Backend comptage + persistance | **Story 9.11** | `denomination-count`, `COMPTAGE_REQUIRED`, snapshot enrichi |
| Wizard grille + relecture + pictos | **Story 9.12** | `CashflowCloseWizard`, assets SVG |
| Schéma `comptage-pieces-billets.v1.json` | **Fait** (9.13) | `config-modules-site-id/schemas/` |
| Registre `ACTIVE_MODULE_KEYS` | **Fait** (9.13) | `registry.py` — clé `comptage-pieces-billets` active |
| Site pilote La Clique — config module | **Fait** (9.13) | Migration `s9_13_*` + procédure ops documentée |
| Recette Q-HITL-09 / Q-HITL-11 | **Fait** (9.13) | Matrice module off/on (pytest + e2e) |

**Positionnement :** cette story **ne code pas** la grille ni les endpoints métier (9.11) ni le wizard Peintre (9.12). Elle **promou** `comptage-pieces-billets` au rang de module **actif** dans la chaîne 9.6, publie le contrat config, étend l’admin, seed le pilote et **valide** la recette on/off.

## Dépendances

| Story | Relation | Apport requis |
|-------|----------|---------------|
| **9.6** | **done** | Pattern `kpi-live-banner` : GET/PATCH, ETag, `/admin/modules`, tests `test_module_config_site.py` |
| **9.10** | **done** | Clôture legacy + D33 inchangés quand module **off** |
| **9.11** | **done** | `is_comptage_module_required()`, codes `COMPTAGE_*`, lecture `module-config` côté close |
| **9.12** | **done** | Wizard complet (grille, relecture, `show_images` côté UI) — recette flux complet exécutable |

**Ordre d’exécution recommandé :** 9.11 → 9.12 → **9.13** (ou 9.13 en parallèle de fin 9.12 si recette finale différée).

## Ordre de lecture obligatoire (session dev)

1. [`references/artefacts/2026-06-06_01_decisions-hitl-comptage-pieces-billets-pilote.md`](../../references/artefacts/2026-06-06_01_decisions-hitl-comptage-pieces-billets-pilote.md)
2. [`_bmad-output/implementation-artifacts/9-11-comptage-pieces-billets-contrats-backend-persistance.md`](9-11-comptage-pieces-billets-contrats-backend-persistance.md)
3. [`_bmad-output/implementation-artifacts/9-12-comptage-pieces-billets-wizard-ux-relecture.md`](9-12-comptage-pieces-billets-wizard-ux-relecture.md)
4. [`_bmad-output/implementation-artifacts/9-6-config-admin-simple-modules.md`](9-6-config-admin-simple-modules.md) — pattern extension catalogue modules
5. [`references/protocole-modules-recyclique/05-MOD-registre-module-key.md`](../../references/protocole-modules-recyclique/05-MOD-registre-module-key.md) §5.4 · §3.2
6. [`references/protocole-modules-recyclique/08-MOD-exemple-pilote-comptage-pieces-billets.md`](../../references/protocole-modules-recyclique/08-MOD-exemple-pilote-comptage-pieces-billets.md) — §4.2 config étroite · §10 Phase D/E · Q-HITL-09/11
7. [`references/config-modules-site-id/schemas/README.md`](../../references/config-modules-site-id/schemas/README.md)
8. [`references/protocole-modules-recyclique/06-MOD-cookbook-nouveau-module-optionnel.md`](../../references/protocole-modules-recyclique/06-MOD-cookbook-nouveau-module-optionnel.md) — loup de mer **#7** (pas de compta dans JSON config)

## Acceptance Criteria

1. **Schéma JSON publié** — Étant donné le fichier [`references/config-modules-site-id/schemas/comptage-pieces-billets.v1.json`](../../references/config-modules-site-id/schemas/comptage-pieces-billets.v1.json), quand il est validé par le handler `module-config`, alors il définit `schema_version` **1.0.0** et un `payload` avec **exactement** les propriétés : `enabled` (boolean), `skip_allowed` (boolean), `require_denomination_grid` (boolean), `show_images` (boolean) ; `additionalProperties: false` ; les quatre champs **required**. [Source : Q-HITL-12 · D-CPT-06/07 · 08-MOD §4.2]

2. **Registre serveur — promotion actif** — Étant donné `recyclique/api/.../module_config/registry.py`, quand `comptage-pieces-billets` est ajouté à `ACTIVE_MODULE_KEYS` et `_REGISTRY`, alors `GET/PATCH /v1/sites/{site_id}/module-config/comptage-pieces-billets` répond **200** (et non **404**) pour un admin autorisé ; une clé inconnue reste **404**. [Source : 05-MOD §3.1 · T-MOD-5]

3. **Registre documentaire 05-MOD** — Étant donné [`05-MOD-registre-module-key.md`](../../references/protocole-modules-recyclique/05-MOD-registre-module-key.md), quand la story est livrée, alors la ligne `comptage-pieces-billets` passe de **réservé** / stub à **actif** avec lien vers `comptage-pieces-billets.v1.json` ; §3.2 et fiche §5.4 mises à jour ; [`schemas/README.md`](../../references/config-modules-site-id/schemas/README.md) indexé. [Source : 05 §9 · L-06]

4. **Defaults API — sites sans surcharge** — Étant donné un site **sans** ligne `site_module_configs` pour cette clé, quand un client autorisé appelle `GET module-config`, alors le document par défaut expose : `enabled: false`, `skip_allowed: true`, `require_denomination_grid: false`, `show_images: true` (comportement **safe** = parité legacy, pictos prêts si activation ultérieure). [Source : Q-HITL-11 module off · 9.11 AC7]

5. **Validation PATCH** — Étant donné un corps `payload` invalide (champ manquant, type incorrect, propriété inconnue), quand `PATCH module-config` est appelé, alors l’API renvoie **422** avec détail lisible ; `If-Match` / ETag inchangés (pattern 9.6). [Source : `validation.py` · `test_module_config_site.py`]

6. **Admin `/admin/modules` — carte module** — Étant donné un administrateur avec `transverse.admin.view` sur le site courant, quand il ouvre `/admin/modules`, alors une entrée **« Comptage pièces / billets (clôture) »** apparaît dans le catalogue (pattern `MODULES_CATALOG` + accordion 9.6) avec champs : interrupteur **Module activé** (`enabled`), **Autoriser le passage sans comptage** (`skip_allowed`), **Grille complète obligatoire** (`require_denomination_grid`), **Afficher les pictos** (`show_images`) ; libellés terrain en français ; indication **qui peut agir** / **effet** (activation = étape comptage dans wizard clôture). [Source : 9.6 AC1–2 · `KpiLiveBannerSettingsFields` pattern]

7. **Admin — persistance serveur** — Étant donné un PATCH réussi depuis l’admin, quand on recharge la page ou appelle `GET module-config`, alors les valeurs reflètent le serveur (pas `localStorage`) ; motif de changement tracé (header / log `module_config_patch` existant). [Source : 9.6 AC3–4 · DEC-03]

8. **Site pilote La Clique — config figée** — Étant donné le **site pilote La Clique** (site de prod / préprod désigné par Strophe — résoudre `site_id` via admin Sites ou [`guide-pilotage-v2.md`](../../_bmad-output/planning-artifacts/guide-pilotage-v2.md)), quand la procédure d’activation pilote est exécutée (seed Alembic **ou** PATCH admin documenté), alors `payload` = `{ "enabled": true, "skip_allowed": false, "require_denomination_grid": true, "show_images": true }`. [Source : D-CPT-07 · D-CPT-06 · décisions HITL 2026-06-06]

9. **Resolver backend aligné** — Étant donné `is_comptage_module_required(db, site_id)` (9.11), quand la config 9.13 est en place, alors il lit **uniquement** `module-config` / `site_module_configs` (plus de fixture réservée) ; `enabled: false` → helper retourne `False` ; `enabled: true` + `skip_allowed: false` → comptage requis à la clôture. [Source : 9.11 tasks · 08-MOD §4.3]

10. **Recette Q-HITL-09 — module off** — Étant donné `enabled: false` sur le site de test, quand un opérateur exécute le wizard clôture, alors : **aucune** étape comptage / grille visible ; saisie **`actual_amount`** legacy fonctionne ; clôture réussit comme **9.10 / 6.7** ; **aucun** `PUT denomination-count` requis. [Source : Q-HITL-09 · 9.11 AC7 · audit 1.4.4]

11. **Recette Q-HITL-11 — module on** — Étant donné `enabled: true`, `skip_allowed: false`, `require_denomination_grid: true` (config pilote), quand l’opérateur tente `closeSession` **sans** grille enregistrée, alors **400** `COMPTAGE_REQUIRED` ; avec grille complète + relecture (9.12), clôture **200** ; **pas** de bouton « passer » visible si `skip_allowed: false`. [Source : Q-HITL-11 · D-CPT-07]

12. **Recette Q-HITL-09 — module on (flux complet)** — Étant donné module activé et wizard 9.12 livré, quand l’opérateur enchaîne ouverture clôture → grille 15 lignes → relecture → PIN, alors le panel comptage est **dans** `cashflow-close-wizard` **avant** `closeSession` ; snapshot contient `denomination_count_v1` ; chaîne Paheko T1–T3 **inchangée** (9.10). [Source : Q-HITL-09 · Q-HITL-10 · 08-MOD §5–8]

13. **`show_images` — toggle seul** — Étant donné `show_images: false` en config, quand le wizard 9.12 affiche la grille, alors les pictos sont masqués mais la saisie quantités reste possible ; `show_images: true` affiche le pack SVG stylisé (assets 9.12). **Aucune** UI d’upload / personnalisation d’images dans 9.13. [Source : D-CPT-06 · hors scope upload]

14. **Tests pytest module-config** — Étant donné `recyclique/api/tests/test_story_9_13_comptage_module_config.py` (ou extension `test_module_config_site.py`), quand la suite story est exécutée, alors elle couvre : GET default, PATCH nominal pilote, 404 clé inconnue, 403 IDOR site B, 422 payload invalide, cohérence defaults vs seed pilote. [Source : pattern 9.6 · 9.11 tests]

15. **Tests Vitest admin** — Étant donné `peintre-nano/tests/unit/admin-modules-widget.test.tsx` (étendu) ou fichier dédié `comptage-pieces-billets-settings.test.tsx`, quand les tests passent, alors ils couvrent : rendu carte module, édition des 4 toggles, PATCH mocké avec ETag, refus save si GET en échec (garde 9.6). [Source : 9.6 Dev Agent Record]

16. **Procédure activation Strophe** — Étant donné un document [`references/operations-speciales-recyclique/2026-06-06_procedure-activation-comptage-pieces-billets-pilote.md`](../../references/operations-speciales-recyclique/2026-06-06_procedure-activation-comptage-pieces-billets-pilote.md) *(chemin cible)*, quand un responsable non-dev suit les étapes, alors il peut : (a) vérifier l’état module via `/admin/modules`, (b) activer/désactiver le site pilote, (c) exécuter la check-list recette §Recette ci-dessous, (d) rollback vers `enabled: false` sans migration BDD métier. [Source : demande PO · Phase D 08-MOD]

## Hors scope

| Exclusion | Report |
|-----------|--------|
| Comptage par **poids** / balance | D-CPT-10 — phase ultérieure |
| UI **upload** / personnalisation images par dénomination | D-CPT-06 « plus tard » — v1 = toggle `show_images` seulement |
| Endpoints `denomination-count`, tables SQL, snapshot | Story **9.11** |
| Wizard grille, relecture, PDF anomalie, assets SVG | Story **9.12** |
| Batch Paheko T3, seuil D33 | Story **9.10** (inchangé) |
| Tag **`v2.0.2` prod** | Gates Coordinateur, QA2 story, validation EC — hors DS seul |
| Activation **autres sites** que pilote documenté | Hors procédure ; defaults `enabled: false` |

## Tasks / Subtasks

### Schéma et registre documentaire

- [x] Créer `references/config-modules-site-id/schemas/comptage-pieces-billets.v1.json` (`schema_version` 1.0.0, 4 booléens required)
- [x] MAJ `references/config-modules-site-id/schemas/README.md`
- [x] MAJ `references/protocole-modules-recyclique/05-MOD-registre-module-key.md` §3, §3.2, §5.4 (réservé → **actif**)
- [x] MAJ `references/protocole-modules-recyclique/18-MOD-config-modules-crosswalk.md` §7 (L-06 comptage)

### Backend — whitelist et service

- [x] `registry.py` : `MODULE_KEY_COMPTAGE_PIECES_BILLETS`, `SCHEMA_VERSION_*`, entrée `_REGISTRY`, ajout à `ACTIVE_MODULE_KEYS`
- [x] `service.py` : `COMPTAGE_PIECES_BILLETS_DEFAULT_PAYLOAD` ; étendre `default_document()` (ne plus tout router sur KPI seul)
- [x] Helper `comptage_module_enabled_from_payload(payload) -> bool` (lit `enabled`)
- [x] `access_registry.py` : entrée optionnelle si intersect permissions caisse (`caisse.access` ou permission admin modules existante) — aligner sur 9.11
- [x] Remplacer tolérance fixture 9.11 par lecture registre réelle dans `is_comptage_module_required`
- [x] OpenAPI : description param `module_key` — ajouter `comptage-pieces-billets` dans l’exemple liste blanche (si présent)

### Backend — seed pilote La Clique

- [x] Migration Alembic **data** idempotente `s9_13_comptage_pilot_site_module_config` **ou** script ops documenté : upsert `site_module_configs` pour site pilote avec payload pilote §AC8
- [x] Résolution `site_id` pilote : constante env `PILOT_SITE_ID` **ou** lookup par nom site « La Clique » en seed dev — **documenter** dans procédure Strophe (pas de UUID en dur dans le code applicatif sauf tests)

### Front Peintre — extension `/admin/modules`

- [x] Étendre `peintre-nano/src/api/comptage-module-config.ts` (9.12) : ajouter `require_denomination_grid` au type + parser ; réutiliser `COMPTAGE_PIECES_BILLETS_MODULE_KEY` existant
- [x] `ComptagePiecesBilletsSettingsFields.tsx` (pattern `KpiLiveBannerSettingsFields`)
- [x] Provider / hook settings **ou** généraliser `AdminModulesWidget` pour N modules (éviter dette N×providers si faisable sans refonte large)
- [x] Ajouter entrée `MODULES_CATALOG` : titre, description, lien wizard clôture
- [x] Copy terrain : expliquer effet `skip_allowed` / `require_denomination_grid` / D-CPT-07 pour pilote
- [x] `register-admin-config-widgets.ts` si widget dédié requis

### Recette et documentation ops

- [x] Rédiger `references/operations-speciales-recyclique/2026-06-06_procedure-activation-comptage-pieces-billets-pilote.md` :
  - Prérequis (9.11 + 9.12 déployés)
  - Étapes admin `/admin/modules`
  - Check-list **module off** (Q-HITL-09)
  - Check-list **module on** (Q-HITL-11 + flux complet)
  - Rollback `enabled: false`
  - Contacts / validation Strophe
- [x] MAJ `references/operations-speciales-recyclique/index.md` si présent
- [x] Test-summary : `_bmad-output/implementation-artifacts/tests/test-summary-story-9-13-comptage-activation.md`

### Tests

- [x] `recyclique/api/tests/test_story_9_13_comptage_module_config.py`
- [x] Extension `peintre-nano/tests/unit/admin-modules-widget.test.tsx` (ou fichier dédié)
- [x] Non-régression : `test_module_config_site.py` (kpi-live-banner intact)
- [x] Test d’intégration léger : module off → `test_cash_session_close` legacy ; module on → `test_story_9_11_*` (si 9.11 done)

## Dev Notes

### Schéma JSON cible (proposition)

Fichier : `references/config-modules-site-id/schemas/comptage-pieces-billets.v1.json`

| Propriété `payload` | Type | Rôle |
|---------------------|------|------|
| `enabled` | boolean | Module actif pour le site — **master switch** |
| `skip_allowed` | boolean | Autoriser clôture sans comptage détaillé (audit si utilisé) |
| `require_denomination_grid` | boolean | Forcer les 15 lignes (quantités 0 explicites) vs saisie totale seule |
| `show_images` | boolean | Afficher pictos stylisés dans wizard (9.12) — D-CPT-06 |

**Interdit dans le payload :** montants, lignes dénomination, comptes compta, seuil D33 (cookbook loup de mer **#7**).

### Defaults vs pilote

| Contexte | `enabled` | `skip_allowed` | `require_denomination_grid` | `show_images` |
|----------|-----------|----------------|----------------------------|---------------|
| **GET default** (aucune ligne PG) | `false` | `true` | `false` | `true` |
| **Site pilote La Clique** (seed / procédure) | `true` | `false` | `true` | `true` |

Le pilote **n’altère pas** le default global : seul le site désigné reçoit la surcharge.

### État brownfield (pré-9.13 — snapshot historique DS)

```text
ACTIVE_MODULE_KEYS = { kpi-live-banner, reception }  # comptage absent
default_document() → branche KPI uniquement
AdminModulesWidget → MODULES_CATALOG = [ kpi-live-banner ]
08-MOD §4.2 : show_images absent du stub historique — ajouté HITL 2026-06-06
comptage-module-config.ts (9.12) : type sans require_denomination_grid — à aligner 9.13
resolve_comptage_module_payload() : lit PG direct sans ACTIVE_MODULE_KEYS — migrer vers ModuleConfigService
DEFAULT_PAYLOAD_MODULE_OFF (9.11) : déjà aligné AC4 — réutiliser pour defaults service.py
```

### Intelligence stories prérequis (9-11 / 9-12 livrées)

| Élément | État post-9.12 | Impact 9.13 |
|---------|----------------|-------------|
| `resolve_comptage_module_payload` | Lecture directe `site_module_configs` | Remplacer par `ModuleConfigService` après promotion registre (AC9) |
| `DEFAULT_PAYLOAD_MODULE_OFF` | `cash_denomination_service.py` — aligné AC4 | Source pour `COMPTAGE_PIECES_BILLETS_DEFAULT_PAYLOAD` dans `service.py` |
| `comptage-module-config.ts` | Clé + parser partiel (sans `require_denomination_grid`) | Étendre type ; admin et wizard partagent la même clé module |
| `useComptageModuleConfig` | 404 / erreur → module off (parité legacy) | Inchangé wizard ; admin ajoute carte MODULES_CATALOG |
| Tests 9-11 / 9-12 | Seed config via fixture DB/API | Tests 9-13 passent par registre officiel + GET/PATCH 200 |

### Fichiers d’ancrage (priorité)

| Priorité | Fichier |
|----------|---------|
| 1 | `recyclique/api/src/recyclic_api/modules/module_config/registry.py` |
| 2 | `recyclique/api/src/recyclic_api/modules/module_config/service.py` |
| 3 | `recyclique/api/src/recyclic_api/modules/module_config/validation.py` |
| 4 | `recyclique/api/src/recyclic_api/modules/module_config/access_registry.py` |
| 5 | `references/config-modules-site-id/schemas/comptage-pieces-billets.v1.json` *(nouveau)* |
| 6 | `peintre-nano/src/domains/admin-config/AdminModulesWidget.tsx` |
| 7 | `peintre-nano/src/api/module-config-client.ts` |
| 8 | `peintre-nano/src/domains/admin-config/KpiLiveBannerSettingsFields.tsx` *(pattern)* |
| 9 | `recyclique/api/tests/test_module_config_site.py` |
| 10 | `references/protocole-modules-recyclique/05-MOD-registre-module-key.md` |
| 11 | `recyclique/api/src/recyclic_api/services/cash_denomination_service.py` — `is_comptage_module_required`, `resolve_comptage_module_payload` (9.11) |
| 12 | `peintre-nano/src/api/comptage-module-config.ts` — hook wizard 9.12 (étendre type admin) |

### Pattern extension admin (story 9.6)

Réutiliser **sans refonte ACL** :

- Catalogue `MODULES_CATALOG` + accordéon par `module_key`
- Client `GET/PATCH` avec ETag ; blocage save si GET échoué
- Traçabilité motif PATCH
- Permission `transverse.admin.view` (guard manifeste existant)

**Éviter :** dupliquer toute la logique save KPI — extraire un petit hook `useModuleConfigEditor(moduleKey)` si le widget grossit à 2+ modules.

### Recette HITL — matrice exécutable (Strophe / QA)

#### Q-HITL-09 — Parité legacy (module **off**)

| # | Étape | Résultat attendu |
|---|-------|------------------|
| R09.1 | `GET module-config` → `enabled: false` | Document cohérent |
| R09.2 | Ouvrir wizard clôture caisse | Pas d’onglet / panel « Comptage pièces » |
| R09.3 | Saisir `actual_amount`, clôturer sous seuil D33 | **200**, session fermée |
| R09.4 | Vérifier snapshot | Pas de bloc `denomination_count_v1` (ou absent) |
| R09.5 | Outbox Paheko | T1–T3 selon 9.10, pas de régression |

#### Q-HITL-11 — Module **on** (pilote)

| # | Étape | Résultat attendu |
|---|-------|------------------|
| R11.1 | Config pilote §AC8 active | `enabled: true`, `skip_allowed: false` |
| R11.2 | Clôture sans `PUT denomination-count` | **400** `COMPTAGE_REQUIRED` |
| R11.3 | Grille complète + relecture (9.12) | Close **200** |
| R11.4 | UI | Pas de « Passer » / skip |
| R11.5 | `show_images: false` puis `true` | Pictos masqués puis visibles (9.12) |

#### Rollback

| # | Étape | Résultat attendu |
|---|-------|------------------|
| RB.1 | PATCH `enabled: false` via admin | Immédiat côté prochaine session |
| RB.2 | Clôture suivante | Flux legacy R09.x |

### Garde-fous

- Ne pas stocker lignes de comptage dans JSON `module-config`
- Ne pas activer `skip_allowed: true` sur pilote La Clique sans décision PO écrite
- Ne pas implémenter upload images custom (D-CPT-06 phase 2)
- Ne pas modifier indices batch Paheko 0–3 (9.10)
- Ne pas casser `kpi-live-banner` ni `reception` dans `ACTIVE_MODULE_KEYS`
- `show_images` est **préférence UI** — le backend 9.11 ne dépend pas de ce flag pour valider la grille

### Testing / gates Story Runner

- **Pytest obligatoire vert** ; `timeout_sec` **≥ 330**
- Peloton minimal suggéré :
  - `pytest recyclique/api/tests/test_story_9_13_comptage_module_config.py`
  - `pytest recyclique/api/tests/test_module_config_site.py`
  - `pytest recyclique/api/tests/test_story_9_11_comptage_pieces_billets_backend.py -k module`
  - `pytest recyclique/api/tests/test_cash_session_close.py -k variance`
- Vitest : `admin-modules-widget.test.tsx` (+ nouveau si créé)
- Test-summary dédié avant passage **review**

### Stories prérequis

| Clé | Apport | Statut |
|-----|--------|--------|
| **9.6** | Shell admin + API module-config | done |
| **9.10** | Clôture legacy + Paheko T3 | done |
| **9.11** | Backend comptage + lecture config | **done** |
| **9.12** | Wizard + pictos + relecture (recette flux complet) | **done** |
| **6.7** | Hôte `CashflowCloseWizard` | done |

### References

- [Source: `references/artefacts/2026-06-06_01_decisions-hitl-comptage-pieces-billets-pilote.md`](../../references/artefacts/2026-06-06_01_decisions-hitl-comptage-pieces-billets-pilote.md)
- [Source: `references/protocole-modules-recyclique/08-MOD-exemple-pilote-comptage-pieces-billets.md`](../../references/protocole-modules-recyclique/08-MOD-exemple-pilote-comptage-pieces-billets.md)
- [Source: `references/protocole-modules-recyclique/05-MOD-registre-module-key.md`](../../references/protocole-modules-recyclique/05-MOD-registre-module-key.md)
- [Source: `_bmad-output/implementation-artifacts/9-6-config-admin-simple-modules.md`](9-6-config-admin-simple-modules.md)
- [Source: `_bmad-output/implementation-artifacts/9-11-comptage-pieces-billets-contrats-backend-persistance.md`](9-11-comptage-pieces-billets-contrats-backend-persistance.md)
- [Source: `references/recherche/2026-06-06_comptage-pieces-billets-fermeture-caisse-ux-terrain_perplexity_reponse.md`](../../references/recherche/2026-06-06_comptage-pieces-billets-fermeture-caisse-ux-terrain_perplexity_reponse.md)

## Dev Agent Record

### Agent Model Used

Composer (DS sub-agent Task, 2026-06-06) — re-vérification DS Story Runner

### Debug Log References

- Pytest : `tests/test_story_9_13_comptage_module_config.py` + `tests/test_module_config_site.py` — **17 passed** (2026-06-06 re-vérif.)
- Pytest : `tests/test_story_9_11_comptage_pieces_billets_backend.py -k module` — **2 passed**
- Vitest : `peintre-nano/tests/unit/admin-modules-widget.test.tsx` — **6 passed**

### Completion Notes List

- Schéma `comptage-pieces-billets.v1.json` publié (4 booléens required, `additionalProperties: false`).
- Registre serveur : `MODULE_KEY_COMPTAGE_PIECES_BILLETS` dans `ACTIVE_MODULE_KEYS` + `_REGISTRY` ; defaults `COMPTAGE_PIECES_BILLETS_DEFAULT_PAYLOAD` ; `resolve_payload_for_site` ; `comptage_module_enabled_from_payload`.
- `cash_denomination_service.resolve_comptage_module_payload` délègue à `ModuleConfigService` (AC9).
- `access_registry` : entrée comptage + permission `caisse.access`.
- Migration data idempotente `s9_13_comptage_pilot_site_module_config` (lookup `%La Clique%` ou `PILOT_SITE_ID`).
- Admin Peintre : carte module + `ComptagePiecesBilletsModulePanel` (4 toggles, PATCH ETag).
- Type wizard `require_denomination_grid` aligné dans `comptage-module-config.ts`.
- Docs : 05-MOD, 18-MOD §7, schemas README, procédure ops Q-HITL-09/11.
- OpenAPI : exemple `comptage-pieces-billets` dans description param `module_key`.

### File List

- `references/config-modules-site-id/schemas/comptage-pieces-billets.v1.json`
- `references/config-modules-site-id/schemas/README.md`
- `references/protocole-modules-recyclique/05-MOD-registre-module-key.md`
- `references/protocole-modules-recyclique/18-MOD-config-modules-crosswalk.md`
- `references/operations-speciales-recyclique/2026-06-06_procedure-activation-comptage-pieces-billets-pilote.md`
- `references/operations-speciales-recyclique/index.md`
- `recyclique/api/src/recyclic_api/modules/module_config/registry.py`
- `recyclique/api/src/recyclic_api/modules/module_config/service.py`
- `recyclique/api/src/recyclic_api/modules/module_config/access_registry.py`
- `recyclique/api/src/recyclic_api/services/cash_denomination_service.py`
- `recyclique/api/migrations/versions/s9_13_comptage_pilot_site_module_config.py`
- `recyclique/api/tests/test_story_9_13_comptage_module_config.py`
- `contracts/openapi/recyclique-api.yaml`
- `peintre-nano/src/api/comptage-module-config.ts`
- `peintre-nano/src/domains/admin-config/AdminModulesWidget.tsx`
- `peintre-nano/src/domains/admin-config/ComptagePiecesBilletsSettingsFields.tsx`
- `peintre-nano/src/domains/admin-config/ComptagePiecesBilletsModulePanel.tsx`
- `peintre-nano/src/domains/admin-config/comptage-pieces-billets-settings.ts`
- `peintre-nano/tests/unit/admin-modules-widget.test.tsx`
- `peintre-nano/tests/e2e/comptage-module-activation-9-13.e2e.test.tsx`
- `peintre-nano/tests/unit/fixtures/cash-denominations-api.ts`
- `_bmad-output/implementation-artifacts/tests/test-summary-story-9-13-comptage-activation.md`

## Change Log

| Date | Auteur | Changement |
|------|--------|------------|
| 2026-06-06 | dev-story (DS re-vérif.) | DS PASS — toutes tasks [x] ; peloton pytest 17+2 + Vitest 6/6 vert ; statut **review** confirmé |
| 2026-06-06 | validate-story (VS) | VS PASS (re-validation post-DS) — cohérence epics/HITL/sprint-status ; sync Contexte chantier + File List e2e ; `vs_loop=0` |
| 2026-06-06 | dev-story (DS) | Implémentation complète — schema, registre, admin, seed pilote, tests pytest/vitest, procédure ops ; statut **review** |
| 2026-06-06 | create-story (BMAD) | Création story **9.13** — schéma module-config, registre, admin `/admin/modules`, seed pilote La Clique, recette Q-HITL-09/11, procédure Strophe ; statut **backlog** ; D-CPT-06/07 intégrées |
| 2026-06-06 | validate-story (VS) | VS PASS — prérequis **9.11**/**9.12** **done** ; intelligence brownfield ; chemins `cash_denomination_service` + `comptage-module-config.ts` ; statut **ready-for-dev** |
