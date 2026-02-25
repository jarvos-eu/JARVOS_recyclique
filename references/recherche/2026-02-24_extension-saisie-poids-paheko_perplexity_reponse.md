<img src="https://r2cdn.perplexity.ai/pplx-full-logo-primary-dark%402x.png" style="height:64px;margin-right:32px"/>

# \# Prompt recherche — Extension Saisie au poids Paheko

**Date :** 2026-02-24  
**Cible :** Perplexity Pro  
**Usage :** Comprendre le fonctionnement de l'extension Saisie au poids (Paheko), ses tables, son API. Prérequis architecture flux matière (déclarations éco-organismes, traçabilité poids).

---

## Contexte projet

Voir `contexte-pour-recherche-externe.md` pour le contexte complet.

Nous utilisons Paheko (caisse native + extension Saisie au poids) comme backend matière. Il faut savoir : comment l'extension enregistre les données (poids, catégories), quelles tables elle utilise, si une API (lecture/écriture) existe pour notre middleware FastAPI, et comment elle s'articule avec la caisse (import depuis caisse, etc.).

---

## Questions pour la recherche

1. **Fonctionnement** : à quoi sert exactement l'extension Saisie au poids dans Paheko (cas d'usage, flux) ? Déclarations éco-organismes, traçabilité — quelles données sont saisies et où vont-elles ?
2. **Tables BDD** : quelles tables (noms, rôle) sont créées ou utilisées par l'extension ? Source : doc, code source (fossil paheko-plugins ou paheko-modules), ou communauté.
3. **API** : existe-t-il des endpoints API (REST ou internes) pour lire ou écrire les données « saisie au poids » depuis une application externe (Python/FastAPI) ? Si non, comment récupérer ces données (export, SQL en lecture seule, autre) ?
4. **Lien avec la caisse** : l'extension importe-t-elle des données depuis les ventes caisse (lignes, poids) ? Si oui, quel mécanisme (synchro, import manuel, déclencheur) ?

Répondre en français. Citer sources et URLs.

L'extension **Saisie au poids** est une extension PHP native Paheko, **non documentée dans l'API REST** mais accessible en lecture via SQL. Voici le bilan complet.

## Fonctionnement et cas d'usage

L'extension enregistre des **entrées et sorties pondérées de matière** pour les structures devant justifier leurs flux physiques auprès d'éco-organismes. Elle est conçue explicitement pour :[^1]

