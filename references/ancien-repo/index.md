# Index — Documentation brownfield RecyClique 1.4.4

**Usage :** Point d'entrée pour l'analyse **référentielle** du repo source en vue de la migration vers **JARVOS Recyclique v0.1.0** (nouveau backend). Cette doc ne sert pas au développement continu de la branche 1.4.4.

---

## Aperçu

- [Aperçu projet](./project-overview.md)
- [Structure du projet et classification](./project-structure.md)
- [Stack technique](./technology-stack.md)
- [Patterns d'architecture](./architecture-patterns.md)

## Documentation existante (inventaire)

- [Inventaire de la documentation existante](./existing-documentation-inventory.md)

## Analyse conditionnelle (API, données, UI)

- [Contrats API (part api)](./api-contracts-api.md)
- [Modèles de données (part api)](./data-models-api.md)
- [Schéma BDD Recyclic dev (tables/colonnes)](../dumps/schema-recyclic-dev.md) — extrait depuis BDD dev (dossier dumps gitignore)
- [Inventaire composants UI (part frontend)](./component-inventory-frontend.md)
- [Liste des endpoints API v1.4.4](./v1.4.4-liste-endpoints-api.md)
- [Architecture brownfield (état actuel)](./architecture-brownfield.md)
- [Fonctionnalités actuelles](./fonctionnalites-actuelles.md)
- [README architecture current](./architecture-current-README.md)

## Arborescence et opérations

- [Arbre source et dossiers critiques](./source-tree-analysis.md)
- [Guide de développement](./development-guide.md)
- [Configuration déploiement](./deployment-configuration.md)
- [Architecture d'intégration (multi-part)](./integration-architecture.md)

## État du workflow

- Fichier d'état : `project-scan-report.json` (référence pour reprise si besoin).

---

## Démarrer la migration v0.1.0

1. Utiliser ce dossier comme **référence** : quoi garder (métier, règles, UX, décisions) et quoi laisser ou refondre (backend, auth, stack).
2. S'appuyer sur **docs/** du repo source (PRD, épics, architecture, stories) pour le Brief et le PRD du refactor.
3. Aligner le nouveau backend sur les besoins identifiés (API, modèles, intégrations) sans reprendre à l'identique l'implémentation 1.4.4.
4. **À chaque import de code** depuis 1.4.4 : appliquer la [checklist import 1.4.4](./checklist-import-1.4.4.md) (copy, consolidate, security).
