# Story 8.5 — BDD (export, purge, import) et import legacy



- **Epic:** epic-8 (Administration, compta v1 et vie associative)

- **Story_key:** 8-5-bdd-export-purge-import-et-import-legacy

- **Livrable:** 1.4.4 — migration/copie 1.4.4 (artefact 10 §7.10)



---



## User story



En tant qu'admin technique,

je veux les actions BDD (export, purge, import) et l'interface d'import legacy CSV,

afin de maintenir et migrer les données.



---



## Critères d'acceptation



- **Étant donné** les permissions super-admin pour les actions BDD (v1 : fallback admin — si la permission super_admin est absente du seed, admin suffit ; voir Conventions ci-dessous),

- **Quand** j'utilise les actions BDD (export, purge transactions, import),

- **Alors** export, purge transactions et import fonctionnent ; l'interface import legacy (analyze, execute, validate, preview) est opérationnelle.

- **Et** livrable = migration/copie 1.4.4 (artefact 10 §7.10) ; scope import legacy à confirmer produit.



### Section BDD (artefact 10 §7.10)



- **Routes :** sous-routes admin pour BDD (ex. `/admin/db` ou `/admin/db-export`, `/admin/db-purge`, `/admin/db-import`).

- **Permissions :** super-admin. En v1, choix « fallback admin » documenté : tant que la permission super_admin n'existe pas dans le seed (alembic seed permissions/groups), l'implémentation autorise admin pour ne pas bloquer ; pas de changement de code tant que super_admin n'est pas ajoutée au seed.

- **Données / appels au chargement :** écran avec boutons Export BDD, Purge transactions, Import BDD ; pas d'appel GET obligatoire au chargement (actions déclenchées par l'utilisateur).

- **Actions :**

  - Export BDD → **POST /v1/admin/db/export** — réponse : fichier sauvegarde (dump ou archive).

  - Purge transactions → **POST /v1/admin/db/purge-transactions** — body optionnel : périmètre (ex. période, types) ; confirmation côté UI.

  - Import BDD → **POST /v1/admin/db/import** — body : fichier ou référence sauvegarde ; confirmation et avertissements côté UI.



### Section Import legacy (artefact 10 §7.10)



- **Route :** `/admin/import/legacy`

- **Permissions :** admin (ou super-admin selon politique).

- **Données / appels au chargement :** **GET /v1/admin/import/legacy/llm-models** — liste des modèles LLM (si applicable).

- **Actions :**

  - Upload CSV + analyse → **POST /v1/admin/import/legacy/analyze** — body : fichier CSV.

  - Prévisualisation → **POST /v1/admin/import/legacy/preview** (résultat après analyse ou mapping).

  - Validation → **POST /v1/admin/import/legacy/validate**.

  - Exécution import → **POST /v1/admin/import/legacy/execute**.

- **Notes :** B46, B47 ; scope import legacy à confirmer en v1 (contenu CSV, modèles LLM, champs mappés).



---



## Tasks



### Frontend



1. **Admin BDD (export, purge, import)**

   - Implémenter la route ou les sous-routes admin pour BDD (ex. `/admin/db` avec onglets ou sections Export, Purge, Import).

   - Bouton Export BDD → appel **POST /v1/admin/db/export** ; téléchargement du fichier retourné.

   - Bouton Purge transactions → confirmation modale puis **POST /v1/admin/db/purge-transactions** ; affichage du résultat ou erreur.

   - Import BDD : formulaire upload fichier (ou sélection référence) → **POST /v1/admin/db/import** ; confirmation et feedback (succès / échec).

   - Protéger l'accès par permission super-admin (redirection ou masquage si non super-admin).



2. **Admin Import legacy**

   - Implémenter la route `/admin/import/legacy`.

   - Au chargement : **GET /v1/admin/import/legacy/llm-models** si applicable (sélecteur modèle LLM).

   - Zone upload CSV ; boutons ou étapes : Analyze, Preview, Validate, Execute.

   - Analyze : **POST /v1/admin/import/legacy/analyze** (fichier) ; affichage résultat analyse (colonnes détectées, erreurs, avertissements).

   - Preview : **POST /v1/admin/import/legacy/preview** ; affichage aperçu des données à importer.

   - Validate : **POST /v1/admin/import/legacy/validate** ; affichage résultat validation.

   - Execute : **POST /v1/admin/import/legacy/execute** ; confirmation puis exécution ; feedback succès / échec.

   - Permission admin (ou super-admin selon politique produit).



