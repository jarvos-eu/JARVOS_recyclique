# Ou on en est — JARVOS Recyclique

Mis a jour : 2026-02-25

## Etat actuel

Projet JARVOS Recyclique v0.1.0 initialise. **Analyse brownfield 1.4.4 disponible** dans `references/ancien-repo/`. **Analyse brownfield Paheko faite** : extensions (plugins/modules), API HTTP, gestion des fichiers et upload, WebDAV — voir [references/paheko/analyse-brownfield-paheko.md](paheko/analyse-brownfield-paheko.md) (index : [references/paheko/index.md](paheko/index.md)). Workflow Git en place. Aucun code source encore.

**Framework de modules : design complet et arbitré.** Artefact : `references/artefacts/2026-02-24_07_design-systeme-modules.md`. Décisions finales posées : TOML, ModuleBase, EventBus Redis Streams (multi-workers), slots React, monorepo. Prêt pour le Brief ; détails PRD à venir.

**Strategie de recherche : spirale.** 1re passe = decouverte / cartographie sur tous les sujets (Kanban + todo) ; 2e passe = recherches detaillees (API Paheko caisse, extension saisie au poids, analyse dumps, etc.). **1re passe spirale clôturée** (2026-02-25) : tous les sujets Kanban et todo ont eu au moins une passe decouverte ; URL repo 1.4.4 renseignee.

**Donnees production :** dumps BDD dans `references/dumps/` (gitignore) — Paheko deja present ; Recyclic a deposer si besoin. Objectif 2e passe = monter Paheko + Recyclic en local et deduire les correspondances.

BMAD 6.0.3 installe. Cursor rules actives. Dossier `references/` operationnel.

## Derniere session

2026-02-25 — Cloture 1re passe spirale.

Realise :
- **URL repo** : https://github.com/La-Clique-qui-Recycle/RecyClique renseignee dans [references/ancien-repo/README.md](ancien-repo/README.md). Todo coché.
- **Notes 1re passe** sur 5 idees Kanban : README international, README contexte projet, module store, Le Fil placeholder, JARVOS Ports. Index idees-kanban mis a jour.
- **Artefact** [references/artefacts/2026-02-25_03_closure-1re-passe-spirale.md](artefacts/2026-02-25_03_closure-1re-passe-spirale.md) : synthese cloture 1re passe, suite 2e passe et Brief.

---

2026-02-25 — Decisions 1re passe spirale (integration Paheko core, catalogue, IA/LLM).

Realise :
- **Integration Paheko core** : decisions actees — version 1.3.19.x, un seul Compose monorepo ; artefact 09 mis a jour (section « Decisions 1re passe », « Catalogue 1re passe »). Reponses Perplexity version + catalogue enregistrees et indexees.
- **Catalogue modules Paheko** : fait (reponse Perplexity + croisement artefact 09).
- **IA/LLM** : inventaire 1.4.4 = import Excel / categories LLM ; decision = placeholder + report apres brief ; idee ia-llm-modules-intelligents mise a jour.
- **Dumps BDD** : nouveau dossier `references/dumps/` (gitignore) pour sauvegardes Paheko / Recyclic prod. Depot direct dans `references/dumps/` ou depot dans _depot puis ventilation (skill traiter-depot). Objectif 2e passe = monter les bases et cartographier correspondances.
- Mises a jour : todo (catalogue, version, inventaire LLM, strategie LLM reportee), index recherche, idees integration-paheko-core et ia-llm.

---

2026-02-25 — Decisions calendrier, fichiers, RAG (tour de discussion).

Realise :
- **Decision agenda** : Recyclic + services externes ; utilisateur = ref Paheko ; multi-agendas ; v0.1.0 = placeholders. Artefact [references/artefacts/2026-02-25_01_decision-agenda-recyclic-externe.md](artefacts/2026-02-25_01_decision-agenda-recyclic-externe.md). Idee calendar-espace-fichiers-paheko mise a jour.
- **Chantier fichiers** : ouverture chantier (versions futures). Idee Kanban [references/idees-kanban/a-creuser/2026-02-25_chantier-fichiers-politique-documentaire.md](idees-kanban/a-creuser/2026-02-25_chantier-fichiers-politique-documentaire.md) + artefact [references/artefacts/2026-02-25_02_chantier-fichiers-politique-documentaire.md](artefacts/2026-02-25_02_chantier-fichiers-politique-documentaire.md). Todo ajoute.
- **RAG** : Recyclic donne acces a la base documentaire (Paheko + services tiers) a JARVOS Nano/Mini pour indexation.
- Mises a jour : index artefacts, index idees-kanban, todo, vision-projet (note RAG).

---

2026-02-25 — Analyse brownfield Paheko (document-project deep-dive).

Realise :
- **Document** `references/paheko/analyse-brownfield-paheko.md` : analyse complete du repo Paheko (extensions plugins/modules, API REST, gestion fichiers, WebDAV, routes upload/reference) ; synthese pour integration RecyClique.
- Mise a jour `references/paheko/index.md` avec lien vers l'analyse.
- Mise a jour du present fichier (ou-on-en-est.md).

---

2026-02-24 — Analyst : doc officielle Paheko + prompts recherche.

Realise :
- **Artefact** `references/artefacts/2026-02-24_10_doc-officielle-paheko-integration-core.md` : synthese doc officielle Paheko (Extensions + API 1.3.17.1), inconnues et renvoi vers les 5 prompts Perplexity.
- **Cinq prompts Perplexity** crees (a executer) : API caisse, Saisie au poids, version Paheko stable, auth/SSO app externe, catalogue plugins/modules. Fichiers dans `references/recherche/` (suffixe `_perplexity_prompt.md`) ; reponses a enregistrer apres execution.
- Mises a jour : index artefacts, index recherche, idee integration-paheko-core.
- **Conversation** : Analyst - Integration Paheko core doc et recherches.

---

## Ordre de priorite 1re passe (spirale) — historique

Ordre qui a ete suivi ; 1re passe cloturee (2026-02-25).

1. **Integration Paheko core** — perimetre, Docker, modules optionnels, ce qu'on branche.
2. **Calendrier / espace fichiers Paheko** — verifier capacites natives (eviter double conception).
3. **Catalogue modules Paheko** — croiser avec integration core, ce qui est installable.
4. **IA/LLM** — inventaire usages 1.4.4 + strategie (placeholder vs Nano/Mini).
5. **Restant Kanban** — nouvelles UI, module store, Le Fil, module correspondance, README, etc.

## Prochaine etape

1. **2e passe** : recherches detaillees — API Paheko caisse, extension saisie au poids, auth/SSO ; decision source de verite caisse ; deposer dumps dans `references/dumps/` (Paheko deja present), monter BDD Recyclic + Paheko en local et analyser correspondances.
2. **Renseigner URL** : fait (2026-02-25).
3. **Quand assez de matiere** : Create Brief JARVOS Recyclique v0.1.0 (`/bmad-bmm-create-product-brief`), puis PRD.
