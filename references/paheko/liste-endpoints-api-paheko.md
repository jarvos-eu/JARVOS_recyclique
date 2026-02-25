# Liste des endpoints API Paheko

Tous les endpoints sont préfixés par **`/api`** (ex. `GET /api/user/categories`).  
Source : code source Paheko `include/lib/Paheko/API.php` et `Web/Router.php`.  
Référence complémentaire : [analyse-brownfield-paheko.md](analyse-brownfield-paheko.md) (section 3. API HTTP).

---

## Authentification

- **Credentials API** : HTTP Basic Auth avec login (clé) et mot de passe (secret). Gérés dans Admin → Configuration → Avancé → API ; table `api_credentials` (key, secret hashé, `access_level`). `API_Credentials::auth($login, $password)` retourne le niveau (read / write / admin).
- **Compte système** : si `API_USER` et `API_PASSWORD` sont définis en config, ils donnent accès **admin**.
- **Niveaux** : chaque route exige un niveau minimal via `requireAccess(Session::ACCESS_READ|WRITE|ADMIN)`. Les routes sans `requireAccess` explicite sont accessibles avec le niveau **read** (lecture seule). Détail des niveaux par route dans les tableaux ci‑dessous (colonne « Niveau min. »).

---

## SQL (requêtes et export)

| Méthode | Chemin | Utilité | Niveau min. |
|--------|--------|---------|-------------|
| GET | `/api/sql` | Exécution requête SQL (paramètre `sql` en query ou body), résultat JSON | read |
| POST | `/api/sql` | Idem ; corps JSON ou form. Paramètre optionnel `format` = `xlsx`, `ods`, `csv` pour export fichier | read |

---

## Download (sauvegardes et fichiers)

| Méthode | Chemin | Utilité | Niveau min. |
|--------|--------|---------|-------------|
| GET | `/api/download` | Dump de sauvegarde (backup) | read |
| GET | `/api/download/files` | ZIP de tous les fichiers (stockage) | read |

---

## Web (pages et pièces jointes)

Toutes les routes **web** sont en **GET** uniquement.

| Méthode | Chemin | Utilité | Niveau min. |
|--------|--------|---------|-------------|
| GET | `/api/web/list` | Liste catégories et pages du site (optionnel : segment pour filtrer) | read |
| GET | `/api/web/list/<param>` | Idem avec paramètre de filtre | read |
| GET | `/api/web/attachment/<uri>` | Servir un fichier par URI (contexte web/documents) | read |
| GET | `/api/web/page/<uri>` | Métadonnées d'une page ; si `?html` : rendu HTML inclus | read |
| GET | `/api/web/html/<uri>` | Rendu HTML brut de la page | read |

---

## User (membres, catégories, import)

| Méthode | Chemin | Utilité | Niveau min. |
|--------|--------|---------|-------------|
| GET | `/api/user/categories` | Liste des catégories de membres avec statistiques | read |
| GET | `/api/user/category/<id>.<format>` | Export d'une catégorie (format ex. json) | read |
| POST | `/api/user/new` | Création d'un membre (body form/JSON) | write |
| GET | `/api/user/<id>` | Détail d'un membre | read |
| POST | `/api/user/<id>` | Mise à jour d'un membre | write |
| DELETE | `/api/user/<id>` | Suppression d'un membre | admin |
| POST | `/api/user/<id>/subscribe` | Abonner le membre à un service (param. `id_service`, optionnel `id_fee`) | write |
| POST | `/api/user/import` | Import CSV membres (multipart `file` ou corps brut) | admin |
| PUT | `/api/user/import` | Import CSV membres (corps brut) | admin |
| POST | `/api/user/import/preview` | Aperçu de l'import CSV (sans appliquer) | admin |

---

## Accounting (comptabilité)

