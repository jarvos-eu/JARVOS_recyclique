# 04-PEINTRE — Langage CREOS de composition : profil `presentation`

> **But** : donner à CREOS une **grammaire de composition** (aujourd'hui CREOS décrit la *structure* — slots/widgets/flows — mais quasiment pas la *présentation*). Ce profil est le **cœur du langage v0.1**. Il est complété par deux extensions spécialisées : `04A` (modèle d'autorité défaut/app/user) et `04B` (adaptation au support). Les trois forment un seul schéma cohérent.
> **Grammaire unique** : ce même profil est émis par l'**app** (intention métier), surchargé par le **user** (voix, poignées), et plus tard produit par l'**agent** (final cut). Un seul vocabulaire pour les trois → voir `04A`.
> **Respecte AR39** : la composition est **sous** les autorisations du `ContextEnvelope` — elle ne peut **rien** afficher que les contrats n'autorisent. Détail des invariants : `04A` §4.

## 1. Principe : intentions, pas pixels

Le profil présentation déclare des **intentions** résolues par le moteur en tokens (`03`) et en layout (`05`). Il ne contient **jamais** de valeur visuelle brute (pas de `px`, pas de `#hex`, pas de gradient).

Mauvais (ce qu'on fait aujourd'hui, en dur dans le runtime) :
```ts
widgetProps: { workspace_heading: 'Ouverture de Session', hide_register_selection_row: true }
```
Bon (déclaratif, dans le PageManifest) :
```json
{ "slot_id": "main", "widget_type": "caisse-brownfield-dashboard",
  "presentation": { "emphasis": "primary", "region": "body", "density": "inherit" } }
```

## 2. Où le profil s'attache

Trois niveaux, du plus large au plus fin (le plus fin gagne) :

1. **PageManifest.presentation** — intention de page (layout global, densité par défaut, rythme).
2. **slot.presentation** — intention par zone (`region`, ordre, responsive).
3. **widget.presentation** — intention par widget (`emphasis`, `state_style`).

## 3. Schéma du profil (à ajouter aux schémas CREOS)

Fichier cible : `contracts/creos/schemas/presentation-profile.schema.json` (nouveau), référencé en option par `page-manifest` et `widget-declaration`.

```jsonc
{
  "$id": "presentation-profile.schema.json",
  "type": "object",
  "additionalProperties": false,   // strict — pas d'évolution sauvage comme widget_props aujourd'hui
  "properties": {
    "emphasis":  { "enum": ["primary", "secondary", "muted"] },
    "region":    { "enum": ["hero", "body", "aside", "footer", "toolbar"] },
    // ↑ RÔLES de présentation, pas régions de shell. Le shell réel a 5 régions
    //   (header/nav/main/aside/footer — cf shell-slot-regions.ts). hero/body/toolbar
    //   sont résolus DANS main/header par le LayoutResolver. Voir 0A §2.4.
    "density":   { "enum": ["comfortable", "compact", "inherit"] },
    "elevation": { "enum": ["flat", "raised", "overlay"] },
    "rhythm":    { "enum": ["tight", "normal", "relaxed"] },
    "responsive": {
      "type": "object",
      "additionalProperties": false,
      "properties": {
        "collapse_below": { "enum": ["sm", "md", "lg"] },   // ex. aside → drawer sous md
        "reflow":         { "enum": ["stack", "grid", "keep"] }
      }
    },
    "state_style": {              // mise en forme des WidgetDataState (loading/empty/error)
      "type": "object",
      "additionalProperties": false,
      "properties": {
        "loading": { "enum": ["skeleton", "spinner", "inherit"] },
        "empty":   { "enum": ["illustration", "text", "inherit"] },
        "error":   { "enum": ["banner", "inline", "inherit"] }
      }
    },

    "override_policy": { "$ref": "presentation-authority.schema.json#/override_policy" }, // 04A §5
    "adaptive":        { "$ref": "presentation-adaptive.schema.json#/adaptive" }          // 04B §5
  }
}
```

Le profil `presentation` est donc le **point d'entrée** d'un schéma en trois fichiers : composition (ici), autorité (`presentation-authority.schema.json`, voir `04A`), adaptation (`presentation-adaptive.schema.json`, voir `04B`). Tous `additionalProperties:false`. C'est ce schéma unifié que valident la CI CREOS et le résolveur.

