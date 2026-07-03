# 03-PEINTRE — Contrat de tokens (rempli par le theme CREOS de l'app)

> **But** : Peintre v0.1 ne *contient pas* une palette ; il **expose un contrat de tokens** (les *slots sémantiques* qu'un theme doit remplir) et **résout** le theme CREOS fourni par l'application. Recyclique fournit son vert ; une autre app fournit autre chose. Le moteur ne connaît aucune couleur en propre — seulement des **noms de rôles** et des **valeurs par défaut neutres** de secours.
> **Respecte l'ADR P1** (`references/peintre/2026-04-01_adr-p1-p2…` : CSS Modules + variables CSS, **pas** Tailwind, **pas** CSS-in-JS runtime).
> **Agnosticité** : le moteur définit *quels* tokens existent (le contrat) ; l'app définit *leurs valeurs* (le theme CREOS).

## 0. Le contrat vs le theme

- **Contrat de tokens (moteur, agnostique)** : la liste normative des variables sémantiques (`--pn-surface`, `--pn-text-primary`, `--pn-emphasis-primary-bg`…) + leur *type* (couleur, espace, durée…) + un **défaut neutre de secours**. C'est `03`.
- **Theme CREOS (app)** : un manifest CREOS qui **remplit** le contrat avec les valeurs de l'app (palette, identité, rayons préférés…). Recyclique en fournit un ; il vit côté app, pas dans le moteur.

```jsonc
// theme CREOS fourni par l'APP (ex. Recyclique) — remplit le contrat
{ "creos_kind": "theme",
  "tokens": {
    "brand.6": "#2e7d32",            // le vert Recyclique vit ICI, pas dans le moteur
    "accent": "{brand.6}",
    "radius.md": "8px",
    "surface.raised.elevation": "2"
  } }
```

Le moteur **valide** que le theme remplit le contrat (types corrects, références résolues) puis **injecte** les variables CSS résultantes. Token manquant → **défaut neutre de secours** (jamais d'écran cassé, jamais une couleur d'app codée dans le moteur).

## 1. Architecture à deux niveaux (inchangée, désormais *contractuelle*)

**Niveau 1 — tokens primitifs** : la palette brute *fournie par le theme app*. Le moteur ne porte que des primitifs **neutres de secours** (gris, un bleu neutre) pour le mode dégradé.

**Niveau 2 — tokens sémantiques** : les rôles que les widgets consomment. **C'est le contrat stable** exposé par le moteur. Les widgets ne consomment QUE le niveau 2 ; ils ignorent quelle app/theme les remplit → agnosticité côté widget aussi.

Cette séparation permet le theming par application (chaque app son theme CREOS) et, plus tard, mode sombre / thèmes multiples, sans toucher widgets ni moteur.

## 2. Couleur

### 2.1 Primitifs — **DÉFAUTS NEUTRES DE SECOURS uniquement** (le theme app les écrase)
```css
/* Ces valeurs ne sont PAS l'identité de Peintre : ce sont des secours neutres
   utilisés seulement si le theme CREOS de l'app ne fournit pas le token.
   Le moteur ne porte AUCUNE couleur de marque. */
:root {
  /* Gris neutres (secours) */
  --pn-gray-0:#f8f9fa; --pn-gray-1:#f1f3f5; --pn-gray-2:#e9ecef; --pn-gray-3:#dee2e6;
  --pn-gray-4:#ced4da; --pn-gray-5:#adb5bd; --pn-gray-6:#868e96; --pn-gray-7:#495057;
  --pn-gray-8:#343a40; --pn-gray-9:#212529;
  /* Brand : secours NEUTRE volontairement fade (bleu-gris) — JAMAIS une marque d'app.
     Recyclique fournit son vert via son theme CREOS, pas ici. */
  --pn-brand-5:#5b7083; --pn-brand-6:#4a5d6e; --pn-brand-7:#3a4a58;
  /* Status (sémantique universelle, pas une identité de marque → secours acceptables) */
  --pn-success-6:#2f9e44; --pn-warning-6:#f08c00; --pn-danger-6:#e03131; --pn-info-6:#1c7ed6;
  --pn-success-0:#ebfbee; --pn-warning-0:#fff9db; --pn-danger-0:#fff5f5; --pn-info-0:#e7f5ff;
}
```

### 2.2 Sémantiques (niveau consommé)
```css
:root {
  --pn-bg-app: var(--pn-gray-0);
  --pn-surface: #ffffff;
  --pn-surface-raised: #ffffff;        /* + ombre, voir §4 */
  --pn-surface-sunken: var(--pn-gray-1);
  --pn-border: var(--pn-gray-3);
  --pn-border-subtle: var(--pn-gray-2);  /* remplace le token fantôme observé */
  --pn-text-primary: var(--pn-gray-9);
  --pn-text-secondary: var(--pn-gray-7);
  --pn-text-muted: var(--pn-gray-6);
  --pn-text-on-accent:#ffffff;
  --pn-accent: var(--pn-brand-6);
  --pn-accent-hover: var(--pn-brand-7);

  /* Feedback (couleurs sémantiques absentes aujourd'hui = cause du rendu plat) */
  --pn-feedback-success-bg: var(--pn-success-0); --pn-feedback-success-fg: var(--pn-success-6);
  --pn-feedback-warning-bg: var(--pn-warning-0); --pn-feedback-warning-fg: var(--pn-warning-6);
  --pn-feedback-danger-bg:  var(--pn-danger-0);  --pn-feedback-danger-fg:  var(--pn-danger-6);
  --pn-feedback-info-bg:    var(--pn-info-0);    --pn-feedback-info-fg:    var(--pn-info-6);
}
```

## 3. Typographie (échelle absente aujourd'hui)

```css
:root {
  --pn-font-sans: system-ui, -apple-system, 'Segoe UI', Roboto, sans-serif;
  --pn-font-mono: ui-monospace, 'Cascadia Code', Menlo, monospace;

  /* Échelle type (ratio ~1.2) */
  --pn-text-2xs:.6875rem; --pn-text-xs:.75rem; --pn-text-sm:.875rem;
  --pn-text-md:1rem; --pn-text-lg:1.125rem; --pn-text-xl:1.375rem;
  --pn-text-2xl:1.75rem; --pn-text-3xl:2.25rem;

  --pn-leading-tight:1.2; --pn-leading-normal:1.5; --pn-leading-relaxed:1.7;
  --pn-weight-regular:400; --pn-weight-medium:500; --pn-weight-semibold:600; --pn-weight-bold:700;

  /* Rôles typographiques (ce que les widgets consomment) */
  --pn-type-display-size: var(--pn-text-3xl); --pn-type-display-weight: var(--pn-weight-bold);
  --pn-type-title-size: var(--pn-text-xl);    --pn-type-title-weight: var(--pn-weight-semibold);
  --pn-type-body-size: var(--pn-text-md);     --pn-type-body-weight: var(--pn-weight-regular);
  --pn-type-caption-size: var(--pn-text-xs);  --pn-type-caption-weight: var(--pn-weight-medium);
  --pn-type-numeric: tabular-nums;  /* pour KPI / montants caisse */
}
```

## 4. Élévation (absente aujourd'hui = tout est plat)

```css
:root {
  --pn-elevation-0: none;
  --pn-elevation-1: 0 1px 2px rgb(0 0 0 / 6%), 0 1px 1px rgb(0 0 0 / 4%);
  --pn-elevation-2: 0 2px 8px rgb(0 0 0 / 8%), 0 1px 3px rgb(0 0 0 / 6%);
  --pn-elevation-3: 0 8px 24px rgb(0 0 0 / 12%), 0 2px 6px rgb(0 0 0 / 8%);
}
```
**C'est le levier le plus rentable pour « convaincant »** : une `--pn-surface-raised` avec `--pn-elevation-2` transforme immédiatement le ressenti vs la bordure grise plate actuelle.

## 5. Espacement, rayon, densité

```css
:root {
  --pn-space-2xs:.125rem; --pn-space-xs:.25rem; --pn-space-sm:.5rem;
  --pn-space-md:1rem; --pn-space-lg:1.5rem; --pn-space-xl:2rem; --pn-space-2xl:3rem;
  --pn-radius-sm:4px; --pn-radius-md:8px; --pn-radius-lg:12px; --pn-radius-full:999px;

  /* Densité : pilotée par UserRuntimePrefs.uiDensity (toggle déjà présent dans le runtime) */
  --pn-density-pad: var(--pn-space-md);   /* comfortable par défaut */
  --pn-density-gap: var(--pn-space-md);
  --pn-density-row-h: 2.5rem;
}
[data-pn-density="compact"] {
  --pn-density-pad: var(--pn-space-sm);
  --pn-density-gap: var(--pn-space-sm);
  --pn-density-row-h: 2rem;
}
```
**Branchement** : le shell pose `data-pn-density={prefs.uiDensity}` sur la racine. Les widgets consomment `--pn-density-*`. Plus aucune densité codée par widget. *(C'est aussi le premier point de contact de l'intelligence par règles — voir `08` §2.)*

## 6. Intention d'emphase (le pont vers le profil CREOS)

```css
:root {
  --pn-emphasis-primary-bg: var(--pn-accent);
  --pn-emphasis-primary-fg: var(--pn-text-on-accent);
  --pn-emphasis-secondary-bg: var(--pn-surface-raised);
  --pn-emphasis-secondary-fg: var(--pn-text-primary);
  --pn-emphasis-muted-bg: var(--pn-surface-sunken);
  --pn-emphasis-muted-fg: var(--pn-text-secondary);
}
```
Le profil présentation (`04`) déclare `emphasis: primary|secondary|muted` ; le LayoutResolver (`05`) mappe sur ces tokens.

## 7. Breakpoints

```css
/* En CSS Modules via media queries ; exposés aussi en TS pour le LayoutResolver */
/* --pn-bp-sm: 640px ; --pn-bp-md: 900px ; --pn-bp-lg: 1280px */
```
Exporter une copie TS (`src/styles/breakpoints.ts`) pour que le LayoutResolver raisonne sur les mêmes seuils que le CSS.

## 8. Réconciliation Mantine v8 (ne pas créer de 3ᵉ système)

- **Mapper** le thème Mantine sur les primitifs `--pn-*` (provider thème : `primaryColor`, `colors`, `fontFamily`, `radius`, `spacing` pointent vers nos tokens).
- **Interdire** la fuite directe de `--mantine-*` dans les CSS modules (lint, §9). Les 7 fichiers fautifs identifiés (`KpiLiveStrip.module.css`…) sont à corriger.
- Objectif : *un seul* vocabulaire de tokens côté widgets (`--pn-*`), Mantine devient un détail d'implémentation du moteur.

## 9. Garde-fous (lint dédié, Definition of Done)

- Échec de build si un `*.module.css` contient un hex/`rgb()` en dur (hors `tokens.css`).
- Échec si un `*.module.css` référence `--mantine-*`.
- Échec si un widget consomme un primitif niveau 1 (`--pn-gray-*`, `--pn-brand-*`) directement.
- Cible : ramener les **105 couleurs en dur → 0** et les **7 fuites Mantine → 0**.

## 10. Résolveur de theme CREOS (le pont app → contrat)

Le moteur expose une fonction de résolution :
```
resolveTheme(themeCreos, contract) → cssVariables
  1. valider que chaque token fourni correspond à un slot du contrat (type correct)
  2. résoudre les références internes ({brand.6} → valeur)
  3. pour chaque slot du contrat NON fourni → défaut neutre de secours (§2.1)
  4. émettre les variables CSS (injectées au :root du scope app)
```
Règles :
- **aucune** couleur d'app n'est jamais écrite dans le moteur ; elle transite par `themeCreos` ;
- theme invalide (type faux, ref cassée) → rejet du token fautif + secours + warning, jamais d'écran cassé ;
- plusieurs apps de l'écosystème = plusieurs themes CREOS, même contrat.

**Empilage futur (Q-10, préparé via D-15)** : `resolveTheme` accepte en réalité une **pile** de themes `resolveTheme(themeStack[], contract)` fusionnés dans l'ordre (base → overrides). v0.1 n'empile **qu'un** theme, mais l'API prend un tableau et un **mock à 2 themes** (base + retouche) prouve l'empilage en test. Activer l'empilage = passer 2 entrées au lieu d'1, sans changer le résolveur.

## 11. Definition of Done de la spec tokens

- [ ] **Contrat de tokens** (liste normative niveau 2 + types + défauts neutres) publié par le moteur.
- [ ] `resolveTheme(themeCreos, contract)` implémenté + testé (token manquant → secours ; type faux → rejet).
- [ ] **Aucune couleur de marque dans le moteur** (grep : pas de `#2e7d32` ni équivalent Recyclique ; brand de secours = neutre fade). Lint/revue.
- [ ] Recyclique fournit son `theme` CREOS (le vert vit côté app) — voir portage Tour 2.
- [ ] `tokens.css` (contrat + secours) à deux niveaux couvrant couleur/typo/espace/élévation/densité/intention/breakpoints.
- [ ] Thème Mantine remappé sur `--pn-*` (Mantine = détail d'implémentation moteur).
- [ ] `data-pn-density` branché sur la racine depuis `UserRuntimePrefs`.
- [ ] Lint anti-hardcode + anti-fuite-Mantine en CI (cible : 105 couleurs en dur → 0 ; 7 fuites → 0).
- [ ] Token fantôme `--color-border-subtle` remplacé par `--pn-border-subtle` partout.
- [ ] Pilote bandeau-live migré sur tokens sémantiques (0 valeur magique dans `KpiLiveStrip.module.css`).