### APIs (backend)



3. **BDD export, purge, import**

   - **POST /v1/admin/db/export** : génération d'une sauvegarde (dump SQL ou format défini) ; retour en stream ou fichier ; protégé par permission super-admin.

   - **POST /v1/admin/db/purge-transactions** : suppression des données de transactions selon périmètre (body optionnel) ; protégé par super-admin ; audit event recommandé.

   - **POST /v1/admin/db/import** : restauration depuis un fichier ou référence ; protégé par super-admin ; validation format et sécurité (pas d'exécution arbitraire) ; audit event recommandé.



4. **Import legacy**

   - **GET /v1/admin/import/legacy/llm-models** : liste des modèles LLM disponibles (pour mapping / analyse) — peut retourner liste vide ou stub en v1.

   - **POST /v1/admin/import/legacy/analyze** : accepte fichier CSV ; analyse structure et contenu ; retourne rapport (colonnes, types, erreurs, suggestions).

   - **POST /v1/admin/import/legacy/preview** : retourne un aperçu des lignes qui seraient importées (après mapping/analyse).

   - **POST /v1/admin/import/legacy/validate** : valide le jeu de données (contraintes, doublons, etc.) ; retourne rapport validation.

   - **POST /v1/admin/import/legacy/execute** : exécute l'import ; body peut contenir options ou référence à une analyse précédente ; retourne résumé (lignes importées, erreurs).

   - Permissions : admin ou super-admin selon décision produit ; scope (types d'entités importables, format CSV) à confirmer produit.



---



## Références



- **Epic 8, Story 8.5 :** `_bmad-output/planning-artifacts/epics.md`

- **Traçabilité écran → API :** `references/artefacts/2026-02-26_10_tracabilite-ecran-donnees-appels-api.md` (§7.10 BDD, Import legacy) — **écran #26** (index §3).

- **Architecture et conventions :** `_bmad-output/planning-artifacts/architecture.md` ; `references/artefacts/2026-02-26_03_checklist-v0.1-architecture.md`

- **Sprint status :** `_bmad-output/implementation-artifacts/sprint-status.yaml`



## Conventions d'implémentation



- **UI / styling :** Mantine (alignement 1.4.4).

- **Layout admin :** écrans intégrés au layout admin (navigation / sidebar) dans `frontend/src/admin/`.

- **Tests frontend :** Vitest + React Testing Library + jsdom ; tests co-locés `*.test.tsx`.

- **Tests backend :** couvrir les endpoints `POST /v1/admin/db/*` et `GET/POST /v1/admin/import/legacy/*` (recommandé, alignement autres stories admin).

- **Backend :** respect des conventions API (snake_case, pluriel, erreur `{ "detail": "..." }`, dates ISO 8601).

- **Sécurité :** endpoints BDD (export/purge/import) réservés super-admin ; audit events pour purge et import.



---



## Code review



- **Fichier :** `8-5-bdd-export-purge-import-et-import-legacy.review.json`

- **Pass 1 (2026-02-27), adversarial :** `changes-requested`. Vérifiés : routes `/admin/db`, `/admin/import/legacy` ; endpoints POST db/export, purge-transactions, import ; GET llm-models, POST analyze, preview, validate, execute ; permission import legacy admin/super_admin. Findings : (1) Permissions BDD — story exige super_admin uniquement, implémentation autorise admin ou super_admin ; frontend utilise admin pour /admin/db. (2) Audit events manquants pour purge-transactions et import. À traiter avant approbation.

- **Corrections (2026-02-27) :** (1) Permissions BDD — choix v1 « fallback admin » documenté dans la story (critères d'acceptation, section BDD) et en commentaire dans `api/routers/v1/admin/db.py` ; pas de changement de code tant que super_admin n'existe pas dans le seed. (2) Audit — `write_audit_event` appelé pour purge-transactions et import BDD dans `db.py` (actions `admin.db.purge_transactions`, `admin.db.import`). Story remise en review (pass 2).

- **Pass 2 (2026-02-27) :** `approved`. Vérifiés : (1) fallback admin v1 documenté dans la story (critères d'acceptation, section BDD) et dans api/routers/v1/admin/db.py (en-tête + commentaire _DbAdmin). (2) write_audit_event appelé pour purge-transactions (action admin.db.purge_transactions) et pour import (action admin.db.import). Story done.


