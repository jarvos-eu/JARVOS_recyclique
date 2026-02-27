# Story 5.2: Enregistrement des ventes et push par ticket vers Paheko

Status: done

<!-- Note: Validation is optionnelle. Exécuter validate-create-story pour contrôle qualité avant dev-story. -->

## Story

En tant qu'**opérateur caisse**,
je veux **enregistrer des ventes (tickets avec lignes et paiements multi-moyens) et que chaque ticket soit poussé automatiquement vers Paheko**,
afin qu'**aucun ticket ne soit perdu et que la compta reçoive les ventes sans double saisie** (FR2, FR7).

## Acceptance Criteria

1. **Étant donné** une session de caisse ouverte (Story 5.1)  
   **Quand** j'ajoute des lignes à un ticket (catégorie, quantité, prix en centimes, poids éventuel) et je saisis un ou plusieurs paiements  
   **Alors** le ticket et les lignes sont persistés en BDD RecyClique (tables `sales`, `sale_items`, `payment_transactions`) (FR2)  
   **Et** les conventions BDD sont respectées (snake_case, index idx_{table}_{colonne}) ; livrable = migration/copie 1.4.4 (artefact 08 §2.3, audit caisse §2).

2. **Étant donné** un ticket créé en RecyClique  
   **Quand** la vente est enregistrée avec succès  
   **Alors** le ticket est ajouté à la file Redis Streams (événement type `pos.ticket.created` ou équivalent)  
   **Et** le worker Epic 4 consomme la file et envoie au plugin Paheko (HTTPS + secret partagé) ; ACK après succès (FR7, NFR-S1, NFR-I1).

3. **Étant donné** une session ouverte et les référentiels chargés (catégories, presets)  
   **Quand** je suis sur l'écran saisie vente (étape sale)  
   **Alors** je peux composer un panier (lignes avec category_id ou preset_id, quantity, unit_price/total_price, weight optionnel), saisir plusieurs paiements (payments[] : payment_method, amount), une note et optionnellement sale_date (sessions différées)  
   **Et** l'envoi déclenche **POST /v1/sales** ; la réponse renvoie la vente créée ; le front vide le panier (artefact 10 §5.3).

4. **Étant donné** des conditions réseau normales  
   **Quand** j'enregistre une vente  
   **Alors** le temps de réponse (écriture RecyClique + ajout en file) reste **< 2 s** (NFR-P1)  
   **Et** en cas d'échec temporaire Paheko, le ticket reste en file et est repris par le worker selon la config retry (FR20, NFR-I1).

5. **Étant donné** des ventes existantes (admin ou rapports)  
   **Quand** j'accède à la liste ou au détail  
   **Alors** les endpoints `GET /v1/sales`, `GET /v1/sales/{sale_id}` répondent correctement  
   **Et** `GET /v1/sales` accepte les paramètres de filtre et pagination : `cash_session_id`, `date_from`, `date_to` (optionnels), `limit`, `offset`  
   **Et** la mise à jour de la note est possible via `PUT /v1/sales/{sale_id}` (body : `{ note }`) ; l'édition item (prix, destination) et poids sont couverts par `PATCH /v1/sales/{sale_id}/items/{item_id}` et `PATCH /v1/sales/{sale_id}/items/{item_id}/weight` (artefact 09 §3.6, artefact 10 §5.3).

6. Livrable = **migration/copie 1.4.4** : structure BDD, payload et flux alignés sur `references/migration-paeco/audits/audit-caisse-recyclic-1.4.4.md`, `references/artefacts/2026-02-26_08_catalogue-qui-stocke-quoi-recyclic-paheko.md` §2.3, `references/artefacts/2026-02-26_09_perimetre-api-recyclique-v1.md` §3.6, `references/artefacts/2026-02-26_10_tracabilite-ecran-donnees-appels-api.md` §5.3.

## Tasks / Subtasks

- [x] **Task 1 : Modèle et migration BDD ventes** (AC: 1, 6)
  - [x] Créer/migrer tables `sales` (id, cash_session_id, operator_id, total_amount, note, sale_date, created_at, updated_at ; champs legacy donation, payment_method selon audit), `sale_items` (id, sale_id, category_id, preset_id nullable, quantity, unit_price, total_price, weight nullable), `payment_transactions` (id, sale_id, payment_method, amount) avec FK vers cash_sessions, users, categories, preset_buttons.
  - [x] Index idx_sales_cash_session_id, idx_sales_operator_id, idx_sale_items_sale_id, idx_payment_transactions_sale_id.
