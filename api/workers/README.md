# Workers API RecyClique — EventBus (Redis Streams)

Point d'entrée pour les **consumers EventBus** (Redis Streams). Pas d'implémentation métier complète dans la story 1.4 ; uniquement la structure et la documentation.

## Rôle

- **Consommateurs** des streams Redis (push caisse → Paheko, événements métier).
- Exécutés dans le même processus ou en tâches de fond (à définir selon déploiement).
- Référence : architecture.md — API & Communication Patterns, Event System.

## Nommage des streams et événements

- **Nom d'événement** : **dot.lowercase** ou **snake_case** (ex. `pos.ticket.created`, `reception.ticket.closed`).
- **Payload** : JSON, champs en **snake_case**.
- **Évolution** : prévoir `event_type` et `payload_version` dans le payload pour compatibilité future.

Exemples :

- `pos.ticket.created` → `{ "ticket_id": "...", "session_id": "...", "total_cents": 1000, "event_type": "pos.ticket.created", "payload_version": "1" }`
- `reception.ticket.closed` → `{ "ticket_id": "...", "event_type": "reception.ticket.closed", "payload_version": "1" }`

## Idempotence et acks

- Traiter les messages de façon **idempotente** si possible.
- **Ack** après traitement réussi.
- **Retry** avec backoff en cas d'échec (aligné NFR-I1, aucun ticket perdu).

## Structure

- Les consumers concrets (ex. `pos_push_consumer.py`) seront ajoutés dans les stories métier (caisse, réception).
- Ce dossier contient pour l'instant uniquement ce README et le `__init__.py` pour réserver la place.
