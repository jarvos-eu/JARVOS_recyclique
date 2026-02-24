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

(Ajouter ici les futurs artefacts non-Git : briefs, handoffs, etc. Une ligne par fichier ou par theme.)
