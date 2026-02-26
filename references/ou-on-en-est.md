# Ou on en est — JARVOS Recyclique

Mis a jour : 2026-02-25

**Perimetre par version** : voir [references/versioning.md](versioning.md) (v0.1.0 → v1.0.0).

## Etat actuel

Projet JARVOS Recyclique v0.1.0 initialise. **Analyse brownfield 1.4.4 disponible** dans `references/ancien-repo/`. **Analyse brownfield Paheko faite** : extensions (plugins/modules), API HTTP, gestion des fichiers et upload, WebDAV — voir [references/paheko/analyse-brownfield-paheko.md](paheko/analyse-brownfield-paheko.md) (index : [references/paheko/index.md](paheko/index.md)). Workflow Git en place. Aucun code source encore.

**Framework de modules : design complet et arbitré.** Artefact : `references/artefacts/2026-02-24_07_design-systeme-modules.md`. Décisions finales posées : TOML, ModuleBase, EventBus Redis Streams (multi-workers), slots React, monorepo. **Product Brief v0.1.0 complété** (2026-02-25) : `_bmad-output/planning-artifacts/product-brief-JARVOS_recyclique-2026-02-25.md` ; détails PRD à venir. **UX v1.0** : mêmes écrans que 1.4.4, copie du code des mises en page (copy+consolidate+security), pas de refonte écrans pour la v1.0.

**Strategie de recherche : spirale.** 1re passe = decouverte / cartographie sur tous les sujets (Kanban + todo) ; 2e passe = recherches detaillees (API Paheko caisse, extension saisie au poids, analyse dumps, etc.). **1re passe spirale clôturée** (2026-02-25) : tous les sujets Kanban et todo ont eu au moins une passe decouverte ; URL repo 1.4.4 renseignee.

**Donnees production :** dumps BDD dans `references/dumps/` (gitignore) — Paheko deja present ; Recyclic a deposer si besoin. **Schéma BDD Recyclic dev documenté** : [references/dumps/schema-recyclic-dev.md](dumps/schema-recyclic-dev.md) (tables et colonnes, correspondances Paheko à préciser). **Schéma BDD Paheko dev documenté** : [references/dumps/schema-paheko-dev.md](dumps/schema-paheko-dev.md) — tables core + **tables réelles** du plugin Caisse (plugin_pos_*) et du module Saisie au poids (module_data_saisie_poids), extraites de l'instance avec plugins installés ; pour correspondances avec RecyClique. **2e passe réalisée** : instance Paheko + accès BDD Recyclic en local, schémas et confrontation (artefact 08).

**Decisions 2026-02-25** : push par ticket, Redis Streams pour file push Paheko, source officielle EEE dans RecyClique, reception/poids RecyClique sans sync manuelle, objectif interfaces compta dans RecyClique. Voir [artefact 2026-02-25_07](artefacts/2026-02-25_07_decisions-push-redis-source-eee.md).

BMAD 6.0.3 installe. Cursor rules actives. Dossier `references/` operationnel.

## Derniere session

2026-02-25 — Product Brief JARVOS Recyclique complété (workflow Create Product Brief).

Brief disponible : `_bmad-output/planning-artifacts/product-brief-JARVOS_recyclique-2026-02-25.md`. Sections : Executive Summary, Core Vision (problem, solution, differentiators), Target Users (terrain, compta/admin, bénévoles, journey), Success Metrics (v1.0 livrée en prod, adoption 2e ressourcerie), MVP Scope (v0.1→v1.0, hors scope, future vision). Prochaine étape logique : PRD.

---

2026-02-25 — Décisions matrice caisse/poids (session=session, manques v0.2+, compatibilité Paheko).

Matrice [references/migration-paeco/audits/matrice-correspondance-caisse-poids.md](migration-paeco/audits/matrice-correspondance-caisse-poids.md) mise à jour : 1 session RecyClique = 1 session Paheko (ouverture → clôture) ; clôture RecyClique déclenche clôture Paheko (contrôle totaux + syncAccounting) ; section 2.5 unité de poids (kg ↔ g, convention PRD) ; section 4 fonctionnalités Paheko absentes (v0.1 ignorer, v0.2+ à développer) ; section 5 principe de compatibilité Paheko (config Paheko = référence). Grille 05 axe 6 (module correspondance) → statut décidé.

---

2026-02-25 — Schéma Paheko dev : plugins Caisse et Saisie au poids (tables réelles).

Plugins Caisse (POS) et Saisie au poids installés sur l'instance dev. Ré-extraction du schéma : [references/dumps/schema-paheko-dev.md](dumps/schema-paheko-dev.md) mis à jour avec les tables réelles plugin_pos_* et module_data_saisie_poids.

---

2026-02-25 — Schéma BDD Paheko dev (exploration instance Docker, documentation correspondances).

