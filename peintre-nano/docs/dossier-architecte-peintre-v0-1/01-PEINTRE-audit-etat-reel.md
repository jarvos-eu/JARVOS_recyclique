# 01-PEINTRE — Audit de l'état réel

> **Méthode** : analyse du code source réel (`RuntimeDemoApp.tsx`, `src/domains/**`, `src/styles/tokens.css`) + docs runtime du snapshot documentaire. **Limite** : le runtime/registry/types/templates n'étaient pas dans l'export code — à reconfirmer sur le repo vivant (voir §6).

## 1. Ce qui marche (à préserver)

- **Pipeline conceptuel sain** : `manifests → validation → résolution → rendu shell/slots/widgets`. La doctrine « moteur ≠ métier » est documentée et juste (`peintre-nano/docs/02-architecture-runtime.md`).
- **AR39 respecté côté données** : `OpenAPI > ContextEnvelope > NavigationManifest > PageManifest > UserRuntimePrefs`. Les widgets consomment des `operation_id` contractuels, pas de schémas réinventés.
- **Liaison Recyclique→Peintre opérationnelle** : tout s'affiche au bon endroit. **Le problème n'est PAS la plomberie.**
- **Le pilote bandeau-live est un bon citoyen** : `BandeauLive.module.css` consomme sagement les tokens `--pn-*`. C'est la preuve que la discipline est possible — elle manque juste d'outils (voir §3).

## 2. Cause racine n°1 — `tokens.css` squelettique

État réel mesuré de `src/styles/tokens.css` :

| Catégorie | Tokens présents | Manquant critique |
|-----------|-----------------|-------------------|
| Couleurs | 6 (`bg`, `surface`, `text`, `text-muted`, `accent`, `border`) | **Aucune couleur sémantique** (success / warning / danger / info), aucune nuance (50→900), aucun état (hover/active) |
| Espacement | 5 (`xs`→`xl`) | Échelle incomplète, pas de densité |
| Rayons | 2 (`sm`, `md`) | pas de `lg`/`full` |
| Typo | 1 taille (`sm`) + 2 familles | **Aucune échelle typographique** (h1→h6, body, caption), aucun line-height, aucun poids nommé |
| Élévation | **0** | **Aucune ombre** → tout est plat, sans profondeur |
| Densité | **0** | Aucun token de densité malgré un toggle `uiDensity` dans le runtime |
| Breakpoints | **0** | Aucune intention responsive |
| Intention | **0** | Aucun `emphasis` (primary/secondary/muted) |

**Conséquence directe** : un widget qui veut du « joli » n'a aucun outil → il code en dur ou pioche dans Mantine. C'est exactement ce qu'on observe (§3).

## 3. Preuves chiffrées du contournement du système

Mesures `grep` sur `src/**` :

- **`--pn-color-accent` : utilisé 1 seule fois.** `--pn-radius-md` : 3 fois. Les tokens existent mais sont quasi morts.
- **105 couleurs en dur** (hex / `rgb()`) dans les CSS modules, contre ~85 usages de tokens couleur. **Plus de la moitié des couleurs échappent au système.**
- **7 fichiers CSS fuient des `--mantine-*`** directement (`KpiLiveStrip.module.css` mélange `--pn-*` et `--mantine-color-dark-7`, `--mantine-spacing-sm`…). → **double système de tokens non réconcilié.**
- **Token fantôme** : `CaisseBrownfieldDashboardWidget.module.css` invente `--color-border-subtle` (absent de `tokens.css`) avec fallback inline `rgba(0,0,0,0.08)`. Incohérence inter-fichiers.
- **`KpiLiveStrip` code des valeurs magiques** : `10px`, `minmax(118px,1fr)`, `rgb(46 125 50 / 22%)`, gradients `linear-gradient(135deg, …)`. Dès qu'un écran doit être « convaincant », il sort du système.

**Lecture** : le système de tokens n'est pas violé par négligence — il est violé par **insuffisance**. La spec `03` corrige la cause, pas le symptôme.

## 4. Cause racine n°2 — l'égout d'alias legacy dans le runtime

`src/app/demo/RuntimeDemoApp.tsx` (886 lignes) concentre l'anti-pattern qui **bloque l'extractibilité** :

