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
- Contraintes : découverte dynamique, pas d’exécution arbitraire, possibilité de dépendances entre modules, configuration par instance. Idéalement déclaratif (manifeste, entry points, etc.).

---

## Question pour la recherche

Compare les frameworks et approches Python pour implémenter un **système de modules / plugins** dans un backend FastAPI, en production :

1. **Pluggy** (utilisé par pytest, pip) : forces, limites, exemples d’usage dans une app métier (pas seulement outil CLI/test).
2. **Stevedore** (écosystème OpenStack, entry points) : idem, maturité, cas d’usage hors OpenStack.
3. **Entry points setuptools** seuls (sans stevedore) : suffisant pour une app modulaire ? Bonnes pratiques.
4. **Autres solutions** (importlib.metadata, manifeste YAML/JSON + loader custom, ou librairies dédiées) : avantages / inconvénients.
5. **Recommandation** : pour une application FastAPI avec modules optionnels (certains fournis par le projet, d’autres potentiellement par des tiers), quelle approche privilégier et pourquoi ? Critères : simplicité, maintenabilité, découverte au démarrage ou à la demande, gestion des dépendances entre modules.

Répondre en français. Citer versions récentes et sources (docs officielles, articles, retours d’expérience) quand c’est pertinent.

Voici une comparaison complète des approches Python pour un système de modules optionnels dans un backend FastAPI, adaptée au contexte **JARVOS Recyclique** (solo dev, FastAPI, contrainte anti-over-engineering).

***

## Vue d'ensemble

Python offre plusieurs niveaux d'abstraction pour les systèmes de plugins : des **entry points** natifs (stdlib), des bibliothèques de découverte comme **Stevedore**, un système de hooks complet comme **Pluggy**, ou des loaders custom. Il n'existe pas de solution universelle — le choix dépend du niveau de formalisme souhaité et du nombre d'auteurs de plugins.[^1]

***

## 1. Pluggy — Hooks formels et légers

Pluggy est le moteur de plugins derrière `pytest`, `tox` et `pip`. Il repose sur deux décorateurs : `@hookspec` (définit le contrat côté hôte) et `@hookimpl` (implémente le hook côté plugin).[^2]

**Forces :**

- Contrats formels et vérifiés à l'enregistrement — pas de duck-typing silencieux[^1]
- Supporte les priorités d'exécution (`tryfirst`, `trylast`) et le mode `hookwrapper` (équivalent d'un middleware autour du hook)[^2]
- Bibliothèque éprouvée, très légère (~500 lignes de code core), zéro dépendance externe
- Découverte via `pm.register()` ou combinable avec entry points setuptools[^3]

**Limites :**

- Conçu pour le **calling de hooks**, pas pour le lifecycle complet (pas d'état ACTIVE/ERROR/DISABLED natif)[^4]
- Pas de découverte automatique via le système de fichiers — il faut coupler avec entry points ou un scan `importlib`
- La documentation se concentre sur pytest ; les exemples d'apps métier sont rares[^5]

**Usage app métier :** Pluggy est pertinent pour des points d'extension transversaux — ex. un hook `on_sale_closed(session)` que le module Paheko et le module codes-barres interceptent chacun. C'est l'approche la plus proche du système de **signals Django** mais sans le framework.[^1]

***

## 2. Stevedore — Découverte via entry points

Stevedore (OpenStack) est une couche d'abstraction au-dessus des entry points setuptools. Il propose plusieurs types de managers : `DriverManager` (un seul plugin actif), `ExtensionManager` (tous les plugins d'un namespace), `HookManager` (appels en cascade).[^6]

**Forces :**

- Discovery standardisée et battle-tested dans des systèmes critiques (OpenStack, Horizon, Ceilometer)[^7]
- Chaque plugin est un package Python installé avec ses dépendances — gestion de dépendances via pip naturellement[^8]
- Isole bien les échecs : `propagate_map_exceptions=False` par défaut[^8]
- Supporte le rechargement et l'invocation parallèle[^9]

**Limites :**

