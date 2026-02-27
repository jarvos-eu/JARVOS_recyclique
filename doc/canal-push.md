# Canal push RecyClique → Paheko

Configuration et résilience du canal d’envoi des tickets (caisse → Paheko). Référence : Epic 4, FR19, NFR-S1, NFR-S2.

## Configuration

Les variables sont chargées par `api/config/settings.py` (Pydantic Settings) depuis `.env` ou l’environnement. Voir [.env.example](../.env.example) pour la liste complète.

| Variable | Obligatoire (worker) | Description |
|----------|----------------------|-------------|
| `PAHEKO_PLUGIN_URL` | Oui | URL du plugin Paheko (ex. `https://paheko.example/plugin/recyclic/push`) |
| `PAHEKO_PLUGIN_SECRET` | Oui | Secret partagé pour authentifier les requêtes ; pas de valeur par défaut en prod |
| `PAHEKO_PUSH_MAX_RETRIES` | Non (défaut : 5) | Nombre max de tentatives d’envoi d’un message |
| `PAHEKO_PUSH_BACKOFF_SECONDS` | Non (défaut : 1.0) | Délai initial (secondes) avant la première retentative |
| `PAHEKO_PUSH_BACKOFF_FACTOR` | Non (défaut : 2.0) | Facteur d’exponentiel entre chaque retentative |

Aucun secret n’est loggé ni exposé dans les réponses API (NFR-S1, NFR-S2).

## Résilience (FR19)

- **Nombre de tentatives :** `PAHEKO_PUSH_MAX_RETRIES` (défaut 5). Chaque message est réessayé jusqu’à ce nombre en cas d’échec (réseau, 5xx, timeout).
- **Stratégie de backoff :** exponentielle. Délai avant la tentative `n` = `PAHEKO_PUSH_BACKOFF_SECONDS * PAHEKO_PUSH_BACKOFF_FACTOR^(n-1)` (ex. 1 s, 2 s, 4 s, 8 s, 16 s pour 5 tentatives).
- **Comportement en cas d’échec définitif :** le message reste dans la file Redis (Streams). Il n’est pas supprimé tant qu’un accusé de réception valide n’a pas été reçu. Un worker ou un processus de rejeu pourra le reprendre plus tard (Story 4.2 et au-delà).

Cette logique est consommée par le worker Redis Streams (Story 4.2) via le même module `api.config.settings` ; pas de config dupliquée.

## Worker et reprise après crash (Story 4.2)

Le consumer utilise un **consumer group** Redis (`recyclic-push`). Les messages sont ACK uniquement après succès HTTP 2xx du plugin. En cas de crash du worker :

- Les messages **déjà lus mais non ACK** restent dans la liste « pending » (PEL) du stream.
- Au redémarrage, le worker relit d’abord les messages en attente (`XREADGROUP … 0`), puis les nouveaux (`XREADGROUP … >`).
- Aucun message n’est perdu : reprise au dernier ID non ACK.
- Variable optionnelle : `REDIS_STREAM_PUSH_CAISSE` (défaut : `recyclic:push:caisse`) pour le nom du stream.
