# Story 9.6 : Livrer la config admin simple pour modules et reglages simples

Status: done (Story Runner BMAD 2026-05-26 : CR1 CHANGES_REQUESTED → DS → GATE → QA → CR2 APPROVE ; `cr_loop=1`)

<!-- Validation : lancer `bmad-create-story` mode Validate ou `bmad-dev-story` apres lecture ordre ci-dessous. -->

## Story

En tant que **super-admin ou administrateur responsable**,  
je veux une **surface de configuration simple** pour les **modules** et les **reglages de faible complexite**,  
afin de piloter l'activation et quelques controles module sans refonte ACL ni panneau expert comptable (hors perimetre 9.6).

## Contexte chantier (etat au 2026-05-23)

Cette story est le **T-MOD-4** du chantier modules v2. Elle **generalise** le toggle transitoire Epic **4.5** vers un **interrupteur unique** pour tous les modules deja dans l'app.

| Bloc | Statut | Reference |
|------|--------|-----------|
| ADR-007 Accepted (v0.1 TOML abandonne) | **Fait** | [`07-MOD-adr`](../../references/protocole-modules-recyclique/07-MOD-adr-reconciliation-v01-v02.md) · [`architecture/2026-05-20-adr-007-…`](../../_bmad-output/planning-artifacts/architecture/2026-05-20-adr-007-reconciliation-modularite-v01-v2.md) |
| Pack protocole + cookbook | **GO doc ~96 %** | [`protocole-modules-recyclique/index.md`](../../references/protocole-modules-recyclique/index.md) · [`qa2-rapport-global-chantier-modules-2026-05-20.md`](../../references/protocole-modules-recyclique/qa2-rapport-global-chantier-modules-2026-05-20.md) |
| PRD §4.2.1 + §7.1 modularite | **Fait** 2026-05-21 | [`prd.md` §4.2.1](../../_bmad-output/planning-artifacts/prd.md) |
| OpenAPI + handler `module-config` (T-MOD-3) | **Fait** | [`recyclique-api.yaml`](../../contracts/openapi/recyclique-api.yaml) · [`test_module_config_site.py`](../../recyclique/api/tests/test_module_config_site.py) |
| **Cette story** — Peintre + merge config | **done** (BMAD Story Runner 2026-05-26) | ci-dessous |
| Matiere produit 23/05 (+24 idees VIS/ORG/WFL) | **PM / roadmap** | [`2026-05-23_01_addendum…`](../../references/artefacts/2026-05-23_01_addendum-transcripts-1423-visions-rec-pko.md) — lecture **PM**, pas dev obligatoire ; **hors scope** 9.6 |

**Vision produit (figee HITL, ne pas rouvrir) :**

- Modules **optionnels par site** ; fabrication via **recette cookbook** (pas marketplace v2).
- **Pas** loader `module.toml` / `ModuleBase` en AC nominal.
- Zip / Recyclique allege / install runtime = **post-v2** (hors 9.6) ; 9.6 pose l'**activation admin** pour modules **deja dans le repo**.

## Ordre de lecture obligatoire (session dev / agent)

Charger **dans cet ordre** avant d'implementer :

1. **[`2026-05-20_05_notes-architecte-loup-de-mer-modules-v2.md`](../../references/artefacts/2026-05-20_05_notes-architecte-loup-de-mer-modules-v2.md)** — pièges terrain (primordial).
2. **[`2026-05-20_06_reco-hitl-post-bouclage-modules-v2.md`](../../references/artefacts/2026-05-20_06_reco-hitl-post-bouclage-modules-v2.md)** — DEC-03, F1, F3, ordre P0.
3. **[`06-MOD-cookbook-nouveau-module-optionnel.md`](../../references/protocole-modules-recyclique/06-MOD-cookbook-nouveau-module-optionnel.md)** — contexte ; **ne pas** fabriquer un 2e module dans cette story.
4. **[`15-MOD-matrice-gaps-bmad-story-9-6.md`](../../references/protocole-modules-recyclique/15-MOD-matrice-gaps-bmad-story-9-6.md)** — L-08, L-05, dependances.
5. Cette story + [`epics.md` Story 9.6](../../_bmad-output/planning-artifacts/epics.md).

**Agents :** ordre pack **05 loup de mer → 04 bouclage → 06 cookbook** si session large.

## Acceptance Criteria

