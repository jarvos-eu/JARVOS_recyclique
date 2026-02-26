# Vérification Phase 0 — Tool Task

**À faire manuellement** : Confirmer que le tool **Task** est disponible pour l'orchestrateur lorsqu'il invoque les agents `.cursor/agents/` (bmad-sm, bmad-dev, bmad-revisor, bmad-qa).

1. Dans un chat Cursor, charger l'orchestrateur : mentionner `@bmad-orchestrator` ou lancer la commande `/run-epic` (sans exécuter toute la boucle).
2. Demander : « Use the Task tool to invoke bmad-sm with prompt: say hello ».
3. Vérifier dans les tools disponibles (ou la réponse de l'agent) si **Task** apparaît et peut être appelé.

- **Si Task est disponible** : la boucle Autopilot peut s'exécuter normalement via `/run-epic` ou `/run-story`.
- **Si Task n'est pas disponible** (bug connu 2.4/2.5 sur certains plans) : documenter la limitation ici, et utiliser le contournement : l'orchestrateur décrit les étapes et l'utilisateur lance les commandes ou agents un par un (ex. @bmad-sm, @bmad-dev, etc.) jusqu'à résolution ou contournement MCP.

**Validé le 2026-02-26** : Task disponible ; run-story (epic-1, story 1-1) a enchaîné Create Story → Validate → Dev → Revision → Code Review avec succès.

Référence : `references/recherche/2026-02-26_cursor-autopilot-phase0-subagents-commands-agents_perplexity_reponse.md`.
