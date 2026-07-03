# 10-PEINTRE — Guide de portage Recyclique sur Peintre v0.1 (Tour 2)

> **But** : transformer Recyclique de *propriétaire implicite du moteur* en *consommateur explicite du langage Peintre*. Tout ce que Recyclique décide d'affichage doit sortir du code et entrer en **CREOS** (theme + profils de composition + manifests). Le moteur ne doit plus rien savoir de Recyclique.
> **Prérequis** : Tour 1 (noyau langage) livré — `03` tokens-contrat, `04`/`04A`/`04B`/`04C` langage, `05` LayoutResolver. Ancrage code : `0A`.
> **Méthode** : portage **pilote-d'abord** (caisse), puis généralisation. Parité observable préservée à chaque étape (tests e2e existants = filet).

## 1. Principe du portage

Pour chaque chose que Recyclique « impose » à l'écran aujourd'hui, on se demande : *est-ce une donnée d'app (→ CREOS) ou une mécanique générique (→ moteur) ?* Quasiment tout est donnée d'app. Le portage = **déplacer ces décisions du code vers des fichiers CREOS** que Recyclique possède.

| Ce que Recyclique impose aujourd'hui | Où ça vivait (mauvais) | Où ça va (Tour 2) |
|--------------------------------------|------------------------|-------------------|
| Le vert `#2e7d32`, l'identité | en dur dans CSS modules | **theme CREOS Recyclique** (`03` §0) |
| « cette page a un héros kiosque » | surcouche `with…Presentation` runtime | `presentation` dans le PageManifest (`04`) |
| « masquer l'aside en mode vente » | `suppressCashflowNominal…` dans le shell | `presentation`/`adaptive` du slot (`04B`) |
| priorités (quoi sacrifier en petit écran) | nulle part (pas géré) | `display_priority` CREOS (`04B`) |
| alias de routes (`/cash-register/sale`…) | constantes dans `RuntimeDemoApp` | `aliases[]` du NavigationManifest (`05`) |
| libellés (« Ouverture de session ») | patchés au runtime | `widget_props` reviewables du manifest |

> ⚠️ **Bandeau-live = module publié versionné** (`kpi-live-banner` 1.0.0, pack MOD). Lui ajouter un profil `presentation` = bump de version au registre `05-MOD` + revue `21-MOD`. Ne pas le traiter comme un widget interne ordinaire.

## 2. Étape 1 — Le theme CREOS Recyclique

**Livrable** : un manifest CREOS `theme` côté app (ex. `contracts/creos/themes/recyclique.theme.json`) qui remplit le contrat de tokens (`03`).

```jsonc
{ "creos_kind": "theme",
  "id": "recyclique",
  "tokens": {
    "brand.6": "#2e7d32",          // LE vert Recyclique vit ICI, plus dans le moteur
    "brand.7": "#1b5e20",
    "accent": "{brand.6}",
    "surface.raised.elevation": "2",
    "radius.md": "8px"
    // … remplir le reste du contrat ; non fourni → défaut neutre moteur
  } }
```

Actions :
1. **Extraire** toutes les couleurs/dimensions en dur des CSS modules Recyclique (105 couleurs repérées, `01` §3) → les exprimer comme tokens dans le theme.
2. **Brancher** `resolveTheme(recyclique.theme, contract)` au démarrage de l'app Recyclique (le moteur injecte les variables CSS).
3. **Vérifier** : grep `#2e7d32` dans le moteur = 0. Le vert n'existe plus que dans le theme CREOS.

**Critère** : on pourrait changer `recyclique` pour `autre-app.theme.json` et le moteur rendrait l'autre identité sans une ligne modifiée.

## 3. Étape 2 — Migrer les 5 surcouches caisse en profils de composition

Les surcouches `with…Presentation` de `RuntimeDemoApp.tsx` (`01` §4) deviennent des déclarations `presentation` dans les PageManifests Recyclique.

