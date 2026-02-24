# Prompt recherche — Auth / SSO Paheko avec application externe

**Date :** 2026-02-24  
**Cible :** Perplexity Pro  
**Usage :** Savoir comment authentifier une application externe (Python/FastAPI) auprès de Paheko : API tokens, SSO (OpenID Connect, LDAP), ou auth HTTP pour les appels API.

---

## Contexte projet

Voir `contexte-pour-recherche-externe.md` pour le contexte complet.

Notre backend FastAPI (Recyclic) appelle l'API REST Paheko. Les utilisateurs sont gérés côté Paheko (décision projet). Nous devons : (1) authentifier les appels API FastAPI → Paheko (identifiants API déjà documentés : Configuration → API) ; (2) si possible, permettre un login unique (SSO) entre l'interface Recyclic et Paheko (optionnel mais souhaitable). Documenter les options (tokens API, OpenID Connect, LDAP, autre).

---

## Questions pour la recherche

1. **Auth pour appels API** : la doc Paheko indique identifiant + mot de passe en HTTP Basic pour l'API. Existe-t-il un mécanisme par token (API key, JWT, OAuth2) pour éviter de passer un mot de passe ? Durée de vie, renouvellement ?

2. **SSO Paheko** : la doc mentionne « Utiliser Paheko avec un système SSO (LDAP, OpenID Connect, etc.) ». Où est documenté ceci (page wiki, configuration) ? En mode « Paheko comme fournisseur d'identité » ou « Paheko consomme un IdP externe » ?

3. **Application externe comme client** : pour une app Python/FastAPI qui veut que l'utilisateur se connecte « une fois » et accède à la fois à l'UI Recyclic et aux données Paheko (sans ressaisir le mot de passe Paheko), quelles options existent ? Ex. : Paheko expose-t-il OpenID Connect pour que notre front puisse faire un login SSO vers Paheko ; ou faut-il garder auth HTTP Basic pour les appels API backend uniquement ?

4. **Recommandation** : pour un scénario « utilisateurs dans Paheko, appels API depuis FastAPI avec un compte de service », quelle approche recommander (compte API dédié, permissions, bonnes pratiques) ?

Répondre en français. Citer sources et URLs.
