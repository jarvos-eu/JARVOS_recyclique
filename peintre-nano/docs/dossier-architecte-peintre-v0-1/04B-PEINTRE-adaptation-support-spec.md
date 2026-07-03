# 04B-PEINTRE — Adaptation au support (réarrangement adaptatif)

> **But** : faire de l'adaptation au support une **capacité centrale du moteur**, pas un responsive bricolé par widget. Peintre réarrange widgets, colonnes, afficheurs selon le support (desktop / tablette / téléphone / tactile / autre), guidé par des **priorités** et la **nature** de chaque contenu (information en lecture vs interface tactile à fort encombrement), le tout déclaré en CREOS par l'app et surchargeable par le user (`04A`).
> **Agnosticité** : le moteur connaît des *catégories de support* et des *règles de réarrangement*, jamais un écran Recyclique précis.

## 1. Le support n'est pas qu'une largeur

Un « support » est un **profil multi-critères**, pas un simple breakpoint :

```jsonc
"support_profile": {
  "form_factor": "phone | tablet | desktop | kiosk | other",
  "viewport":    { "w": 0, "h": 0 },        // px logiques
  "input":       "touch | pointer | hybrid", // tactile vs souris
  "density_class":"comfortable | compact",   // dérive du form_factor + prefs
  "orientation": "portrait | landscape",
  "pointer_fine":true                        // précision du pointeur (gros doigts = false)
}
```

Le moteur **détecte** ce profil au runtime (et le réévalue au resize/rotation). Il est passé au LayoutResolver (`05`) avec le profil de composition mergé (`04A`).

## 2. Nature du contenu : info vs interaction tactile

Chaque widget/slot déclare sa **nature**, qui change les règles d'adaptation :

```jsonc
"content_nature": {
  "kind": "info | input | action | navigation",
  "touch_weight": "light | heavy",   // heavy = gros boutons, encombrant au doigt
  "reflow": "fluid | atomic"         // atomic = ne pas casser (ex. pavé numérique caisse)
}
```

