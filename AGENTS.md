# AGENTS — JARVOS_recyclique

## Purpose

Monorepo **Recyclique v2** : front canon **peintre-nano**, back canon **recyclique/api**, contrats partagés **contracts/**. Ce fichier est le **rail DOX-lite** : traversal, index des zones code, renvois vers le canon applicatif et la doc durable.

**Hors périmètre agent (ne pas éditer ni implémenter par défaut) :** le dossier **`recyclique-1.4.4/`** — référence historique / compose legacy ; le travail actif se fait dans les trois zones indexées ci-dessous.

## Traversal (avant toute édition)

1. Lire ce fichier (`AGENTS.md` racine).
2. Marcher jusqu’au dossier cible ; lire **chaque** `AGENTS.md` sur le chemin parent → enfant.
3. Charger **`_bmad-output/project-context.md`** — **canon applicatif** (pile, anti-patterns, règles Epic 26, etc.). Ne pas dupliquer son contenu ici.
4. Mémoire projet / état programme : `references/index.md` (ciblé, pas en entier) ; mémoire trio BMAD → skills Mentor / Ariane / Clio, pas d’écriture dans ces `AGENTS.md`.
5. Rules Cursor (`.cursor/rules/`) s’appliquent en plus de cette hiérarchie.

## Ownership

- **Strophe** — décisions produit, validation push Git, GO sur changements contractuels majeurs.
- **Agents IA** — implémentation dans peintre-nano, recyclique/api, contracts ; respect traversal + canon.

## Canon et doc (renvois, pas copies)

| Besoin | Fichier |
|--------|---------|
| Règles implémentation agents | `_bmad-output/project-context.md` |
| Cadrage métier / specs | `references/index.md` → sous-index ciblés |
| Architecture & boundaries | `_bmad-output/planning-artifacts/architecture/project-structure-boundaries.md` |
| Pilotage BMAD / epics | `_bmad-output/planning-artifacts/guide-pilotage-v2.md`, `sprint-status.yaml` |
| Git (commit, format, ordre) | `references/procedure-git-cursor.md` — **pas de `git push` sans OK explicite Strophe** |

**`references/`** = *project knowledge* documentaire uniquement — **aucun import runtime** depuis le front ou l’API.

## Child AGENTS Index

| Zone | Chemin | Rôle |
|------|--------|------|
| Front canon | [`peintre-nano/AGENTS.md`](peintre-nano/AGENTS.md) | React 18, TS strict, Vite 6, Vitest 3, Mantine 8 |
| Back canon | [`recyclique/api/AGENTS.md`](recyclique/api/AGENTS.md) | FastAPI, SQLAlchemy sync, Pydantic v2 (`recyclic-api`) |
| Contrats | [`contracts/AGENTS.md`](contracts/AGENTS.md) | OpenAPI + CREOS, codegen `recyclique-api.ts` |

## Work guidance (transverse)

- Implémenter par défaut dans **peintre-nano** + **recyclique/api** ; synchroniser **contracts/** quand l’API ou les manifests CREOS évoluent.
- Après changement de contrat local dans un `AGENTS.md` enfant : mettre à jour l’enfant touché ; mettre à jour cet index seulement si une zone est ajoutée ou retirée.
- Pas de journal de session dans ces fichiers — handoffs datés → `references/artefacts/`.

## Verification (smoke transverse)

| Zone | Commande |
|------|----------|
| Front | `cd peintre-nano && npm run lint && npm run test && npm run build` |
| API | Voir [`recyclique/api/tests/README.md`](recyclique/api/tests/README.md) |
| Contrats TS | `cd contracts/openapi && npm run generate` (après évolution du YAML) |

Détail et périmètres pytest : README de chaque zone (index ci-dessus).