1. **Perimetre simple admin** — Etant donne que v2 inclut une capacite de config admin simple (PRD §7.1), quand le module admin-config est livre, alors les utilisateurs autorises peuvent gerer le perimetre prevu : **activation**, **ordre** (si applicable), **variantes simples d'affichage**, ou autres controles module explicitement autorises — **sans** devenir un plan de controle expert transverse. [Source : `epics.md` Story 9.6 · PRD §7.1]

2. **Clarte roles et effet** — Etant donne que certains reglages sont plus sensibles, quand l'UI de configuration est utilisee, alors l'ecran indique **qui peut agir**, sur **quel perimetre**, et avec **quel effet** ; les changements sensibles restent **traçables** pour la supervision. [Source : epics.md · AR45]

3. **Persistance ADR P2 + merge deterministe** — Etant donne que **ADR P2** gouverne la persistance du perimetre simple-admin, quand des surcharges sont stockees et fusionnees au runtime, alors le stockage durable utilise **PostgreSQL** avec **merge deterministe** sur les **defauts des manifests build** ; **pas** de fichier JSON **sur disque** en production pour la config dynamique. La couche **`module_key`** (JSON **en base**, table `site_module_configs`) **complete** P2 sans la remplacer (PRD §7.1 phrase modularite). [Source : epics.md · PRD §4.2.1 · `core-architectural-decisions.md`]

4. **DEC-03 — JSON `module_key` fait foi** — Etant donne **DEC-03**, quand `sites.configuration` et un document JSON `module_key` divergent, alors **le JSON gagne** ; `sites.configuration` ne **reactive jamais** un module desactive. La story 9.6 edite le JSON via l'admin, pas une autorite concurrente. [Source : [`2026-05-20_04`](../../references/artefacts/2026-05-20_04_reponse-architecte-bouclage-modules-v2.md) · [`06_reco`](../../references/artefacts/2026-05-20_06_reco-hitl-post-bouclage-modules-v2.md)]

5. **API `module-config` interne jusqu'a stabilite** — Etant donne **F1** (HITL), les routes `recyclique_moduleConfig_*` restent **API interne Recyclique** jusqu'a stabilite de cette story. [Source : `recyclique-api.yaml` · reco 06 §F1]

6. **Migration toggle bandeau → `kpi-live-banner`** — Etant donne la dette Epic **4.5**, quand la config admin est operationnelle pour le pilote bandeau, alors l'activation transite vers **`module_key=kpi-live-banner`** via `patchSiteModuleConfig` et [`kpi-live-banner.v1.json`](../../references/config-modules-site-id/schemas/kpi-live-banner.v1.json) ; le chemin transitoire (`bandeau_live_slice_enabled`, `patchBandeauLiveSlice`) est **deprecie** documente. Le poll conserve **`recyclique_exploitation_getLiveSnapshot`**. [Source : [`05-MOD-registre`](../../references/protocole-modules-recyclique/05-MOD-registre-module-key.md) §6 · [`18-MOD-crosswalk`](../../references/protocole-modules-recyclique/18-MOD-config-modules-crosswalk.md) · loup de mer piège #2]

7. **UI Peintre — route `/admin/modules`** — Quand le panneau « Gestion des modules » est livre, alors il est accessible via **`/admin/modules`** (CREOS / `navigation-transverse-served.json`) et remplace le prototype `localStorage` / widget admin KPI par la **verite serveur** + merge P2. [Source : `peintre-nano/src/domains/admin-config/` · transcript `0c9a9709`]

8. **Cloture L-08 (double activation)** — Apres livraison, un seul chemin d'activation documente pour le bandeau : **`module_key` JSON** (admin 9.6) ; plus de triple autorite toggle + localStorage + JSON en prod sans migration explicite. [Source : [`09-MOD-lacunes`](../../references/protocole-modules-recyclique/09-MOD-lacunes-et-questions-ouvertes.md) L-08 · [`18-MOD-crosswalk`](../../references/protocole-modules-recyclique/18-MOD-config-modules-crosswalk.md)]

## Repartition des lots (2026-05-23)

| Lot | Statut | Contenu |
|-----|--------|---------|
| Backend contrat + handler P0 | **Fait** T-MOD-3 | OpenAPI, handler, whitelist, 5 tests nominaux |
| Backend durcissement P1 | **Fait** | 401, 422 If-Match, Cache-Control ; IDOR 403 (existant) |
| Merge PostgreSQL P2 | **Fait** | `resolve_bandeau_live_slice_enabled` DEC-03 ; PG `site_module_configs` |
| Front Peintre `/admin/modules` | **Fait** | `AdminModulesWidget` + client module-config |
| Migration bandeau | **Fait** | Provider API ; PATCH bandeau-live-slice DEPRECATED → PG |
| Registre / schemas | **Partiel** | `kpi-live-banner` seul actif ; T-MOD-5 = autres cles **apres** 9.6 |