**Note de gouvernance** : `additionalProperties: false` ici — contrairement à `widget-declaration.schema.json` qui est encore `true` pour absorber l'évolution. La présentation doit être **stricte dès le départ** pour ne pas reproduire le bricolage `widgetProps`.

## 4. Sémantique de résolution (qui décide quoi)

| Champ | Résolu par | En quoi |
|-------|-----------|---------|
| `emphasis` | tokens (`03` §6) | `--pn-emphasis-{value}-{bg,fg}` |
| `region` | LayoutResolver (`05`) | placement dans la grille du shell |
| `density` | tokens (`03` §5) | `data-pn-density` / `--pn-density-*` ; `inherit` = prend la page/prefs |
| `elevation` | tokens (`03` §4) | `--pn-elevation-{0,2,3}` |
| `rhythm` | tokens espace | `--pn-density-gap` ajusté |
| `responsive` | LayoutResolver + breakpoints | reflow/collapse aux seuils `03` §7 |
| `state_style` | moteur de rendu des `WidgetDataState` | skeleton vs spinner, etc. |

## 5. Migration des surcouches runtime existantes

Chaque `with…Presentation` de `RuntimeDemoApp.tsx` devient une **déclaration dans le PageManifest** ou une **règle LayoutResolver**, pas du code shell.

| Surcouche runtime actuelle | Devient |
|----------------------------|---------|
| `withCashflowNominalCaisseHubPresentation` (`presentation_surface: caisse_hub`) | variante de PageManifest `caisse-hub` OU profil `presentation` sur le slot |
| `withCashflowNominalKioskSaleDashboard` (`sale_kiosk_minimal_dashboard`) | profil `presentation.region: hero` + règle kiosque LayoutResolver |
| `suppressCashflowNominalWorkspaceSaleAndAside` | composition de manifest (slots conditionnés par contexte), pas filtrage shell |
| libellés (`workspace_heading`, `fund_field_label`…) | `widget_props` **reviewables** dans le manifest (donnée métier, légitime) — mais déclarés dans le JSON, pas patchés au runtime |

**Règle** : le libellé métier reste légitime en `widget_props` (c'est de la donnée Recyclique). Ce qui migre, c'est la **décision de présentation** (emphasis, masquage, layout) qui n'a rien à faire dans le shell générique.

## 6. Distinction widgetProps vs presentation (à ne pas confondre)

- `widget_props` = **données/config métier** du widget (libellés, chemins de retour, flags fonctionnels). Writer = Recyclique. Reste reviewable.
- `presentation` = **intentions visuelles** résolues par le moteur. Vocabulaire fermé. C'est la nouveauté v1.

Un widget reçoit les deux ; il consomme `widget_props` pour son métier, et le **moteur** applique `presentation` autour de lui (le widget n'a pas à lire `presentation` lui-même → c'est ce qui le rend générique).

## 6bis. Modules optionnels (lien pack MOD)

Un module optionnel (slice CREOS, ex. `kpi-live-banner`, activé par `site_id`+`module_key`, Story 9.6) **injecte des slots**. Règles :
- un slot injecté par un module **porte son profil `presentation`** dans le manifest **du module** (même grammaire, aucune exception) ;
- **module désactivé** : le LayoutResolver n'a rien de spécial à faire — `effectiveModuleKeys` du ContextEnvelope filtre en amont (AR39). Le slot n'arrive tout simplement pas ;
- **versioning** : ajouter `presentation` à un manifest de module publié (schéma versionné, ex. `kpi-live-banner` 1.0.0) = **bump de version** au registre `05-MOD` → à cadrer avec `21-MOD-gouvernance-contrats`.

## 6ter. Gouvernance des nouveaux `creos_kind`

`theme`, `layout_template`, `overlay`, `presentation-*` entrent dans le **même régime de gouvernance que les contrats modules** (`21-MOD-gouvernance-contrats-modules`) : writer = app, versioning au registre, revue. Pas de canal parallèle.

## 7. Definition of Done

- [ ] `presentation-profile.schema.json` créé, `additionalProperties:false`.
- [ ] `page-manifest` et `widget-declaration` référencent le profil en option.
- [ ] Types TS générés/étendus (`src/types/page-manifest.ts`).
- [ ] CI CREOS étendue (Épic 10 modules) : valider que tout `presentation` respecte le schéma.
- [ ] Au moins le pilote caisse migré : surcouches `with…Presentation` supprimées du runtime, intentions déclarées dans le manifest.
- [ ] Aucun `presentation_*` patché au runtime restant (grep = 0 hors LayoutResolver).
