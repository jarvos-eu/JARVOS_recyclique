# Plugin framework Recyclic

---

## 2026-02-24 — Mary (brainstorm migration)

Framework plugin pour combiner modules Paheko + RecyClique automatiquement (ex. 2 plugins Paheko + 1 module JARVOS = une config installee d'un coup). Rechercher Pluggy, stevedore, manifeste YAML declaratif. Chantier complet — aucune solution identifiee pour l'instant.

Intention : a-rechercher

---

## 2026-02-24 — Terminologie (session migration)

- **Modules** : les unites fonctionnelles optionnelles qu'on installe (Paheko, JARVOS, codes-barres, etc.). Terme retenu pour la doc et le metier — plus clair.
- **Framework de plugins** : le mecanisme technique (decouverte, chargement, lifecycle). C'est bien un plugin framework qu'on recherche pour implémenter le systeme de modules.
- Prompt recherche cree : `references/recherche/2026-02-24_prompt_perplexity_frameworks-modules-python.md` (a lancer dans Perplexity Pro) ; reponse a ranger en `2026-02-24_reponse_perplexity_frameworks-modules-python.md`.

---

## 2026-02-24 — Recherche + design (session modules/plugins — Mary)

Recherche faite : 3 reponses Perplexity rangees dans `references/recherche/`. Analyse critique produite. Design arbitre dans `references/artefacts/2026-02-24_07_design-systeme-modules.md`.

Decisions posees :
- Manifeste TOML (`module.toml`) par module, modules internes dans monorepo (pas de packaging pip).
- Loader hybride : manifeste pour internes, entry points pour tiers si besoin.
- Activation par instance : `config.toml` (`[modules] enabled = [...]`), migration DB possible plus tard.
- Contrat `ModuleBase` : `startup`, `shutdown`, `register_routes`, `register_ui_extensions`.
- Hooks inter-modules : place reservee dans `core/hooks.py` (hookspecs vides). Choix final Pluggy vs. Blinker en attente de recherche.
- Prompt cree : `references/recherche/2026-02-24_pluggy-vs-alternatives-hooks_perplexity_prompt.md` (convention : date_titre-court_IA_type).

Zones d'ombre residuelles : choix final mecanisme hooks (Pluggy/Blinker/EventBus) ; tests interactions modules.

Passage a a-creuser.

---

## 2026-02-24 — Recherche hooks (reponses Perplexity)

**Reponse 1** (`2026-02-24_pluggy-vs-alternatives-hooks_perplexity_reponse-1.md`) : Reco **async-signals** (async natif, send_robust, pattern Django porté). Blinker = sync, inadapté. Pluggy = non async, over-engineered pour 5-10 events. EventBus maison = risqué sauf si send_robust + first-party. Place reservee : `core/signals.py` avec Signal() par event ; modules enregistrent via `register_signals(signals)`.

**Reponse 2 Redis** (`2026-02-24_pluggy-vs-alternatives-hooks_perplexity_reponse-2-redis.md`) : Recyclic utilise deja Redis (cache). Redis Pub/Sub = temps reel mais **sans persistance** (message perdu si subscriber absent) — inadapté pour hooks metier critiques. **Redis Streams** = durable, consumer groups, ack, replay — excellent pour evenements critiques (sale_closed, sync Paheko) quand on passe multi-workers ou qu'on veut zero perte. Reco initiale : phase 1 = async-signals ; phase 2 = Redis Streams. → Decision finale ci-dessous.

---

## 2026-02-24 — Decision finale : Redis Streams directement (session architecture)

**Contexte** : deploiement central par ressourcerie (une instance, plusieurs etablissements, plusieurs postes). Gunicorn multi-workers necessaire pour la concurrence → async-signals in-process ne traverse pas les workers : evenement emis par Worker 1 non recu par Worker 2.

**Decision** : Redis Streams comme systeme d'evenements principal, des le depart. Pas de phase intermediaire. Pas de debt a refactorer plus tard.

- Redis deja en stack → zero dependance nouvelle.
- EventBus wrapper (~60 lignes, `core/events.py`) — les modules ne connaissent pas Redis.
- Contrat : `register_signals(self, bus: EventBus)` dans `ModuleBase`.
- Redis Pub/Sub exclu (pas de persistance). async-signals exclu (in-process uniquement). Pluggy exclu (sync).

Design complet : `references/artefacts/2026-02-24_07_design-systeme-modules.md` (section Hooks / evenements).