## Tasks / Subtasks

### Backend (handler + persistance)

- [x] Router/handler `module-config` (`recyclique_moduleConfig_*`) — T-MOD-3 2026-05-20.
- [x] Whitelist = registre [`05`](../../references/protocole-modules-recyclique/05-MOD-registre-module-key.md) §3 (`kpi-live-banner`).
- [x] Validation `kpi-live-banner` ; GET membership ; ETag / 409 PATCH mismatch — 5 tests.
- [x] Merge PG P2 (AR45) + ordre merge deterministe avec manifests build.
- [x] Deprecier `PATCH bandeau-live-slice` apres bascule Peintre (doc + code si applicable).
- [x] Tests pytest etendus : PATCH IDOR site B, 401, If-Match malforme → 422, Cache-Control (QA2 global P1).

### Front Peintre (coeur story)

- [x] Page `/admin/modules` : liste modules simples (activation + reglages bornes registre).
- [x] Remplacer `localStorage` bandeau par `GET/PATCH module-config` (`show_on_caisse`, `show_on_reception`, `refresh_interval_seconds`).
- [x] Signal « module off » backend-autoritaire jusqu'a fin migration toggle.
- [x] Traçabilite UI : auteur / date / motif sur PATCH sensibles.
- [x] Tests Vitest + e2e jsdom : admin modules, bandeau on/off API mockee.

### Documentation / contrats (fin de story)

- [x] MAJ [`05-MOD-registre`](../../references/protocole-modules-recyclique/05-MOD-registre-module-key.md) si meta-config admin.
- [x] Cloturer **L-08** dans [`18-MOD-crosswalk`](../../references/protocole-modules-recyclique/18-MOD-config-modules-crosswalk.md) et [`09-MOD-lacunes`](../../references/protocole-modules-recyclique/09-MOD-lacunes-et-questions-ouvertes.md).
- [x] MAJ [`ou-on-en-est.md`](../../references/ou-on-en-est.md) : story 9.6 review / prochaine = cookbook module N+1.

## Dev Notes

### HITL et ordre chantier (reco 06)

- **ADR-007 Accepted** ; ordre : T-MOD-2 → T-MOD-3 → T-MOD-1 → **9.6** (T-MOD-4).
- **F1** : API interne jusqu'a 9.6 stable.
- **F3** : 1 `module_key` = 1 package backend.
- **Pas dans 9.6** : 2e module metier (comptage T-MET-1), marketplace, zip install, T-PEINT-1 (gardien seuil — idee kanban separee).

### Pièges loup de mer (9.6)

| # | Piège | Action 9.6 |
|---|-------|------------|
| 2 | Copier le **toggle** 4.5 comme modele | Utiliser **`module_key` JSON** uniquement |
| 3 | Page orpheline | `/admin/modules` dans navigation CREOS existante |
| 5 | Renommer `operationId` poll bandeau | **Interdit** — garder `getLiveSnapshot` |
| 7 | Mettre de la compta dans JSON config | Payload = prefs UI / activation seulement |

### Garde-fous

- Pas de parametrage comptable expert (sprint-change 2026-04-15).
- Pas de secrets HelloAsso ou gros volumes metier dans `ModuleConfigDocument.payload`.
- Pas de 2e `module_key` actif sans decision produit (T-MOD-5 apres preuve 9.6 sur bandeau).

### Shell reutilisable `/admin/modules`

La page livree en 9.6 doit accueillir les **modules metier post-9.6** via le meme mecanisme `module_key` + registre — dont les idees addendum 23/05 (**VIS-005/006** interfaces, **VIS-010** workflows, etc.) **sans** les implementer dans cette story.

### Apres 9.6 (roadmap — hors scope story)