- **~15 constantes de chemins legacy codées en dur** (`CASH_REGISTER_SALE_PATH`, `…_VIRTUAL_SALE_PATH`, `…_DEFERRED_SESSION_OPEN_PATH`, `…_SESSION_CLOSE_PATH`…) + ~8 fonctions de détection (`isCashRegisterSaleKioskPath`, `isCashflowNominalCertificationPathRoute`…).
- **`syncSelectionFromPath` = routeur manuel** : cascade de ~20 `if (pathForMatch === '/admin/...')` qui réécrit à la main la sélection nav. **Cette information devrait être dérivée du `NavigationManifest`**, pas recodée.
- **5 surcouches présentationnelles fusionnées au runtime** : `withCashflowNominalSessionOpenPresentation`, `…SessionClose…`, `…CaisseHub…`, `…KioskSaleDashboard…`, `…KioskSaleWizard…`. Chacune patche des `widgetProps` (`presentation_surface`, `workspace_heading`, `hide_register_selection_row`…) **dans le shell générique**.
- **`presentation_surface` n'est lu que par 2 fichiers** alors qu'il est produit par 5 surcouches → le « contrat de présentation » actuel est un bricolage `widgetProps` ad hoc, **pas une grammaire**.
- **Logique métier de suppression dans le shell** : `suppressCashflowNominalWorkspaceSaleAndAside` filtre des slots selon le path. Le shell « générique » décide d'affichage métier.

**Diagnostic** : la présentation est décidée par du `if/else` applicatif dans le moteur. C'est précisément ce que `docs/05-monorepo-et-extraction.md` interdit (« ne pas coder les règles métier Recyclique dans le shell générique »). La violation est massive et concentrée.

**4bis — Variante plus propre mais même maladie : `app/templates/transverse/`** *(confirmé sur le code)*. `resolveTransverseMainLayoutMode(pageKey)` sélectionne le gabarit (`hub`/`consultation`) par une **cascade de `if (pageKey === 'transverse-…')` codée en dur**, et `TransverseHubLayout` code la **géométrie en dur** (grille 2 colonnes, ligne impaire pleine largeur). C'est mieux que les surcouches caisse (la discipline « gabarit CSS, pas de métier » est respectée), mais le **mode de layout et la géométrie devraient être des données** (PageManifest/LayoutTemplate, `04C`), pas du code. → cible de rapatriement de l'Épic B/C, pas seulement modèle à imiter. Bon point à préserver : les testids `data-transverse-layout`/`-family` servent de filet de parité à la migration.

## 5. Cause racine n°3 — widgets monolithiques (métier + présentation + données fusionnés)

Tailles réelles (lignes) :

| Fichier | Lignes |
|---------|--------|
| `AdminCategoriesWidget.tsx` | 2342 |
| `CashflowNominalWizard.tsx` | 2033 |
| `AdminUsersWidget.tsx` | 1864 |
| `ReceptionNominalWizard.tsx` | 1464 |
| `CaisseBrownfieldDashboardWidget.tsx` | 1203 |

Un widget de 2000+ lignes mélange fetch, logique métier, état, **et** présentation. Impossible d'y appliquer une couche présentation cohérente, impossible d'extraire le moteur sans charrier le métier. Ces widgets restent **applicatifs** (côté Recyclique, c'est normal) — mais la **présentation** doit en être extraite vers le langage déclaratif (`04`).

## 6. Zones reconfirmées sur le code réel (extraction runtime reçue)

L'extraction `src/runtime` + `src/registry` + `src/types` + `PageRenderer.tsx` a **confirmé et nuancé** le diagnostic (détail complet : `0A-PEINTRE-ancrage-code-reel.md`). Synthèse :

- **Le *moteur* est sain et déjà quasi-agnostique.** `runtime/`, `registry/`, `types/` ne contiennent **aucune couleur ni route métier**. `resolve-page-access.ts` documente même la frontière (« les prefs UI ne participent pas à la garde page »). `mapSlotIdToShellRegion` et `buildPageManifestRegions` sont purs.
- **Les saletés sont concentrées dans `RuntimeDemoApp.tsx`** (couche démo/app), pas dans le moteur. → Le rapatriement (Tour 2) est **plus localisé** que craint : sortir les alias/surcouches de `RuntimeDemoApp` vers manifests + theme CREOS, sans toucher au cœur.
- **Les types sont minimaux (Story 3.0)** → le profil `presentation` s'ajoute en champ **optionnel rétrocompatible**, zéro casse.
- **Traces de présentation déjà éparpillées dans le runtime** (`context-presentation-keys.ts`, `nav-label-presentation-fallbacks.ts`, `prune-navigation-for-live-toolbar.ts`…) → candidates à rapatrier sous le profil `presentation` (dette tracée).

**Conséquence sur l'effort** : le chantier v0.1 est davantage un **enrichissement du langage + généralisation d'embryons existants** qu'une réécriture. Bon signe.

## 7. Synthèse : 3 causes, 1 fondation

| Cause | Symptôme visible | Corrigé par |
|-------|------------------|-------------|
| Tokens squelettiques | Rendu plat, sans profondeur | `03` design tokens |
| Pas de grammaire de présentation | `widgetProps` ad hoc, surcouches runtime | `04` profil CREOS presentation |
| Alias legacy dans le shell | Extractibilité bloquée, shell pollué | `05` LayoutResolver |
| Widgets monolithiques | Présentation noyée dans le métier | `04` + `06` Épic B |

La fondation commune des trois : **rendre la présentation déclarative et la sortir du code impératif.** C'est le cœur de Peintre v0.1.
