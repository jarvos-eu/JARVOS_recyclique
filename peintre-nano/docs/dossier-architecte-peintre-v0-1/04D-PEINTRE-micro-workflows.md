# 04D-PEINTRE — Micro-workflows UI déclaratifs

> **But** : combler le trou identifié (IDEA-2026-03-31-001) — enchaînements de vues, navigation selon saisie, transitions « si saisie validée → aller à telle étape/panneau/action », **sans mini-langage de script**. Vocabulaire fermé CREOS, résolu par le moteur, agnostique. Même doctrine que le reste : app déclare, user surcharge, agent futur pilote (D-09), tout futur en prise inerte (D-15).
> **Ne pas confondre** avec la navigation *structurelle* (`NavigationManifest`, `05`) : ici ce sont des **micro-workflows internes à une page/flow**.
> **Existant à réutiliser** : `FlowRenderer.tsx` (chrome onglets/étapes, props impératives) devient le *rendu* d'un flow ; la **définition** passe en donnée CREOS (aujourd'hui codée en React dans les wizards caisse).

## 1. Grammaire (vocabulaire fermé)

```jsonc
{ "creos_kind": "flow_definition",
  "id": "cashflow-nominal",
  "kind": "wizard | tabbed | decision",      // formes closes
  "steps": [ { "id": "count", "panel_id": "count-panel" }, … ],
  "transitions": [
    { "from": "count", "on": "validated",     // event émis par un widget
      "guard": "count.balanced",              // RÉFÉRENCE à une rule (pas d'expression libre)
      "target": { "type": "step", "ref": "confirm" } }
  ],
  "shortcuts": [ { "key": "mod+enter", "command_id": "flow.next" } ]
}
```

- `target.type` ∈ `step | panel | overlay | command` (ferme les possibilités).
- `guard` = **référence** à une rule déclarée (réutilise le mapping CREOS State/Command/Event/Rule de la vision), jamais du code inline.
- `on` = event nommé émis par un widget (pas d'accès DOM libre).

## 2. Résolution (dans le moteur)

Le **MicroWorkflowOrchestrator** (moteur) : reçoit un event widget → évalue le(s) `guard` via les rules → si vrai, applique `target` (change step courant / ouvre panel / overlay / déclenche command). Le step courant alimente la visibilité des slots (`05` étape 2bis) et respecte AR39 (un target non autorisé est ignoré).

## 3. Hook inerte v0.1 (D-15 / D-16)

```ts
interface MicroWorkflowOrchestrator {
  onEvent(flowId: string, event: string, ctx): FlowTransitionResult; // v0.1: lit guards, log, NE navigue pas
}
const passthroughFlow: MicroWorkflowOrchestrator = { onEvent: () => ({ applied:false, reason:'reserved-v0.1' }) };
```
v0.1 : l'orchestrateur **lit** les `flow_definition`, **évalue** les guards (testable), mais **ne pilote pas** la navigation (les wizards caisse gardent leur logique React). Activer = remplacer l'implémentation. Preuve : fixture `flow-cashflow-nominal-steps.json` + test que les guards sont lus.

## 4. Articulation

- `FlowRenderer` = rendu (chrome) ; `flow_definition` = donnée ; orchestrator = résolution. Trois choses distinctes.
- Raccourcis de flow → passent par la même couche overlay/registre raccourcis que `04C`.
- Validation : schéma `flow-definition.schema.json` greffé sur la chaîne `validation/` (comme `presentation`).

## 5. DoD
- [ ] `flow-definition.schema.json` (`additionalProperties:false`), greffé validation.
- [ ] `MicroWorkflowOrchestrator` inerte branché + test guards lus (fixture cashflow).
- [ ] `FlowRenderer` documenté comme rendu d'un flow (pas la définition).
- [ ] Distinction micro-workflow vs navigation structurelle explicite.
- [ ] Cible de portage : sortir la logique step des wizards caisse vers `flow_definition` (post-v0.1, tracé).
