# Index — references/artefacts/

Artefacts temporaires de handoff entre agents. Convention : `YYYY-MM-DD_NN_titre-court.md` (NN = ordre d'execution 01, 02, …).

> Charger uniquement l'artefact dont la session a besoin (souvent indique dans `ou-on-en-est.md`).

---

## Plan Git (tests, procedure, subagent)

| Fichier | Role |
|---------|------|
| `2026-02-24_01_mission-agent-test-git-cursor.md` | Mission pour agent test (session Cursor vide) : init repo, tests, remplir rapport |
| `2026-02-24_02_rapport-tests-git-cursor.md` | Rapport a remplir pendant les tests ; synthese credentials et recommandations |
| `2026-02-24_03_mission-rediger-procedure-git.md` | Mission : rediger `references/procedure-git-cursor.md` a partir du rapport |
| `2026-02-24_04_brief-create-subagent-git.md` | Brief pour Strophe : /create-subagent avec prompt Git |
| `2026-02-24_05_mission-creer-regle-git-workflow.md` | Mission : creer `.cursor/rules/git-workflow.mdc` et mettre a jour l'index principal |

Ordre d'execution : 01 → 02 (phase 1) ; puis 03 → 04 → 05 une fois le rapport valide. **Plan execute** : procedure, subagent (`.cursor/agents/git-specialist.md`) et regle (`.cursor/rules/git-workflow.mdc`) en place.

---

## Autres artefacts

| Fichier | Role |
|---------|------|
| `2026-02-24_06_brainstorm-migration-paheko.md` | Brainstorm migration Paheko : contexte, themes, analyse critique, 10 idees Kanban, 7 todos, decisions posees. Point d'entree pour sessions suivantes. |
| `2026-02-24_07_design-systeme-modules.md` | Design systeme de modules : decisions arbitrees, contrat ModuleBase, module.toml, loader, slots React, zones d'ombre residuelles. |
| `2026-02-24_08_decision-architecture-max-paheko.md` | Decision architecture « max Paheko » : caisse native, saisie au poids, module correspondance, tensions, agenda recherche. |
| `2026-02-24_09_cartographie-integration-paheko-core.md` | Cartographie 1re passe integration Paheko core : guides (archi, Docker, extensions), decisions 1re passe (version 1.3.19.x, un Compose), catalogue ; suite 2e passe. |
| `2026-02-24_10_doc-officielle-paheko-integration-core.md` | Complement doc officielle Paheko (Extensions + API) ; inconnues et renvoi vers les 5 prompts Perplexity (API caisse, Saisie au poids, version, auth/SSO, catalogue). |
| `2026-02-24_11_capacites-paheko-calendrier-fichiers-communication.md` | Synthese capacites natives Paheko : fichiers (oui), calendrier collaboratif (non — extension Agenda = individuel), communication (oui). Impact pour Recyclic. |
| `2026-02-25_01_decision-agenda-recyclic-externe.md` | Decision agenda dans Recyclic + services externes ; utilisateur = ref Paheko ; multi-agendas ; v0.1.0 = placeholders. |
| `2026-02-25_02_chantier-fichiers-politique-documentaire.md` | Chantier fichiers / politique documentaire : exploration, matrice vivante, backends, scan factures, upload, frontiere plugin/Recyclic ; scope versions futures. |
| `2026-02-25_03_closure-1re-passe-spirale.md` | Cloture 1re passe spirale : synthese sujets traites, URL repo renseignee, suite 2e passe et Brief. |
