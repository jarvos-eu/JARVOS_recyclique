# Session de confrontation RecyClique vs Paheko

**Date :** 2026-02-25  
**Contexte :** Exécution de la session de confrontation (analyste) : remplir les cases « - » de la grille, trancher ou documenter les questions ouvertes de l'artefact 07, produire un artefact réutilisable pour le PRD.  
**Références :** [grille 05](2026-02-25_05_grille-confrontation-recyclic-paheko.md), [décisions 07](2026-02-25_07_decisions-push-redis-source-eee.md), [point global 06](2026-02-25_06_point-global-avant-prd.md), [versioning](../versioning.md), [analyse plugins 04](2026-02-25_04_analyse-plugins-caisse-decisions-push.md).

---

## 1. Résumé des décisions prises pendant la session

| Sujet | Décision | Justification courte |
|-------|----------|----------------------|
| **Montants / devises** | Alignement **centimes** RecyClique ↔ Paheko, pas de conversion. | Plugin Caisse Paheko en centimes ; 1.4.4 documenté en centimes. À valider en BDD Recyclic (schéma dev en `double precision`) : si stockage en unités, conversion à l'écriture plugin. |
| **Catégories caisse Paheko** | **Plugin recyclique crée ou matche les catégories à la volée** (libellé/code) au push. | Évite dépendance à une config admin manuelle ; fallback config admin si référentiel préalable souhaité. À préciser avec dumps BDD. |
| **Source de vérité poids** | **RecyClique = source de vérité** pour les poids déclaratifs. | Compta matière/poids dans RecyClique ; Paheko Saisie au poids optionnel (stats, export manuel) ou alimenté en lecture seule par le plugin ; pas de sync bidirectionnelle. |
| **Module Saisie au poids Paheko** | **Garder le module Brindille activé** ; plugin recyclique peut écrire dans `module_data_saisie_poids` après push caisse (logique type sync.html automatisée). | Pas de fusion en v0.1 ; réévaluer en v0.5 (éco-organismes). Donnée matière dans Paheko = copie optionnelle pour traçabilité. |
| **Données déclaratives** | **RecyClique produit et conserve** les données (poids, flux, catégories, périodes). | Paheko peut garder une copie minimale pour traçabilité compta ; pas d'obligation. Détail dans PRD module décla. |
| **Auth v0.1 / SSO v0.2** | **v0.1** : auth séparée (compte Paheko pour admin/API, JWT FastAPI pour app terrain). **v0.2** : SSO à documenter. | Figer dans le PRD ; recherche existante dans references/recherche/. |
| **Sécurité endpoint plugin** | **Secret partagé** (header ou paramètre) + HTTPS ; optionnel : whitelist IP ou credentials API Paheko. | À figer dans le PRD (v0.2). Pas de secret en clair dans les requêtes. |
| **Données sensibles** | Alignement **bonnes pratiques** : pas de secrets en dur ; env / secrets manager ; config Paheko et credentials gérés de même façon. | Cohérence checklist import 1.4.4 et déploiement. |

---

## 2. Points laissés ouverts (avec raison)

| Point | Statut | Raison / recommandation |
|-------|--------|--------------------------|
| **Périmètre module correspondance** | **À trancher lors de la confrontation BDD + analyste** | Champs et règles de mapping exacts dépendent des dumps BDD Recyclic + Paheko et de l'instance dev. Prérequis : BDD montées, correspondances cartographiées. |
| **Fichiers / politique documentaire** | **À trancher dans le chantier fichiers** (artefact 02) | Frontière RecyClique ↔ Paheko pour documents, scan factures, upload ; scope versions futures (post-v0.1). |
| **Stratégie LLM/IA** | **Reportée après brief** | v0.1 = placeholder ; déjà décidé (point global 06). |

---

## 3. Mises à jour effectuées sur la grille (artefact 05)

- **Axe 1 (Caisse)** : Montants/devises - colonne « À creuser / décision » remplie ; statut → **décidé**.
- **Axe 2 (Catégories)** : Catégories boutique - décision « plugin à la volée » ; statut → **décidé**.
- **Axe 3 (Poids)** : Stockage - RecyClique source de vérité, rôle Paheko optionnel ; statut → **décidé**.
- **Axe 4 (Décla)** : Données déclaratives - RecyClique produit et conserve ; statut → **décidé**.
- **Axe 6 (Rôles)** : Utilisateurs/auth - v0.1 et v0.2 documentés ; statut → **décidé**. Module correspondance - périmètre documenté, dépendance dumps BDD + analyste ; statut → **en cours**.
- **Axe 7 (Sécurité)** : Canal push - secret partagé + HTTPS ; Données sensibles - bonnes pratiques ; statuts → **décidé**.
- **Axe 8 (Calendrier/fichiers)** : Fichiers/politique documentaire - renvoi chantier 02 ; statut → **en cours**.

---

## 4. Synthèse pour le PRD

- **À figer dans le PRD** : push par ticket, Redis Streams, centimes, catégories à la volée, source de vérité poids RecyClique, données déclaratives RecyClique, auth v0.1 (et SSO v0.2), sécurisation endpoint plugin (secret partagé), bonnes pratiques secrets.
- **À trancher avant ou pendant le PRD (prérequis instance + BDD)** : périmètre exact du module correspondance (champs, règles de mapping).
- **Hors périmètre session** : politique fichiers (chantier 02), stratégie LLM/IA (après brief).

---

*Artefact produit lors de la session de confrontation RecyClique vs Paheko (mission analyste).*
