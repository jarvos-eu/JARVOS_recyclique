<img src="https://r2cdn.perplexity.ai/pplx-full-logo-primary-dark%402x.png" style="height:64px;margin-right:32px"/>

# \# Prompt recherche — Frameworks « modules / plugins » Python

**Date :** 2026-02-24  
**Cible :** Perplexity Pro  
**Usage :** Comparer et recommander des approches techniques pour un système de **modules optionnels** (chargement dynamique, découverte, lifecycle) dans un backend Python.

en KB, il y a un fichier qui s'appelle contexte pour recherche externe. Il y a un peu de contexte.
et si besoin, tu as accès aussi au repo JARVOS_recyclique
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

Pour un backend FastAPI avec modules optionnels, voici une comparaison des principales approches Python de système de plugins/modules en production :

## Pluggy

**Pluggy** est le framework de plugins de pytest, cristallisé pour permettre des architectures extensibles basées sur des hooks. Il offre un système déclaratif avec `@hookspec` (définition des points d'extension) et `@hookimpl` (implémentation par les plugins).[^1][^2]

### Forces

- **Architecture hooks robuste** : système de « specification → implémentation » éprouvé en production (pytest, tox, devpi)[^2][^1]
- **Contrôle fin du cycle d'appel** : ordre d'exécution (`tryfirst`, `trylast`), wrappers pour code pré/post-hook, gestion d'exceptions[^1]
- **Flexible** : les hookimpls peuvent accepter moins d'arguments que les hookspecs (évolution compatible), support de `firstresult` pour optimisation[^1]
- **Pas de dépendance aux entry points** : découverte manuelle ou via setuptools selon le besoin[^1]


### Limites

- **Pas d'architecture « app métier » native** : conçu pour des outils CLI/test ; nécessite de structurer soi-même l'intégration avec FastAPI (registre de routes, lifecycle événementiel)[^3][^4]
- **Courbe d'apprentissage** : concepts `hookspec`/`hookimpl` plus abstraits qu'un simple `import module`[^5][^2]
- **Pas de gestion de dépendances inter-plugins** : à implémenter manuellement[^2]


### Usage dans une app métier

Peu d'exemples documentés hors outils dev. Le projet **pAPI** (2025) utilise Pluggy pour créer un framework modulaire FastAPI avec découverte automatique de routes et addons, démontrant la faisabilité mais nécessitant une couche d'abstraction.[^6]

## Stevedore

**Stevedore** est la bibliothèque d'OpenStack pour gérer les plugins via setuptools entry points. Elle fournit des gestionnaires (`DriverManager`, `ExtensionManager`, etc.) pour charger dynamiquement des extensions déclarées dans `setup.py` ou `pyproject.toml`.[^7][^8]

### Forces

- **Standards Python** : repose sur les entry points setuptools, mécanisme natif de découverte de code[^9][^7]
- **Patterns préfabriqués** : plusieurs managers (driver unique, liste d'extensions, nommées, dispatcher) pour cas d'usage courants[^7]
- **Maturité** : utilisé massivement dans l'écosystème OpenStack depuis 2012[^10][^11]
- **Déclaratif** : déclaration dans `pyproject.toml`, pas de code dans l'app pour enregistrer manuellement[^8]


### Limites

- **Moins flexible que Pluggy** : pas de système de hooks/wrappers, ordre d'exécution LIFO simple[^7]
- **Dépendance packaging** : chaque module doit être un package installable (même en mode editable), plus lourd pour dev/tests[^8]
- **Usage hors OpenStack limité** : peu d'exemples d'apps métier (pas CLI) l'utilisant en 2025[^12][^9]


### Cas d'usage métier

L'exemple tutoriel montre un système de drivers matériels (relais) avec instanciation à la demande. Applicable à votre cas : modules activés par config → stevedore charge ceux déclarés via entry points.[^9]

## Entry points setuptools seuls

Les entry points sont le mécanisme standard de Python pour découverte de plugins : un namespace déclaré dans `pyproject.toml` et `importlib.metadata.entry_points()` pour charger.[^13][^14]

### Avantages

- **Simplicité** : pas de dépendance externe (stdlib depuis Python 3.8), 10-15 lignes pour un loader basique[^13]
- **Standard** : compris par tout l'écosystème (pip, poetry, etc.)[^15]
- **Suffisant pour cas simples** : découverte au démarrage, chargement à la demande, activation conditionnelle[^13]


### Inconvénients

- **Pas de lifecycle** : pas de gestion startup/shutdown, hooks ou wrappers[^13]
- **Code répétitif** : stevedore ou pluggy existent justement pour éviter de réécrire la logique de gestion[^7]
- **Gestion dépendances inter-modules** : à coder manuellement (graphe, ordre de chargement)[^13]


### Bonnes pratiques

- Déclarer un namespace dédié (`jarvos_recyclique.modules`)[^15]
- Loader au démarrage FastAPI (lifespan) avec `importlib.metadata.entry_points(group='...')`[^14]
- Chaque module expose une classe/fonction standardisée (`setup(app, config)`)[^4]


## Autres solutions

### `importlib.metadata` + manifeste YAML

Approche hybride : manifestes JSON/YAML pour métadonnées (dépendances, config) et `importlib.import_module()` pour charger. Utilisée par pAPI en complément.[^14][^6]

**Avantages** : contrôle total, pas de contrainte packaging
**Inconvénients** : réinvente stevedore, maintenance à long terme[^14]

### Frameworks dédiés FastAPI

- **fastapi-plugins** : utilitaires cache/scheduler/logging, pas système de modules métier[^16]
- **pAPI** : framework expérimental (WIP) pour APIs modulaires + LLM, intéressant mais jeune[^6]


## Recommandation pour JARVOS Recyclique

Pour votre backend FastAPI avec modules optionnels (Paheko sync, codes-barres, JARVOS connecteur), je recommande **entry points setuptools seuls** pour démarrer, avec migration vers **Stevedore** si la complexité augmente.

### Justification

1. **Simplicité** : entry points couvrent découverte + chargement, pas besoin de hooks complexes pour vos modules (pas de wrapping, ordre simple)[^15][^13]
2. **Découverte au démarrage** : charger modules activés via config dans `lifespan` FastAPI, suffisant pour vos besoins[^13]
3. **Éviter over-engineering** : Pluggy pertinent si besoin de hooks multi-phases (pré/post-traitement, wrapping), pas le cas actuellement[^12][^2]
4. **Dépendances entre modules** : implémenter un ordre de chargement simple (graphe topologique 50 lignes) si nécessaire[^4]

### Architecture proposée

```python
# pyproject.toml de chaque module
[project.entry-points."recyclique.modules"]
paheko = "recyclique_modules.paheko:PahekoModule"

# core/loader.py
from importlib.metadata import entry_points

def load_modules(app, config):
    for ep in entry_points(group='recyclique.modules'):
        if ep.name in config.enabled_modules:
            module_class = ep.load()
            module = module_class(app, config)
            await module.setup()  # lifecycle standardisé
```


### Migration ultérieure

Si besoin de hooks avancés (ex : module A modifie comportement module B, wrappers), migrer vers **Pluggy** avec pattern hookspec/hookimpl. Stevedore reste pertinent si volonté stricte de découplage via packaging.[^2][^12][^7]
<span style="display:none">[^17][^18][^19][^20][^21][^22][^23][^24][^25][^26][^27][^28][^29][^30][^31][^32][^33][^34][^35][^36][^37][^38][^39][^40]</span>

<div align="center">⁂</div>

[^1]: contexte-pour-recherche-externe.md

[^2]: https://pluggy.readthedocs.io

[^3]: https://waylonwalker.com/pluggy-minimal-example/

[^4]: https://alysivji.github.io/simple-plugin-system.html

[^5]: https://kracekumar.com/post/build_plugins_with_pluggy

[^6]: https://github.com/efirvida/pAPI

[^7]: https://docs.openstack.org/stevedore/2025.2/

[^8]: https://docs.openstack.org/stevedore/latest/user/tutorial/creating_plugins.html

[^9]: https://chinghwayu.com/2021/11/how-to-create-a-python-plugin-system-with-stevedore/

[^10]: https://opendev.org/openstack/stevedore

[^11]: https://www.freshports.org/devel/py-stevedore

[^12]: https://lab.abilian.com/Tech/Programming Techniques/Plugins/

[^13]: https://setuptools.pypa.io/en/latest/userguide/entry_point.html

[^14]: https://docs.python.org/3/library/importlib.metadata.html

[^15]: https://packaging.python.org/specifications/entry-points/

[^16]: https://github.com/madkote/fastapi-plugins

[^17]: presentation-plateforme-recyclic.md

[^18]: paheko_guide_a4.pdf

[^19]: TODO Christophe - RecycClique \& Paheko.pdf

[^20]: 2025-01-30_RETRAITEMENT_recyclique-guide-complet-Paheko.md

[^21]: 00_JARVOS_mini.md

[^22]: JARVOS_nano analyse-opus_4.6

[^23]: appercu_ecosysteme.md

[^24]: 📋 __RecyClique - Système RAG Intelligent _ Dossier.pdf

[^25]: Comment les ressourceries doivent peuvent faire po.pdf

[^26]: Paheko RecyClique.md

[^27]: https://dev.to/mrchike/fastapi-in-production-build-scale-deploy-series-a-codebase-design-ao3

[^28]: https://python-gino.org/docs/en/master/tutorials/fastapi.html

[^29]: https://testdriven.io/blog/fastapi-crud/

[^30]: https://fastapi.tiangolo.com/tutorial/testing/

[^31]: https://github.com/pytest-dev/pluggy

[^32]: https://semaphore.io/blog/custom-middleware-fastapi

[^33]: https://blog.yusufberki.net/deploy-machine-learning-model-with-rest-api-using-fastapi-288f229161b7

[^34]: https://isense-gitlab.iccs.gr/pluggy_public/pluggy-examples

[^35]: https://python.berlin/en/latest/_downloads/a9d076c8249896c6f5bdd90e3ccfcfd9/writing-plugin-friendly-applications-in-python.pdf

[^36]: https://blog.jetbrains.com/pycharm/2025/09/the-most-popular-python-frameworks-and-libraries-in-2025-2/

[^37]: https://docs.pytest.org/en/stable/how-to/writing_hook_functions.html

[^38]: https://deepnote.com/blog/ultimate-guide-to-fastapi-library-in-python

[^39]: https://stackoverflow.com/questions/38740649/is-plug-in-based-approach-considered-good-practice-for-gui-app-development-in-py

[^40]: https://www.augmentcode.com/tools/fastapi-ai-development-tools-developer-guide-for-2025