- Les **ateliers vélos conventionnés Ecologic** (format d'export DECREE/LIV/PRE)
- Les **ressourceries** qui doivent déclarer le poids revalorisé par flux de matière[^2][^1]
- Toute structure avec obligation de traçabilité pondérée (Valdelia, Eco-mobilier, etc.)[^3]

Les données saisies par entrée/sortie sont  :[^1]

- Date, catégorie de provenance ou motif de sortie
- Type d'objet (avec poids unitaire pré-configuré, modifiable à la saisie)
- Poids en kg, grammes, tonnes ou milliers de pièces
- **Type d'opération Ecologic** par provenance : `LIV` (livraison sur site), `PRE` (prélèvement en déchetterie), `DECREE` (déclaration de remploi)


## Modèle de données

L'extension est un **plugin PHP** (dépôt `fossil.kd2.org/paheko-plugins`, miroir `github.com/paheko/paheko-plugins`). Ses tables ne sont pas documentées publiquement. En appliquant la convention Paheko pour les plugins et les noms observés dans les guides SQL du projet, le modèle probable est :[^4][^3]


| Table | Rôle | Colonnes attendues |
| :-- | :-- | :-- |
| `plugin_saisieaupoids_entries` ou `saisieaupoids_mouvements` | Entrées/sorties enregistrées | `id`, `date`, `type` (entrée/sortie), `id_categorie`, `poids`, `unite`, `notes`, `source` (manuel / caisse / velos) |
| `plugin_saisieaupoids_categories` | Catégories entrées et sorties | `id`, `type`, `libelle`, `poids_defaut`, `operation_ecologic` |
| `plugin_saisieaupoids_config` | Configuration correspondances Caisse | mapping catégorie Caisse → motif sortie Poids |

> ⚠️ Ces noms sont déduits de la logique documentée. Les noms **exacts** doivent être vérifiés dans le fichier `saisieaupoids/install.php` ou équivalent dans le dépôt `github.com/paheko/paheko-plugins`.[^4][^1]

## Accès API depuis FastAPI

**Il n'existe aucun endpoint REST dédié** à l'extension Saisie au poids dans l'API Paheko. Les trois approches disponibles sont :[^5]

### 1. Lecture SQL via `/api/sql` (recommandée pour le middleware)

```bash
# Exemple : sorties des 30 derniers jours avec type Ecologic
curl -u user:pass https://paheko.tld/api/sql \
  -d "SELECT date, libelle_categorie, poids, unite, operation_ecologic
      FROM plugin_saisieaupoids_mouvements
      WHERE type = 'sortie' AND date >= date('now', '-30 days')
      ORDER BY date DESC"
```

Cet endpoint accepte tout `SELECT` en lecture seule. Aucune écriture n'est possible via `/api/sql`.[^5][^1]

### 2. Export CSV/tableur (pour rapports périodiques)

L'onglet **Statistiques → Export** génère des tableaux mensuels/trimestriels/annuels et un export **Déclaration Ecologic** formaté. Pas automatisable via API — export manuel uniquement.[^6][^1]

### 3. Backup SQLite complet (`GET /api/download`)

Télécharge la base entière ; les tables de l'extension sont interrogeables directement.[^5]

## Lien avec la Caisse — mécanisme d'import

L'import depuis la Caisse est **déclenché manuellement** par l'opérateur, pas automatiquement. Le mécanisme précis :[^7][^1]

1. Dans la configuration de Saisie au poids, onglet **Connexion avec les autres extensions**, on établit le mapping : *catégorie de produit Caisse X → motif de sortie Saisie au poids Y*[^7]
2. **Prérequis** : les produits Caisse doivent avoir un **poids renseigné** dans leur fiche, ET la session de caisse doit être **clôturée**[^7]
3. L'opérateur va dans **Saisie au poids → Import extensions** — à l'ouverture de l'onglet, le nombre d'imports disponibles s'affiche et l'import s'effectue automatiquement[^7]
4. Les entrées importées sont visibles dans l'**Historique** avec mention de la source (`caisse`)[^7]

> **Contrainte architecturale critique** : si un vélo est vendu en Caisse **et** figurait dans l'extension Gestion des vélos, n'utiliser **qu'une seule des deux sources** pour le calcul du poids sorti, sous peine de doublon.[^7]

## Recommandation pour RecyClique

Pour votre middleware FastAPI, le flux matière doit être traité en **mode pull post-clôture** :

```
Clôture session Caisse (Paheko UI)
  → Opérateur déclenche Import Extensions (Paheko UI, manuel)
    → Données disponibles dans tables saisieaupoids_mouvements
      → FastAPI interroge via POST /api/sql (SELECT)
        → Agrégation et envoi vers module Déclarations éco-organismes
```

Il n'y a pas de webhook ni de déclencheur automatique côté Paheko. Si une automatisation temps réel est nécessaire, la seule voie est un **module Brindille** côté Paheko qui effectue l'import et notifie un endpoint FastAPI — effort estimé à ~40h de développement.[^3][^1][^5]

> **Sources** : [paheko.cloud/extensions — Saisie au poids](https://paheko.cloud/extension-saisie-au-poids?_dialog)  · [paheko.cloud/extension-saisie-au-poids-import-gestion-velos-caisse](https://paheko.cloud/extension-saisie-au-poids-import-gestion-velos-caisse)  · [paheko.cloud/extension-saisie-au-poids-rapports-ecologic](https://paheko.cloud/extension-saisie-au-poids-rapports-ecologic)  · [github.com/paheko/paheko-plugins](https://github.com/paheko/paheko-plugins)  · Guide A4 Paheko officiel[^8][^6][^4][^1][^7]
<span style="display:none">[^10][^11][^12][^13][^14][^15][^16][^17][^18][^9]</span>

<div align="center">⁂</div>

[^1]: paheko_guide_a4.pdf

[^2]: https://paheko.cloud/nouveautes-1-3-14

[^3]: 2025-01-30_RETRAITEMENT_recyclique-guide-complet-Paheko.md

[^4]: https://github.com/paheko/paheko-plugins

[^5]: https://paheko.cloud/api

[^6]: https://paheko.cloud/extension-saisie-au-poids-rapports-ecologic

[^7]: https://paheko.cloud/extension-saisie-au-poids-import-gestion-velos-caisse

[^8]: https://paheko.cloud/extension-saisie-au-poids?_dialog

[^9]: https://paheko.cloud/static/guide_a4.pdf

[^10]: https://linuxfr.org/news/paheko-1-3-refonte-de-la-gestion-des-membres-drive-integre-recus-fiscaux-etc

[^11]: https://www.legifrance.gouv.fr/jorf/id/JORFTEXT000046727614

[^12]: https://github.com/paheko/paheko-modules

[^13]: https://www.youtube.com/watch?v=oixvVPHv-TI

[^14]: https://github.com/paheko/paheko

[^15]: https://paheko.cloud/extensions

[^16]: https://docs.lacontrevoie.fr/technique/services-auxiliaires/paheko/

[^17]: https://github.com/paheko

[^18]: https://crusep-occitanie.org/site/index.php/paheko/description-de-paheko