- [x] **Task 2 : API création et lecture ventes** (AC: 1, 3, 5)
  - [x] POST /v1/sales — body : cash_session_id, items[] (category_id?, preset_id?, quantity, unit_price?, total_price, weight?), payments[] (payment_method, amount), note?, sale_date? ; persister en RecyClique puis publier événement Redis Streams (pos.ticket.created) avec payload ticket pour le worker Epic 4. Contraintes : refuser si cash_session_id invalide ou session fermée ; refuser si la somme des montants de payments[] est différente du total des lignes (ou de total_amount).
  - [x] GET /v1/sales (paramètres : cash_session_id?, date_from?, date_to?, limit, offset), GET /v1/sales/{sale_id} (détail avec lignes et paiements).
  - [x] PUT /v1/sales/{sale_id} — body : note (mise à jour note).
  - [x] PATCH /v1/sales/{sale_id}/items/{item_id} (preset_id?, unit_price?) et PATCH /v1/sales/{sale_id}/items/{item_id}/weight (weight) pour éditeur item / poids (admin).
- [x] **Task 3 : Intégration file Redis Streams et worker** (AC: 2, 4)
  - [x] Après écriture BDD réussie dans POST /v1/sales : ajouter le message ticket (id, session_id, lignes, paiements, mapping catégories/presets) à la file configurée en Epic 4 (utiliser la clé de config du stream depuis api/config/settings ou équivalent) ; format payload conforme au contrat attendu par le worker et le plugin Paheko (montants en centimes, poids en kg ; conversion g côté plugin si besoin).
  - [x] S'assurer que la réponse HTTP 201 est renvoyée avant ou juste après l'ajout en file (pas d'attente du traitement Paheko) pour respecter NFR-P1 (< 2 s).
  - [x] Documenter ou réutiliser le format d'événement (pos.ticket.created) déjà consommé par le worker Story 4.2.
- [x] **Task 4 : Permissions et audit** (AC: 5, 6)
  - [x] Protéger les routes sales par permissions caisse (caisse.access et variantes virtual/deferred selon session).
  - [x] Tracer les créations de ventes et modifications sensibles (éditeur item, poids) dans audit_events si requis par l'audit 1.4.4.
- [x] **Task 5 : Frontend — écran saisie vente (étape sale)** (AC: 3)
  - [x] Route/étape sale : chargement GET /v1/cash-sessions/current, GET /v1/presets/active, GET /v1/categories/sale-tickets.
  - [x] UI : grille presets, panier (lignes, total, poids), sélecteur catégories, formulaire paiements multiples, note, option sale_date pour différée.
  - [x] Action « Enregistrer ticket » → POST /v1/sales avec body construit ; vidage du panier après succès ; gestion erreur (session fermée, validation).
- [x] **Task 6 : Tests** (AC: 1–6)
  - [x] Tests API : pytest pour POST/GET/PUT/PATCH sales et items (structure tests/ miroir des routers).
  - [x] Tests frontend : Vitest + React Testing Library, composants co-locés (*.test.tsx) pour écran saisie vente, panier, envoi ticket.
  - [ ] Optionnel : test d'intégration vérifiant qu'un ticket créé apparaît en file Redis et est consommé par le worker (ou mock worker).
- **Review Follow-ups (AI)**
  - [x] [AI-Review][CRITICAL] Créer migration Alembic pour sales, sale_items, payment_transactions sous api/db/alembic/versions/ (convention projet). Livrable AC1/AC6 et Task 1 incomplet sans fichier de migration.
  - [x] [AI-Review][LOW] Corriger annotations de type : list_sales → list[SaleListResponse], get_sale / update_sale_note → SaleResponse (api/routers/sales.py).

## Dev Notes

- **Règle brownfield** : migration/copie depuis 1.4.4 selon `references/ancien-repo/checklist-import-1.4.4.md`. S'appuyer sur les colonnes et contraintes décrites dans l'audit caisse (§2) et le catalogue qui stocke quoi (§2.3).
- **Canal push** : Epic 4 a livré le worker Redis Streams et la config (endpoint, secret). En 5.2, côté API : après création du ticket en BDD, publier un message dans la file (événement type `pos.ticket.created`) ; le worker existant consomme et appelle le plugin Paheko. Ne pas bloquer la réponse HTTP sur le résultat Paheko (push asynchrone).
- **Montants** : toujours en centimes (API et BDD RecyClique). Poids : kg en RecyClique ; conversion en g pour Paheko si nécessaire côté plugin/worker.
- **Presets et catégories** : livrés par Epic 2 (stories 2.3, 2.4). Les lignes de vente référencent category_id et optionnellement preset_id ; GET /v1/presets/active et GET /v1/categories/sale-tickets servent l'écran caisse.
- **Conventions** : BDD snake_case, index idx_{table}_{colonne} ; API pluriel snake_case ; erreur = `{ "detail": "..." }` ; dates ISO 8601. Événements Redis : dot.lowercase, payload JSON snake_case (epics.md § Additional Requirements).

### Project Structure Notes

- **API** : router ventes sous `api/` (ex. `api/routers/sales.py` ou domaine `caisse`), schemas Pydantic pour Sales, SaleItem, PaymentTransaction, service métier pour création + publication file.
- **Frontend** : écran saisie vente dans le domaine caisse (ex. `frontend/src/.../cash-register/sale` ou équivalent), Mantine pour l'UI ; routes et appels alignés sur artefact 10 §5.3.
- **File Redis** : réutiliser la config et le nom de stream/consumer group définis en Epic 4 ; format du message documenté ou aligné avec le worker 4.2.

### References

- [Source: references/artefacts/2026-02-26_08_catalogue-qui-stocke-quoi-recyclic-paheko.md §2.3] Sessions et ventes (RecyClique source, miroir Paheko) ; tables sales, sale_items, payment_transactions.
- [Source: references/artefacts/2026-02-26_09_perimetre-api-recyclique-v1.md §3.6] POST /v1/sales = RecyClique + push Paheko ; GET/PUT/PATCH sales et items.
- [Source: references/artefacts/2026-02-26_10_tracabilite-ecran-donnees-appels-api.md §5.3] Saisie vente : chargement (current, presets, categories sale-tickets), action POST /v1/sales body (items, payments, note, sale_date).
- [Source: references/migration-paeco/audits/audit-caisse-recyclic-1.4.4.md §2] Création vente → tables sales, sale_items, payment_transactions ; paiements multiples, poids, presets, sale_date.
- [Source: _bmad-output/planning-artifacts/epics.md] FR2, FR7, FR20, NFR-P1, NFR-S1, NFR-I1 ; décisions montants centimes, événements Redis dot.lowercase.

## Dev Agent Record

### Agent Model Used

(à remplir par l'agent d'implémentation)

### Debug Log References

### Completion Notes List

- Modèles BDD : sales, sale_items, payment_transactions (api/models) avec index requis. Migration 5.2 : api/db/alembic/versions/2026_02_27_5_2_sales_sale_items_payment_transactions.py (convention projet).
- API : router api/routers/sales.py — POST/GET/PUT/PATCH /v1/sales et items ; push Redis pos.ticket.created après commit.
- Permissions caisse + audit_events (sale_created, sale_item_updated, sale_item_weight_updated).
- Frontend : CashRegisterSalePage, chargement current + presets/active + categories/sale-tickets ; panier, paiements, note, sale_date ; POST /v1/sales puis vidage panier.
- Tests : api/tests/test_sales.py (9 pytest), frontend CashRegisterSalePage.test.tsx (4 Vitest+RTL).

### File List

- api/models/sale.py, sale_item.py, payment_transaction.py
- api/models/cash_session.py (relation sales), api/models/__init__.py
- api/db/alembic/versions/2026_02_27_5_2_sales_sale_items_payment_transactions.py
- api/schemas/sale.py, api/services/push_caisse.py, api/routers/sales.py, api/main.py
- api/tests/conftest.py, api/tests/test_sales.py
- frontend/src/api/caisse.ts, frontend/src/caisse/CashRegisterSalePage.tsx, CashRegisterSalePage.test.tsx, index.ts
- frontend/src/App.tsx

## Senior Developer Review (AI)

- **Date** : 2026-02-27
- **Résultat** : Approved (re-review). Migration et types corrigés vérifiés.
- **Blocant** : Résolu. Migration livrée et vérifiée.
- **Vérifié** : Modèles (Sale, SaleItem, PaymentTransaction) et index conformes ; router sales POST/GET/PUT/PATCH correct ; push Redis pos.ticket.created après commit ; worker consomme le champ `payload` ; permissions caisse et audit_events en place ; frontend CashRegisterSalePage et tests API/frontend présents.
- **Mineur** : Annotations list_sales/get_sale/update_sale_note corrigées. Optionnel : update_sale_item et update_sale_item_weight pourraient déclarer SaleItemResponse en retour.

## Change Log

| Date       | Phase        | Commentaire |
|------------|--------------|-------------|
| 2026-02-27 | code-review  | Review adversarial : changes-requested — migration Alembic manquante (api/db/alembic/versions/) ; story repassée in-progress. |
| 2026-02-27 | corrections  | Migration créée api/db/alembic/versions/2026_02_27_5_2_sales_sale_items_payment_transactions.py ; annotations type sales.py corrigées ; status → review. |
| 2026-02-27 | code-review  | Re-review : approved. Migration et types vérifiés ; story → done, sprint 5-2 → done. |
