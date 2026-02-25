# Analyse brownfield — Paheko (backend Recyclique)

**Date :** 2026-02-25  
**Objectif :** Documenter le dépôt Paheko pour une intégration comme backend de RecyClique (JARVOS Recyclique).  
**Source analysée :** `references/paheko/repo/` (clone GitHub miroir de Fossil).

---

## 1. Vue d'ensemble technique

- **Stack :** PHP, SQLite, pas de framework MVC externe (routing et entités maison).
- **Point d'entrée HTTP :** `www/_route.php` → `Router::route()` (`Paheko\Web\Router`). (Dans certaines versions le code peut être sous `src/` ; dans le repo actuel tout est à la racine de `repo/` : `include/`, `www/`, `modules/`.)
- **Racine projet :** `include/init.php` charge la config, l'autoload (dont namespace `Paheko\Plugin\` pour les plugins), constantes (ROOT, PLUGINS_ROOT, etc.).

---

## 2. Système d'extensions

### 2.1 Deux types d'extensions

| Type     | Classe / table     | Emplacement code              | Usage principal                          |
|----------|--------------------|-------------------------------|------------------------------------------|
| **Module** | `Paheko\Entities\Module` / `modules` | `modules/<nom>/` (fichiers dans le stockage fichiers, contexte `modules`) ou `ROOT/modules/<nom>/` (dist) | Snippets (templates Brindille), page d'accueil, menu ; un seul module “web” actif à la fois |
| **Plugin** | `Paheko\Entities\Plugin` / `plugins` | `PLUGINS_ROOT/<nom>/` ou `.tar.gz` (phar) | Code PHP exécutable, signaux, interface admin dédiée |

- **Extensions** : façade unifiée `Paheko\Extensions` qui liste/active/désactive modules et plugins et normalise en `Paheko\Entities\Extension`.

### 2.2 Plugins

- **Métadonnées :** `plugin.ini` (nom, version, auteur, `menu`, `home_button`, `restrict_section`/`restrict_level`, `min_version`).
- **Fichiers clés :** `install.php`, `upgrade.php`, `uninstall.php`, `admin/index.php`, `admin/config.php`, `admin/icon.svg`. Fichiers protégés (non appelables directement) : `plugin.ini`, `install.php`, `upgrade.php`, `uninstall.php`.
- **Routage :**
  - Admin : `ADMIN_URL . 'p/<nom>/'` → `Plugin::route($uri)` → `Plugin::call($file)` (inclut le PHP du plugin avec constantes PLUGIN_ROOT, PLUGIN_URL, etc.).
  - Public : `WWW_URL . 'p/<nom>/'` pour partie publique.
