# Prompt recherche — Catalogue plugins et modules Paheko officiels

**Date :** 2026-02-24  
**Cible :** Perplexity Pro  
**Usage :** Obtenir la liste officielle des plugins et modules fournis avec Paheko (Caisse, Stock, Saisie au poids, Agenda, etc.), leurs versions et où les trouver.

---

## Contexte projet

Voir `contexte-pour-recherche-externe.md` pour le contexte complet.

Nous déployons Paheko avec les extensions nécessaires à une ressourcerie : Caisse informatisée, Gestion de stock, Saisie au poids, éventuellement Agenda et contacts, etc. Nous voulons un catalogue fiable : quels plugins/modules sont officiels, fournis à l'installation ou activables, et où les trouver (fossil.kd2.org, paheko.cloud, doc).

---

## Questions pour la recherche

1. **Liste officielle** : quels sont les plugins et modules officiels fournis avec Paheko (inclus à l'install ou disponibles via le dépôt officiel) ? Pour chaque : nom, type (plugin PHP ou module Brindille), fonction principale. Ex. : Caisse, Stock, Saisie au poids, Agenda/Contacts, Reçus fiscaux, etc.

2. **Où les trouver** : URLs des dépôts (fossil.kd2.org/paheko-plugins, paheko-modules), page de doc listant les extensions (wiki Paheko), et pour Paheko.cloud quelles extensions sont installables (liste ou interface).

3. **Versions et compatibilité** : les extensions sont-elles versionnées avec Paheko (même numéro) ou indépendamment ? Comment vérifier la compatibilité extension X / version Paheko Y ?

4. **Installation** : rappel du mode d'installation (plugins : .tar.gz dans data/plugins ; modules : fournis avec le core ?). Pour un déploiement Docker, quelles extensions pré-activer (noms exacts, ordre si dépendances).

Répondre en français. Citer sources et URLs.
