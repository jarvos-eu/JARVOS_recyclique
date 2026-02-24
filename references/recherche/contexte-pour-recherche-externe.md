# Contexte projet — pour recherches externes (Perplexity, Claude, etc.)

À joindre ou coller en début de conversation quand tu lances une recherche technique ou métier sur le projet. Mettre à jour quand les décisions ou la phase changent.

---

## Projet

**JARVOS Recyclique v0.1.0** — Refonte de Recyclic 1.4.4 (caisse, dépôts, flux matière pour ressourcerie). Nouveau backend ; intégration avec **Paheko** (compta, gestion associative). Solo dev. Pas de code encore : phase recherche / conception.

**Déploiement cible** : une instance Docker Compose par ressourcerie (backend central), plusieurs postes de travail et potentiellement plusieurs établissements par ressourcerie. Un repo par ressourcerie. Gunicorn multi-workers dès le premier déploiement multi-poste.

**Stratégie recherche** : spirale — 1re passe découverte sur tous les sujets (Kanban, todo), 2e passe recherches détaillées (API Paheko, analyse dumps). Accès aux dumps BDD production Recyclic + Paheko prévu ; objectif = montage en local pour analyser et déduire les correspondances.

## Stack cible

- **Backend** : Python, FastAPI, Gunicorn multi-workers.
- **Front** : React / Vite / TS (PWA). Monorepo, un seul build.
- **Données** : PostgreSQL, Redis (cache + Redis Streams pour événements inter-modules). Docker Compose.
- **Dual-backend** : Recyclic (FastAPI) + Paheko (PHP) coexistent. **Architecture « max Paheko »** : Paheko = backend financier et matière complet (caisse native, extension Saisie au poids) ; Recyclic = surcouche UX + workflow terrain. Module de correspondance = traducteur Recyclic → API Paheko.

## Décisions posées

- Utilisateurs = Paheko natif (pas de gestion users côté Recyclic).
- Import code 1.4.4 : copier + consolider + contrôle sécurité/qualité à chaque import.
- Ganglion / Le Fil : hors scope ; placeholder GitHub public pour partage de ressources.
- **Système de modules** : manifeste TOML par module (`module.toml`), modules internes dans monorepo. Activation par instance via `config.toml`. Contrat `ModuleBase` (startup, shutdown, register_routes, register_signals, register_ui_extensions).
- **Événements inter-modules** : Redis Streams (EventBus wrapper `core/events.py`). Redis Pub/Sub et async-signals exclus (in-process ou pas de persistance). Durabilité, multi-workers, replay natifs.
- **UI modules** : routes dédiées par module + slots React (`<ModuleSlot />`), lazy loading, un seul build Vite. Pas de Module Federation.

## Ce qu'on cherche (recherches en cours ou à faire)

- **API Paheko caisse** : endpoints, modèles (sessions, ventes, paiements), mapping Recyclic → Paheko. Prérequis pour décision source de vérité caisse.
- **Extension Saisie au poids Paheko** : fonctionnement, tables, import depuis caisse, API lecture/écriture. Prérequis architecture flux matière.
- **Source de vérité caisse** : Paheko seul vs miroir Recyclic — à décider après recherche API.
- **Paheko** : catalogue des modules optionnels ; capacités natives (calendrier, fichiers, communication).
- **LLM/IA** : stratégie (hardcodé + placeholder vs. JARVOS Nano/Mini) ; usages actuels dans 1.4.4.

## Sujets résolus (ne plus poser de questions dessus)

- Framework de modules : décidé (TOML + loader + EventBus Redis Streams). Voir `references/artefacts/2026-02-24_07_design-systeme-modules.md`.
- Architecture « max Paheko » : caisse native + Saisie au poids ; module correspondance = traducteur. Voir `references/artefacts/2026-02-24_08_decision-architecture-max-paheko.md`.

## Sujets non résolus (à trancher après recherche)

- Source de vérité caisse (Paheko seul vs miroir). Résilience si Paheko down. Réception/dépôts Recyclic vs périmètre extension Saisie au poids.

## Contraintes

- Éviter l'over-engineering ; privilégier solutions éprouvées.
- Réponses en français sauf si la source technique est en anglais.
