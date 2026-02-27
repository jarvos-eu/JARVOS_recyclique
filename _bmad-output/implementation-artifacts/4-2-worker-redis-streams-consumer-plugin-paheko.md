# Story 4.2: Worker Redis Streams — consumer → plugin Paheko



Status: done



<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->



## Story



As a **système**,

I want **un worker qui consomme la file Redis Streams et envoie les événements au plugin Paheko**,

so that **chaque ticket de vente soit traité de façon résiliente**.



## Acceptance Criteria



1. **Étant donné** une file Redis Streams configurée et le plugin Paheko accessible  

   **Quand** un événement est publié dans la file (type `pos.ticket.created` ou similaire)  

   **Alors** le worker le consomme, appelle le plugin Paheko (HTTPS, secret partagé) et ACK après succès (NFR-I1).



2. **Étant donné** un échec temporaire (réseau, 5xx Paheko)  

   **Quand** l'appel au plugin échoue  

   **Alors** le message reste en file et est repris selon la config retry (FR20) ; les erreurs sont loguées (niveau error + request_id ou correlation_id).



3. **Étant donné** l'application RecyClique déployée  

   **Quand** le worker est actif  

   **Alors** il démarre avec l'application (ou comme process séparé selon l'archi workers) et sa santé est visible dans le health check.



## Tasks / Subtasks



