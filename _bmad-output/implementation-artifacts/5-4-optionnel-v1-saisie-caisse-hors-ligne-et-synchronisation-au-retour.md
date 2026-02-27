# Story 5.4: Optionnel v1 — Saisie caisse hors ligne et synchronisation au retour

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->
<!-- Story optionnelle v1 : HITL-5.4 permet de trancher si dans le périmètre v1 ou reportée (epics.md). -->

## Story

En tant qu'**opérateur caisse**,
je veux **enregistrer des ventes en local quand le réseau est indisponible, puis synchroniser les tickets vers Paheko au retour en ligne**,
afin de **ne pas bloquer la vente en cas de coupure**.

## Acceptance Criteria

1. **Étant donné** un frontend avec buffer local (ex. IndexedDB) et une file Redis Streams côté backend  
   **Quand** le frontend est hors ligne, je continue à saisir des ventes ; au retour en ligne, les tickets sont envoyés  
   **Alors** les tickets sont bien en file et traités comme en Story 5.2 ; aucune perte de donnée (FR7b).

2. Si la story est reportée en post-v1, elle reste marquée optionnelle ou déplacée en conséquence (décision HITL-5.4).

## Tasks / Subtasks

- [x] Task 1 — Détection hors ligne et buffer local (AC: #1)
  - [x] Détecter l'état en ligne / hors ligne (navigator.onLine + événements online/offline).
  - [x] Mettre en place un buffer local côté frontend (ex. IndexedDB) pour stocker les tickets créés hors ligne (même structure que payload envoyé en 5.2).
  - [x] Lors de la saisie hors ligne : persister le ticket (lignes + paiements) dans le buffer au lieu d'appeler l'API.
- [x] Task 2 — Envoi au retour en ligne (AC: #1)
  - [x] Au retour en ligne : envoyer les tickets du buffer vers l'API RecyClique (même contrat que Story 5.2) pour alimenter la file Redis Streams.
  - [x] Vider ou marquer comme envoyés les tickets du buffer après succès (idempotence si rejeu).
  - [x] Gérer les échecs partiels (retry, garder en buffer jusqu'à succès).
- [x] Task 3 — Alignement avec 5.2 et Epic 4 (AC: #1)
  - [x] S'assurer que les tickets envoyés après retour en ligne passent par les mêmes endpoints et la même file Redis Streams que 5.2 ; le worker Epic 4 les traite sans changement.
  - [x] Aucune perte de donnée : pas de ticket supprimé du buffer avant confirmation côté serveur.
- [x] Task 4 — UX et tests (AC: #1)
  - [x] Indication visuelle « hors ligne » / « synchronisation en attente » sur l'écran caisse.
  - [x] Tests : frontend co-locés `*.test.tsx` (Vitest + React Testing Library) pour le flux buffer → envoi ; pas de Jest. Si tests API du contrat envoi, les placer dans `api/tests/` selon structure projet.

## Dev Notes

- **FR7b** : Saisie caisse hors ligne (buffer local) + sync vers Paheko au retour (file Redis Streams backend). Référence : epics.md Epic 5, FR Coverage Map.
- **Stories dépendantes** : 5.1 (sessions), 5.2 (ventes + push par ticket), Epic 4 (worker Redis Streams). Le backend ne change pas de contrat : les tickets « hors ligne » arrivent via les mêmes endpoints que 5.2 et rejoignent la file Redis Streams.
- **Frontend** : buffer local recommandé = IndexedDB (epics.md) ; même format de payload que pour un ticket créé en ligne (lignes, catégories, paiements, session_id). Détection offline : `navigator.onLine` + `window.addEventListener('online'|'offline')`.
- **Architecture** : EventBus / Redis Streams côté serveur uniquement ; le front passe par l'API. Pas de nouveau type d'événement Redis : les tickets issus du buffer sont soumis comme des tickets normaux (Story 5.2). [Source: _bmad-output/planning-artifacts/architecture.md]
- **Idempotence** : au rejeu (retry après retour en ligne), éviter les doublons côté serveur — soit identifiant client (ex. `offline_id`) dans le payload et déduplication API, soit envoi ticket par ticket avec même contrat que 5.2 si l'API est déjà idempotente.
- **Conventions** : API REST, JSON, snake_case côté API ; montants en centimes. Tests frontend co-locés `*.test.tsx`, Vitest + RTL. [Source: epics.md Décisions architecturales]

### Project Structure Notes

- **Frontend** : module caisse existant (écrans 5.1–5.3) ; ajout d'un store ou service « offline queue » + persistance IndexedDB (ex. `frontend/src/.../caisse/offlineQueue` ou équivalent selon structure par domaine).
- **API** : réutilisation des endpoints de création de ticket / lignes / paiements de la Story 5.2 ; pas de nouveau route dédiée « batch offline » obligatoire si l'envoi ticket par ticket au retour suffit (à trancher en implémentation pour performance).

### References

- [Source: _bmad-output/planning-artifacts/epics.md — Epic 5, Story 5.4]
- [Source: _bmad-output/planning-artifacts/epics.md — FR7b, FR Coverage Map]
- [Source: _bmad-output/planning-artifacts/architecture.md — Redis Streams, EventBus, stack v1]
- [Source: references/artefacts/2026-02-26_09_perimetre-api-recyclique-v1.md — endpoints caisse si détail nécessaire]
- [Source: references/artefacts/2026-02-26_10_tracabilite-ecran-donnees-appels-api.md — §5 caisse]

## Dev Agent Record

### Agent Model Used

(à remplir par l'agent d'implémentation)

### Debug Log References

### Completion Notes List

- **Task 1–2** : Hook `useOnlineStatus` (navigator.onLine + online/offline). Module `offlineQueue` avec IndexedDB (DB `recyclic_offline`, store `tickets`, clé `offline_id`). En saisie hors ligne : payload identique à POST /v1/sales + `offline_id` (UUID client) et `created_at` ; enregistrement dans le buffer, panier vidé.
- **Task 2** : Au retour en ligne, `syncOfflineQueue(accessToken)` envoie chaque ticket via `postSale` avec `offline_id` ; après 201 on retire du buffer ; en échec on laisse en buffer (retry au prochain online).
- **Task 3** : POST /v1/sales inchangé côté contrat ; ajout optionnel `offline_id` (UUID) dans le body. API : colonne `sales.offline_id` (UUID, unique, nullable) ; si `offline_id` fourni et déjà présent → retour 201 avec vente existante (pas de doublon Redis). Tickets synchronisés passent par le même flux Redis Streams (publish_ticket_created) que 5.2.
- **Task 4** : Bandeaux « Hors ligne » (orange) et « Synchronisation en attente : N ticket(s) » (bleu) sur la page saisie vente. Tests co-locés `CashRegisterSalePage.test.tsx` : bandeau offline/sync, soumission en ligne → postSale, soumission hors ligne → addTicket avec offline_id (5 tests).
- **Migration BDD** : Si la base existe déjà, ajouter la colonne `offline_id` à la table `sales` (UUID, unique, nullable). Nouvelle installation depuis les modèles SQLAlchemy inclut la colonne.
- **Migration Alembic** : Ajout de `api/db/alembic/versions/2026_02_27_5_4_add_sales_offline_id.py` (revision 2026_02_27_5_4, revises 2026_02_27_5_3) — colonne `sales.offline_id` UUID nullable, index unique `ix_sales_offline_id`.

### File List

- api/db/alembic/versions/2026_02_27_5_4_add_sales_offline_id.py (nouveau — migration sales.offline_id)
- api/models/sale.py (ajout colonne offline_id)
- api/schemas/sale.py (SaleCreate.offline_id optionnel)
- api/routers/sales.py (dedup par offline_id avant creation)
- frontend/src/api/caisse.ts (SaleCreatePayload.offline_id, postSale inchange)
- frontend/src/caisse/useOnlineStatus.ts (nouveau)
- frontend/src/caisse/offlineQueue/types.ts (nouveau)
- frontend/src/caisse/offlineQueue/indexedDb.ts (nouveau)
- frontend/src/caisse/offlineQueue/sync.ts (nouveau)
- frontend/src/caisse/offlineQueue/index.ts (nouveau)
- frontend/src/caisse/CashRegisterSalePage.tsx (integration offline + sync + bandeaux)
- frontend/src/caisse/CashRegisterSalePage.test.tsx (nouveau, 5 tests Story 5.4)

## Senior Developer Review (AI)

**Date:** 2026-02-27  
**Résultat:** Approved (re-review)

**Re-review 2026-02-27 :** Migration Alembic `2026_02_27_5_4_add_sales_offline_id.py` verifiee : revision 5_4, down_revision 5_3 ; colonne `sales.offline_id` (postgresql.UUID, nullable, comment) ; index unique `ix_sales_offline_id` ; upgrade/downgrade corrects. Alignement avec `api/models/sale.py`. Bloquant precedent (migration manquante) resolu. Story approuvee.

**Git vs Story :** Fichiers de la story en grande partie untracked (??) ; File List cohérente avec les fichiers présents.

**Problème bloquant (HIGH) :**
- **Migration Alembic manquante** — Convention projet : si colonne BDD ajoutée (sales.offline_id), une migration Alembic doit exister dans `api/db/alembic/versions/` pour les bases déjà déployées. La migration `2026_02_27_5_2` crée la table `sales` sans la colonne `offline_id`. Le modèle `api/models/sale.py` et le router `api/routers/sales.py` utilisent cette colonne. Sur toute base ayant déjà exécuté 5_2 ou 5_3, la colonne n'existe pas → erreur au runtime. **Action requise :** ajouter une migration (ex. `2026_02_27_5_4_add_sales_offline_id.py`) revises 5_3, qui ajoute à `sales` la colonne `offline_id` (UUID, nullable, unique, index).

**Vérifié conforme :**
- AC#1 : buffer local (IndexedDB), file Redis inchangée, tickets envoyés au retour en ligne, idempotence par offline_id côté API.
- Tasks 1–4 : useOnlineStatus, offlineQueue (types, indexedDb, sync), intégration CashRegisterSalePage, bandeaux « Hors ligne » / « Synchronisation en attente », tests co-locés Vitest/RTL (5 tests).
- Dédup par offline_id dans create_sale (201 sur vente existante, pas de republish Redis).
- Pas de perte de donnée : retrait du buffer uniquement après succès postSale.

**Recommandation (LOW) :** Test API optionnel dans `api/tests/` pour l'idempotence (double POST même offline_id → 201 une fois).

## Change Log

- 2026-02-27 : Re-review approuvee — migration Alembic 5_4 verifiee conforme. Story status -> done.
- 2026-02-27 : Migration Alembic 2026_02_27_5_4 ajoutee (sales.offline_id). Status repasse en review.
- 2026-02-27 : Code review (AI) — changes-requested : migration Alembic manquante pour sales.offline_id (convention projet). Story repassée en in-progress.
- 2026-02-27 : Story 5.4 implementee — detection offline, buffer IndexedDB, sync au retour en ligne, idempotence offline_id API, bandeaux UX, tests Vitest/RTL.
