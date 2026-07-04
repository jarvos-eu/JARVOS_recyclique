# 05-PEINTRE — Spec : `LayoutResolver` (pipeline de résolution)

> **But** : remplacer les `if/else` + alias legacy de `RuntimeDemoApp.tsx` par un **pipeline de résolution déterministe** qui (1) **fusionne** les couches d'autorité (`04A`), (2) **adapte au support** (`04B`), (3) passe par le **hook d'arbitrage inerte**, (4) résout en régions + tokens. C'est le composant qui matérialise l'agnosticité et débloque l'extractibilité.
> **Embryon existant (confirmé par le code)** : `registry/shell-slot-regions.ts::mapSlotIdToShellRegion` (pure, régions `header/nav/main/aside/footer`, fallback `unmapped→main`) et `app/PageRenderer.tsx::buildPageManifestRegions` (pure, bucketing par région, hook `wrapUnmappedSlotContent` déjà présent). Le LayoutResolver **généralise et enveloppe** ces deux fonctions — il ne les réécrit pas. Points d'injection exacts : `0A-PEINTRE-ancrage-code-reel.md` §2.

## 1. Responsabilité & pipeline

```
LayoutResolver(
  pageManifest,          // structure + profil composition app (couche 1)
  engineDefaults,        // profil défaut moteur (couche 0)
  userPrefs,             // prefs user local + app/back (couche 2) — 04A §7
  contextEnvelope,       // AR39 : ce qui est autorisé/actif
  supportProfile,        // form factor / input / viewport / orientation — 04B §1
  arbiter                // CompositionArbiter — INERTE en v0.1 (04A §6)
) → ResolvedLayout
```

Étapes (ordre strict) :
```
1. MERGE AUTORITÉ (04A) : effective = merge(défaut, app, user) par champ
                          + invariants AR39/required + override_policy
                          → profil de composition effectif (+ provenance)
1bis. STEP COURANT (04D): micro-workflow orchestrator résout le step actif →
                          alimente la visibilité slots/overlays (inerte v0.1)
2. ARBITRAGE (04A §6)   : effective = arbiter.arbitrate(effective, ctx)
                          v0.1 = pass-through (ne change rien, mais EST appelé)
3. ADAPTATION SUPPORT (04B) : applique colonnes / per_support / priorité /
                          réarrangement / ergonomie tactile au profil effectif
4. RÉSOLUTION TOKENS (03) : emphasis/density/elevation → variables CSS
5. ÉMISSION : ResolvedLayout { regions, slotPlacements, densityAttr, classes }
```

`ResolvedLayout` :
```
{ regions: { … selon LayoutTemplate courant (04C — 1..N régions, pas figé à 5) … },
  slotPlacements: SlotPlacement[],   // slot → region + ordre + collapse appliqué
  densityAttr, emphasisClasses,      // dérivés tokens (03)
  overlays?,                         // overlays actifs (strate au-dessus, 04C §4)
  provenance?                        // mode dev : d'où vient chaque décision (04A §3)
}
```

