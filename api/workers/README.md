# Workers — consommateurs Redis Streams (Event System)

Ce dossier contient les **points d'entrée** des consumers Redis Streams. En v1 : file push caisse → plugin Paheko (worker `push_consumer`).

## Conventions (architecture § Event System)

- **Nommage des événements** : **dot.lowercase** (ex. `pos.ticket.created`, `reception.ticket.closed`). Payload JSON en **snake_case**.
- **Consommateurs** : idempotence si possible ; **ACK après traitement réussi uniquement** ; retry avec backoff en cas d'échec (NFR-I1).
- **Streams** : un stream dédié par flux métier (ex. push caisse). Nom du stream configuré dans `api/config/settings.py` (ex. `redis_stream_push_caisse`).

## Structure

- `push_consumer.py` : consumer du stream push caisse ; lit les événements (type `pos.ticket.created` ou équivalent), appelle le plugin Paheko en HTTPS avec secret partagé, ACK après succès 2xx ; en échec : pas d'ACK, retry selon config (résilience FR19/FR20).
- Config : `api/config/settings.py` (URL plugin, secret, retry/backoff, nom du stream). Réutiliser `get_settings()`, pas de config dupliquée.

## Démarrage

Le worker est lancé avec l'application FastAPI (même process) au startup ; sa santé est exposée dans le health check (`GET /health` → indicateur `push_worker`).

## Références

- Architecture : `_bmad-output/planning-artifacts/architecture.md` (Event System, Redis, Workers).
- Canal push : `doc/canal-push.md`.
- Story 4.1 (config), Story 4.2 (worker).
