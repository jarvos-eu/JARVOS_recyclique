# 09-PEINTRE — Risques, dette assumée, questions HITL

## 1. Questions ouvertes nécessitant arbitrage Strophe (HITL)

| # | Question | Statut | Décision / défaut |
|---|----------|--------|-------------------|
| ~~Q-01~~ | Identité visuelle cible (vert Recyclique vs neutre) | **TRANCHÉE** (D-00/D-11) | Le moteur ne porte aucune identité ; Recyclique fournit son vert via **theme CREOS**. Plus une question. |
| Q-02 | Premier livrable visible : tout, ou pilote caisse d'abord ? | ouverte | Pilote caisse d'abord (déjà le plus instrumenté), généralisation ensuite |
| ~~Q-03~~ | Profil composition : qui en est writer ? | **TRANCHÉE** (D-09) | App writer (couche 1) ; user surcharge (couche 2) même grammaire ; moteur fournit défauts (couche 0) |
| Q-04 | Intelligence générative (3b) : in-scope v0.1 ou v0.1.x ? | ouverte | 3a en v0.1 (branchée sur hook inerte), 3b après stabilisation |
| Q-05 | Theming / mode sombre : court terme ou seulement préparé ? | ouverte | Préparé par l'archi 2-niveaux + theme CREOS, pas livré |
| Q-06 | Extraction physique du repo : horizon ? | ouverte | Reportée (D-08) ; durcir frontières seulement |
| **Q-07** | **Précédence prefs user** : local (device) vs app/back (identity) — qui gagne ? | **ouverte (nouvelle)** | Trancher par `pref_scope` device/identity (`04A` §7) plutôt qu'une règle globale |
| **Q-08** | **Setting multi-critères de « l'affichage parfait par défaut »** : quels critères, quel barème ? | **ouverte (nouvelle)** | À définir : pondération support × nature contenu × priorité ; v0.1 = règles simples, barème affinable |

## 2. Risques

| Risque | Probabilité | Impact | Mitigation |
|--------|-------------|--------|------------|
| **Régression de parité observable caisse** lors du rapatriement des surcouches (B-3) | moyenne | élevé | tests e2e existants comme filet (`runtime-demo-cash-register-*`, `cash-register-*-e2e`) ; migration surcouche par surcouche, pas big-bang |
| **Double système de tokens persistant** (Mantine vs `--pn-*`) | élevée | moyen | lint bloquant dès A-1 ; remap Mantine au provider avant migration widgets |
| **Widgets monolithiques résistants** à l'extraction présentation (2000+ lignes) | élevée | moyen | ne pas tout refactorer ; extraire seulement le *chrome de conteneur* via `PresentationSurface` ; le métier reste dans le widget |
| **Sur-ingénierie du profil présentation** (trop de champs trop tôt) | moyenne | moyen | `additionalProperties:false` + démarrer minimal (emphasis/region/density) ; étendre par besoin prouvé |
| **Intelligence 3b ingouvernable** si lancée trop tôt | moyenne | élevé | D-06 : 3a d'abord ; profil figé avant 3b ; sortie strictement validée |
| **Snapshot code incomplet** (runtime/registry/types absents de l'export) | certaine | moyen | Épic C-1 inventaire sur repo vivant **avant** d'écrire le LayoutResolver |

## 3. Dette assumée (à tracker, pas à résoudre maintenant)

- **Widgets monolithiques non démantelés** : on extrait leur présentation, pas leur logique. Le refactor métier reste hors scope v1.
- **`widget-declaration.schema.json` reste `additionalProperties:true`** : on ne le durcit pas dans ce chantier (risque de casser l'existant) ; seul le **nouveau** profil présentation est strict.
- **Alias legacy autres que caisse** : on traite caisse en pilote ; les alias admin/réception migrent au fil de la généralisation, pas tous d'un coup.
- **Mantine reste la lib de composants** : Peintre v0.1 ne vise pas à s'en affranchir, seulement à ne pas la laisser fuir dans le vocabulaire de tokens.

## 4. Dépendances amont à confirmer

- ADR P1/P2 (`references/peintre/2026-04-01_adr-p1-p2…`) — toujours en vigueur ? (CSS Modules + tokens, pas Tailwind/CSS-in-JS).
- CI CREOS (Épic 10 modules) — état réel : la validation `data_contract.operation_id` ↔ `operationId` existe-t-elle déjà ? On greffe la validation présentation dessus.
- Gouvernance contrats (`21-MOD-gouvernance-contrats-modules`) — le profil présentation entre-t-il dans le même régime reviewable ? (réponse posée : oui, `04` §6ter).
- **Story 9.6 / T-MOD-3** (activation modules générique + OpenAPI module-config non fusionné) : le portage `10` suppose l'activation par `module_key` ; si 9.6/T-MOD-3 traînent, seul le toggle bandeau existe. **Non bloquant** pour Épics A/B (Piste A, mocks) ; à confirmer avant la généralisation multi-modules.

## 5. Prochaine action concrète pour l'agent Cursor

1. Lire `01`–`05` + `08` de ce dossier.
2. **Épic C-1 d'abord en lecture** (inventaire repo vivant : `src/runtime`, `src/registry`, `src/types`, `PageRenderer`, `templates/transverse`) pour confirmer les points de §6 de `01`.
3. Démarrer **Épic A** (tokens) — c'est le levier le plus rentable et sans dépendance.
4. Remonter à Strophe les réponses nécessaires aux questions Q-01…Q-06 avant d'attaquer Épic B-3 (rapatriement caisse) et Phase 3.
