# Checklist onboarding BMAD — jarvos-recyclique

**Profil** : brownfield (mono-repo Recyclique v2, epics BMAD actifs)  
**Runbook exécution** : `JARMES/jarmes-skills-rules/Skills/jarmes-bmad-trio/docs/forge/BROWNFIELD_RUNBOOK.md`  
**Copie locale** : maintenir ce fichier à jour pendant l'onboarding du repo.

---

## Rails config actifs

| Composant | Rail actif | Fichier |
|-----------|------------|---------|
| `resolve_config.py` | TOML + custom | `_bmad/config.toml`, `_bmad/custom/*.toml` |
| Workflows BMM | Shim YAML | `_bmad/bmm/config.yaml` |
| Workflows core | Shim YAML | `_bmad/core/config.yaml` |
| BMAD Builder | YAML unifié | `_bmad/config.yaml` |
| Skills Cursor | Cursor installer | `.agents/skills/` (**51** bundles) |
| Trio Mentor/Ariane/Clio | Sanctums globaux | `JARMES/jarmes-cockpit/global-bmad/sanctums/` |

---

## Lot 1 — Install technique

- [x] Preflight prefs (`read_install_prefs` — habitat `jarmes-cockpit/global-bmad`) — 2026-07-03
- [x] `npx bmad-method install` — core + bmm **6.2.1 → 6.9.0**, bmb **v2.1.0** — 2026-07-03
- [x] `bmad-bmb-setup` (merge-config + merge-help-csv + cleanup-legacy) — 2026-07-03
- [x] Shim core + BMM — `sync_bmm_config_shim.py --project-root JARVOS_recyclique` — 2026-07-03
- [x] `resolve_config.py` exit 0 — FR · `project_knowledge=references` · `user_skill_level=expert`
- [x] `resolve_customization.py` (project-context) exit 0 — 2026-07-03
- [x] Legacy `.cursor/skills/bmad-*` retirés du disque actif (doublons vs `.agents/skills/` — canon `.agents/skills/` 51 bundles)
- [x] Sanctums trio rafraîchis (`global-bmad/sanctums/{mentor,ariane,clio}`)
- [x] Signaux bootstrap (`project-memory-signal.json`, `project-program-signal.json`)
- [x] `REPRISE.md` stub fil Clio

---

## Lot 2 — Contexte brownfield

- [x] `_bmad-output/project-context.md` — `status: complete` (2026-04-23 pré-existant ; **relu 2026-07-03** post-migration BMAD 6.9)
- [x] Hiérarchie DOX-lite `AGENTS.md` — **4 fichiers** déployés (2026-07-03, GO Strophe)
- [x] Validation opérateur post-migration BMAD 6.9 + DOX-lite — **sign-off auto QA95 2026-07-03** → [`references/artefacts/2026-07-03_01_validation-operateur-post-migration-bmad-dox.md`](../references/artefacts/2026-07-03_01_validation-operateur-post-migration-bmad-dox.md)
- [x] Gate QA95 post-context (cohérence `project-context` + `AGENTS.md` + `REPRISE.md`) — rapport [`2026-07-03_02_qa95-post-context-jarvos-recyclique.md`](../references/artefacts/2026-07-03_02_qa95-post-context-jarvos-recyclique.md)
- [ ] `bmad-document-project` — sur décision Mentor uniquement

### DOX-lite — hiérarchie `AGENTS.md`

**Canon** : `JARMES/docs/programme/JARMES_DOX_LITE.md` · runbook Mentor `dox-lite-adoption.md`

| Niveau | Chemin | Rôle |
|--------|--------|------|
| Racine | `AGENTS.md` | Rail traversal, index enfants, renvois `_bmad-output/` et `references/` |
| 2 | `peintre-nano/AGENTS.md` | Front canon Peintre_nano (UI v2 manifest-driven) |
| 2 | `recyclique/api/AGENTS.md` | Backend canon FastAPI (`recyclique/api/`) |
| 2 | `contracts/AGENTS.md` | Gouvernance OpenAPI / CREOS / ContextEnvelope |

**Traversal** (avant édition code) : lire `AGENTS.md` racine → enfant de la zone touchée.  
**Hors périmètre DOX** : `recyclique-1.4.4/` (legacy — mention racine uniquement).  
**Validation opérateur** : sign-off auto QA95 2026-07-03 — onboarding lot 2 clos.

---

## Lot 2bis — Kanban idées v2

- [x] Arborescence `docs/ideas/kanban/` + `DEPOT/` — 2026-07-03
- [x] Migration brownfield 24 fiches (`references/idees-kanban/` → `IDEA-*.md`) — [`MIGRATION-MAP-v1.md`](../docs/ideas/kanban/MIGRATION-MAP-v1.md)
- [x] Archive v1 : `references/archive/idees-kanban-v1-2026-07-03/`
- [x] Signal `project-kanban-signal.json` publié
- [x] Skill projet v1 archivé (`.cursor/skills/.archives/idees-kanban-v1-2026-07-03/`) — canon global `~/.cursor/skills/idees-kanban/`

---

## Lot 3 — Programme (optionnel)

- [x] Programme actif : epics 1–26 via `_bmad-output/planning-artifacts/` (ligne courante)
- [ ] Handoff Ariane + Clio pour republication signaux après validation opérateur

---

## Registre global

- [x] Entrée `jarvos-recyclique` dans `global-bmad/registry/projects/`
- [x] `projects.status` → `active` après validation opérateur lot 2 — 2026-07-03 (sign-off auto QA95)
- [ ] Consolidation Mentor (`run_consolidation_v2 --lab`) — si demandé

---

## Références pack

- `jarmes-skills-rules/Skills/jarmes-bmad-trio/docs/programme/INSTALL_BMAD_REPO.md`
- `jarmes-skills-rules/Skills/jarmes-bmad-trio/docs/programme/ONBOARDING_BROWNFIELD.md`
- `references/ou-on-en-est.md` — fil métier historique
- `references/index.md` — point d'entrée agents