| Surcouche runtime (à supprimer) | PageManifest cible | `presentation` déclaré |
|---------------------------------|--------------------|------------------------|
| `withCashflowNominalCaisseHubPresentation` | page `caisse-hub` | `region: body`, emphasis selon hub |
| `withCashflowNominalKioskSaleDashboard` | page `caisse-vente` | slot vente `region: hero`, `adaptive.per_support.kiosk` |
| `withCashflowNominalSessionOpenPresentation` | page `session-open` | `emphasis: primary` sur le formulaire |
| `withCashflowNominalSessionClosePresentation` | page `session-close` | idem close |
| `suppressCashflowNominalWorkspaceSaleAndAside` | page `caisse-vente` | slots aside : `display_priority` + visibilité conditionnée au contexte (pas filtrage shell) |

Procédure par surcouche (une à la fois, pas big-bang) :
1. lire ce que la surcouche patche (`presentation_surface`, `workspace_heading`, `hide_*`…) ;
2. traduire en `presentation` (intentions) + `widget_props` (libellés reviewables) dans le PageManifest ;
3. supprimer la surcouche du runtime ;
4. lancer les tests e2e caisse (`runtime-demo-cash-register-*`, `cash-register-*-e2e`) → **parité verte avant de passer à la suivante**.

## 4. Étape 3 — Routage : alias caisse en données

`01` §4 / `05` §4. Les ~15 constantes `*_PATH` + `syncSelectionFromPath` de `RuntimeDemoApp` :
1. ajouter `aliases?: string[]` aux `NavigationEntry` concernées (le type a déjà `routeKey`/`path`) ;
2. déplacer `/cash-register/sale`, `/cash-register/virtual/sale`, `/cash-register/deferred/sale`… dans les `aliases[]` du NavigationManifest Recyclique ;
3. remplacer `syncSelectionFromPath` par `resolveEntryForPath(path, navigation)` (moteur) ;
4. supprimer les constantes et les fonctions `isCashRegister*` du runtime.

**Critère** : `RuntimeDemoApp.tsx` ne contient plus aucun chemin métier en dur.

## 5. Étape 4 — Alléger les widgets monolithiques (chrome → PresentationSurface)

`01` §5. Cibles : `CashflowNominalWizard` (2033 l.), `CaisseBrownfieldDashboard` (1203 l.). **On n'éclate pas le métier** ; on sort seulement le *chrome de présentation* (conteneurs, bordures, espacements, élévations) vers `PresentationSurface` (`0A` §2.2) + tokens. Le widget garde sa logique, perd son style en dur.

## 6. Étape 5 — Généralisation (réception, admin)

Une fois la caisse portée et verte, répéter §3-§5 pour réception (`ReceptionNominalWizard`) et admin (`AdminCategoriesWidget`, `AdminUsersWidget`). Même procédure, même filet de tests. Pas de nouveau concept : c'est de la répétition mécanique.

## 7. Étape 6 — Template & overlay Recyclique

- Déclarer le template `standard-5` côté contrats Recyclique (`04C` §2) — identique au layout actuel, mais désormais en donnée.
- Brancher l'overlay pilote `keyboard-shortcuts` sur les actions Recyclique (lecture des bindings existants ; remap réservé).

## 8. Ordre d'exécution recommandé (Tour 2)

```
1. theme CREOS Recyclique (§2)          ← débloque le rendu convaincant tout de suite
2. template standard-5 en donnée (§7)   ← rend le moteur template-agnostique sans rien casser
3. surcouches caisse → profils (§3)     ← pilote, surcouche par surcouche, tests verts
4. routage alias caisse (§4)
5. chrome widgets caisse → Surface (§5)
6. généralisation réception + admin (§6)
7. overlay raccourcis clavier (§7)
```

## 9. Definition of Done (portage Recyclique)

- [ ] Theme CREOS Recyclique fournit l'identité ; **0 couleur de marque dans le moteur**.
- [ ] 5 surcouches caisse supprimées ; intentions en PageManifests ; parité e2e verte.
- [ ] Alias caisse en `aliases[]` ; `RuntimeDemoApp` sans chemin métier en dur.
- [ ] Widgets caisse allégés de leur chrome (Surface + tokens) ; 0 valeur visuelle en dur.
- [ ] Réception + admin portés de même.
- [ ] Template `standard-5` en donnée ; overlay raccourcis clavier branché.
- [ ] **Preuve d'agnosticité** : une 2ᵉ app fictive (theme + manifests CREOS only) rend dans le même moteur sans modification du moteur.