- Nécessite que chaque module soit un **package installé** (`pip install`) — inadapté pour des modules internes dans un monorepo sans packaging[^6]
- Pas de système de hooks formels : le contrat est informel (signature de classe ou de fonction)[^1]
- Dépendance sur `pbr` (outil OpenStack) qui alourdit le projet[^9]
- Moins adapté pour des modules qui doivent s'enregistrer eux-mêmes dans FastAPI (routes, middlewares)

***

## 3. Entry points setuptools seuls

Depuis Python 3.9+, `importlib.metadata` est stdlib et permet de lire les entry points sans Stevedore  :[^10]

```python
from importlib.metadata import entry_points
plugins = entry_points(group="recyclic.modules")
for ep in plugins:
    module_class = ep.load()
```

Et dans le `pyproject.toml` du module :

```toml
[project.entry-points."recyclic.modules"]
paheko = "recyclic_paheko:PahekoModule"
```

**Suffisant pour une app modulaire ?** Oui, si les modules sont des **packages installés séparément** et que le lifecycle est géré manuellement. C'est la base de tous les autres systèmes. En revanche, entry points seuls ne fournissent ni hooks, ni état de cycle de vie, ni gestion des dépendances inter-modules — tout est à coder.[^10][^6]

***

## 4. Autres approches

### Manifeste YAML/TOML + loader custom

L'approche la plus pragmatique pour un monorepo avec modules internes : un fichier de configuration par instance déclare les modules actifs, et un loader `importlib.util` les charge.[^4]

```yaml
# instance.yml
modules:
  - recyclic.modules.caisse
  - recyclic.modules.paheko
  - recyclic.modules.barcodes
```

**Avantages :** zéro dépendance, contrôle total, pas besoin de packager chaque module, idéal pour des modules tous internes au projet.
**Inconvénients :** aucun standard, découverte tierce-partie impossible sans conventions explicites.

### Scan de répertoire via `importlib.util`

Scan d'un dossier `modules/` pour charger dynamiquement les fichiers `.py` présents. Simple mais fragile : pas de gestion des dépendances, ordre d'import non garanti, moins adapté à un environnement packagé.[^4]

### ABC + Protocol Python

Définir une `PluginInterface` avec `ABC` ou `Protocol` (typing structurel) pour valider la conformité des modules à l'enregistrement. C'est une technique complémentaire plutôt qu'une solution de découverte.[^4]

***

## Comparatif rapide

| Critère | Entry points seuls | Stevedore | Pluggy | Manifeste + loader |
| :-- | :-- | :-- | :-- | :-- |
| **Découverte** | Standard packaging | Standard packaging | Manuel ou EP | Config fichier |
| **Contrat formel** | Non | Non (informel) | Oui (`@hookspec`) | Non (ABC manuel) |
| **Lifecycle** | À coder | Partiel | À coder | À coder |
| **Dépendances inter-modules** | Non | Via pip | Non natif | Non |
| **Modules internes** | Lourd (packaging) | Lourd | Facile | Très facile |
| **Modules tiers** | Natif | Natif | Avec EP | Impossible |
| **Complexité** | Faible | Moyenne | Faible-Moyenne | Très faible |
| **Dépendances** | 0 (stdlib) | pbr, setuptools | 0 | 0 (+ PyYAML) |


***

## Recommandation pour JARVOS Recyclique

Compte tenu du contexte (solo dev, phase conception, anti-over-engineering, modules majoritairement internes avec quelques potentiels tiers), une **approche hybride en deux couches** est recommandée :

**Couche 1 — Découverte (immédiate) : Manifeste YAML + entry points**

- Les modules internes (caisse, Paheko, codes-barres) sont déclarés dans un fichier `modules.yml` par instance. Pas besoin de les packager séparément.
- Les modules tiers sont déclarés comme entry points sous `recyclic.modules` et découverts via `importlib.metadata`.[^10]
- Lors du démarrage FastAPI (`lifespan`), le loader parcourt les deux sources et instancie les modules activés.

**Couche 2 — Hooks (quand le besoin se présente) : Pluggy**

- Dès qu'un module doit réagir à un événement d'un autre module (ex. : clôture de caisse → écriture Paheko), ajouter Pluggy pour définir des `@hookspec` formels.[^2]
- Pluggy peut être introduit progressivement : commencer sans, l'ajouter uniquement si les appels inter-modules deviennent complexes.

