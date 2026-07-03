# 06-PEINTRE — PRD du chantier Peintre v0.1

> **But** : transformer le cadrage (`01`–`05`, `08`) en backlog exécutable par Cursor. Stories avec critères d'acceptation (AC) testables. **Promotion BMAD après HITL.**
> **Séquençage non négociable** : Épic A → B → C → E. *(Le saut « D » est volontaire : l'identifiant `D-xx` est réservé aux décisions ADR dans `07` ; l'épic intelligence est nommé **E** / stories `INT-x` pour éviter toute confusion story↔ADR.)* Au sein d'un épic, ordre des stories indicatif.

## Épic A — Noyau langage agnostique *(Tour 1 — débloque affichage convaincant + agnosticité)*

### A-1 — Contrat de tokens + résolveur de theme CREOS
**Réf** : `03`. **Objectif** : remplacer `tokens.css` squelettique par le **contrat** à deux niveaux + `resolveTheme`, sans aucune couleur de marque dans le moteur.
- AC1 : contrat de tokens (niveau 2 + types + défauts neutres) couvrant couleur/typo/espace/élévation/densité/intention/breakpoints.
- AC2 : `resolveTheme(themeCreos, contract)` testé (token manquant → secours ; type faux → rejet).
- AC3 : **aucune couleur de marque dans le moteur** (grep `#2e7d32` = 0 ; brand de secours neutre). Lint/revue.
- AC4 : thème Mantine v8 remappé sur `--pn-*` ; `data-pn-density` posé depuis `UserRuntimePrefs`.
- AC5 : lint CI échoue sur hex/`rgb()` en dur et fuite `--mantine-*` ; token fantôme `--color-border-subtle` éliminé.

### A-2 — Migration pilote bandeau-live sur tokens
**Réf** : `01` §3. **Objectif** : prouver le système sur le citoyen modèle.
- AC1 : `KpiLiveStrip.module.css` et `BandeauLive.module.css` : 0 valeur magique, 0 `--mantine-*`.
- AC2 : rendu visuellement amélioré (élévation, hiérarchie typo) sans changer le comportement.
- AC3 : non-régression tests existants bandeau-live.

### A-3 — Langage de composition CREOS (schéma unifié + types)
**Réf** : `04`, `04A`, `04B`, `0A` §2.1. 
- AC1 : `presentation-profile.schema.json` + `presentation-authority.schema.json` + `presentation-adaptive.schema.json`, tous `additionalProperties:false`, reliés par `$ref`.
- AC2 : référencés en option par `page-manifest` + `widget-declaration`.
- AC3 : `PresentationProfile` ajouté **en champ optionnel rétrocompatible** sur `PageSlotPlacement.presentation` et `PageManifest.presentation` (`types/page-manifest.ts` réel). Manifests Story 3.x non cassés.
- AC4 : CI CREOS valide les profils (composition + autorité + adaptation).

### A-4 — Composant de surface générique (`PresentationSurface`)
**Réf** : `0A` §2.2. **Objectif** : composant moteur appliquant `emphasis`/`elevation`/`density` autour de tout widget.
- AC1 : `<PresentationSurface presentation={…}>` dans le moteur, dérive classes depuis tokens (`03`).
- AC2 : injecté dans `PageRenderer.tsx::renderPlacements` autour du `Component` résolu (remplace `<C widgetProps=… />` nu) ; widgets allégés de leur chrome de conteneur.

### A-5 — Modèle d'autorité défaut→app→user + hook d'arbitrage inerte
**Réf** : `04A`. **Objectif** : grammaire unique, merge par champ, place réservée à l'âme.
- AC1 : `merge(défaut, app, user)` deep-merge par champ, testé (tables de cas) + provenance en mode dev.
- AC2 : invariants AR39/`required` appliqués (user ne peut pas franchir) ; `override_policy` respecté sans connaissance métier.
- AC3 : `CompositionArbiter` pass-through branché dans le pipeline + test prouvant qu'il est appelé et neutre.
- AC4 : `pref_scope` device/identity posé ; précédence documentée (Q-07).

### A-6 — Adaptation au support
**Réf** : `04B`. **Objectif** : réarrangement par support comme capacité moteur.
- AC1 : `support_profile` détecté + réévalué (resize/rotation/input), debounced.
- AC2 : règles de réarrangement (colonnes, aside→drawer, toolbar tactile, atomic, sacrifice par priorité) implémentées + unit-testées par table support→layout.
- AC3 : ergonomie tactile (`touch_weight heavy`) et protection `atomic` prouvées sur un cas (pavé de saisie caisse).
- AC4 : overrides user survivent au changement de support ; défaut moteur adaptatif sûr si l'app ne déclare rien.

## Épic B — LayoutResolver & dé-pollution du shell *(Phase 1 suite)*

### B-1 — LayoutResolver (cœur)
**Réf** : `05`. 
- AC1 : `LayoutResolver(pageManifest, envelope, prefs, viewport) → ResolvedLayout`, dans le moteur.
- AC2 : table de règles de placement testée (unitaires).
- AC3 : `buildPageManifestRegions` consomme `ResolvedLayout`.

### B-2 — Routage déclaratif
**Réf** : `05` §4. 
- AC1 : `aliases[]` + `path_pattern` ajoutés au NavigationManifest + schéma.
- AC2 : `resolveEntryForPath` remplace `syncSelectionFromPath`.
- AC3 : alias caisse legacy déplacés du code vers le manifest.

