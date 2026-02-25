# Point global — Avant PRD (état des lieux)

**Date :** 2026-02-25  
**Objectif :** Où on en est, ce qu'on sait de l'architecture, ce qui manque, et proposition de suite (dont ménage artefacts).

---

## 1. Où on en est (résumé)

- **1re passe spirale** : **clôturée**. Tous les sujets du Kanban et du todo ont eu au moins une passe de découverte ; URL repo 1.4.4 renseignée.
- **2e passe** : **en cours**. Réalisé : checklist import 1.4.4, procédure Paheko dev (dev-tampon), grille confrontation RecyClique vs Paheko (8 axes), vision module décla éco-organismes, ancrage périmètre dans versioning. **Pas encore fait** : instance Paheko dev (Docker local), montage BDD Recyclic + Paheko en local, confrontation détaillée avec l'analyste.
- **Brief / PRD** : pas encore lancés. Prochaine étape logique : « quand assez de matière » → Create Brief puis PRD.

Tu as raison : il reste des **zones d'ombre** volontairement laissées pour une **confrontation avancée** (instance + BDD + analyste) après Brief. Le présent document les liste clairement.

---

## 2. Ce qu'on sait de l'architecture (à développer)

### 2.1 Décisions stables (à mettre dans le PRD)

| Domaine | Décision |
|--------|----------|
| **Backend** | Dual : RecyClique (FastAPI) + Paheko (PHP). Un seul Compose monorepo. Paheko 1.3.19.x. |
| **Système de modules** | TOML (`module.toml`), `ModuleBase`, activation par `config.toml` (`[modules] enabled`), EventBus **Redis Streams** (multi-workers), slots React, monorepo. Design complet : `references/artefacts/2026-02-24_07_design-systeme-modules.md`. |
| **Caisse** | RecyClique pilote la saisie (UI terrain, éventuellement offline). **Paheko = source de vérité** compta. Push **par ticket** au fil de l'eau ; clôture = syncAccounting + contrôle. File d'attente push = **Redis Streams** (résilience). Plugin PHP custom (`public/api.php`) écrit dans `plugin_caisse_*` et appelle `syncAccounting`. |
| **Source officielle EEE** | RecyClique (liste open data, mapping, module décla éco-organismes ; interrogable par JARVOS Nano / tiers). |
| **Réception matière / poids** | RecyClique (réception, tickets réception ; pas de sync manuelle ; compta matière/poids peut rester uniquement RecyClique ; rôle Paheko Saisie au poids à trancher). |
| **Interfaces compta** | Objectif = vues et workflows compta dans RecyClique (bilan, factures, rapprochement bancaire) ; pas d'accès admin Paheko en idéal ; plus tard JARVOS Nano/Mini. |
| **Utilisateurs** | Gestion users = Paheko natif. v0.1 : auth séparée (compte Paheko + JWT FastAPI) ; SSO reporté v0.2. |
| **Calendrier / fichiers** | v0.1.0 = placeholders ; chantier fichiers ouvert pour versions futures. |
| **IA/LLM** | v0.1 = placeholder ; stratégie (hardcodé + Ganglion vs Nano/Mini) après brief. |
| **Import 1.4.4** | Copy + consolidate + security à chaque pioche ; checklist formalisée : `references/ancien-repo/checklist-import-1.4.4.md`. |

### 2.2 Périmètre par version (source de vérité)

`references/versioning.md` :

- **v0.1.0** : Socle Docker Paheko + API stub FastAPI  
- **v0.2.0** : Vertical slice caisse/ventes fonctionnel  
- **v0.3.0** : Réception fonctionnelle  
- **v0.4.0** : Auth + users + admin  
- **v0.5.0** : Éco-organismes  
- **v1.0.0** : Déployé en prod, stable  

---

## 3. Ce qui nous manque (zones d'ombre avant PRD)

Ces points sont soit **ouverts** dans la grille de confrontation, soit **todos non faits**, soit **décisions reportées**. Ils ne bloquent pas le Brief, mais certains devront être tranchés avant ou pendant le PRD.

### 3.1 Confrontation RecyClique vs Paheko (grille 8 axes)

La grille a été mise à jour (2026-02-25). Les questions encore à trancher sont listées dans [artefact 07](2026-02-25_07_decisions-push-redis-source-eee.md) (section « Questions encore à trancher »). À creuser notamment : qui crée les catégories caisse Paheko ; rôle module Saisie au poids Paheko ; périmètre module correspondance ; sécurité endpoint plugin.

**Prérequis pour avancer** : instance Paheko dev (Docker) + BDD Recyclic et Paheko montées en local + session de confrontation avec l'analyste.