**Ce qu'il faut éviter :** Stevedore force à packager chaque module comme un projet Python indépendant — inadapté à un monorepo solo en phase de prototypage. Un scan de répertoire pur est trop fragile pour de la production.[^9]

**Pattern concret pour FastAPI :**

```python
# app/core/module_loader.py
from importlib.metadata import entry_points
import yaml, importlib

class ModuleRegistry:
    def __init__(self): self._modules = {}

    def load_from_config(self, path: str):
        with open(path) as f:
            cfg = yaml.safe_load(f)
        for mod_path in cfg.get("modules", []):
            mod = importlib.import_module(mod_path)
            self._modules[mod_path] = mod.setup()  # convention

    def load_from_entry_points(self):
        for ep in entry_points(group="recyclic.modules"):
            self._modules[ep.name] = ep.load()()

    def startup(self, app):  # appelé dans lifespan FastAPI
        for m in self._modules.values():
            if hasattr(m, "register_routes"):
                m.register_routes(app)
```

Ce pattern est simple, testable, extensible, et s'aligne avec la convention FastAPI `lifespan` pour les événements startup/shutdown.[^10][^4]
<span style="display:none">[^11][^12][^13][^14][^15][^16][^17][^18][^19][^20][^21][^22][^23][^24][^25][^26][^27][^28][^29]</span>

<div align="center">⁂</div>

[^1]: https://lab.abilian.com/Tech/Python/Useful Libraries/Plugin Systems/Comparison/

[^2]: https://pluggy.readthedocs.io

[^3]: https://waylonwalker.com/pluggy-minimal-example/

[^4]: https://oneuptime.com/blog/post/2026-01-30-python-plugin-systems/view

[^5]: https://github.com/pytest-dev/pluggy/issues/130

[^6]: https://docs.openstack.org/stevedore/latest/user/tutorial/creating_plugins.html

[^7]: https://opendev.org/openstack/stevedore

[^8]: https://chinghwayu.com/2021/11/how-to-create-a-python-plugin-system-with-stevedore/

[^9]: https://github.com/openstack/stevedore

[^10]: https://lyz-code.github.io/blue-book/python_plugin_system/

[^11]: contexte-pour-recherche-externe.md

[^12]: https://github.com/orgs/community/discussions/162829

[^13]: https://dev.to/mrchike/fastapi-in-production-build-scale-deploy-series-b-services-queues-containers-2i08

[^14]: https://pypi.org/project/fastapi-plugins/0.1.0/

[^15]: https://www.reddit.com/r/Python/comments/1iif99x/must_know_python_libraries_new_and_old/

[^16]: https://blog.yusufberki.net/deploy-machine-learning-model-with-rest-api-using-fastapi-288f229161b7

[^17]: https://discuss.python.org/t/best-practices-for-managing-dynamic-imports-in-plugin-based-architecture/99482

[^18]: https://dev.to/mrchike/fastapi-in-production-build-scale-deploy-series-a-codebase-design-ao3

[^19]: https://www.linkedin.com/pulse/production-ready-fastapi-2025-architecture-glue-alexander-goncharenko-gd2gf

[^20]: https://cfp.in.pycon.org/2025/talk/U3TRT9/

[^21]: https://docs.pytest.org/en/stable/how-to/writing_plugins.html

[^22]: https://python.berlin/en/latest/_downloads/a9d076c8249896c6f5bdd90e3ccfcfd9/writing-plugin-friendly-applications-in-python.pdf

[^23]: https://tryolabs.com/blog/top-python-libraries-2025

[^24]: https://www.reddit.com/r/Python/comments/6q3myo/python_entry_points_explained/

[^25]: https://intellij-support.jetbrains.com/hc/en-us/community/posts/5162135977106-Running-pycharm-pytest-with-pluggy-hooks

[^26]: https://deepnote.com/blog/ultimate-guide-to-fastapi-library-in-python

[^27]: https://docs.pytest.org/en/stable/reference/plugin_list.html

[^28]: https://news.ycombinator.com/item?id=14873852

[^29]: https://fastapi.tiangolo.com

