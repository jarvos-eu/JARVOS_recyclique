# Prompt recherche — API Paheko caisse

**Date :** 2026-02-24  
**Cible :** Perplexity Pro  
**Usage :** Trouver la documentation ou les sources de l'API caisse Paheko (sessions, ventes, paiements). Prérequis pour décision source de vérité caisse (architecture JARVOS Recyclique).

---

## Contexte projet

Voir `contexte-pour-recherche-externe.md` pour le contexte complet.

Nous intégrons Paheko comme backend financier ; la caisse native Paheko (plugin) est utilisée. La doc API générale Paheko (fossil.kd2.org, version 1.3.17) ne liste pas d'endpoints dédiés à la caisse / point de vente / sessions de vente. Nous devons savoir comment accéder par API aux sessions de caisse, ventes, paiements (pour le module de correspondance Recyclic → Paheko).

---

## Questions pour la recherche

1. **API caisse Paheko** : existe-t-il une documentation (wiki, manuel, dépôt) des endpoints API liés au plugin Caisse ? Chemins, méthodes HTTP, paramètres pour : sessions de caisse, ventes, lignes de ticket, moyens de paiement.

2. **Modèles / tables** : quelles tables ou entités métier (noms, structure sommaire) sont utilisées par le plugin Caisse (ex. registre, session, vente, paiement) ? Source : code source du plugin (fossil.kd2.org/paheko-plugins), doc, ou communauté.

3. **Où est documentée l'API caisse** : page wiki précise, fichier dans le repo du plugin, ou uniquement dans le code source ? Si uniquement code, indiquer le dépôt et les fichiers clés à lire.

Répondre en français. Citer sources et URLs.
