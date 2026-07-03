# 0A-PEINTRE — Ancrage code réel & points d'injection (vérité terrain)

> **But** : relier chaque spec à l'état **réel** du runtime (extraction `src/runtime`, `src/registry`, `src/types`, `src/app/PageRenderer.tsx`). Confirme les points d'injection exacts pour Cursor. **Bonne nouvelle** : le runtime est sain, minimal et déjà aligné sur l'agnosticité ; v0.1 *étend* proprement, ne réécrit pas.

## 1. Ce que le runtime fait déjà bien (à préserver tel quel)

| Fichier | Constat | Conséquence pour v0.1 |
|---------|---------|-----------------------|
| `types/page-manifest.ts` | `PageManifest`/`PageSlotPlacement` **minimaux et propres** (Story 3.0). `widgetProps` plat JSON. | Point d'attache du profil `presentation` = ajouter un champ optionnel sur `PageSlotPlacement` et `PageManifest`. Pas de refonte. |
| `types/user-runtime-prefs.ts` | `UserRuntimePrefs` **explicitement non-métier**, commentaire : *« ne doit jamais devenir une seconde source de vérité pour permissions ou navigation »* + `normalizeUserRuntimePrefs` tolérant. | **Valide le modèle 04A** : les prefs user d'affichage vivent ici légitimement. Le merge tolérant est déjà le bon pattern. |
| `runtime/resolve-page-access.ts` | Autorité AR39 **pure** ; commentaire : *« Aucun paramètre UserRuntimePrefs : les prefs UI ne participent pas à la garde page »*. | **Valide l'invariant 04A §4** : le user surcharge la présentation, jamais l'accès. Frontière déjà codée. |
| `registry/widget-registry.ts` | `resolveWidget` propre, agnostique, fallback `UNKNOWN_WIDGET_TYPE`. | Point d'injection `PresentationSurface` = autour du `Component` résolu. Pas de changement du registry. |
| `registry/shell-slot-regions.ts` | `mapSlotIdToShellRegion` **pure**, régions `['header','nav','main','aside','footer']`, fallback `unmapped→main`. | **Embryon exact du LayoutResolver.** À généraliser, pas dupliquer. |
| `app/PageRenderer.tsx` | `buildPageManifestRegions` **pure**, bucketing par région, `wrapUnmappedSlotContent` (hook présentationnel déjà présent), fallbacks instrumentés (`reportRuntimeFallback`). | Point d'injection central du LayoutResolver + `PresentationSurface`. |
| `types/navigation-manifest.ts` | `NavigationEntry` distingue déjà `routeKey` (stable) vs `path` (présentation), visibilité déclarative. | Routage déclaratif 05 : ajouter `aliases[]`/`pathPattern`, le reste existe. |

## 2. Points d'injection exacts (où Cursor touche)

### 2.1 Profil `presentation` sur le type (A-3)
`types/page-manifest.ts` — ajout **optionnel, rétrocompatible** :
```ts
export interface PageSlotPlacement {
  readonly slotId: string;
  readonly widgetType: string;
  readonly widgetProps?: PageWidgetProps;
  readonly presentation?: PresentationProfile;   // ← NOUVEAU (04 / 04A / 04B), optionnel
}
export interface PageManifest {
  // … existant inchangé …
  readonly presentation?: PresentationProfile;    // ← NOUVEAU : profil de page (défaut local)
}
```
Rétrocompat : un manifest sans `presentation` se résout via le **défaut moteur** (couche 0, `04A`). Zéro casse des manifests Story 3.x.

### 2.2 `PresentationSurface` dans le rendu (A-4)
`app/PageRenderer.tsx` → `renderPlacements`, ligne actuelle :
```tsx
return <C key={…} widgetProps={p.widgetProps} />;
```
devient :
```tsx
return (
  <PresentationSurface key={…} presentation={resolved.presentationFor(p)}>
    <C widgetProps={p.widgetProps} />
  </PresentationSurface>
);
```
`PresentationSurface` est **moteur**, agnostique : il applique `emphasis`/`elevation`/`density` via tokens (`03`). Le widget n'a pas à lire `presentation`.

### 2.3 LayoutResolver enveloppe `buildPageManifestRegions` (B-1)
Aujourd'hui `buildPageManifestRegions(page, options)` bucketise par `mapSlotIdToShellRegion(slotId)`.
v0.1 : le **LayoutResolver** calcule en amont un `ResolvedLayout` (merge couches `04A` → arbitre inerte → adaptation support `04B`), puis `buildPageManifestRegions` consomme ce résultat :
- le bucket d'un slot vient de `presentation.region` **si présent**, sinon `mapSlotIdToShellRegion(slotId)` (compat) ;
- l'ordre, le `collapse` (drawer/accordion/hide) et le placement adaptatif viennent du resolver ;
- `wrapUnmappedSlotContent` (déjà là) devient un cas particulier du placement adaptatif.

### 2.4 Régions : géométrie variable via templates (révisé)
`shell-slot-regions.ts` expose aujourd'hui `['header','nav','main','aside','footer']` **en constante**. v0.1 ne fige plus ce nombre : la liste devient un **LayoutTemplate déclaré en CREOS** (`04C`). `mapSlotIdToShellRegion(slotId)` → `mapSlotToRegion(slotId, template)`. Le template `standard-5` reproduit exactement les 5 zones actuelles (zéro régression), mais le moteur devient **template-agnostique** (1, 5 ou N régions selon le template). `hero`/`toolbar`/`body` restent des **rôles de présentation** résolus dans une région — commodité, plus contrainte. Les **overlays** (raccourcis clavier, onboarding, modales) sont une **strate au-dessus** du template (`OverlayHost`), pas des régions. Détail : `04C`.