1. **T-MOD-5** : promouvoir autres `module_key` + schemas JSON au fil des modules metier.
2. **Cookbook** : chaque nouveau module = session dediee, 1 `module_key`, phases 0→8.
3. **Candidats `module_key` futurs** (addendum 23/05, via cookbook un par un) : reseau local (**VIS-002**), editeur workflows (**VIS-010**), HelloAsso (**VIS-015**), documents K-Drive (**VIS-012**), cercles echo-eco (**VIS-009**) — **apres** preuve bandeau sur shell admin 9.6.
4. **Post-v2** : extraction / zip / Recyclique allege — hypothese documentee, pas engagement v2.
5. **VIS-018** (schema BDD transverse) : informe le modele long terme ; ne pas sur-elargir le merge P2 de 9.6.

### Fichiers typiques

| Zone | Chemins |
|------|---------|
| Contrats | `contracts/openapi/recyclique-api.yaml` ; `generated/recyclique-api.ts` |
| Schemas | `references/config-modules-site-id/schemas/` |
| Registre | `references/protocole-modules-recyclique/05-MOD-registre-module-key.md` |
| Admin UI | `peintre-nano/src/domains/admin-config/` |
| Bandeau | `peintre-nano/src/domains/bandeau-live/` |
| Backend | `recyclique/api/src/recyclic_api/modules/module_config/` |
| Convention back | `references/protocole-modules-recyclique/03-MOD-protocole-backend.md` §6 C.4 |
| Matrice gaps | `references/protocole-modules-recyclique/15-MOD-matrice-gaps-bmad-story-9-6.md` |

### Dette absorbee (Epic 4.5)

Story **4.5** reste **done** ; 9.6 **generalise** vers registre `module_key` sans elargir ACL globale. Voir [`4-5-ajouter-un-toggle-admin-minimal-borne-au-module-bandeau-live.md`](4-5-ajouter-un-toggle-admin-minimal-borne-au-module-bandeau-live.md).

## Definition of Done

- [x] AC 1–8 verifies (tests + doc).
- [x] Checklist post-promotion modules (grep PRD stale) si touch doc.
- [x] `sprint-status.yaml` : story 9-6 → done (apres CR BMAD si applicable).
- [x] Bandeau pilote : activation via admin 9.6, pas localStorage seul.

## Dev Agent Record

### Implementation Plan

- Backend : merge DEC-03 (`resolve_bandeau_live_slice_enabled`), durcissement GET/PATCH, deprecation `patchBandeauLiveSlice`.
- Front : `AdminModulesWidget`, `module-config-client`, provider bandeau sur API, manifest `admin.modules`.
- Traçabilité : log structuré `module_config_patch` + en-tête `X-Module-Config-Change-Reason`.

### Completion Notes

- Pytest : `test_module_config_site.py` + `test_exploitation_live_snapshot.py` — **22 passed**.
- Vitest ciblé : `admin-modules-widget.test.tsx`, `module-config-client.test.ts`, `navigation-transverse-served-5-1.test.ts` — **47 passed**.
- CR follow-up 2026-05-26 : `/admin/modules` aligne sur le guard admin site (`transverse.admin.view`) ; plus de gate super-admin cote manifeste/widget.
- CR follow-up 2026-05-26 : si le `GET module-config` echoue, l’UI interdit tout `PATCH` sans ETag et demande un rechargement reussi avant enregistrement.
- Story Runner BMAD 2026-05-26 : **CR2 APPROVE** ; `sprint-status` story 9-6 → **done** ; `vs_loop=0` `qa_loop=0` `cr_loop=1`.
- Note gate : pytest peloton ~**303 s** sur machine courante ; prevu `timeout_sec` **> 300** pour gate shell si timeout strict.

### File List

- `recyclique/api/src/recyclic_api/modules/module_config/service.py`
- `recyclique/api/src/recyclic_api/modules/module_config/validation.py`
- `recyclique/api/src/recyclic_api/api/api_v1/endpoints/module_config.py`
- `recyclique/api/src/recyclic_api/services/exploitation_live_snapshot_service.py`
- `recyclique/api/src/recyclic_api/api/api_v2/endpoints/exploitation.py`
- `recyclique/api/tests/test_module_config_site.py`
- `recyclique/api/tests/test_exploitation_live_snapshot.py`
- `peintre-nano/src/api/module-config-client.ts`
- `peintre-nano/src/domains/admin-config/AdminModulesWidget.tsx`
- `peintre-nano/src/domains/admin-config/KpiLiveBannerSettingsFields.tsx`
- `peintre-nano/src/domains/admin-config/AdminKpiLiveBannerSettingsWidget.tsx`
- `peintre-nano/src/domains/bandeau-live/kpi-live-banner-settings.ts`
- `peintre-nano/src/domains/bandeau-live/kpi-live-banner-settings-provider.tsx`
- `peintre-nano/src/registry/register-admin-config-widgets.ts`
- `contracts/creos/manifests/page-transverse-admin-modules.json`
- `contracts/creos/manifests/navigation-transverse-served.json`
- `peintre-nano/tests/unit/admin-modules-widget.test.tsx`
- `peintre-nano/tests/unit/module-config-client.test.ts`
- `peintre-nano/tests/contract/navigation-transverse-served-5-1.test.ts`
- `references/protocole-modules-recyclique/18-MOD-config-modules-crosswalk.md`
- `references/protocole-modules-recyclique/09-MOD-lacunes-et-questions-ouvertes.md`
- `references/ou-on-en-est.md`

