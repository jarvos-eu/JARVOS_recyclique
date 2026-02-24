# Brainstorm — Migration Paheko / Architecture JARVOS Recyclique

**Date :** 2026-02-24  
**Session :** Brainstorming avec Mary (analyst BMAD)  
**Agent suivant :** lire `references/ou-on-en-est.md` + `references/idees/index.md` pour reprendre.

---

## Contexte posé

- **Recyclic en production** (v1.4.4) : caisse, dépôts, flux matière. Stack : FastAPI / React-Vite-TS (PWA) / PostgreSQL / Redis / Docker Compose.
- **Paheko en production** (parallèle, indépendant) : comptabilité saisie manuellement, gestion associative native.
- **Utilisateurs Recyclic actuels** : 2 seulement (La Clique opérateur + Strophe admin). Futur : gestion users = Paheko natif.
- **Source de vérité établie** : Recyclic = flux matière (caisse, dépôts, catégories EEE) ; Paheko = flux financiers/comptabilité. Question ouverte : comment les sessions de caisse Recyclic génèrent des écritures Paheko.
- **Brownfield 1.4.4** : analyse complète disponible dans `references/ancien-repo/`.
- **Code 1.4.4** : fragile, immature. Règle d'import : copier + consolider + contrôle sécurité/qualité systématique à chaque import. Refactoring ultérieur dans le cadre modulaire.
- **Ganglion** : hors scope de ce projet. Juste l'illustration du pattern "placeholder GitHub public → Le Fil plus tard".

---

## Brainstorm brut — thèmes identifiés

### 1. Intégration Paheko (coeur)
- Dual-backend : Recyclic (FastAPI) + Paheko (PHP, moteur asso). Les deux coexistent.
- Paheko : comptabilité, gestion adhérents, communication native.
- Docker setup pour Paheko à créer.
- Modules optionnels Paheko à cataloguer et installer automatiquement.
- Interface Paheko native = accès super-admin ; nouvelles UI dans Recyclic = workflows terrain.

### 2. Système modulaire / plugin framework
- Framework plugin permettant de combiner des modules automatiquement (ex. 2 plugins Paheko + 1 module JARVOS = une config installée d'un coup).
- Module store RecyClique : modules optionnels par ressourcerie (codes-barres, imports intelligents, etc.).
- Distribution via dépôt GitHub public (placeholder pour Le Fil inter-ressourceries).
- Chantier complet : aucune solution identifiée pour l'instant. Recherche nécessaire.

### 3. Nouvelles UI pour workflows Paheko
- Depuis Recyclic : interfaces dédiées aux routines terrain utilisant Paheko.
- Paheko natif : accessible en mode super-admin.
- UI modulaire dès la conception (contrainte d'architecture, pas une feature) : future intégration JARVOS Peintre.

### 4. JARVOS Ports
- Port unique pour Nano / Mini.
- Agit aussi comme relay Peintre : connecté au service Peintre quand il existe ; à la sortie Peintre Nano/Mini en attendant.

### 5. Le Fil / placeholder GitHub
- Le Fil : réseau inter-ressourceries, vision long terme, hors scope.
- En attendant : dépôt GitHub public pour partage de ressources. Ganglion = illustration de ce pattern uniquement.

### 6. IA / LLM dans Recyclic
- Existant dans 1.4.4 : appels LLM pour classification automatique catégories EEE à l'import.
- Futur : modules intelligents (import papier, Excel, vocal, reconnaissance visuelle, etc.).
- Décision non tranchée : appels LLM hardcodés + placeholder Ganglion, OU intégration JARVOS Nano/Mini.
- Ganglion SDK (quand il existera) : LLM serving + meilleurs workflows agents par situation.

### 7. Calendrier collaboratif / espace fichiers
- Calendrier : gestion réunions, planification. Paheko a peut-être cela nativement — à vérifier avant de concevoir quoi que ce soit.
- Espace fichiers : potentiellement sous intégration JARVOS Nano.

---

## Analyse critique (Mary)

**Points forts :**
- Dual-backend pragmatique : ne pas réinventer Paheko.
- "Ports" = bonne pratique d'architecture évolutive (placeholder connecté plus tard).
- Règle copy+consolidate+security : protège contre la dette technique héritée.
- Kanban + todos + artefacts : continuité entre sessions garantie.

**Risques identifiés :**
1. Sync caisse Recyclic → Paheko comptabilité : question non résolue, prérequis critique avant tout développement financier.
2. Plugin framework : risque d'over-engineering si solution custom. Recherche obligatoire en amont.
3. LLM/IA : décision architecture non tranchée. Placeholder indispensable si hardcodé.
4. Code 1.4.4 fragile : la checklist sécurité/qualité doit être formalisée avant le premier import.

---

## Décisions posées dans cette session

| Décision | Statut |
|----------|--------|
| Garder interfaces Recyclic actuelles (copy+consolidate+security, refactor plus tard) | POSÉE |
| Gestion users → Paheko natif | POSÉE |
| Ganglion : hors scope projet | POSÉE |
| Brownfield 1.4.4 : disponible dans `references/ancien-repo/` | CONFIRMÉ |

---

## Questions ouvertes (non tranchées)

- Sync financière : modèle exact caisse Recyclic → écritures Paheko ?
- Plugin framework : quelle solution technique ?
- LLM/IA : hardcodé + placeholder Ganglion vs. intégration JARVOS Nano/Mini ?
- Paheko natif : calendrier collaboratif ? Gestion fichiers ?
- Checklist sécurité/qualité pour import code 1.4.4 : à formaliser.

---

## Idées créées dans le Kanban

| Fichier idée | Stade |
|---|---|
| `2026-02-24_integration-paheko-core.md` | a-rechercher |
| `2026-02-24_sync-financiere-caisse-paheko.md` | a-rechercher |
| `2026-02-24_plugin-framework-recyclic.md` | a-rechercher |
| `2026-02-24_nouvelles-ui-workflows-paheko.md` | a-conceptualiser |
| `2026-02-24_module-store-recyclic.md` | a-conceptualiser |
| `2026-02-24_jarvos-le-fil-placeholder-github.md` | a-conceptualiser |
| `2026-02-24_jarvos-ports-nano-mini-peintre.md` | a-creuser |
| `2026-02-24_ui-modulaire-configurable.md` | a-conceptualiser |
| `2026-02-24_ia-llm-modules-intelligents.md` | a-creuser |
| `2026-02-24_calendar-espace-fichiers-paheko.md` | a-rechercher |

## Tâches ajoutées dans todo.md

- `[ ]` Cataloguer modules Paheko optionnels disponibles dans leur écosystème
- `[ ]` Rechercher frameworks plugin Python (Pluggy, stevedore, manifeste déclaratif)
- `[ ]` Vérifier capacités natives Paheko : calendrier, fichiers, communication
- `[ ]` Cartographier sync financière : sessions de caisse Recyclic → écritures Paheko
- `[ ]` Formaliser checklist "copy+consolidate+security" pour import code depuis 1.4.4
- `[ ]` Inventorier usages LLM actuels dans Recyclic 1.4.4
- `[ ]` Définir stratégie LLM/IA : hardcodé + placeholder Ganglion vs. JARVOS Nano/Mini