- [x] Task 1 (AC: #1, #2) — Consumer Redis Streams

  - [x] Créer le point d'entrée consumer dans `api/workers/` (convention : nommage et structure selon `api/workers/README.md` et architecture § Event System).

  - [x] Consommer la file Redis Streams (stream dédié push caisse, type événement `pos.ticket.created` ou équivalent dot.lowercase).

  - [x] Lire la config depuis `api/config/settings.py` (endpoint plugin, secret, retry/backoff — livrés par Story 4.1).

  - [x] Appeler le plugin Paheko en HTTPS avec secret partagé (header ou param selon contrat) ; ACK uniquement après succès HTTP 2xx.

  - [x] En échec : ne pas ACK ; logger (niveau error, request_id/correlation_id) ; retry selon config (nb tentatives, backoff).

- [x] Task 2 (AC: #3) — Démarrage et health check

  - [x] Intégrer le worker au démarrage de l'app (même process ou process séparé selon décision archi — voir `architecture.md` § Workers).

  - [x] Étendre le health check existant GET /health (`api/routers/admin/health.py`) : conserver `status`, `database`, `redis` ; ajouter indicateur push worker (ex. `push_worker` : ok / unconfigured / error, optionnel : dernière consommation).

- [x] Task 3 (AC: #2) — Logging et résilience

  - [x] Logs structurés (JSON) ; pas de données sensibles ; request_id/correlation_id propagé.

  - [x] Documenter ou coder le comportement en cas de crash (reprise au dernier ID non ACK).



## Dev Notes



- **Conventions EventBus** : nom d'événement **dot.lowercase** (ex. `pos.ticket.created`) ; payload JSON **snake_case** ; idempotence si possible ; acks après traitement réussi ; retry avec backoff (NFR-I1). [Source: `_bmad-output/planning-artifacts/architecture.md` § Event System, Additional Requirements.]

- **Structure workers** : point d'entrée des consumers dans `api/workers/` ; nommage et exemples dans `api/workers/README.md` si présent, sinon créer ce README avec conventions (Event System, nommage dot.lowercase, structure consumer). [Source: architecture.md § Event System.]

- **Config** : Story 4.1 livre `api/config/settings.py` (Pydantic Settings) : URL plugin, secret, options retry/backoff. Aucun secret en clair dans les requêtes (NFR-S1, NFR-S2).

- **Story 4.1 livrée** : `api/config/settings.py` expose `paheko_plugin_url`, `paheko_plugin_secret`, `paheko_push_max_retries`, `paheko_push_backoff_seconds`, `paheko_push_backoff_factor` ; résilience dans `doc/canal-push.md`. Réutiliser get_settings(), pas de config dupliquée.

- **Nom du stream Redis** : à définir dans settings (ex. `redis_stream_push_caisse` / `REDIS_STREAM_PUSH_CAISSE`) ou convention documentée ; si absent en 4.1, l'ajouter dans settings lors de cette story. Consommer uniquement ce stream dédié push caisse.

- **Health check** : GET /health déjà dans `api/routers/admin/health.py` ; réponse actuelle : `status`, `database`, `redis`. **Étendre** cette réponse (ne pas modifier les champs existants) avec indicateur worker (ex. `push_worker` : ok / unconfigured / error, optionnel : dernière lecture stream). [Source: architecture.md § Logging and Observability.]

- **Redis en v1** : EventBus + file de push uniquement. [Source: architecture.md § Redis.]



### Project Structure Notes



- `api/workers/` : consommateurs Redis Streams (caisse → Paheko). Pas de doublon avec `api/core/modules/` (loader modules) ni avec les routers. Si `api/workers/README.md` est absent, le créer avec conventions (Event System, nommage dot.lowercase, structure consumer).

- Backend : modules/fichiers **snake_case** ; classes **PascalCase** ; événements **dot.lowercase**.



### References



- Epic 4 et Story 4.2 : `_bmad-output/planning-artifacts/epics.md` (Canal push Paheko, critères 4.2).

- Story 4.1 (config livrée) : `_bmad-output/implementation-artifacts/4-1-configuration-du-canal-push-endpoint-secret-resilience.md` — settings, doc/canal-push.md.

- Architecture : `_bmad-output/planning-artifacts/architecture.md` (Event System, Redis, Health, Workers, Data flow).

- Checklist v0.1 : `references/artefacts/2026-02-26_03_checklist-v0.1-architecture.md`.

- FR19, FR20, NFR-I1 : epics.md § Functional Requirements / NFR.



## Change Log



- 2026-02-27 : Implémentation Story 4.2 — worker Redis Streams consumer, push Paheko (HTTPS, secret), ACK/retry, health push_worker, logging structuré, doc reprise crash.

- 2026-02-27 : Code review (BMAD QA) — Correctifs : health push_worker tient compte de `running` (après shutdown → error) ; pas de retry sur HTTP 4xx (FR20 : 5xx/réseau uniquement). Suivis optionnels : mocker httpx dans test_send_to_paheko, tests ACK après 2xx et retry/backoff.



## Dev Agent Record



### Agent Model Used



bmad-dev



### Debug Log References



—



### Completion Notes List



- **Task 1** : Création de `api/workers/` avec `README.md` (conventions Event System), `push_consumer.py` (XREADGROUP, consumer group `recyclic-push`), lecture config depuis `get_settings()` (stream `redis_stream_push_caisse` ajouté en settings), POST Paheko avec header `X-Paheko-Secret`, ACK après 2xx, retry/backoff en échec. Dépendance `httpx` ajoutée.

- **Task 2** : Lifespan FastAPI dans `api/main.py` lance le worker en thread de fond ; arrêt propre via `threading.Event`. Health étendu avec `push_worker` (ok / unconfigured / error) dans `api/routers/admin/health.py`.

- **Task 3** : Logs JSON dans `push_consumer.py` (`_log_structured`, correlation_id = message id), pas de champs sensibles. Section « Worker et reprise après crash » ajoutée dans `doc/canal-push.md` (PEL, XREADGROUP 0 pour pending). Tests : `api/tests/test_push_consumer.py`, extension `test_config_settings.py` pour `redis_stream_push_caisse`.



### File List



- api/config/settings.py (modifié : redis_stream_push_caisse)

- api/requirements.txt (modifié : httpx)

- api/workers/__init__.py (nouveau)

- api/workers/README.md (nouveau)

- api/workers/push_consumer.py (nouveau)

- api/main.py (modifié : lifespan, thread worker)

- api/routers/admin/health.py (modifié : _check_push_worker, push_worker dans réponse)

- doc/canal-push.md (modifié : section reprise après crash)

- .env.example (modifié : REDIS_STREAM_PUSH_CAISSE)

- api/tests/test_config_settings.py (modifié : redis_stream_push_caisse)

- api/tests/test_push_consumer.py (nouveau)



## Senior Developer Review (AI)



**Date :** 2026-02-27  

**Résultat :** Approved (après correctifs appliqués)



### Constat

- AC1, AC2, AC3 et tâches [x] vérifiés contre le code : implémentés.

- File List cohérente avec les fichiers concernés (story 4.2).



### Problèmes traités

1. **HIGH — Health push_worker après shutdown** : Après arrêt du worker, `running=False` mais `last_error=None` → le health renvoyait encore "ok". Corrigé dans `api/routers/admin/health.py` : prise en compte de `state["running"]` ; si configuré et non running → "error".

2. **MEDIUM — Retry sur 4xx** : La story précise « échec temporaire (réseau, 5xx Paheko) ». Les 4xx (erreur client) ne doivent pas être retentés. Corrigé dans `api/workers/push_consumer.py` : pas de retry si erreur type "HTTP 4xx" ; message reste en PEL sans boucle de retries.



### Suivis optionnels (non bloquants)

- [ ] [AI-Review][MEDIUM] Mocker httpx dans `test_send_to_paheko_returns_false_on_connection_error` pour éviter appel réseau / timeout (api/tests/test_push_consumer.py).

- [ ] [AI-Review][MEDIUM] Ajouter test avec mocks Redis + Paheko vérifiant ACK après succès 2xx (api/tests/test_push_consumer.py).

- [ ] [AI-Review][MEDIUM] Ajouter test retry/backoff (nombre tentatives, délai) (api/tests/test_push_consumer.py).

- [ ] [AI-Review][LOW] Exposer optionnellement `last_success_at` (ou dernière lecture) dans GET /health (api/routers/admin/health.py).