### Change Log

- 2026-05-26 : Story Runner BMAD — CR1 CHANGES_REQUESTED, DS correctifs, GATE+QA, CR2 APPROVE → **done** YAML + story.
- 2026-05-26 : DS story 9.6 — admin `/admin/modules`, module-config serveur, migration bandeau L-08.
- 2026-05-26 : DS story 9.6 — corrections CR P1 (`/admin/modules` admin site + blocage save apres echec GET) ; crosswalk 18 harmonise.

## References

### BMAD

- [`_bmad-output/planning-artifacts/prd.md`](../../_bmad-output/planning-artifacts/prd.md) — §4.2, §4.2.1, §7.1
- [`_bmad-output/planning-artifacts/epics.md`](../../_bmad-output/planning-artifacts/epics.md) — Epic 9, Story 9.6, AR45
- [`_bmad-output/planning-artifacts/architecture/core-architectural-decisions.md`](../../_bmad-output/planning-artifacts/architecture/core-architectural-decisions.md)
- [`_bmad-output/implementation-artifacts/sprint-status.yaml`](sprint-status.yaml)

### Chantier modules v2

- [`references/protocole-modules-recyclique/index.md`](../../references/protocole-modules-recyclique/index.md)
- [`references/protocole-modules-recyclique/06-MOD-cookbook-nouveau-module-optionnel.md`](../../references/protocole-modules-recyclique/06-MOD-cookbook-nouveau-module-optionnel.md)
- [`references/protocole-modules-recyclique/qa2-rapport-global-chantier-modules-2026-05-20.md`](../../references/protocole-modules-recyclique/qa2-rapport-global-chantier-modules-2026-05-20.md)
- [`references/ou-on-en-est.md`](../../references/ou-on-en-est.md)

### HITL / architecte

- [`references/artefacts/2026-05-20_05_notes-architecte-loup-de-mer-modules-v2.md`](../../references/artefacts/2026-05-20_05_notes-architecte-loup-de-mer-modules-v2.md)
- [`references/artefacts/2026-05-20_06_reco-hitl-post-bouclage-modules-v2.md`](../../references/artefacts/2026-05-20_06_reco-hitl-post-bouclage-modules-v2.md)
- [`references/artefacts/2026-05-20_04_reponse-architecte-bouclage-modules-v2.md`](../../references/artefacts/2026-05-20_04_reponse-architecte-bouclage-modules-v2.md)

### Matiere produit post-23/05 (PM)

- [`references/artefacts/2026-05-23_01_addendum-transcripts-1423-visions-rec-pko.md`](../../references/artefacts/2026-05-23_01_addendum-transcripts-1423-visions-rec-pko.md)
- [`.transcription/meetings/2026-05-23-terrain-1423/final/2026-05-23-terrain-1423.md`](../../.transcription/meetings/2026-05-23-terrain-1423/final/2026-05-23-terrain-1423.md)
- [`.transcription/meetings/2026-05-23-recyclique-bilans-audit-visions/final/2026-05-23-recyclique-bilans-audit-visions.md`](../../.transcription/meetings/2026-05-23-recyclique-bilans-audit-visions/final/2026-05-23-recyclique-bilans-audit-visions.md)
- Brief handoff PM : [`2026-05-26_02_brief-bmad-remise-a-flot-modules-9-6.md`](../../references/artefacts/2026-05-26_02_brief-bmad-remise-a-flot-modules-9-6.md)

### Stories liees

- [`4-5-ajouter-un-toggle-admin-minimal-borne-au-module-bandeau-live.md`](4-5-ajouter-un-toggle-admin-minimal-borne-au-module-bandeau-live.md) — dette transitoire
- Epic 4 stories `4-1` … `4-6b` — pilote bandeau
