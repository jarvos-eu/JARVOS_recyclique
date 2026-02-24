<img src="https://r2cdn.perplexity.ai/pplx-full-logo-primary-dark%402x.png" style="height:64px;margin-right:32px"/>

# \# Prompt recherche — Pluggy vs. alternatives légères pour hooks inter-modules

**Date :** 2026-02-24
**Cible :** Perplexity Pro
**Usage :** Comparer Pluggy avec des alternatives plus légères pour un système de hooks/events inter-modules dans un backend FastAPI. Décider ce qu'on adopte (et quand).

---

## Contexte projet

Voir `contexte-pour-recherche-externe.md` pour le contexte complet.

On a un système de modules optionnels (manifeste TOML + entry points). Les modules doivent pouvoir réagir à des événements du reste du système — ex. :

- Clôture d'une session de caisse → le module Paheko Sync génère des écritures comptables
- Import d'un article → le module codes-barres génère un QR code
- Création d'un membre → le module Paheko met à jour l'adhérent

Ces interactions inter-modules nécessitent un mécanisme de hooks ou d'events. **Pluggy** est la solution identifiée, mais sa courbe d'apprentissage (hookspec / hookimpl / PluginManager) est non négligeable. On veut évaluer si une alternative plus légère suffit.

---

## Questions pour la recherche

1. **Blinker** (bibliothèque de signaux Python, utilisée par Flask) : comment fonctionne-t-il ? Est-il compatible async (FastAPI/asyncio) ? Peut-il gérer des hooks inter-modules avec le même niveau de robustesse que Pluggy ? Limites ?
2. **Pluggy vs. Blinker** : comparaison directe pour un cas d'usage comme « clôture caisse → réactions de plusieurs modules ». Lequel est plus simple à maintenir ? Lequel offre plus de contrôle (ordre d'exécution, gestion d'erreurs, annulation) ?
3. **EventBus maison** (20-30 lignes, `asyncio.Queue` ou dictionnaire `{event: [callbacks]}`) : est-ce une option raisonnable en production pour un projet solo, ou est-ce réinventer la roue avec des risques ?
4. **Autres options** (PyDispatcher, pydispatch, Pymitter, etc.) : y en a-t-il une particulièrement bien adaptée à FastAPI async ?
5. **Recommandation** : pour un backend FastAPI solo, avec ~5-10 événements max au départ, modules first-party uniquement — quelle approche pour les hooks inter-modules ? Critères : simplicité, async natif, gestion d'erreurs propre, évolutivité si le nombre d'événements grandit.

Répondre en français. Citer sources et versions récentes.

Excellente question ! Pour un solo dev en phase conception avec 5-10 événements au départ et des modules first-party, voici une analyse comparative des options légères.

***

## 1. Blinker — Signaux synchrones historiques

Blinker est la bibliothèque de signaux utilisée par Flask et SQLAlchemy depuis 2010. Elle offre un système pub-sub simple avec découplage par `sender`.[^1][^2]

### Fonctionnement de base

```python
from blinker import Signal

sale_closed = Signal()

@sale_closed.connect
def sync_to_paheko(sender, **kwargs):
    session_id = kwargs['session_id']
    # Synchroniser avec Paheko

# Émission
sale_closed.send("caisse_module", session_id=123)
```


### Compatibilité async FastAPI

**Problème majeur** : Blinker est fondamentalement **synchrone**. Depuis la version 1.6 (2023), elle propose `send_async()` pour envoyer à des receivers coroutines, mais c'est un ajout tardif et la documentation est minimale.[^1]

```python
# Blinker 1.6+
async def async_receiver(sender, **kwargs):
    await httpx.post(...)

await signal.send_async("sender", data=123)
```

**Limites async**  :[^1]

- Les receivers synchrones ne sont pas appelés dans `send_async()` — il faut choisir sync ou async, pas de mix
- Pas de gestion d'ordre d'exécution entre receivers async
- Pas de contrôle d'erreurs fin (un receiver qui échoue stop la propagation par défaut)


### Forces

- Très légère (zéro dépendance, stdlib pure)
- Weak references automatiques pour éviter les memory leaks[^2]
- Filtrage par sender : `signal.connect(receiver, sender="specific_sender")`
- Context manager `muted()` pour désactiver temporairement un signal[^1]


### Verdict pour FastAPI

Blinker est **inadapté pour un backend async moderne** en 2026. Son support async est un bolt-on tardif, pas une conception native.[^3][^1]

