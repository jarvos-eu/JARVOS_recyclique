# Ou on en est — JARVOS Recyclique

Mis a jour : 2026-02-24

## Etat actuel

Projet JARVOS Recyclique v0.1.0 initialise. **Analyse brownfield 1.4.4 disponible** dans `references/ancien-repo/`. Workflow Git en place. Aucun code source encore.

**Framework de modules : design complet et arbitré.** Artefact : `references/artefacts/2026-02-24_07_design-systeme-modules.md`. Décisions finales posées : TOML, ModuleBase, EventBus Redis Streams (multi-workers), slots React, monorepo. Prêt pour le Brief ; détails PRD à venir.

**Strategie de recherche : spirale.** 1re passe = decouverte / cartographie sur tous les sujets (Kanban + todo) ; 2e passe = recherches detaillees (API Paheko caisse, extension saisie au poids, analyse dumps, etc.). On reste sur la 1re passe jusqu'a avoir fait le tour.

**Donnees production :** acces aux dumps BDD Recyclic + Paheko (prod) prevu ; objectif = monter les deux bases en local pour analyser et deduire les correspondances.

BMAD 6.0.3 installe. Cursor rules actives. Dossier `references/` operationnel.

## Derniere session

2026-02-24 — Analyst : doc officielle Paheko + prompts recherche.

Realise :
- **Artefact** `references/artefacts/2026-02-24_10_doc-officielle-paheko-integration-core.md` : synthese doc officielle Paheko (Extensions + API 1.3.17.1), inconnues et renvoi vers les 5 prompts Perplexity.
- **Cinq prompts Perplexity** crees (a executer) : API caisse, Saisie au poids, version Paheko stable, auth/SSO app externe, catalogue plugins/modules. Fichiers dans `references/recherche/` (suffixe `_perplexity_prompt.md`) ; reponses a enregistrer apres execution.
- Mises a jour : index artefacts, index recherche, idee integration-paheko-core.
- **Conversation** : Analyst - Integration Paheko core doc et recherches.

---

## Ordre de priorite 1re passe (spirale)

1. **Integration Paheko core** — perimetre, Docker, modules optionnels, ce qu'on branche.
2. **Calendrier / espace fichiers Paheko** — verifier capacites natives (eviter double conception).
3. **Catalogue modules Paheko** — croiser avec integration core, ce qui est installable.
4. **IA/LLM** — inventaire usages 1.4.4 + strategie (placeholder vs Nano/Mini).
5. **Restant Kanban** — nouvelles UI, module store, Le Fil, module correspondance, README, etc.

## Prochaine etape

1. **Poursuivre 1re passe spirale** : traiter les sujets dans l'ordre ci-dessus (sync financiere = fait). Objectif = vision globale avant 2e passe.
2. **2e passe** (apres 1re passe complete) : recherches detaillees — API Paheko caisse, extension saisie au poids, decision source de verite caisse ; monter dumps BDD Recyclic + Paheko en local et analyser correspondances.
3. **Renseigner URL** du repo GitHub public Recyclique 1.4.4 dans `references/ancien-repo/README.md`.
4. **Quand assez de matiere** : Create Brief JARVOS Recyclique v0.1.0 (`/bmad-bmm-create-product-brief`), puis PRD.
