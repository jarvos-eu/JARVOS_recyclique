# Story 6.3: Export CSV et stats live réception



Status: done



<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->



## Story



En tant qu'opérateur ou admin réception,

je veux exporter les données d'un ticket en CSV et consulter les KPI réception en temps réel,

afin de suivre les flux matière sans quitter RecyClique.



## Acceptance Criteria



1. **Étant donné** des tickets et lignes de réception existants (postes, tickets, lignes créés en Stories 6.1 et 6.2),

   **Quand** je clique « Export CSV » sur un ticket (depuis le détail ticket ou la liste),

   **Alors** un fichier CSV du ticket est généré et téléchargeable ; le flux utilise `POST /v1/reception/tickets/{ticket_id}/download-token` (si token requis par l'API) puis `GET /v1/reception/tickets/{ticket_id}/export-csv` (avec token en query si besoin) ; le contenu inclut les données du ticket et de ses lignes (poids_kg, catégorie, destination, etc.) (artefact 09 §3.10, artefact 10 §6.5).



2. **Étant donné** des lignes de réception sur une période,

   **Quand** je demande l'export CSV des lignes (période),

   **Alors** `GET /v1/reception/lignes/export-csv` avec paramètres de période (ex. `date_from`, `date_to`) retourne un fichier CSV téléchargeable des lignes concernées ; les colonnes sont cohérentes avec l'audit réception (ticket_depot, ligne_depot, categories) (artefact 09 §3.10, audit §2 Export CSV lignes).



3. **Étant donné** un opérateur ou admin sur l'accueil réception ou une page réception,

   **Quand** la page se charge ou que je consulte les KPI,

   **Alors** `GET /v1/reception/stats/live` (ou `GET /v1/stats/live` selon convention unifiée) retourne les KPI de réception en temps réel (agrégations sur poste_reception, ticket_depot, ligne_depot) ; option d'exclusion des sessions différées si documenté (B44-P5) (artefact 10 §6.5, audit §2 Stats réception live).



4. **Étant donné** un utilisateur avec permission `reception.access` ou admin,

   **Alors** les endpoints d'export et de stats sont protégés par la même permission ; l'export bulk tickets (admin) reste `POST /v1/admin/reports/reception-tickets/export-bulk` pour un usage admin (artefact 10 §7.8).



5. Livrable = migration/copie depuis RecyClique 1.4.4 selon `references/ancien-repo/checklist-import-1.4.4.md` et `references/migration-paeco/audits/audit-reception-poids-recyclic-1.4.4.md` (artefact 09 §3.10, artefact 10 §6.5).



## Tasks / Subtasks



- [x] Task 1 — API Export CSV ticket (AC: 1, 4, 5)

  - [x] `POST /v1/reception/tickets/{ticket_id}/download-token` : génère un token court (ex. JWT ou secret temporaire) pour autoriser le téléchargement ; vérifier que le ticket existe et que l'utilisateur a `reception.access` (ou admin).

  - [x] `GET /v1/reception/tickets/{ticket_id}/export-csv` : query optionnelle `token=…` si l'API exige le token ; réponse `Content-Disposition: attachment`, type `text/csv` ; contenu = en-têtes + lignes du ticket (id ticket, dates, bénévole, puis pour chaque ligne : catégorie, poids_kg, destination, notes, is_exit, etc.). Réutiliser `_get_ticket_for_user` (story 6.2) pour vérifier les droits.

- [x] Task 2 — API Export CSV lignes période (AC: 2, 4, 5)

  - [x] `GET /v1/reception/lignes/export-csv` : query `date_from`, `date_to` (ISO 8601 ou YYYY-MM-DD) ; pagination ou limite raisonnable pour éviter export massif non filtré ; réponse CSV des lignes (avec colonnes ticket_id, catégorie, poids_kg, destination, created_at, etc.). Permission `reception.access` ou admin.

- [x] Task 3 — API Stats live réception (AC: 3, 4, 5)

  - [x] `GET /v1/reception/stats/live` : agrégations en temps réel (ex. nombre de tickets ouverts aujourd'hui, poids total reçu sur la période courante, nombre de lignes, par poste si pertinent) ; source = poste_reception, ticket_depot, ligne_depot. Option query `exclude_deferred=true` si B44-P5 est implémenté. Réponse JSON (ex. `{ tickets_today, total_weight_kg, lines_count, ... }`). Permission `reception.access` ou admin.

  - [x] Si le projet unifie les stats sous `/v1/stats/live`, documenter ou implémenter le délégué depuis `/v1/reception/stats/live` vers `/v1/stats/live` pour la partie réception (artefact 10 §6.1, 6.5).

- [x] Task 4 — Frontend Export CSV et affichage KPI (AC: 1, 2, 3)

  - [x] Détail ticket (ReceptionTicketDetailPage) : bouton « Export CSV » qui appelle download-token puis export-csv (ou export-csv direct si pas de token) et déclenche le téléchargement du fichier (blob + lien temporaire ou window.open avec token). Prévoir `data-testid` pour les tests (alignement 6.2).

  - [x] Page réception (accueil ou liste) : zone ou modal « Export lignes (période) » : champs date_from / date_to, bouton qui appelle `GET /v1/reception/lignes/export-csv?date_from=…&date_to=…` et télécharge le CSV.

  - [x] Affichage KPI live : sur l'accueil réception (`/reception`), appeler `GET /v1/reception/stats/live` au chargement et afficher les indicateurs (ex. ReceptionKPIBanner ou bloc stats) ; rafraîchissement périodique optionnel (ex. toutes les 30 s) ou au retour sur la page. Alignement Mantine (Text, Group, Card, etc.). Prévoir `data-testid` sur la zone KPI pour les tests.

- [x] Task 5 — Tests (AC: 1–5)

  - [x] Tests API : dans `api/tests/routers/reception/` (ex. `test_reception_export_stats.py` ou extension des tests existants). 401 sans auth pour download-token, export-csv ticket, export-csv lignes, stats/live ; avec auth et ticket existant → export ticket CSV contient les lignes ; avec auth et période → export lignes CSV ; stats/live retourne un JSON cohérent. Validation des query (date_from, date_to).

  - [x] Tests frontend : bouton Export CSV sur le détail ticket déclenche l'appel et le téléchargement (mock de l'API) ; affichage des KPI après chargement de GET /v1/reception/stats/live (mock). Tests co-locés `*.test.tsx` (convention `frontend/README.md`), Vitest + RTL + jsdom.



- [x] **Review Follow-ups (AI)**

  - [x] [AI-Review][HIGH] Tests API avec auth + ticket existant : ajouter test qui crée un ticket/lignes (conftest ou fixture) puis appelle GET export-csv et vérifie que le CSV contient les lignes (api/tests/routers/reception/test_reception_export_stats.py).

  - [x] [AI-Review][HIGH] Tests API avec auth + période : ajouter test qui appelle GET lignes/export-csv avec date_from/date_to et vérifie statut 200 et contenu CSV (même fichier).

  - [x] [AI-Review][HIGH] Tests API stats/live : ajouter test avec auth qui appelle GET stats/live et vérifie JSON (tickets_today, total_weight_kg, lines_count) cohérent (même fichier).

  - [x] [AI-Review][MEDIUM] Export CSV : implémentation actuelle lit tout en mémoire puis iter([body]) ; pour très gros volumes envisager vrai streaming (generator) si besoin (api/routers/v1/reception.py).

  - [x] [AI-Review][MEDIUM] Tokens download : _download_tokens en mémoire non partagé entre workers ; documenter ou prévoir stockage partagé (ex. Redis) si déploiement multi-worker (api/routers/v1/reception.py).

  - [x] [AI-Review][LOW] Export lignes CSV : nom de fichier fixe reception-lignes.csv ; optionnel ajouter la plage de dates dans le filename (api/routers/v1/reception.py).



## Dev Notes



- **Références obligatoires** : `references/migration-paeco/audits/audit-reception-poids-recyclic-1.4.4.md` (§2 Export CSV ticket, Export CSV lignes, Stats réception live ; §3 hébergement données). `references/artefacts/2026-02-26_09_perimetre-api-recyclique-v1.md` §3.10 (Réception). `references/artefacts/2026-02-26_10_tracabilite-ecran-donnees-appels-api.md` §6.5 (Export CSV / Stats live réception).

- **Stories 6.1 et 6.2** : router `api/routers/v1/reception.py`, modèles `ticket_depot`, `ligne_depot`, `poste_reception` ; helpers `_get_ticket_for_user` ; frontend `frontend/src/reception/`, `frontend/src/api/reception.ts` ; permission `reception.access`. Réutiliser le même router et le même client API pour ajouter les endpoints et les appels.

- **Token download** : en 1.4.4 le pattern download-token est utilisé pour sécuriser le téléchargement (éviter URL guessable). Implémenter un token court (ex. JWT exp 1–5 min ou secret one-time) stocké côté backend et validé dans GET export-csv. Si l'audit 1.4.4 n'impose pas le token, on peut livrer d'abord GET export-csv protégé par auth seule et ajouter download-token en option.

- **Format CSV** : séparateur `;` ou `,` selon convention 1.4.4 ; en-têtes en première ligne ; encodage UTF-8 avec BOM si Excel est cible. Colonnes ticket : id, created_at, closed_at, benevole_user_id, poste_id, status ; colonnes ligne : id, ticket_id, category_id, poids_kg, destination, notes, is_exit, created_at. Joindre le libellé catégorie si disponible (categories.name).

- **Stats live** : KPI typiques = tickets ouverts aujourd'hui, poids total reçu (sum poids_kg) sur période courante (jour ou poste ouvert), nombre de lignes. Éviter des agrégations trop lourdes (pas de full scan sans filtre). Option `exclude_deferred` = exclure les postes avec opened_at dans le passé (saisie différée).

- **Export bulk tickets (admin)** : `POST /v1/admin/reports/reception-tickets/export-bulk` est cité en artefact 10 §7.8 ; peut être implémenté dans cette story (admin) ou reporté à l'Epic 8 (admin réception). Si implémenté ici, body = filtres (date_from, date_to, site_id optionnel) ; réponse = fichier CSV ou ZIP de plusieurs CSV.

- Conventions : API REST, JSON pour stats ; snake_case ; erreur `{ "detail": "..." }` ; dates ISO 8601. Frontend : composants PascalCase, hooks camelCase ; état immuable ; isLoading/isPending pour les appels export et stats.



### Project Structure Notes



- **API** : étendre le router existant `api/routers/v1/reception.py` (Stories 6.1, 6.2) avec les routes export et stats. Pas de nouveau domaine. Services optionnels : `reception_export_service.py` ou logique dans le router pour génération CSV et agrégations stats.

- **Frontend** : étendre `frontend/src/reception/` (ReceptionTicketDetailPage pour bouton Export ; page accueil ou liste pour export lignes + KPI). Étendre `frontend/src/api/reception.ts` (getExportTicketCsv, getExportLignesCsv, getReceptionStatsLive).



### Previous Story Intelligence (6.2)



- Réutiliser `_get_ticket_for_user` et `_get_ligne_for_user` pour vérifier les droits sur le ticket avant d'autoriser l'export.

- Destination côté API est un Literal (recyclage, revente, destruction, don, autre) ; le CSV doit exporter la valeur telle quelle.

- Tests API : conftest avec client authentifié et fixtures ticket/lignes ; éviter de partager l'état entre tests (isolation).

- Frontend : Mantine (Button, NumberInput, Select, Table, Card) ; labels et data-testid pour les tests ; aria pour accessibilité NFR-A1.



### References



- [Source: references/migration-paeco/audits/audit-reception-poids-recyclic-1.4.4.md] — §2 Export CSV ticket, Export CSV lignes, Stats réception live ; §3 données

- [Source: references/artefacts/2026-02-26_09_perimetre-api-recyclique-v1.md §3.10] — Réception : download-token, export-csv, lignes/export-csv, stats/live

- [Source: references/artefacts/2026-02-26_10_tracabilite-ecran-donnees-appels-api.md §6.5] — Export CSV / Stats live : routes, appels API, actions utilisateur

- [Source: references/ancien-repo/fonctionnalites-actuelles.md] — Export CSV ticket, Export CSV lignes période, Stats live réception

- [Source: _bmad-output/planning-artifacts/epics.md] — Epic 6, Story 6.3, FR8–FR10

- [Source: _bmad-output/implementation-artifacts/6-2-saisie-des-lignes-de-reception-poids-categorie-destination.md] — API lignes, GET ticket avec lignes, permission, helpers

- [Source: _bmad-output/planning-artifacts/architecture.md] — Conventions API, auth, structure dossiers, tests co-locés



## Senior Developer Review (AI)



**Date:** 2026-02-27  

**Résultat:** Changes requested



**Git vs Story :** Fichiers du File List présents. État git : fichiers Epic 6 non commités (untracked).



**AC validés :** AC1–AC5. Tâches 1–4 implémentées.



**Problèmes :** HIGH (3) — Tests API avec auth + ticket/période/stats non présents (Task 5 partiel). MEDIUM (2) — CSV en mémoire non streamé ; tokens non partagés multi-worker. LOW (1) — Filename export lignes sans plage de dates. Voir Review Follow-ups (AI) dans Tasks.



**Date (2e passage):** 2026-02-27  

**Résultat:** Approved



**Vérification follow-ups :** (1) Tests API avec auth + contenu : 3 tests présents (export ticket contient lignes, export lignes période 200+contenu, stats/live JSON cohérent), fixture conftest reception_user_with_ticket_and_lignes ; 9 tests passent. (2) Commentaires streaming/tokens : présents dans api/routers/v1/reception.py (limitation _download_tokens multi-worker, limitation streaming export ticket/lignes). (3) Nom fichier plage : reception-lignes-{date_from}_{date_to}.csv implémenté. AC et tâches validés.



## Change Log



| Date       | Event    | Description |

|------------|----------|-------------|

| 2026-02-27 | Code review (AI) | Changes requested : tests API auth+contenu manquants, streaming/tokens. Statut → in-progress. |

| 2026-02-27 | Corrections review | HIGH : 3 tests API auth+ticket/période/stats ajoutés (conftest + test_reception_export_stats). MEDIUM : commentaires limitation streaming + tokens multi-worker. LOW : nom fichier export lignes avec plage (reception-lignes-YYYY-MM-DD_YYYY-MM-DD.csv). Statut → review. |

| 2026-02-27 | Code review (AI) 2e passage | Approved. Follow-ups vérifiés : tests auth+contenu, commentaires, filename plage. Statut → done. |



## Dev Agent Record



### Agent Model Used



{{agent_model_name_version}}



### Debug Log References



### Completion Notes List



- Story 6.3 implémentée : API export CSV ticket (download-token + GET export-csv), export CSV lignes (période date_from/date_to), stats live (GET /v1/reception/stats/live). Frontend : bouton Export CSV sur détail ticket, modal Export lignes (période) sur accueil, bandeau KPI (tickets_today, total_weight_kg, lines_count) avec rafraîchissement 30 s. Tests API (6 tests, 401 + validation query), tests frontend (Export CSV + KPI mock).

- Corrections code review 2026-02-27 : (1) HIGH : 3 tests API avec auth + fixture (conftest reception_user_with_ticket_and_lignes) : export ticket CSV contient les lignes, export lignes CSV avec période 200+contenu, stats/live JSON cohérent. (2) MEDIUM : commentaires en tête de _download_tokens (limitation multi-worker) et avant StreamingResponse export ticket/lignes (limitation streaming mémoire). (3) LOW : nom fichier export lignes = reception-lignes-{date_from}_{date_to}.csv.



### File List



- api/routers/v1/reception.py (étendu : download-token, export-csv ticket/lignes, stats/live ; commentaires limitation streaming/tokens ; nom fichier export lignes avec plage dates)

- api/tests/__init__.py (nouveau)

- api/tests/routers/__init__.py (nouveau)

- api/tests/routers/reception/__init__.py (nouveau)

- api/tests/routers/reception/conftest.py (nouveau — fixtures auth + ticket/lignes pour tests 6.3)

- api/tests/routers/reception/test_reception_export_stats.py (nouveau ; +3 tests auth : export ticket contient lignes, export lignes période, stats/live JSON)

- frontend/src/api/reception.ts (étendu : createDownloadToken, exportTicketCsv, exportLignesCsv, getReceptionStatsLive, ReceptionStatsLive)

- frontend/src/reception/ReceptionTicketDetailPage.tsx (bouton Export CSV, data-testid)

- frontend/src/reception/ReceptionAccueilPage.tsx (KPI banner, modal Export lignes, data-testid)

- frontend/src/reception/ReceptionTicketDetailPage.test.tsx (test Export CSV)

- frontend/src/reception/ReceptionAccueilPage.test.tsx (test KPI live, mock getReceptionStatsLive)