| Méthode | Chemin | Utilité | Niveau min. |
|--------|--------|---------|-------------|
| POST | `/api/accounting/transaction` | Création d'une écriture (body API) ; optionnel : `linked_users`, `linked_transactions`, `linked_subscriptions`, `move_attachments_from` | write |
| GET | `/api/accounting/transaction/<id>` | Détail d'une transaction (format journal) | read |
| POST | `/api/accounting/transaction/<id>` | Mise à jour d'une transaction et liens | write |
| GET | `/api/accounting/transaction/<id>/transactions` | Liste des transactions liées | read |
| POST | `/api/accounting/transaction/<id>/transactions` | Mettre à jour les transactions liées | write |
| DELETE | `/api/accounting/transaction/<id>/transactions` | Supprimer toutes les liaisons transactions | write |
| GET | `/api/accounting/transaction/<id>/users` | Liste des membres liés à la transaction | read |
| POST | `/api/accounting/transaction/<id>/users` | Mettre à jour les membres liés | write |
| DELETE | `/api/accounting/transaction/<id>/users` | Supprimer les liaisons membres | write |
| GET | `/api/accounting/transaction/<id>/subscriptions` | Liste des abonnements liés | read |
| POST | `/api/accounting/transaction/<id>/subscriptions` | Mettre à jour les liaisons abonnements | write |
| DELETE | `/api/accounting/transaction/<id>/subscriptions` | Supprimer toutes les liaisons abonnements | write |
| GET | `/api/accounting/charts` | Liste des plans comptables | read |
| GET | `/api/accounting/charts/<id>/accounts` | Liste des comptes d'un plan | read |
| GET | `/api/accounting/years` | Liste des exercices avec statistiques | read |
| GET | `/api/accounting/years/current/journal` | Journal de l'exercice courant | read |
| GET | `/api/accounting/years/<id>/journal` | Journal d'un exercice | read |
| GET | `/api/accounting/years/<id>/export/<type>.<format>` | Export comptable (type/format selon `Export::export`) | read |
| GET | `/api/accounting/years/<id>/account/journal` | Journal d'un compte (param. `code` ou `id`) | read |

---

## Services (abonnements)

| Méthode | Chemin | Utilité | Niveau min. |
|--------|--------|---------|-------------|
| POST | `/api/services/subscriptions/import` | Import CSV des abonnements (multipart `file` ou corps brut) | admin |
| PUT | `/api/services/subscriptions/import` | Idem (corps brut) | admin |

---

## Errors (technique, si activé)

Disponible seulement si `ENABLE_TECH_DETAILS` est activé et qu'un error log est configuré.

| Méthode | Chemin | Utilité | Niveau min. |
|--------|--------|---------|-------------|
| POST | `/api/errors/report` | Envoyer un rapport d'erreur (body JSON avec `context.id`) vers le log | admin |
| GET | `/api/errors/log` | Lire les rapports depuis le log d'erreurs (niveau read ; disponibilité soumise à ENABLE_TECH_DETAILS et error_log) | read |

---

## Note sur l'upload de fichiers

Il **n'existe pas** d'endpoint générique « upload fichier » dans l'API Paheko. Les seuls flux fichier sont :

- **Import membres** : `POST`/`PUT` `/api/user/import` (fichier CSV).
- **Import abonnements** : `POST`/`PUT` `/api/services/subscriptions/import` (fichier CSV).
- **Comptabilité** : à la création/mise à jour de transaction, paramètre optionnel `move_attachments_from` = chemin d'un **répertoire** déjà présent dans le stockage (usage interne / module avec `setAllowedFilesRoot`).

Pour un upload générique (ex. RecyClique), il faudrait ajouter un endpoint dédié (plugin ou core) ou s'appuyer sur WebDAV (`/dav/`). Voir [analyse-brownfield-paheko.md](analyse-brownfield-paheko.md) section 3.3.

---

*Document généré à partir du code source Paheko (API.php). Pour l'authentification et les niveaux, voir [analyse-brownfield-paheko.md](analyse-brownfield-paheko.md).*
