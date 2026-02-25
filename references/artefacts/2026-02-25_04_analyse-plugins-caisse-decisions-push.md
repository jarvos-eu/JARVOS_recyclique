# Analyse plugins Paheko, décisions push et vision RecyClique

**Date :** 2026-02-25  
**Contexte :** 2e passe spirale (recherches Perplexity API caisse, saisie au poids, auth/SSO ; analyse code plugins ; décisions architecture).  
**Usage :** Référence pour le plugin Paheko à créer, la sync RecyClique → Paheko, et la confrontation à venir avec l'analyste.

---

## 1. Vision RecyClique et confrontation à venir

### 1.1 Intentions et besoins

- **RecyClique** : web app avec **catégories, sous-catégories**, etc. ; objectif **module de déclaration automatique aux éco-organismes** (ex. Ecologic). Le module Paheko Saisie au poids intègre déjà une partie de ce besoin (flag Ecologic, sorties/entrées pondérées) ; l'intention est d'**aller beaucoup plus loin** tout en restant en **parfaite cohérence** (données, sécurité).
- **Fonctionnement cible** : RecyClique permet de **saisir la caisse même en cas de coupure internet** ; au retour du réseau, **synchronisation avec le back-end** ; avec la nouvelle installation Paheko, le **plugin à créer** doit faire **au fur et à mesure** les synchronisations vers Paheko : **caisse**, **poids**, **catégories**, etc.
- **Décision à prendre plus tard** : **confronter** les capacités de RecyClique + les besoins à venir avec les capacités actuelles de Paheko (core + plugin Caisse + module Saisie au poids) pour une **décision claire** (périmètre, qui fait quoi, mapping catégories, sécurité). Cette confrontation n'est pas faite maintenant ; elle est **documentée comme étape ultérieure** de conception.

### 1.2 Précision importante

Les éléments ci-dessus reflètent l'**intention et les hypothèses actuelles**. Les modalités techniques et les bons choix de conception devront être **tranchés avec l'analyste** en phase de réflexion avancée — rien n'est figé.

---

## 2. Plugin Caisse — ce qui a été lu

- **Tables** : préfixe `plugin_caisse_` (sessions, sessions_balances, tabs, tabs_items, tabs_payments, categories, products, methods, locations, etc.) ; montants en **centimes**.
- **Écritures comptables** : créées par **syncAccounting** (POS::syncAccounting), **pas** à la fermeture de session. Déclenchement manuel ou par le plugin après insertion des données.
- **Plugin PHP** : le répertoire **public/** expose des routes HTTP ; ex. `POST /p/recyclique/api.php` pour recevoir le push RecyClique, écrire en base puis appeler syncAccounting.
- **Source** : dépôt paheko-plugins (Fossil / archive distribution), dossier `caisse/`.

---

## 3. Module Saisie au poids — ce qui a été lu

- **Nature** : **module Brindille** (pas plugin PHP). Nom technique **saisie_poids**. Emplacement : **repo/modules/saisie_poids/**.
- **Contenu** : saisie entrées/sorties avec poids unitaire (kg), quantité, poids total ; **catégories** ; **flag Ecologic** (LIV, PRE, DEC_REE, etc.) ; stats par période ; historique ; **synchronisation** avec d'autres extensions (Caisse, atelier vélos) pour importer les poids.
- **Fichiers** : module.ini, templates Brindille (index.html, stats.html, history.html, sync.html, config.html), table.js, schémas JSON (entry, exit, object, category), defaults.json.
- **Stockage** : table **module_data_saisie_poids** (documents JSON) ; config dans le module (mapping caisse_exit, velos_entry, velos_exit).
- **Sync depuis la Caisse** : page sync.html lit les sessions clôturées (plugin_pos_sessions / plugin_caisse_* selon préfixe), joint tabs, tabs_items (avec weight), products, categories ; filtre par **config caisse_exit** (catégorie caisse → motif de sortie saisie au poids) ; enregistre des **sorties** avec **pos_session_id** pour éviter doublons. Déclenchement **manuel** (admin ouvre la page Sync).
- **Config** (config.html) : mapping « catégorie de produit caisse » → « motif de sortie » saisie au poids ; idem pour vélos si extension activée.
- **Utilisation** : activer le module tel quel, configurer les mappings ; sync manuelle après chaque push caisse. **Automatisation** possible en v0.2 en réimplémentant la logique de sync dans le plugin PHP recyclique (écriture directe dans module_data_saisie_poids après push caisse).

---

## 4. Brindille vs Plugin PHP

- **Module Brindille** : ne peut pas écrire dans plugin_caisse_* ni exposer de route HTTP entrante.
- **Plugin PHP** : peut exécuter du PHP, lire/écrire toute table, exposer des routes via **public/** (tout fichier PHP dans public/ est accessible à `https://paheko.tld/p/<nom-plugin>/<fichier>.php`).

---

## 5. Architecture push (décision 2e passe)

```
RecyClique (frontend, éventuellement offline)
    → sync quand en ligne
FastAPI (back-end)
    → POST /p/recyclique/api.php (plugin PHP custom)
Paheko — plugin écrit dans plugin_caisse_* puis appelle POS::syncAccounting()
    → lectures ultérieures : /api/sql, déclarations, etc.
```

Push **par ticket** au fil de l'eau ; file d'attente **Redis Streams** côté FastAPI (résilience). Clôture = syncAccounting + contrôle totaux. Paheko = source de vérité compta. Pas d'écriture directe RecyClique → BDD Paheko ; pas de modification du core Paheko.

---

## 6. Docker

- Image basée sur archive distribution Fossil (ex. paheko-1.3.19.tar.gz).
- Plugin RecyClique copié dans data/plugins/recyclique (versionné dans le repo projet). Activation une fois via UI ou script CLI.

---

## 7. Odoo vs Paheko

- Décision de **rester sur Paheko** (recherche Perplexity) ; cohérence écosystème JARVOS ; dette maîtrisable par l'architecture push.

---

*Artefact produit dans le cadre du plan de mise à jour 2e passe (session migration Paheko).*