- **Signaux :** `Plugins::fire($name, $stoppable, $in, $out)`. Enregistrement en base `plugins_signals` (signal, plugin, callback). Les callbacks doivent être dans le namespace `Paheko\Plugin\<NomPlugin>\`. Exemples de signaux : `menu.item`, `home.button`, `file.mkdir`, `file.store`, `file.delete`, `file.rename`, `file.trash`, `file.restore`, `web.request.before`, `web.request`, `web.request.after`.
- **Stockage dédié :** chaque plugin a un “storage root” `ext/p/<nom>` (contexte fichiers `ext`).
- **Sécurité :** allowlist/blocklist (`PLUGINS_ALLOWLIST`, `PLUGINS_BLOCKLIST`), validation du nom (`[a-z][a-z0-9]*(?:_[a-z0-9]+)*`), vérification que `plugin.ini` est sous `PLUGINS_ROOT`.
- **Ressources statiques :** `Plugins::routeStatic($name, $uri)` pour `public/` et `admin/` (MIME par extension).

### 2.3 Modules

- **Métadonnées :** `module.ini` (ou fichier dans le stockage) ; peuvent être “système” (fournis en dist dans `ROOT/modules/`).
- **Stockage :** contexte `modules/<nom>` pour le code éditable ; données optionnelles en table `module_data_<nom>` et champ `config` en base.
- **Templates :** Brindille (UserTemplate), enregistrés en `modules_templates`. Snippets prédéfinis (transaction, user, home_button, my_services, my_details, markdown, etc.).
- **URL :** `BASE_URL . 'm/<nom>/'` pour l'espace membre ; un module peut être “web” et servir le site public (un seul actif).
- **API interne :** depuis un template, fonction Brindille `api` qui instancie `API` avec niveau d'accès et `setAllowedFilesRoot($module->storage_root())` pour limiter les chemins fichiers (ex. `move_attachments_from`).

### 2.4 Intérêt pour RecyClique

- **Plugin dédié** : ajouter un plugin (ex. `recyclique` ou `caisse`) avec ses propres routes admin, signaux et stockage dans `ext/p/<nom>`.
- **Module** : plutôt pour affichage membre / site (snippets, pages) et stockage de données métier dans `module_data_*` et fichiers dans `modules/<nom>`.
- **Signaux** : brancher sur `file.*`, `web.request.*` ou menus pour intégrer sans modifier le cœur.

---

## 3. API HTTP

### 3.1 Point d'entrée et authentification

- **URL :** préfixe `/api` (Router enlève `api` et passe le reste à `API::routeHttpRequest($uri)`).
- **Méthodes :** GET, POST, PUT, DELETE.
- **Auth :**
  - **Credentials API** : login/mot de passe (table `api_credentials` : key, secret hashé, access_level). `API_Credentials::auth($login, $password)` retourne le niveau (read/write/admin). Gestion dans Admin → Configuration → Avancé → API.
  - **Compte système** : si `API_USER` et `API_PASSWORD` sont définis en config, ils donnent accès admin.
- **Corps :** JSON ou form selon `Content-Type` ; pour PUT, corps brut possible (stream mis dans `file_pointer` pour imports fichier).

### 3.2 Arborescence des routes

Tout est sous un premier segment de chemin ; le reste est passé en `$uri` aux méthodes protégées.

| Préfixe        | Méthode(s) | Description sommaire |
|----------------|------------|------------------------|
| `sql`         | GET, POST  | Exécution requête SQL (Search), export xlsx/ods/csv possible |
| `download`    | GET        | `''` → backup dump ; `files` → zip de tous les fichiers |
| `web`         | GET        | `list` (catégories/pages), `attachment/<uri>` (servir fichier), `page/<uri>`, `html/<uri>` (rendu HTML) |
| `user`        | GET, POST, PUT, DELETE | Catégories, export catégorie, `user/new`, `user/<id>`, `user/<id>/subscribe`, `user/import` (CSV, POST/PUT), `user/import/preview` |
| `accounting`  | GET, POST, DELETE | Transactions (création, liaison users/transactions/subscriptions), charts, years, journal, exports |
| `services`    | POST, PUT  | `services/subscriptions/import` (CSV) |
| `errors`      | GET, POST  | `report` (POST body JSON), `log` (GET) — si technique activé |

- **Niveaux d'accès :** `requireAccess(Session::ACCESS_READ|WRITE|ADMIN)` selon la route ; compte API avec `access_level` ou compte système.

### 3.3 Fichiers et API

- **Pas d'endpoint générique “upload fichier”** dans l'API actuelle. Les fichiers sont :
  - **Import utilisateurs :** `user/import` (POST multipart avec `file`, ou PUT avec corps brut) → fichier temporaire puis CSV traité.
  - **Import abonnements :** `services/subscriptions/import` (idem).
  - **Comptabilité :** à la création de transaction (`accounting/transaction` POST), paramètre optionnel `move_attachments_from` : chemin d'un **répertoire** existant dans le stockage ; ce répertoire est **déplacé** vers le répertoire des pièces jointes de la transaction. Pour que ce chemin soit accepté, l'appelant doit avoir défini une racine autorisée via `setAllowedFilesRoot()` (cas usage interne depuis un module).
- **Téléversement “côté web” :** hors API, via formulaires admin :
  - `admin/common/files/upload.php` : `Files::uploadMultiple($parent, 'file', Session)` (paramètre `p` = parent).
  - Pièces jointes pages web : `admin/web/_attach.php` (upload dans `$page->dir_path()`).

Donc pour RecyClique : **soit** utiliser l'API avec un répertoire préalablement rempli (ex. via WebDAV ou un futur endpoint), **soit** ajouter un endpoint d'upload (ex. sous `files/upload` ou dans un plugin) qui appelle `Files::createFromPath` / `createFromPointer` dans un contexte autorisé.

### 3.4 Référencement de fichiers existants

- **Web :** `web/attachment/<uri>` : `Files::getFromURI($param)` puis `$attachment->serve()`. L'URI peut être un chemin de contexte (ex. `documents/...` ou contexte web).
- **Comptabilité :** les transactions ont un répertoire d'attachments (contexte `transaction/<id_transaction>/`) ; le lien se fait en base (`acc_transactions_files`) et par déplacement de répertoire via `move_attachments_from`.

---

## 4. Gestion des fichiers utilisateurs

### 4.1 Modèle et stockage

- **Entité :** `Paheko\Entities\Files\File` (table `files`). Champs principaux : `path`, `parent`, `name`, `type` (fichier/dossier), `mime`, `size`, `modified`, `image`, `md5`, `hash_id`, `trash`.
- **Contextes** (`File::CONTEXTS_NAMES`) : `documents`, `user`, `transaction`, `config`, `web`, `modules`, `trash`, `versions`, `attachments`, `ext` (extensions : plugins + modules).
- **Stockage physique :** délégué à un backend (`Files::callStorage()`) configurable (`FILE_STORAGE_BACKEND`, `FILE_STORAGE_CONFIG`), avec quota optionnel (`FILE_STORAGE_QUOTA`). Méthodes type : `storePath`, `storeContent`, `storePointer`, `getLocalFilePath`, `getReadOnlyPointer`, `delete`, `rename`, etc.

### 4.2 Permissions

- **Matrice par contexte :** `Files::buildUserPermissions(Session)` retourne pour chaque préfixe de contexte les droits `mkdir`, `move`, `create`, `read`, `write`, `delete`, `share`, `trash`. Dépend des sections/niveaux Paheko (config, accounting, users, documents, web).
- **Fichiers utilisateur :** contexte `user/<id>/` ou `user/<id>/<champ_dynamique>/` ; la vérification fine est gérée dans `Session::checkFilePermission` et les traits de `File` (canRead, canWrite, etc.).

### 4.3 Création / upload (côté appli)

- **Upload formulaire :** `Files::upload($parent, $key, $session, $name)` ou `Files::uploadMultiple($parent, $key, $session)` (clé = input form, ex. `file`).
- **Programmatique :** `Files::createFromPath($target, $path, $session)`, `createFromString($target, $content, $session)`, `createFromPointer($target, $pointer, $session)` ; en interne `Files::create()` puis `$file->store($source)`.
- **Répertoires :** `Files::mkdir($path, $create_parent, $throw_on_conflict)`.
- **Quota :** `Files::checkQuota($size)` avant création ; désactivable temporairement (`disableQuota`).

### 4.4 Versions, corbeille, recherche

- **Versions :** contexte `versions/` ; politique configurable (`FILE_VERSIONING_POLICY`), création automatique avant écrasement pour certains contextes (`VERSIONED_CONTEXTS`).
- **Corbeille :** déplacement vers `trash/<hash>/` + champ `trash` ; `restoreFromTrash()`.
- **Recherche plein texte :** table FTS `files_search` ; `Files::search($search, $path)` ; indexation via `File::indexForSearch()` (texte, conversion doc si dispo).

### 4.5 WebDAV et WOPI

- **WebDAV :** base URI `/dav/` ; `Paheko\Files\WebDAV\Server::route($uri)` avec storage `Paheko\Files\WebDAV\Storage` (mappe vers les contextes fichiers et permissions Session). Authentification possible par cookie dédié (`Paheko\Files\WebDAV\Session`). Permet création/suppression/renommage de fichiers et dossiers selon les droits.
- **WOPI :** intégration pour édition en ligne (Collabora, etc.) ; URLs et propriétés WOPI sur les fichiers.

### 4.6 Pièces jointes “web” et écritures

- **Pages web :** répertoire par page ; upload via `_attach.php` dans ce répertoire.
- **Écritures comptables :** répertoire `transaction/<id>/` ; liaison en base ; possibilité de déplacer un dossier entier vers ce répertoire via l'API (`move_attachments_from`).

---

## 5. Synthèse pour l'intégration RecyClique

| Besoin                          | Disponible aujourd'hui | Recommandation |
|---------------------------------|-------------------------|----------------|
| Extension métier (caisse, recyclage) | Plugins (PHP, signaux, storage dédié) | Créer un plugin Paheko dédié ; utiliser signaux si besoin de couplage avec fichiers/compta/web |
| API REST (membres, compta, etc.) | Oui, sous `/api`, credentials + niveaux | Utiliser l'API existante ; ajouter des credentials dédiés RecyClique |
| Upload de fichiers par API      | Non (sauf imports CSV et `move_attachments_from`) | Ajouter un endpoint (plugin ou core) type `POST /api/files/upload` avec parent et flux, en s'appuyant sur `Files::createFromPointer` / `createFromPath` et permissions par contexte |
| Référencement de fichiers (lien vers un fichier existant) | `web/attachment/<uri>`, ou association transaction via répertoire | Exposer en API un “get file by path/id” si besoin (sinon WebDAV ou partage existant) |
| Gestion documentaire (arborescence, partage) | Contextes documents/user/transaction/web, WebDAV, partage (liens `s`) | Réutiliser le modèle fichiers + WebDAV ; éventuellement plugin pour règles métier spécifiques |

### Fichiers clés à garder en tête

- **Extensions :** `Extensions.php`, `Plugins.php`, `Entities/Plugin.php`, `Entities/Module.php`, `Entities/Extension.php` ; admin `config/ext/*`.
- **API :** `API.php`, `API_Credentials.php`, `Web/Router.php` (ligne ~147–148) ; config `admin/config/advanced/api.php`.
- **Fichiers :** `Files/Files.php`, `Entities/Files/File.php` ; upload `admin/common/files/upload.php` ; WebDAV `Files/WebDAV/Server.php`, `Storage.php`.

---

## Addendum — Mise à jour repo et module « Saisie au poids » (2026-02-25)

**Changement de structure du dépôt :** le clone actuel n'a plus de dossier `src/`. Les chemins sont à la racine de `repo/` : `include/` (lib, init, migrations), `www/` (entrée web, admin), `modules/` (modules fournis en dist). La logique (Router, API, Extensions, Fichiers) est inchangée ; seuls les chemins relatifs diffèrent. **Aucun besoin de refaire une analyse brownfield complète.**

### Module natif « Saisie au poids »

- **Nom technique :** `saisie_poids` (répertoire `repo/modules/saisie_poids/`).
- **Type :** **module** Paheko (Brindille / UserTemplate), pas un plugin. Fourni en dist avec le core.
- **module.ini :**  
  `name="Saisie au poids"`  
  `description="Pour enregistrer rapidement le poids des dons reçus, ventes effectuées, etc. Fournit également des statistiques par période. Utile notamment pour les ressourceries et les ateliers vélos en convention avec Ecologic."`  
  `home_button=true`, `menu=true`, `restrict_section="users"`, `restrict_level="write"`.
- **Fonctionnalités :**
  - Saisie **entrées** et **sorties** avec : type d'objet, poids unitaire (kg), quantité, poids total, catégorie (provenance ou motif de sortie), flag Ecologic.
  - Données persistées via `{{:save}}` Brindille avec schémas JSON (`entry.schema.json`, `exit.schema.json`, `object.schema.json`, `category.schema.json`).
  - **Statistiques** par période (`stats.html`).
  - **Historique** des saisies (`history.html`).
  - **Synchronisation avec d'autres extensions** (`sync.html`) : import des poids depuis une extension (ex. stock vélos) vers Saisie au poids — champs `poids`, `source`, `raison_sortie`, etc. Requêtes SQL dans les templates pour mapper entrées/sorties.
  - **Configuration** : association des provenances / motifs de sortie / catégories entre l'extension (ex. atelier vélo) et Saisie au poids (`config.html`).
- **Fichiers principaux :** `index.html` (formulaire de saisie), `_init.tpl`, `_nav.html`, `table.js` (calcul poids total, lignes dynamiques), `defaults.json` (poids par défaut par type d'objet), schémas JSON, `config/` (list, edit, delete des configs).
- **Intégration RecyClique :** ce module correspond exactement au besoin « saisie au poids » pour ressourceries / Ecologic. On peut l'activer tel quel, le personnaliser (objets, catégories, defaults), ou s'en inspirer pour un module/plugin dédié si les conventions Ecologic ou les flux diffèrent.

**Suite (decisions 2e passe, architecture push)** : pour le plugin PHP custom (push caisse, syncAccounting), la vision RecyClique (offline, decla eco-organismes) et la confrontation a venir avec l'analyste, voir [artefact 2026-02-25_04](../artefacts/2026-02-25_04_analyse-plugins-caisse-decisions-push.md).


---

*Document généré dans le cadre du workflow document-project (analyse brownfield ciblée Paheko).*
