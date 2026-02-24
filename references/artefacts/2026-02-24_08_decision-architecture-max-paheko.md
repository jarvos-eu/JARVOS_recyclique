# Decision architecture — Max Paheko

**Date :** 2026-02-24  
**Session :** Brainstorm suite (sync financiere, module correspondance)  
**Point d'entree suite :** `references/ou-on-en-est.md` + `references/idees-kanban/index.md`

---

## Decisions posees

- **Paheko = backend financier et matiere complet.** Recyclic = surcouche UX + workflow terrain. On utilise toute l'API Paheko, y compris la caisse native et l'extension Saisie au poids.
- **Caisse Paheko native** utilisee (Option B confirmee et etendue). Pas d'ecritures comptables directes injectees par Recyclic ; on se cale sur le workflow Paheko.
- **Module de correspondance** : middleware dans le back-end Recyclic qui traduit les objets metier Recyclic (sessions, ventes, depots) vers les appels API Paheko. Traducteur, pas synchroniseur BDD.
- **Extension Saisie au poids Paheko** utilisee pour la comptabilite matiere. A creuser : ce qu'elle fait, ou elle ecrit, comment recuperer via API pour affichage/stats Recyclic.
- **Source de verite caisse** (Paheko seul vs miroir Recyclic) : **a decider apres recherche API Paheko** — prerequis pour le design du schema BDD v0.1.0.
- **Correspondances Recyclic <-> Paheko** : pas de document fourni par Germaine/Corinne. En revanche : acces aux dumps BDD production Recyclic + Paheko prevu ; objectif = monter les deux bases en local pour analyser et deduire les correspondances (matiere concrete).

---

## Tensions residuelles (non bloquantes)

- **Source de verite caisse** non tranchee → decision bloquante pour architecture BDD.
- **Reception / depots matiere** Recyclic : probablement hors scope strict de l'extension Saisie au poids Paheko (entrees vs sorties caisse). A verifier dans la recherche.
- **Resilience** : si Paheko est down, la caisse Recyclic terrain est en panne. Question ouverte (mode offline souhaite ou non).

---

## Agenda de recherche

1. **API Paheko caisse** : endpoints, modeles (sessions, ventes, paiements), mapping Recyclic -> Paheko. Prerequis pour decider source de verite.
2. **Extension Saisie au poids** : fonctionnement, tables, import depuis caisse, API lecture/ecriture. Prerequis architecture flux matiere.
3. **Catalogue modules Paheko** : deja dans le todo ; a croiser avec integration core.
4. **Analyse dumps BDD** : une fois dumps fournis, monter BDD Recyclic + Paheko en local, puis cartographier les correspondances reelles (2e passe recherche).

---

## Liens

- Design modules : `references/artefacts/2026-02-24_07_design-systeme-modules.md` (EventBus, ModuleBase, module Paheko Sync).
- Idee sync financiere : `references/idees-kanban/a-rechercher/2026-02-24_sync-financiere-caisse-paheko.md`.
- Idee integration core : `references/idees-kanban/a-rechercher/2026-02-24_integration-paheko-core.md`.
- Nouvelle idee : module correspondance Paheko (`references/idees-kanban/a-conceptualiser/2026-02-24_module-correspondance-paheko.md`).