***

## 2. async-signals — Port Django pour FastAPI

[async-signals](https://pypi.org/project/async-signals/) (version 0.2.0, dernière MAJ déc. 2024)  est un portage direct du système de signaux Django, réécrit pour `async/await`.[^4]

### Fonctionnement

```python
from async_signals import Signal

sale_closed = Signal()

@sale_closed.connect
async def sync_to_paheko(sender, **kwargs):
    session_id = kwargs['session_id']
    await httpx.post(f"http://paheko/sync/{session_id}")

# Émission async
results = await sale_closed.send("caisse_module", session_id=123)
```


### Forces

- **Async natif** : `send()` est une coroutine, attend automatiquement les receivers async[^5]
- **Mix sync/async** : accepte des receivers synchrones ET asynchrones — les sync sont exécutés normalement[^5]
- **Filtrage par sender** : comme Blinker, `connect(receiver, sender="specific")`[^5]
- **Gestion d'erreurs** : `send_robust()` continue même si un receiver lève une exception, retourne `list[(receiver, result_or_exception)]`[^4]
- **Type hints complets** : annotations mypy/pyright[^5]
- **Weak references** : par défaut `weak=True`, désactivable[^4]


### Limites

- **Pas de contrôle d'ordre** : les receivers sont appelés dans l'ordre d'enregistrement (FIFO), pas de `tryfirst`/`trylast` comme Pluggy[^4]
- **Dépendance externe** (mais très légère, ~500 lignes)
- **Pas de hooks formels** : le contrat entre émetteur et receiver est informel (duck-typing sur `**kwargs`)


### Verdict

**Excellent choix pour FastAPI** : c'est la solution la plus simple pour des signaux async avec gestion d'erreurs robuste.[^5]

***

## 3. Pluggy — Hooks formels avec contrat

Pluggy (utilisé par pytest, tox, pip)  n'est pas un système de signaux, mais un **système de hooks avec spécification formelle**.[^6]

### Fonctionnement

```python
import pluggy

hookspec = pluggy.HookspecMarker("recyclic")
hookimpl = pluggy.HookimplMarker("recyclic")

class RecyclicHooks:
    @hookspec
    def on_sale_closed(self, session_id: int) -> None:
        """Appelé quand une session est clôturée."""

class PahekoModule:
    @hookimpl(trylast=True)  # Exécuté en dernier
    def on_sale_closed(self, session_id: int):
        # Sync Paheko
        pass

pm = pluggy.PluginManager("recyclic")
pm.add_hookspecs(RecyclicHooks)
pm.register(PahekoModule())

# Appel
pm.hook.on_sale_closed(session_id=123)
```


### Forces

- **Contrat formel** : `@hookspec` définit la signature, validation à l'enregistrement[^6]
- **Ordre d'exécution contrôlé** : `tryfirst`, `trylast`, ou ordre LIFO par défaut[^7]
- **HookWrappers** : équivalent d'un middleware, permet d'intercepter avant/après tous les autres hooks[^6]
- **Gestion d'erreurs** : un hook qui échoue stop la chaîne par défaut, mais récupérable[^7]


### Limites pour FastAPI

**Pluggy n'est PAS async-native**. Il fonctionne en synchrone uniquement. Pour l'utiliser avec FastAPI :[^6]

- Soit wrapper les hooks dans `asyncio.run_in_executor()` (lourd)
- Soit appeler les hooks dans des background tasks (perte de contrôle transactionnel)
- Soit limiter les hooks à de la logique sync (ex. calculs, pas I/O réseau)


### Verdict

Pluggy est **over-engineered pour 5-10 événements** et mal adapté à un backend async. Réserve-le pour un projet avec des dizaines de hooks et des besoins de validation formelle.[^3][^6]

***

## 4. EventBus maison — Risques et bonnes pratiques

### Implémentation minimale

```python
from typing import Callable, Awaitable
from collections import defaultdict

class EventBus:
    def __init__(self):
        self._handlers: dict[str, list[Callable]] = defaultdict(list)
    
    def on(self, event: str, handler: Callable):
        self._handlers[event].append(handler)
    
    async def emit(self, event: str, **kwargs):
        results = []
        for handler in self._handlers[event]:
            if asyncio.iscoroutinefunction(handler):
                results.append(await handler(**kwargs))
            else:
                results.append(handler(**kwargs))
        return results
```


### Risques en production[^8][^9]

1. **Gestion d'erreurs manquante** : un handler qui échoue fait crasher tout le pipeline[^8]
2. **Ordre d'exécution non déterministe** si handlers async concurrents[^10]
3. **Memory leaks** : sans weak references, les handlers persistent même si l'objet est détruit
4. **Debugging difficile** : pas de stacktrace claire quand un event n'est pas écouté[^9]
5. **Event chains** : si un handler émet un autre event, risque de boucles infinies[^10][^9]

### Quand c'est acceptable[^9]

Un EventBus maison est raisonnable **si et seulement si** :

- Tous les modules sont first-party (pas de plugins tiers incontrôlés)
- Tu implémentes `send_robust()` dès le début (try/except autour de chaque handler)
- Tu log explicitement les events émis et les handlers appelés
- Tu as des tests d'intégration pour chaque event

**Ne réinvente pas la roue** sauf si `async-signals` ne couvre pas un besoin critique.[^3][^9]

***

## 5. Autres bibliothèques

### bubus (2025)

[bubus](https://github.com/browser-use/bubus)  est un EventBus production-ready récent avec :[^10]

- Async natif
- WAL (Write-Ahead Logging) pour persistence
- Retry policy avec backoff exponentiel
- Parallel execution (MAIS attention : ordre non-déterministe)[^10]

**Problème** : projet très récent (juin 2025), peu de retours terrain, plus complexe qu'`async-signals`.[^10]

### PyPubSub, Pymitter, PyDispatcher

- **PyPubSub** : mature mais synchrone[^3]
- **Pymitter** : port de Node.js EventEmitter, pas async natif[^3]
- **PyDispatcher** : ancien (2010), remplacé par Blinker[^3]

Tous sont **moins adaptés que async-signals pour FastAPI**.[^3]

***

## Comparatif synthétique

| Critère | async-signals | Blinker | Pluggy | EventBus maison | bubus |
| :-- | :-- | :-- | :-- | :-- | :-- |
| **Async natif** | ✅ Oui | ⚠️ Partiel (1.6+) | ❌ Non | ✅ (si bien codé) | ✅ Oui |
| **Mix sync/async** | ✅ Oui | ❌ Non | — | ✅ (manuel) | ✅ Oui |
| **Ordre contrôlé** | ❌ FIFO seulement | ❌ Non | ✅ tryfirst/last | ❌ Non | ⚠️ Oui mais FIFO |
| **Gestion erreurs** | ✅ send_robust | ⚠️ Basique | ✅ Bonne | ❌ À coder | ✅ Retry policy |
| **Contrat formel** | ❌ Duck typing | ❌ Non | ✅ hookspec | ❌ Non | ❌ Non |
| **Complexité** | Très faible | Faible | Moyenne | Très faible | Moyenne-haute |
| **Maturité** | 2 ans | 14 ans | 8 ans | N/A | <1 an |
| **Dépendances** | 0 | 0 | 0 | 0 | Redis (optionnel) |


***

## Recommandation finale pour JARVOS Recyclique

Pour un backend FastAPI solo, avec ~5-10 événements au départ, modules first-party uniquement :

### Adopte **async-signals** immédiatement

**Pourquoi maintenant** :

- Async natif, zéro friction avec FastAPI
- `send_robust()` pour isoler les erreurs de modules
- Simple à débuguer (retour de `list[(receiver, result)]`)
- Pattern Django éprouvé depuis 2006, porté pour async en 2022[^4]

**Pattern d'usage** :

```python
# app/core/signals.py
from async_signals import Signal

sale_closed = Signal()
article_imported = Signal()
member_created = Signal()

# modules/paheko/handlers.py
from app.core.signals import sale_closed

@sale_closed.connect
async def sync_session_to_paheko(sender, session_id: int, **kwargs):
    async with httpx.AsyncClient() as client:
        await client.post(f"{PAHEKO_URL}/api/sync", json={"session": session_id})

# app/routers/caisse.py
@router.post("/sessions/{id}/close")
async def close_session(id: int):
    # ... logique métier
    await sale_closed.send("caisse", session_id=id, total=total)
    return {"status": "closed"}
```


### Quand considérer Pluggy (plus tard)

**Uniquement si** :

- Tu as >20 hooks et besoin de les organiser formellement
- Tu veux valider les signatures de hooks à l'enregistrement (type safety)
- Tu as besoin de `hookwrapper` (middleware sur hooks)

**Mais** : Pluggy sync + FastAPI async = mauvais mariage. Si tu atteins ce niveau de complexité, repense l'architecture (event sourcing, CQRS, ou Message Queue externe type Redis Streams).[^10][^3]

### N'utilise PAS

- **Blinker** : support async trop limité pour 2026[^1]
- **EventBus maison** : async-signals fait déjà exactement ça en mieux[^9][^4]
- **bubus** : trop récent, over-engineered pour tes besoins[^10]

***

## Implémentation concrète dans le module loader

```python
# app/core/module_loader.py
from async_signals import Signal

class ModuleRegistry:
    def __init__(self):
        self._modules = {}
        self.signals = {
            "sale_closed": Signal(),
            "article_imported": Signal(),
            "member_created": Signal(),
        }
    
    def load_module(self, module_class):
        module = module_class()
        # Enregistrer les routes
        if hasattr(module, "register_routes"):
            module.register_routes(self.app)
        # Enregistrer les signal handlers
        if hasattr(module, "register_signals"):
            module.register_signals(self.signals)
    
# modules/paheko/module.py
class PahekoModule:
    def register_signals(self, signals):
        signals["sale_closed"].connect(self.sync_session)
    
    async def sync_session(self, sender, session_id: int, **kwargs):
        # Logique sync Paheko
        pass
```

**Évolutivité** : si tu atteins 50+ événements ou modules tiers, tu pourras migrer vers une Message Queue (Redis Streams, RabbitMQ) sans changer l'API des modules — juste remplacer `Signal.send()` par `queue.publish()`.[^10]
<span style="display:none">[^11][^12][^13][^14][^15][^16][^17][^18][^19][^20][^21][^22][^23][^24][^25][^26][^27][^28][^29][^30]</span>

<div align="center">⁂</div>

[^1]: https://blinker.readthedocs.io/en/stable/

[^2]: https://github.com/pallets-eco/blinker

[^3]: https://stackoverflow.com/questions/1092531/which-python-packages-offer-a-stand-alone-event-system

[^4]: https://pypi.org/project/async-signals/

[^5]: https://github.com/team23/async-signals

[^6]: https://pluggy.readthedocs.io/en/latest/

[^7]: https://pluggy.readthedocs.io/en/stable/

[^8]: https://dev.to/kuba_szw/how-i-fixed-my-event-bus-before-it-could-lose-money-546i

[^9]: https://www.techyourchance.com/event-bus/

[^10]: https://github.com/browser-use/bubus

[^11]: https://pypi.org/project/blinker-async/

[^12]: https://github.com/jucacrispim/asyncblink

[^13]: https://fastapi.tiangolo.com/fr/alternatives/

[^14]: https://lab.abilian.com/Tech/Python/Useful Libraries/Plugin Systems/Comparison/

[^15]: https://fastapi.tiangolo.com/alternatives/

[^16]: https://www.reddit.com/r/FastAPI/comments/1iduldv/reactive_signals_for_python_with_async_support/

[^17]: https://www.reddit.com/r/Python/comments/cz53ye/blinker_vs_rxpy_for_pubsub_implementation/

[^18]: https://www.reddit.com/r/Python/comments/u6g9bf/are_there_any_task_queue_libraries_with_the/

[^19]: https://www.reddit.com/r/Python/comments/b813r/blinker_fast_simple_objecttoobject_and_broadcast/

[^20]: https://sqlpey.com/python/top-12-python-packages-event-system/

[^21]: https://fastapi.tiangolo.com/async/

[^22]: https://ruarfff.com/posts/understanding-python-async

[^23]: https://fastapi.tiangolo.com/tutorial/background-tasks/

[^24]: https://blog.greeden.me/en/2025/08/05/mastering-asynchronous-processing-with-fastapi-a-guide-to-background-tasks-and-websocket-usage/

[^25]: https://stackoverflow.com/questions/75463993/what-does-async-actually-do-in-fastapi

[^26]: https://www.youtube.com/watch?v=KL6CjNxkZDQ

[^27]: https://leapcell.io/blog/understanding-pitfalls-of-async-task-management-in-fastapi-requests

[^28]: https://www.reddit.com/r/androiddev/comments/2xsinq/reactive_programming_vs_event_bus/

[^29]: https://www.youtube.com/watch?v=tGD3653BrZ8

[^30]: https://stackoverflow.com/questions/8092026/eventbus-event-order

