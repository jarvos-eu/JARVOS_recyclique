# Slots RecyClique — points d'injection pour les modules

Les **slots** permettent d'injecter du contenu fourni par les modules (extension points) dans les layouts ou domaines (caisse, réception, admin). Référence : **FR24, FR25** (epics.md) ; architecture — Frontend (Slots, extension points).

## Rôle

- Un **slot** est un emplacement nommé dans l'UI (ex. `header.actions`, `caisse.toolbar`) où un module peut enregistrer un composant React.
- Les modules frontend pourront **enregistrer** des slots au bootstrap (via un registre ou un contexte) pour personnaliser l'affichage sans modifier le cœur de l'app.

## Convention d'enregistrement (à implémenter dans les stories modulaires)

- **Registre** : un objet (ou contexte) `slotRegistry` ou équivalent exposé par `shared/slots` permettra d'appeler `registerSlot(slotId, component)`.
- **Rendu** : dans un layout ou une page, utiliser `<Slot name="header.actions" />` (ou équivalent) pour rendre le contenu enregistré.
- Alignement avec la recherche technique « affichage dynamique, extension points Peintre » et les stubs LayoutConfigService / VisualProvider (architecture).

## Structure

- `shared/slots/` : point d'entrée et documentation.
- Les implémentations concrètes (registre, composant Slot, enregistrement au chargement des modules) seront ajoutées dans les stories suivantes (modules, layout dynamique).

## Références

- `_bmad-output/planning-artifacts/architecture.md` — Frontend Architecture (Slots, extension points), Project Structure.
- `_bmad-output/planning-artifacts/epics.md` — FR24, FR25.
