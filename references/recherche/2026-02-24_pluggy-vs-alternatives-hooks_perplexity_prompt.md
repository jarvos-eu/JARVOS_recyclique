# Prompt recherche — Pluggy vs. alternatives légères pour hooks inter-modules


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