### B-3 — Rapatriement des surcouches caisse (**mécanisme moteur**)
**Réf** : `04` §5, `05` §2. **Frontière** : B-3 = rendre le *moteur* capable de consommer un profil `presentation` **au lieu** d'une surcouche runtime (mécanique générique). L'écriture des profils Recyclique eux-mêmes est en **C-2** (données). B-3 supprime la mécanique, C-2 fournit la donnée de remplacement.
- AC1 : le LayoutResolver consomme un profil de composition à la place des surcouches ; les 5× `with…Presentation` n'ont plus de point d'appel dans le moteur.
- AC2 : `RuntimeDemoApp.tsx` : 0 constante `*_PATH` métier, 0 `isCashRegister*`. Réduction de lignes mesurée et rapportée.
- AC3 : un profil de test (fixture neutre, non-Recyclique) reproduit hub/kiosque/session via manifest + profil → prouve que le mécanisme est agnostique.
- AC4 : parité observable préservée sur la fixture (pas encore Recyclique — ça, c'est C-2).

### B-4 — Templates de layout à géométrie variable
**Réf** : `04C` §2, `0A` §2.4. **Objectif** : le moteur ne fige plus le nombre de zones.
- AC1 : schéma CREOS `layout_template` + validation greffée sur la chaîne `validation/` existante.
- AC2 : `mapSlotToRegion(slotId, template)` remplace la constante ; `buildPageManifestRegions` itère sur `template.regions` (testé à 1, 5, N régions).
- AC3 : template `standard-5` livré, **parité visuelle** avec l'actuel (non-régression). *Méthode de vérif (testable par agent)* : snapshot DOM sur les testids existants (`data-transverse-layout`, `data-transverse-family`, `transverse-body-grid`) inchangé avant/après ; à défaut, screenshot-diff sur les écrans transverses de référence.

### B-5 — Couche overlays + pilote raccourcis clavier
**Réf** : `04C` §4-6. 
- AC1 : `OverlayHost` + gestionnaire de pile (focus trap, restitution, `capture`) dans le moteur, testés.
- AC2 : schéma CREOS `overlay` validé ; overlay = widget registry standard (AR39 respecté).
- AC3 : pilote `keyboard-shortcuts` : `mod+k` ouvre, affiche les bindings actifs, capture clavier/souris, ferme proprement.
- AC4 : `ShortcutEditor` posé ; `list()` actif, `remap()` réservé (no-op explicite « live-edit-reserved-v0.1 ») + test.

## Épic C — Portage Recyclique sur le langage *(Tour 2 — prouve l'agnosticité)*

### C-1 — Inventaire des couplages + theme CREOS Recyclique
**Réf** : `02` §4, `03` §0, `docs/05-monorepo-et-extraction.md`. 
- AC1 : liste exhaustive des points où le moteur connaît du métier (routes, couleurs, libellés, surcouches).
- AC2 : **theme CREOS Recyclique** créé côté app (le vert `#2e7d32` y vit) ; le moteur n'en porte plus trace.
- AC3 : classement moteur vs application pour chaque fichier `src/app/**`, `src/runtime/**`, `src/domains/**`.

### C-2 — Profils de composition Recyclique (remplacent les surcouches runtime)
**Réf** : `04`/`04A`/`04B` §5, `05` §2. Cible pilote : caisse.
- AC1 : 5× `with…Presentation` supprimées ; intentions déclarées dans les PageManifests Recyclique (emphasis, region, priorité, per_support).
- AC2 : `RuntimeDemoApp.tsx` : 0 constante `*_PATH` métier, 0 `isCashRegister*`, 0 surcouche. Réduction de lignes mesurée.
- AC3 : parité observable caisse préservée (tests e2e existants verts).

### C-3 — Extraction de la présentation hors des widgets monolithiques
**Réf** : `01` §5. Cibles : `CashflowNominalWizard` (2033), `CaisseBrownfieldDashboard` (1203).
- AC1 : chrome de conteneur/présentation déplacé vers `PresentationSurface` + profil.
- AC2 : widgets sans valeurs visuelles en dur ; pas de régression fonctionnelle.

### C-4 — Surface publique moteur documentée
- AC1 : `peintre-nano/docs/06-surface-moteur-v0-1.md` (API publique : registry, LayoutResolver, resolveTheme, arbiter, fallbacks).
- AC2 : preuve d'agnosticité : une 2ᵉ app fictive consomme le moteur via CREOS seul (theme + manifests), sans toucher au moteur.

## Épic E — Intelligence par règles *(Phase 3a — « semblant d'intelligence »)*

> Note : épic renommé **E** (et stories **INT-x**) pour éviter toute collision avec les ADR `D-xx` (`07`). Les `D-xx` sont des décisions, les `INT-x` sont des stories.

### INT-1 — Adaptation densité automatique
**Réf** : `08` §2. 
- AC1 : règle déterministe : densité auto selon viewport + volume de données du slot (sans LLM).
- AC2 : override possible par `UserRuntimePrefs` (l'utilisateur garde la main).

### INT-2 — Adaptation d'emphase / réorganisation par contexte
**Réf** : `08` §3. 
- AC1 : règle : priorité de slots ajustée selon ContextEnvelope (ex. rôle, module actif).
- AC2 : déterministe, testable, jamais en contradiction avec AR39.

## Definition of Done globale du chantier

- [ ] 105 couleurs en dur → 0 ; 7 fuites Mantine → 0.
- [ ] `RuntimeDemoApp.tsx` débarrassé des alias et surcouches métier.
- [ ] Profil `presentation` opérationnel et validé en CI.
- [ ] Pilote caisse : 0 surcouche runtime, 0 valeur visuelle en dur dans les widgets caisse, parité e2e verte (mesurable — remplace « convaincant »).
- [ ] Démo d'adaptation par règles fonctionnelle.
- [ ] Surface moteur documentée.
- [ ] Tous tests existants verts (non-régression parité observable).