### 2.5 Merge des prefs (A-5)
Réutiliser le pattern `normalizeUserRuntimePrefs` (tolérant, ignore l'inconnu) pour le merge `défaut→app→user` du profil de composition. Étendre `UserRuntimePrefs` avec un champ `composition?` (overrides user persistés) **sans** y mettre quoi que ce soit de métier (respecter le contrat du fichier).

### 2.6 Garde AR39 inchangée
`resolvePageAccess` **ne bouge pas**. Le LayoutResolver s'exécute **après** la garde d'accès (page autorisée) et n'a aucun pouvoir sur l'accès. L'invariant 04A §4 = « le profil effectif ne peut pas exposer un slot que l'envelope n'autorise pas » se vérifie en intersectant avec les marqueurs déjà résolus (`resolve-context-markers.ts`).

## 3. Fichiers runtime à connaître (contexte pour Cursor)

- `filter-navigation-for-context.ts`, `resolve-context-markers.ts`, `context-envelope-freshness.ts` : chaîne de visibilité/fraîcheur AR39 — **à ne pas dupliquer** dans le resolver.
- **`validation/` (chaîne lue et confirmée)** : `parsePageManifestJson` (`page-manifest-ingest.ts`) lit déjà des champs **optionnels** (`widgetProps`, `requiredPermissionKeys`, `requiresSite`) selon le pattern « si défini → valide, sinon ignore » → ajouter `presentation` = dupliquer le bloc `widgetProps` (greffe triviale, rétrocompat prouvée car les champs inconnus sont ignorés). `deepMapKeysToCamelCase` (`key-normalize.ts`) gère le snake_case CREOS. `validateManifestBundle` (`validate-bundle-rules.ts`) est une suite de règles **indépendantes et additives** → règles `layout_template`/`overlay` ajoutables en fin sans toucher l'ordre. `defaultAllowedWidgetTypeSet` (`allowed-widget-types.ts`) **dérive du registre** → un widget d'overlay enregistré normalement est auto-autorisé. Bonus : `NavigationEntry.shortcutId` existe déjà (collision détectée) = socle du pilote raccourcis.
- `conceptual-artifacts.ts` confirme l'AR39 noir sur blanc : `UserRuntimePrefs` = « dernier maillon : présentation locale uniquement » → valide la place des prefs user dans `04A`.
- `report-runtime-fallback.ts` : canal d'instrumentation du mode dégradé — **réutiliser** pour les fallbacks présentation (profil invalide, support indétectable, template absent).
- **`app/templates/transverse/` (lu et confirmé)** : embryon de résolution présentationnelle, dans le bon esprit (commentaires : *« pas de nouvelle vérité navigation ; uniquement du gabarit CSS »*, *« contenu métier injecté via PageManifest → registre »*). **Mais à la fois à généraliser ET à nettoyer** :
  - `resolveTransverseMainLayoutMode(pageKey)` choisit le gabarit (`hub`/`consultation`) par **cascade de `if (pageKey === 'transverse-…')` codée en dur** → c'est l'anti-pattern que le LayoutResolver élimine : le mode de layout doit être une **donnée du PageManifest/LayoutTemplate** (`04C`), pas une liste de chaînes dans le code.
  - `TransverseHubLayout` fait déjà un **réarrangement adaptatif primitif** (grille 2 colonnes, dernière carte pleine largeur sur ligne impaire, cas mono-enfant) → à **généraliser** dans l'adaptation support (`04B`) au lieu d'être codé par famille.
  - Bon point : `data-transverse-layout`/`data-transverse-family` (testids) → la migration peut préserver ces ancres de test pour prouver la parité.
  → **Conclusion** : transverse n'est pas qu'un modèle à imiter ; c'est aussi une **cible de rapatriement** (au même titre que les surcouches caisse, en plus propre). À traiter dans l'Épic B (LayoutResolver) + C (portage).
- `context-presentation-keys.ts`, `nav-label-presentation-fallbacks.ts`, `resolve-nav-entry-display-label.ts`, `prune-navigation-for-live-toolbar.ts`, `toolbar-selection-for-live-path.ts` : **traces de présentation déjà éparpillées** dans le runtime → candidats à rapatrier sous le profil `presentation` (dette à tracker, lien `01` §4 et bandeau-live).

## 4. Réévaluation des specs à la lumière du code

| Spec | Ajustement post-code |
|------|----------------------|
| `03` tokens | inchangé ; confirmer que `data-pn-density` se branche sur `uiDensity` existant (déjà typé) |
| `04` profil | s'attache sur `PageSlotPlacement.presentation` + `PageManifest.presentation` (types réels ci-dessus) |
| `04A` autorité | **renforcé** : `resolve-page-access` + `UserRuntimePrefs` prouvent la frontière ; merge calqué sur `normalizeUserRuntimePrefs` |
| `04B` support | régions limitées à 5 (shell réel) ; `hero/toolbar` = rôles de présentation, pas régions |
| `05` resolver | enveloppe `buildPageManifestRegions` (pas réécriture) ; routage ajoute `aliases[]` à `NavigationEntry` existant |

## 5. Confirmation d'agnosticité du runtime actuel

Le runtime extrait **ne contient aucune couleur ni route métier** : ces saletés sont **concentrées dans `RuntimeDemoApp.tsx`** (couche démo/app), pas dans `runtime/`/`registry/`/`types/`. → L'agnosticité du *moteur* est déjà presque tenue ; le chantier v0.1 consiste surtout à (a) enrichir le langage (tokens+profil), (b) sortir les saletés de `RuntimeDemoApp` vers des manifests/theme CREOS (Tour 2), (c) généraliser `mapSlotIdToShellRegion` en LayoutResolver. C'est moins lourd que craint.