Le LayoutResolver **ne fetch rien, ne décide aucune permission** (ça reste `resolve-page-access` + ContextEnvelope) et **ne connaît aucun métier** (test d'agnosticité). Il fusionne, adapte, résout.

## 2. Ce qu'il supprime du runtime actuel

| Aujourd'hui dans `RuntimeDemoApp.tsx` | Devient |
|---------------------------------------|---------|
| ~15 constantes `CASH_REGISTER_*_PATH` | **rien** : la route est une donnée du NavigationManifest |
| `syncSelectionFromPath` (cascade ~20 `if path===`) | dérivation `path → entry` depuis le NavigationManifest (matching déclaratif) |
| `resolvedPageKey` (cascade ~12 `if adminPath===`) | `entry.pageKey` du manifest, point |
| `isCashRegisterSaleKioskPath` & co | profil `presentation.region: hero` + règle kiosque générique |
| `suppressCashflowNominalWorkspaceSaleAndAside` | composition de slots conditionnée par contexte dans le manifest |
| 5× `with…Presentation` | profils `presentation` lus par le resolver |

**Cible** : `RuntimeDemoApp.tsx` passe de 886 lignes de cas particuliers à un orchestrateur générique qui appelle `LayoutResolver` et rend `ResolvedLayout`.

## 3. Règles de placement (déterministes, ordonnées)

Le resolver applique des règles **dans l'ordre**, première qui matche gagne, sinon défaut :

1. **Région explicite** : si `slot.presentation.region` est défini → place là.
2. **Région par convention de slot** : `slot_id` connu (`header`/`nav`/`aside`/`footer`/`main`) → région homonyme.
3. **Défaut** : `main`.

Puis **responsive** :
4. Si `viewport < responsive.collapse_below` → `aside`/`nav` deviennent drawer/overlay (règle générique, pas par route).
5. `responsive.reflow: stack|grid` → ajuste `grid-template` du `main`.

Puis **présentation** :
6. Applique `density` (page → prefs → `inherit`), `emphasis`, `elevation`, `rhythm` via classes/attrs dérivés des tokens.

**Aucune de ces règles ne connaît un nom de route métier.** C'est l'invariant qui rend le moteur extractible.

## 4. Routage : du manuel au déclaratif

Le routeur manuel (`syncSelectionFromPath`) est remplacé par un **matcher déclaratif** :

- `NavigationEntry` distingue **déjà** `routeKey` (clé stable contrat) et `path` (chemin présentation, *« pas une URL locale posée comme vérité métier »*). On **ajoute** seulement `aliases?: string[]` et `pathPattern?: string` (pour `/admin/cash-sessions/:id`) ;
- `resolveEntryForPath(path, navigation)` retourne l'entrée + params, par matching `path` → `aliases` → `pathPattern` déclarés dans le manifest ;
- les **alias legacy** (`/cash-register/sale`, `/virtual/*`…) deviennent des `aliases[]` **dans le manifest**, plus des constantes dans `RuntimeDemoApp.tsx`.

Ajout schéma NavigationManifest (option) :
```jsonc
{ "id": "cashflow-nominal", "path": "/caisse", "page_key": "cashflow-nominal",
  "aliases": ["/cash-register/sale", "/cash-register/virtual/sale", "/cash-register/deferred/sale"],
  "alias_presentation": { "/cash-register/sale": { "region_override": "hero", "kiosk": true } } }
```
→ les surcouches kiosque deviennent de la **donnée**, pas du code shell.

## 5. Point d'injection dans le moteur

- Le LayoutResolver vit dans le **moteur** (`src/runtime/` ou `src/app/layout/`), pas dans `demo/`.
- `buildPageManifestRegions` (`PageRenderer`) consomme `ResolvedLayout` au lieu de recevoir un manifest pré-patché.
- `RootShell` reçoit `regions` du resolver — il ne sait plus rien des routes.
- `registry` reste le point `widget_type → composant` ; le resolver l'entoure.

## 6. Mode dégradé (préserver l'invariant existant)

Reprendre la discipline actuelle (`ManifestErrorBanner`, fallback `widget_props.kpis` du bandeau) :
- profil présentation invalide → on rend la **structure** sans la présentation avancée (jamais d'écran blanc).
- slot inconnu → placeholder honnête (déjà le cas).
- `state_style` non résoluble → défaut `inherit`.

## 7. Definition of Done

- [ ] `LayoutResolver` implémenté dans le moteur, testé (unitaires : table de règles).
- [ ] Matcher de route déclaratif ; `aliases[]` / `path_pattern` ajoutés au NavigationManifest + schéma.
- [ ] `RuntimeDemoApp.tsx` : 0 constante `*_PATH` métier, 0 fonction `isCashRegister*`, 0 `with…Presentation`. Réduction visible du nombre de lignes.
- [ ] `templates/transverse` généralisé **et nettoyé** dans le resolver : remplacer la cascade `resolveTransverseMainLayoutMode` (sélection `hub`/`consultation` par `if pageKey===…` en dur) par une **donnée déclarée** (mode/template dans le PageManifest, `04C`) ; généraliser le réarrangement de `TransverseHubLayout` (grille adaptative) dans l'adaptation support (`04B`). Préserver les testids `data-transverse-*` pour prouver la parité.
- [ ] Mode dégradé conservé et testé.
- [ ] Pilote caisse : tous ses comportements (hub, kiosque, session open/close) reproduits **par données** (manifest + profil), 0 cas spécial dans le shell.
