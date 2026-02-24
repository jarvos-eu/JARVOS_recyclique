# Prompt recherche — Version Paheko recommandée pour intégration

**Date :** 2026-02-24  
**Cible :** Perplexity Pro  
**Usage :** Choisir la version Paheko cible pour un projet d'intégration (middleware FastAPI appelant l'API Paheko). Dernière stable, politique de versions, compatibilité 1.3.x.

---

## Contexte projet

Voir `contexte-pour-recherche-externe.md` pour le contexte complet.

Nous intégrons Paheko (PHP) comme backend ; notre API FastAPI appelle l'API REST Paheko. Les guides internes mentionnent la version 1.3.17. Nous voulons valider : quelle version recommander pour la v0.1.0 (dernière stable, LTS si applicable), et quelle politique de versions Paheko suit (semver, support, compatibilité 1.3.x).

---

## Questions pour la recherche

1. **Dernière version stable** : quelle est la version stable actuelle de Paheko (au 2025-2026) ? Où est-elle annoncée (site, fossil, paheko.cloud) ?

2. **Politique de versions** : Paheko suit-il un schéma de versionnement (semver, autre) ? Existe-t-il des versions LTS ou une recommandation pour les intégrations (ex. rester sur 1.3.x) ?

3. **Compatibilité API** : l'API REST (documentée pour 1.3.17.1) est-elle stable entre versions 1.3.x ? Y a-t-il des breaking changes connus ou des précautions pour une app qui appelle l'API ?

4. **Recommandation** : pour un nouveau projet d'intégration (API consommée par un middleware Python), quelle version Paheko installer : dernière 1.3.x, dernière stable toutes branches, ou autre ?

Répondre en français. Citer sources et URLs.
