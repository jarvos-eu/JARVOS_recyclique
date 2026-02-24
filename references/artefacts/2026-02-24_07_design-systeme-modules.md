# Design — Système de modules JARVOS Recyclique

**Date :** 2026-02-24
**Session :** Analyse critique des réponses Perplexity — Mary (analyst)
**Source :** `references/recherche/2026-02-24_reponse-*_perplexity_frameworks-modules-python.md`

---

## Décisions arbitrées

| Décision | Choix retenu | Raison |
|----------|-------------|--------|
| Manifeste | TOML (`module.toml` par module) | Nativement supporté Python 3.11+, pas d'ambiguité d'indentation, aligné avec pyproject.toml |
| Modules internes | Répertoires dans monorepo, pas de packaging pip | Solo dev, monorepo, pas besoin de publier chaque module |
| Modules tiers | Entry points setuptools si/quand nécessaire | Porte ouverte sans coût immédiat |
| Activation par instance | `config.toml` (`[modules] enabled = [...]`) | Simple, versionnable, pas de dépendance DB au boot |
| Hooks inter-modules | **Redis Streams** (EventBus wrapper, dès le départ). | Déploiement central = Gunicorn multi-workers ; async-signals in-process ne traverse pas les workers. Redis déjà en stack. Redis Pub/Sub exclu (pas de persistance). Durabilité, replay, ack natifs. |
| Frontend | Monorepo React, lazy loading, un seul build | Builds séparés = archi équipe/tiers, pas pertinent ici |
| UI extension | Slots (`<ModuleSlot name="..." />`) | Inspiré snippets Paheko, faisable sans Module Federation |
| Contrat de base | `ModuleBase` avec `startup`, `shutdown`, `register_routes`, `register_ui_extensions` | `startup/shutdown` obligatoires dès le départ pour lifecycle propre |
| Dépendances inter-modules | Déclaration `depends` + validation au démarrage | Pas de topological sort automatique ; erreur explicite si manquant |
| Sécurité modules tiers | Hors scope — modules first-party uniquement | À adresser séparément si/quand modules tiers |

---

## Contrat ModuleBase (proposition)

```python
class ModuleBase(ABC):
    async def startup(self, app: FastAPI, config: dict): pass
    async def shutdown(self): pass
    def register_routes(self, app: FastAPI): pass
    def register_signals(self, bus: "EventBus"): pass  # optionnel ; enregistre handlers sur EventBus
    def register_ui_extensions(self) -> dict[str, list[str]]: return {}
```

---

## Structure module.toml

```toml
name = "Paheko Sync"
version = "0.1.0"
description = "Synchronisation comptable avec Paheko"

[permissions]
section = "accounting"
level = "write"

[ui]
routes = ["/modules/paheko"]
slots = ["sale_details", "settings_menu"]

[dependencies]
modules = ["caisse"]
python = ["httpx>=0.27"]
```

---

## Pattern loader (FastAPI lifespan)

```python
# core/module_loader.py
from importlib.metadata import entry_points
import tomllib, importlib

class ModuleRegistry:
    def __init__(self): self._modules = {}

    def load_from_config(self, config_path: str):
        with open(config_path, "rb") as f:
            cfg = tomllib.load(f)
        for mod_name in cfg.get("modules", {}).get("enabled", []):
            mod = importlib.import_module(f"recyclic.modules.{mod_name}")
            self._modules[mod_name] = mod.MODULE_CLASS()

    def load_from_entry_points(self):
        for ep in entry_points(group="recyclic.modules"):
            self._modules[ep.name] = ep.load()()

    async def startup(self, app: FastAPI, config: dict):
        for m in self._modules.values():
            m.register_routes(app)
            await m.startup(app, config)

    async def shutdown(self):
        for m in self._modules.values():
            await m.shutdown()
```

---

## Pattern frontend (React)

```tsx
// core/ModuleRegistry.tsx — lazy loading par route
const modules = {
  'paheko': lazy(() => import('@/modules/paheko/PahekoApp')),
  'barcodes': lazy(() => import('@/modules/barcodes/BarcodesApp')),
}

// core/ModuleSlot.tsx — slots UI (inspiré snippets Paheko)
export function ModuleSlot({ name }: { name: string }) {
  const extensions = useModuleExtensions(name)
  return <>{extensions.map((Comp, i) => <Comp key={i} />)}</>
}

// Usage dans l'app principale
<SaleDetails>
  <ModuleSlot name="sale_details" />
</SaleDetails>
```

---

## Hooks / événements — EventBus Redis Streams

**Décision finale (2026-02-24)** : Redis Streams directement, dès le départ. Raison : déploiement central avec Gunicorn multi-workers — async-signals est in-process et ne traverse pas les workers. Redis est déjà en stack.

### Principe : les modules ne connaissent pas Redis

```
[Module caisse]  -->  bus.emit("sale_closed", session_id=123)
                              |
                         [EventBus]
                              |
                   [Redis Stream: events:sale_closed]
                              |
                [Consumer group: paheko_sync]
                              |
                    [Module Paheko]  <--  async handler
```

### EventBus wrapper (~60 lignes, fichier core/events.py)

```python
class EventBus:
    def __init__(self, redis: Redis):
        self._redis = redis
        self._handlers: dict[str, list[Callable]] = {}

    def on(self, event: str, handler: Callable):
        """Appelé par chaque module dans register_signals(bus)."""
        self._handlers.setdefault(event, []).append(handler)

    async def emit(self, event: str, **data):
        """Produit un message dans le stream Redis."""
        await self._redis.xadd(f"events:{event}", data, maxlen=10000)

    async def consume(self):
        """Background task lancé dans lifespan FastAPI.
        xreadgroup + ack par message ; erreur d'un handler isolée (les autres continuent)."""
```

### Pattern module (contrat inchangé pour les modules)

```python
class PahekoModule(ModuleBase):
    def register_signals(self, bus: EventBus):
        bus.on("sale_closed", self.sync_session)
        bus.on("member_created", self.sync_member)

    async def sync_session(self, session_id: str, **data):
        # logique sync Paheko ; ack auto après retour sans exception
```

### Ce qu'on obtient

- **Durabilité** : clôture caisse → écriture Paheko garantie même si module Paheko redémarre
- **Multi-worker natif** : tous les Gunicorn workers partagent le même stream
- **Replay** : historique des événements rejoouable (audit comptable)
- **Isolation des erreurs** : un handler qui échoue n'empêche pas les autres
- **Évolutivité** : si on ajoute un worker dédié events plus tard, même API, même streams

### Ce qu'on n'utilise pas

- Redis Pub/Sub : pas de persistance, message perdu si subscriber absent
- async-signals : in-process uniquement, incompatible multi-workers
- Pluggy : synchrone, inadapté FastAPI async

Réfs recherche : `references/recherche/2026-02-24_pluggy-vs-alternatives-hooks_perplexity_reponse-1.md` et `reponse-2-redis.md`.

---

## Zones d'ombre résiduelles

- **Tests interactions modules** : testabilité unitaire de ModuleBase OK ; interactions via slots/signals = non documenté. À adresser quand modules réels.
- **Hot reload en dev** : redémarrage FastAPI nécessaire si module modifié. Acceptable (Docker compose).

---

## Risque principal

Frontend : si la frontière monorepo/builds séparés n'est pas tenue, le premier module UI (Paheko) posera la mauvaise fondation. **À documenter comme contrainte d'architecture dès le Brief.**
