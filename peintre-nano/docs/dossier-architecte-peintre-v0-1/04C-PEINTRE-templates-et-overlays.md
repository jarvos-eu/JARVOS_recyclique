# 04C-PEINTRE — Templates de layout & couche overlays

> **But** : ne jamais figer le moteur sur un nombre de zones. Le moteur sait **résoudre un template** (quel qu'il soit) et **poser des overlays** (par-dessus le fond). v0.1 *livre* un seul template concret (5 zones, pour Recyclique) + le *mécanisme* générique + une couche overlay avec 1 pilote — sans construire de templates spéculatifs.
> **Décisions cadrantes (HITL Strophe)** : (Q1) mécanisme de templates + **1 template livré** (5 zones) ; (Q2) couche overlay **squelette + 1 pilote** (raccourcis clavier) ; (Q3) **hook inerte réservé** pour l'édition live souris/clavier façon Ableton.
> **Principe** : le chiffre « 5 » est un **choix de livraison**, pas une **loi du moteur**.

## 1. Le problème que ça résout

Figer 5 régions dans le code du moteur fermerait la porte à : présentations plein écran, dashboards à géométrie variable, tactile localisé, et surtout aux **overlays** (raccourcis clavier, onboarding IA, modales). Or ces besoins sont déjà identifiés. La solution n'est **pas** de tout construire maintenant, mais de poser une **structure qui ne fige pas le nombre de zones** et ne livre qu'un template concret.

## 2. LayoutTemplate : la géométrie devient une donnée (CREOS)

Aujourd'hui les régions sont une constante du moteur (`shell-slot-regions.ts` : `['header','nav','main','aside','footer']`). v0.1 transforme ça en **template déclaré**, le moteur ne connaît plus « 5 » :

```jsonc
// LayoutTemplate — déclaré en CREOS, lu par le moteur (jamais codé en dur)
{ "creos_kind": "layout_template",
  "id": "standard-5",                 // le SEUL template livré en v0.1
  "regions": [                        // 1..N régions, le moteur ne présume rien
    { "id": "header", "role": "bar-top" },
    { "id": "nav",    "role": "rail-left" },
    { "id": "main",   "role": "canvas", "primary": true },
    { "id": "aside",  "role": "rail-right" },
    { "id": "footer", "role": "bar-bottom" }
  ] }
```

Le moteur :
- lit la liste `regions` (longueur libre) ;
- la fonction actuelle `mapSlotIdToShellRegion(slotId)` devient `mapSlotToRegion(slotId, template)` : elle résout contre **le template courant**, pas contre une constante ;
- un slot dont la région n'existe pas dans le template → fallback sur la région `primary` (équivalent du `unmapped→main` actuel).

**v0.1** : un seul template `standard-5` est fourni (côté app/contrats), identique aux 5 zones d'aujourd'hui → zéro changement visible, mais le moteur est devenu **template-agnostique**. Demain : `fullscreen-1` (une région `canvas`), `dashboard-8`, etc., sans toucher au moteur.

## 3. Rôles de présentation : par template (décision Q-09)

- **Région** = une zone du template courant (peut être 5, 1, ou 8 selon le template).
- **Rôle de présentation** (`hero`, `toolbar`, `body`…) = une *étiquette* sur un slot, résolue **dans** une région.

**Décision Q-09 (HITL)** : chaque template porte **SA propre liste d'étiquettes** (rôles autorisés). `standard-5` déclare la sienne (fermée) ; un autre template est libre de déclarer les siennes. **Pas de liste globale figée** dans le moteur — le moteur lit les rôles permis dans le template courant.

```jsonc
{ "creos_kind": "layout_template", "id": "standard-5",
  "regions": [ /* … */ ],
  "roles": ["hero", "body", "toolbar", "aside", "footer"]   // SA liste, fermée pour CE template
}
```

Un slot qui déclare un `role` absent de la liste du template → fallback rôle `body` (ou `primary`) + warning. → cohérent avec la géométrie variable : rien n'est figé dans le moteur, tout est dans le template.

## 4. Couche overlays : une *strate*, pas une région

Un overlay (raccourcis clavier, onboarding, modale) ne vit pas *à côté* des régions : il se pose **par-dessus tout le template**, temporairement, en capturant éventuellement le focus/clavier/souris.

Modèle :
```
┌─ OVERLAY LAYER (z-dessus, 0..N actifs) ───────────┐
│  overlay "keyboard-shortcuts" (pilote v0.1)       │
│  → voile semi-transparent, capture clavier+souris │
│  → laisse voir le fond, s'allume/s'éteint         │
└───────────────────────────────────────────────────┘
┌─ FOND : LayoutTemplate courant (régions) ─────────┐
│  header / nav / main / aside / footer             │
└───────────────────────────────────────────────────┘
```

Grammaire CREOS overlay (déclaratif, même bus) :
```jsonc
{ "creos_kind": "overlay",
  "id": "keyboard-shortcuts",
  "trigger": { "shortcut": "mod+k" },     // déclaré, pas codé
  "capture": ["keyboard", "pointer"],     // ce qu'il intercepte tant qu'actif
  "backdrop": "scrim",                    // voile laissant voir le fond
  "dismiss": ["escape", "backdrop-click"],
  "content_widget": "keyboard-shortcuts-panel"
}
```

Le moteur fournit :
- un **OverlayHost** (la strate de rendu au-dessus du template) ;
- un **gestionnaire d'overlays** (pile : ouvrir/fermer, focus trap, restitution du focus, `capture`) ;
- l'overlay rend un **widget normal** via le registry (donc soumis à AR39 comme tout widget).

**v0.1** : OverlayHost + gestionnaire (le squelette) + **1 overlay pilote** : `keyboard-shortcuts`. Les overlays onboarding/IA viendront brancher sur la même strate, plus tard.

## 5. Pilote v0.1 : overlay raccourcis clavier

Comportement : `mod+k` ouvre un voile montrant, pour chaque action visible à l'écran, son raccourci courant. L'utilisateur peut presser une combinaison pour **remapper** à la volée (façon Ableton).

Découpage v0.1 :
- **livré** : l'overlay s'ouvre, **affiche** les raccourcis actifs (lecture), capture clavier/souris, se ferme proprement.
- **réservé (hook inerte)** : le **remapping live** (réécriture du binding souris/clavier). v0.1 pose l'interface, l'implémentation est pass-through (lecture seule). Voir §6.

## 6. Hook inerte d'édition live des raccourcis (Q3)

Cohérent avec le `CompositionArbiter` inerte (`04A` §6) : on pose l'interface, pas le comportement.

```ts
// Présent dès v0.1 ; implémentation v0.1 = lecture seule (ne remappe rien)
interface ShortcutEditor {
  // proposer un nouveau binding ; v0.1 : no-op qui retourne l'existant
  remap(actionId: string, binding: KeyBinding): KeyBindingResult;
  list(): readonly ShortcutBinding[];   // actif dès v0.1 (lecture)
}
const readonlyShortcutEditor: ShortcutEditor = {
  remap: (id) => ({ ok: false, reason: 'live-edit-reserved-v0.1', actionId: id }),
  list: () => currentBindings(),
};
```

Garanties : l'overlay pilote **appelle** `editor.list()` (marche) et **expose** `editor.remap()` dans l'UI (mais retourne « réservé » en v0.1). Quand on activera l'édition live, on remplace l'implémentation, **zéro changement** ailleurs.

## 7. Ancrage code réel (points d'injection)

- `registry/shell-slot-regions.ts` : `mapSlotIdToShellRegion` → généraliser en `mapSlotToRegion(slotId, template)`. Le template `standard-5` reproduit la constante actuelle.
- `app/PageRenderer.tsx::buildPageManifestRegions` : itère désormais sur `template.regions` (longueur libre) au lieu des 5 buckets en dur. Le fallback `unmapped` vise la région `primary` du template.
- **OverlayHost** : nouveau composant moteur, monté **au-dessus** du shell (frère du RootShell), indépendant du template.
- Validation : la chaîne `validation/` existante (`validate-bundle-rules`, `page-manifest-ingest`) accueille la validation des `layout_template` et `overlay` (mêmes mécanismes, voir `0A`).

## 8. Ce que v0.1 NE fait pas (anti-spéculation) — mais prépare concrètement (D-15)

- Pas de 2ᵉ/3ᵉ template **monté**, mais **un 2ᵉ template mocké** (ex. `fullscreen-1`, présent en data, non activé) **prouve** que la géométrie variable marche — pas juste une promesse de doc.
- Pas d'overlay onboarding/IA branché, mais la strate `OverlayHost` les **accepte déjà** (le pilote raccourcis le démontre).
- Pas de remapping live effectif, mais `ShortcutEditor.remap` **existe** (no-op réservé).
- Pas de drag-and-drop de régions, mais le mécanisme template **le rendra possible** sans refonte.

→ Application directe de **D-15** : chaque « plus tard » est une prise inerte/mock dans le code, pas une intention.

## 9. Definition of Done

- [ ] `LayoutTemplate` (schéma CREOS) + chargement/validation ; le moteur ne contient plus la constante des 5 régions.
- [ ] `mapSlotToRegion(slotId, template)` + `buildPageManifestRegions` itérant sur `template.regions` (testés à 1, 5 et N régions).
- [ ] Template `standard-5` livré (avec **sa** liste de rôles fermée), parité visuelle avec l'actuel (non-régression).
- [ ] **2ᵉ template mocké** (`fullscreen-1`, en data, non monté) + test prouvant que le moteur le résout (preuve de géométrie variable, D-15).
- [ ] `OverlayHost` + gestionnaire de pile (focus trap, restitution, `capture`) dans le moteur, testés.
- [ ] Overlay pilote `keyboard-shortcuts` : ouverture `mod+k`, affichage des bindings, capture, fermeture — branché via registry (AR39 respecté).
- [ ] `ShortcutEditor` interface posée ; `list()` actif, `remap()` réservé (no-op explicite) + test prouvant la réservation.
- [ ] Overlay = widget registry standard (pas un canal parallèle).