Conséquences moteur (agnostiques) :
- `kind: info` + petit écran → peut être condensé, résumé, mis en accordéon.
- `kind: input` + `touch_weight: heavy` + `input: touch` → **réserver de la place**, agrandir les cibles, ne pas comprimer (un pavé de saisie caisse au doigt a besoin d'air).
- `reflow: atomic` → le bloc se déplace entier, jamais découpé.

C'est la traduction concrète de ton *« savoir quand c'est de l'info affichée ou de l'interface tactile, et rester dans les bons clous »*.

## 3. Priorité d'affichage : quoi survit quand l'espace manque

Chaque slot porte une **priorité** déclarée par l'app (couche 1, `04A`). Quand l'espace se réduit, le moteur dégrade **par priorité croissante de sacrifice**.

```jsonc
"display_priority": {
  "rank": 1,                    // 1 = vital, garanti présent à tout support
  "collapse_strategy": "hide | summarize | drawer | accordion | demote",
  "min_support": "phone"        // visible dès le plus petit support
}
```

Échelle de dégradation (du moins au plus destructeur) :
`keep` → `demote` (région moins proéminente) → `accordion`/`drawer` (repli interactif) → `summarize` (forme condensée) → `hide`.

Le moteur applique la stratégie déclarée ; il ne **choisit** pas quoi cacher (ça, c'est l'app aujourd'hui ; ce sera l'arbitre agentique demain, via les hooks `04A` §6).

## 4. Règles de réarrangement (déterministes, dans le moteur)

Le moteur résout le layout par **règles ordonnées**, à partir du support + nature + priorité. Exemples génériques :

1. **Colonnes adaptatives** : `desktop` → N colonnes ; `tablet` → ⌊N/2⌋ ; `phone` → 1 colonne (stack). N et seuils déclarés ou défaut moteur. *(Les régions cibles dépendent du LayoutTemplate courant — `04C` ; le réarrangement opère dans la géométrie déclarée, pas dans 5 zones figées.)*
2. **Aside → drawer** : un slot `region: aside` sur `viewport < md` devient drawer (sauf `display_priority.rank=1`).
3. **Toolbar → bottom-bar tactile** : `input: touch` + `phone` → la barre d'action passe en bas, cibles agrandies.
4. **Atomic protection** : un bloc `reflow: atomic` ne se subdivise jamais ; il migre entier vers la région qui a la place.
5. **Sacrifice par priorité** : si après réarrangement le contenu déborde encore, appliquer `collapse_strategy` aux slots du `rank` le plus élevé (le plus sacrifiable) d'abord.
6. **Touch ergonomics** : `input: touch` → cibles ≥ taille minimale (token densité tactile), espacement augmenté ; `pointer_fine:false` renforce.

Toutes ces règles sont **paramétrées par tokens et par CREOS** : aucune valeur métier en dur.

## 5. Grammaire CREOS d'adaptation (extension du profil de composition `04`)

Ajout au profil `presentation` (déclaré par l'app, surchargé par user) :

```jsonc
"adaptive": {
  "columns":   { "desktop": 3, "tablet": 2, "phone": 1 },   // ou "auto"
  "per_support": {                                          // overrides ciblés par support
    "phone":  { "region": "body", "collapse_strategy": "accordion" },
    "kiosk":  { "density": "comfortable", "touch_targets": "large" }
  },
  "display_priority": { "rank": 2, "collapse_strategy": "drawer", "min_support": "tablet" },
  "content_nature":   { "kind": "input", "touch_weight": "heavy", "reflow": "atomic" }
}
```

`per_support` = le seul endroit où l'app peut **spécialiser** un support sans casser l'agnosticité : elle déclare *son intention pour ce form_factor*, le moteur l'applique.

## 6. Articulation avec le modèle d'autorité (04A)

L'adaptation support est **soumise au même merge** :
- la couche app déclare `adaptive` (colonnes, priorités, per_support) ;
- le user peut surcharger ce que `override_policy` autorise (ex. forcer 2 colonnes sur sa tablette, déplacer un bloc) ;
- le défaut moteur fournit un comportement adaptatif sûr si l'app ne déclare rien (1 colonne sur phone, aside→drawer, etc.).

Ordre dans le pipeline (`05`) : **merge des couches d'abord (04A), puis résolution support (04B)** — on adapte le profil *effectif*, pas trois profils séparés.

## 7. Réévaluation dynamique

- Le moteur observe `resize` / `orientationchange` / changement d'input (souris branchée sur tablette) → recalcule le `support_profile` → re-résout le layout.
- Recalcul **idempotent et borné** (debounce) : même entrée → même sortie, pas de reflow erratique.
- Les overrides user de position/densité **survivent** au changement de support (réappliqués par-dessus le nouveau layout) tant qu'ils restent valides pour le nouveau support.

## 7bis. Barème « affichage parfait par défaut » v0.1 (réponse Q-08, minimal)

Quand l'app ne déclare rien, le défaut moteur applique **3 règles** (simples, déterministes, affinables plus tard) :
1. **Viewport** : `< sm` → 1 colonne + aside en drawer ; `< md` → densité compact ; sinon confortable multi-colonnes.
2. **Volume** : un slot dont le contenu dépasse un seuil d'items → densité compact + pagination/scroll interne.
3. **Nature** : `content_nature.kind = input` + `touch` → cibles agrandies, jamais comprimé (priorité ergonomie tactile).

Barème pondéré fin = évolution post-v0.1 (Q-08 reste ouverte pour le raffinement, pas pour démarrer).

## 8. Mode dégradé

- Support non détectable → traiter comme `desktop/pointer` (le plus permissif), jamais d'écran cassé.
- `adaptive` absent → défaut moteur (§4 règles 1-6 avec valeurs par défaut).
- Conflit priorité (tout en rank 1, ça déborde) → le moteur garde l'ordre du manifest et `demote` le surplus plutôt que `hide` (préserver l'accès).

## 9. Definition of Done (adaptation support)

- [ ] `support_profile` détecté + réévalué (resize/rotation/input), debounced, testé.
- [ ] Grammaire `adaptive` (colonnes, per_support, display_priority, content_nature) ajoutée au schéma `04`, `additionalProperties:false`.
- [ ] Règles de réarrangement (§4) implémentées dans le LayoutResolver, unit-testées par table support→layout.
- [ ] Protection `atomic` + ergonomie tactile (`touch_weight heavy`) prouvées sur un cas (ex. pavé de saisie).
- [ ] Sacrifice par priorité testé (réduction progressive d'espace → ordre de dégradation attendu).
- [ ] Overrides user survivent au changement de support.
- [ ] Défaut moteur adaptatif sûr si l'app ne déclare rien.