Realise :
- **Exploration** de la BDD SQLite Paheko (instance dev-tampon/paheko/, fichier data/association.sqlite) : listage des tables, extraction des schémas (CREATE TABLE) pour les tables pertinentes.
- **Document** [references/dumps/schema-paheko-dev.md](dumps/schema-paheko-dev.md) : tables api_credentials, users, users_categories, acc_charts, acc_years, acc_accounts, acc_transactions, acc_transactions_lines, acc_transactions_files, files, config, plugins, modules, module_data_* (exemple expenses_claims) ; sections pour les tables attendues avec plugin Caisse (plugin_caisse_*) et module Saisie au poids (module_data_saisie_poids) ; tableau correspondances RecyClique ↔ Paheko.
- Mise a jour [references/paheko/index.md](paheko/index.md) et present fichier.

---

2026-02-25 — Connexion BDD Recyclic dev, extraction schéma, documentation.

Realise :
- Script `dev-tampon/scripts/schema_recyclic_to_md.py` : charge `dev-tampon/.env.recyclic-db` (python-dotenv), se connecte à PostgreSQL et génère le schéma.
- **Schéma BDD Recyclic dev** : [references/dumps/schema-recyclic-dev.md](dumps/schema-recyclic-dev.md) — toutes les tables (users, sites, cash_sessions, sales, sale_items, payment_transactions, poste_reception, ticket_depot, ligne_depot, categories, etc.) avec colonnes et clés primaires ; section correspondances Paheko (caisse, réception, utilisateurs).
- Mise a jour `references/dumps/README.md` et present fichier.

---

2026-02-25 — Decisions confrontation (push, Redis, source EEE, reception, interfaces compta).

Realise :
- Creation de `artefacts/archive/` et deplacement du plan Git (01–05) vers archive.
- Artefact [2026-02-25_07_decisions-push-redis-source-eee.md](artefacts/2026-02-25_07_decisions-push-redis-source-eee.md) : decisions + questions encore a trancher.
- Mise a jour grille [2026-02-25_05](artefacts/2026-02-25_05_grille-confrontation-recyclic-paheko.md) et point global [2026-02-25_06](artefacts/2026-02-25_06_point-global-avant-prd.md).
- Questions restantes listees dans artefact 07.

---

2026-02-25 — Execution plan 2e passe sans BDD (checklist, dev-tampon Paheko, grille confrontation, vision module decla, perimetre).

Realise :
- **Checklist** import 1.4.4 : [references/ancien-repo/checklist-import-1.4.4.md](ancien-repo/checklist-import-1.4.4.md) (copy, consolidate, security — a appliquer a chaque pioche dans le code 1.4.4).
- **Dossier tampon** `dev-tampon/` (gitignore) : procedure Paheko dev dans `dev-tampon/paheko/` (README, Dockerfile, docker-compose) ; Windows / Docker Desktop. Voir [references/paheko/index.md](paheko/index.md).
- **Grille confrontation** RecyClique vs Paheko : [references/artefacts/2026-02-25_05_grille-confrontation-recyclic-paheko.md](artefacts/2026-02-25_05_grille-confrontation-recyclic-paheko.md) (agent-usable, 8 axes).
- **Vision module decla eco-organismes** : [references/vision-projet/vision-module-decla-eco-organismes.md](vision-projet/vision-module-decla-eco-organismes.md) (agnostique, categories boutique libres → mapping par eco-organisme).
- **Perimetre** : ancrage dans [references/versioning.md](versioning.md) ; todo correspondants coches.

---

2026-02-25 — 2e passe spirale (recherches, analyse plugins, decisions push).

Realise :
- **Ventilation** des 3 reponses Perplexity (API caisse, extension saisie au poids, auth/SSO) dans references/recherche/ ; todo mis a jour.
- **Analyse code** plugin caisse (paheko-plugins) : schema tables plugin_caisse_*, syncAccounting (ecritures compta pas a la fermeture).
- **Decisions** : RecyClique pilote la caisse ; push a la fermeture vers Paheko via **plugin PHP custom** (public/api.php) ; Brindille inadapte ; Odoo vs Paheko = rester sur Paheko. Source de verite caisse = Paheko seul.
- **Saisie au poids** : module Brindille (repo/modules/saisie_poids/) ; sync manuelle depuis caisse possible ; repo Paheko remplace par archive officielle (plugins/modules inclus).
- **Artefact** [references/artefacts/2026-02-25_04_analyse-plugins-caisse-decisions-push.md](artefacts/2026-02-25_04_analyse-plugins-caisse-decisions-push.md) : vision RecyClique (offline, decla eco-organismes), doc plugins, confrontation a venir avec l'analyste.

---

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

1. **PRD** : rédiger le PRD en s'appuyant sur le Brief (`_bmad-output/planning-artifacts/product-brief-JARVOS_recyclique-2026-02-25.md`), les artefacts (grille 05, artefact 08, point global 06), les schémas (schema-recyclic-dev.md, schema-paheko-dev.md) et le versioning ; préciser les points encore ouverts (périmètre module correspondance, politique fichiers) comme à affiner pendant ou après le PRD.
2. **Create Brief** : complété 2026-02-25.
