# Prompt recherche — Extension Saisie au poids Paheko

**Date :** 2026-02-24  
**Cible :** Perplexity Pro  
**Usage :** Comprendre le fonctionnement de l'extension Saisie au poids (Paheko), ses tables, son API. Prérequis architecture flux matière (déclarations éco-organismes, traçabilité poids).

---

## Contexte projet

Voir `contexte-pour-recherche-externe.md` pour le contexte complet.

Nous utilisons Paheko (caisse native + extension Saisie au poids) comme backend matière. Il faut savoir : comment l'extension enregistre les données (poids, catégories), quelles tables elle utilise, si une API (lecture/écriture) existe pour notre middleware FastAPI, et comment elle s'articule avec la caisse (import depuis caisse, etc.).

---

## Questions pour la recherche

1. **Fonctionnement** : à quoi sert exactement l'extension Saisie au poids dans Paheko (cas d'usage, flux) ? Déclarations éco-organismes, traçabilité — quelles données sont saisies et où vont-elles ?

2. **Tables BDD** : quelles tables (noms, rôle) sont créées ou utilisées par l'extension ? Source : doc, code source (fossil paheko-plugins ou paheko-modules), ou communauté.

3. **API** : existe-t-il des endpoints API (REST ou internes) pour lire ou écrire les données « saisie au poids » depuis une application externe (Python/FastAPI) ? Si non, comment récupérer ces données (export, SQL en lecture seule, autre) ?

4. **Lien avec la caisse** : l'extension importe-t-elle des données depuis les ventes caisse (lignes, poids) ? Si oui, quel mécanisme (synchro, import manuel, déclencheur) ?

Répondre en français. Citer sources et URLs.