### 3.2 Todos encore ouverts (todo.md)

- Monter en local BDD Recyclic + Paheko (dumps dans `references/dumps/`), analyser et cartographier correspondances.
- Instance Paheko dev : installer Paheko, activer plugins caisse + saisie au poids, tester API / schéma.
- Confronter RecyClique vs Paheko pour décision périmètre et mapping (avec l'analyste, après Brief).
- Définir stratégie LLM/IA (reportée après brief).
- Explorer et formaliser politique fichiers (chantier versions futures).
- Décider de l'architecture technique du nouveau backend (recherche) — en pratique largement couvert par le design modules + versioning ; à interpréter comme « figer et documenter dans le PRD ».

### 3.3 Idées Kanban non stabilisées

Plusieurs idées sont en **a-rechercher** ou **a-creuser** (sync financière, plugin framework, calendrier/fichiers, etc.). Les décisions déjà prises sont reflétées dans les artefacts et le todo ; le Kanban reste utile pour les sujets non encore tranchés (module store, Le Fil, UI modulaire, etc.) et pour la priorisation post-Brief.

---

## 4. Artefacts : état et proposition de ménage

### 4.1 Inventaire (17 fichiers)

- **2026-02-24_01 à 05** : Plan Git (mission test, rapport, procedure, subagent, règle). **Exécuté** ; procédure et règle en place. Désormais dans **`artefacts/archive/`** (référence historique).
- **2026-02-24_06** : Brainstorm migration Paheko. **Point d'entrée** pour les sessions ; à garder.
- **2026-02-24_07** : Design système de modules. **Référence d'architecture** ; à garder.
- **2026-02-24_08** : Décision architecture « max Paheko ». Partiellement **supersédé** par 09 (cartographie), 04 (plugins/décisions push), 05 (grille). Peut être marqué « supersédé par 04, 09, 05 » ou fusionné en note dans 09.
- **2026-02-24_09** : Cartographie intégration Paheko core. **Référence** ; à garder.
- **2026-02-24_10** : Doc officielle Paheko + inconnues + renvoi vers prompts. **Référence** ; à garder.
- **2026-02-24_11** : Capacités Paheko (calendrier, fichiers, communication). **Référence** ; à garder.
- **2026-02-25_01 à 05** : Décision agenda, chantier fichiers, closure 1re passe, analyse plugins caisse, grille confrontation. **Tous utiles** ; à garder.

### 4.2 Proposition de ménage (léger)

1. **Ne pas supprimer** les artefacts 01–05 (Git) : ils documentent le processus ; les laisser dans l'index avec une mention « Plan Git exécuté — référence ».
2. **Dans l'index `references/artefacts/index.md`** : ajouter une courte section « Statut » ou une note sur 08 : « 08 partiellement supersédé par 04, 09, 05 — voir grille et analyse plugins pour décisions actuelles. »
3. **Fait** : sous-dossier `artefacts/archive/` créé ; 01–05 déplacés. Index artefacts et index principal mis à jour.

Aucun fichier à jeter : tout peut servir en référence. Le « ménage » consiste à **clarifier** ce qui est encore actif vs historique.

---

## 5. Synthèse : avant le PRD

- **On a** : vision dual-backend, design modules arbitré, décisions caisse (push par ticket, Redis Streams), source EEE RecyClique, réception/poids RecyClique sans sync manuelle, objectif interfaces compta dans RecyClique, versioning, checklist import, grille confrontation à jour, vision module décla éco-organismes, et une bonne base de doc (artefacts, recherche, paheko, ancien-repo).
- **Il manque** : instance Paheko dev opérationnelle, BDD montées et correspondances cartographiées, et une **session de confrontation** (grille + analyste) pour remplir les « — » et figer les choix (catégories, poids, offline, sécurité, module correspondance).
- **Tu peux** : lancer le **Create Brief** dès que tu te sens prêt (la matière actuelle suffit pour un brief exécutif). Les zones d'ombre peuvent rester listées dans le Brief comme « à trancher en 2e passe / pendant le PRD ». Ensuite, soit tu enchaînes par l'instance Paheko + BDD + confrontation pour un PRD plus précis, soit tu rédiges le PRD en marquant explicitement les décisions reportées et les prérequis (instance + BDD).

Si tu veux, on peut soit (1) mettre à jour l'index des artefacts avec la note sur 08 et le statut du plan Git, soit (2) détailler la prochaine session (instance Paheko + BDD + grille), soit (3) préparer une checklist « Brief → PRD » à cocher au fur et à mesure.
