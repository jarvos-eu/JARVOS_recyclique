# Brief de lancement — `epic-28`

## Objectif

Lancer `@bmad-epic-runner epic-28` sur un backlog désormais préparé pour la Vague A, sans démarrer encore la Vague B automatiquement dans ce chat.

## Pré-conditions Vague A

- `epics.md` contient `Epic 28` et ses stories `28.1` à `28.5`.
- `sprint-status.yaml` contient `epic-28` et le bloc des stories associées.
- `28-1-stabiliser-la-caisse-terrain-p0-session-finalisation-et-cloture.md` existe et est `ready-for-dev`.
- `28-2` à `28-5` existent comme story seeds backlog.
- `00_SYNC_STATUS.md` est initialisé pour le chantier.

## Ordre canonique

`28.1 -> 28.2 -> 28.3 -> 28.4 -> 28.5`

Une seule story active à la fois sur le dépôt.

## Première story candidate

- `28-1-stabiliser-la-caisse-terrain-p0-session-finalisation-et-cloture`

## Rappels de discipline

- Après chaque story : QA/CR puis sync `references/revision/` sur les `REV-*` réellement couverts.
- `Validé HITL` reste manuel.
- Ne pas lancer `9.7` ni `10.7` tant que le flux Epic 28 n’a pas avancé selon le plan.

## Commande canonique

```text
@bmad-epic-runner epic-28
```
