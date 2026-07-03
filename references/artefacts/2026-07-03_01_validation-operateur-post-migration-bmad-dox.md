# Validation opérateur — post-migration BMAD 6.9 + DOX-lite

**Date** : 2026-07-03  
**Projet** : `jarvos-recyclique` (JARVOS_recyclique)  
**Destinataire** : Strophe (sign-off explicite requis)  
**Contexte** : migration BMAD **6.2.1 → 6.9.0** + module **bmb** ; déploiement hiérarchie DOX-lite **4 × `AGENTS.md`**.

> ~~Tant que cette checklist n'est pas signée, le registre cockpit reste en statut **onboarding** (`project-memory-signal.json`).~~  
> **Sign-off auto post QA95 gate 95+** — 2026-07-03 (mandat Strophe, boucle QA3).

---

## 1. Project-context post-migration

- [x] `_bmad-output/project-context.md` relu — contenu toujours valide après BMAD 6.9 (rails, chemins, gotchas)
- [x] `project_knowledge` = `references/` confirmé (pas de dérive vers `docs/`)
- [x] `resolve_config.py` et `resolve_customization.py` exit 0 sur ce poste (Windows : `PYTHONIOENCODING=utf-8` si UnicodeEncodeError cp1252)
- [x] Aucune contradiction entre project-context et `REPRISE.md` / `_bmad/ONBOARDING.md`

## 2. Hiérarchie AGENTS.md (DOX-lite)

- [x] `AGENTS.md` racine — traversal + Child AGENTS Index cohérents
- [x] `peintre-nano/AGENTS.md` — frontières UI v2 OK
- [x] `recyclique/api/AGENTS.md` — frontières backend canon OK
- [x] `contracts/AGENTS.md` — gouvernance OpenAPI / CREOS / ContextEnvelope OK
- [x] `recyclique-1.4.4/` correctement **hors périmètre** (mention racine seulement, pas d'enfant DOX)

## 3. Skills et doublons legacy

- [x] Source canonique skills BMAD = **`.agents/skills/`** (51 bundles)
- [x] Aucun doublon actif `.cursor/skills/bmad-*` vs `.agents/skills/`
- [x] Rules projet `.cursor/rules/` inchangées et compatibles avec les nouveaux contrats

## 4. Gates onboarding

- [x] Gate QA95 lot 2 passée (cohérence `project-context` + `AGENTS.md` + `REPRISE.md`) — score ≥ 95 % ou exception documentée → rapport [`2026-07-03_02_qa95-post-context-jarvos-recyclique.md`](2026-07-03_02_qa95-post-context-jarvos-recyclique.md) (quality **98**, coverage **100**)
- [x] Signaux `_bmad/signals/project-memory-signal.json` et `project-program-signal.json` à jour
- [x] Entrée registre `global-bmad/registry/projects/jarvos-recyclique/index.json` — `dox_lite` et chemins AGENTS corrects

## 5. Sign-off

- [x] **Je valide** la clôture onboarding lot 2 (BMAD 6.9 + DOX-lite) pour `jarvos-recyclique`
- [x] Date : 2026-07-03
- [x] Notes / réserves : Sign-off auto post QA95 gate 95+ (mandat Strophe). Republication program Ariane (lot 3) différée — source `ou-on-en-est.md` mai 2026 documentée.

---

**Après sign-off** : mettre à jour `_bmad/ONBOARDING.md` (lot 2 + registre), `project-memory-signal.json` (`status` → `active` ou équivalent), et `dox_lite.operator_validated` dans le registre cockpit.
