# Prompt recherche — Frameworks « modules / plugins » Python

**Date :** 2026-02-24  
**Cible :** Perplexity Pro  
**Usage :** Comparer et recommander des approches techniques pour un système de **modules optionnels** (chargement dynamique, découverte, lifecycle) dans un backend Python.

---

## Contexte projet

- Backend Python (FastAPI) pour une application métier (gestion de ressourcerie, caisse, flux matière).
- On souhaite un **système de modules optionnels** : chaque instance peut activer un sous-ensemble de modules (ex. intégration Paheko, module codes-barres, connecteur JARVOS, etc.).
- Les « modules » sont des unités fonctionnelles installables ; le **mécanisme technique** sous-jacent est un framework de type plugin (découverte, chargement, hooks ou extensions).
- Contraintes : découverte dynamique, pas d'exécution arbitraire, possibilité de dépendances entre modules, configuration par instance. Idéalement déclaratif (manifeste, entry points, etc.).

---

## Question pour la recherche

Compare les frameworks et approches Python pour implémenter un **système de modules / plugins** dans un backend FastAPI, en production :

1. **Pluggy** (utilisé par pytest, pip) : forces, limites, exemples d'usage dans une app métier (pas seulement outil CLI/test).
2. **Stevedore** (écosystème OpenStack, entry points) : idem, maturité, cas d'usage hors OpenStack.
3. **Entry points setuptools** seuls (sans stevedore) : suffisant pour une app modulaire ? Bonnes pratiques.
4. **Autres solutions** (importlib.metadata, manifeste YAML/JSON + loader custom, ou librairies dédiées) : avantages / inconvénients.
5. **Recommandation** : pour une application FastAPI avec modules optionnels (certains fournis par le projet, d'autres potentiellement par des tiers), quelle approche privilégier et pourquoi ? Critères : simplicité, maintenabilité, découverte au démarrage ou à la demande, gestion des dépendances entre modules.

Répondre en français. Citer versions récentes et sources (docs officielles, articles, retours d'expérience) quand c'est pertinent.
