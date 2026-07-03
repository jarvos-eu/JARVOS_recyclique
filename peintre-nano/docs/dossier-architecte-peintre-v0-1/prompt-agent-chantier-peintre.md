# Prompt agent — Chantier Peintre v0.1

## Ton rôle
Tu recodes **Peintre** (moteur UI agnostique) de `peintre-nano` → v0.1, et tu portes Recyclique dessus. Pack **PEINTRE** (3ᵉ pack doc Recyclique v2, à côté ARCH/MOD). Piste A (mocks OK).

## Règles non négociables
1. **Agnosticité (D-00)** : zéro couleur/route/libellé/règle d'une app dans le moteur. Tout entre par CREOS. Si un fichier moteur connaît du métier → bug.
2. **Grammaire unique (D-09)** : app, user, agent → même profil CREOS. Résolution = défaut moteur → app → user.
3. **AR39** : la composition n'affiche jamais ce que les contrats de données n'autorisent pas.
4. **Tout futur préparé en code (D-15)** : chaque « plus tard » = hook inerte/mock réel, jamais juste une note. Mais *préparer ≠ construire*.
5. **refs_first** : citer `_bmad-output/`, packs ARCH/MOD ; ne pas réécrire le PRD BMAD.

## Ordre de lecture
`index` → `01` (audit) → `0A` (ancrage code réel) → `02` (cible). Puis noyau : `03` `04` `04A` `04B` `04C` → `05`. Exécution : `06` (PRD). Décisions : `07`. Portage : `10`. Reste : `08` `09` `11` `12` `98` `99`.

## Ordre d'exécution
Épic **A** (tokens+resolveTheme, le plus rentable, sans dépendance) → **B** (LayoutResolver + templates + overlays) → **C** (portage Recyclique) → **E** (intelligence règles). Saut « D » volontaire (réservé aux ADR).

## Points d'injection confirmés (code réel, voir 0A)
- profil `presentation` = champ optionnel sur `PageSlotPlacement` (rétrocompat, parser ignore l'inconnu)
- `PresentationSurface` autour du `<C>` dans `PageRenderer.renderPlacements`
- LayoutResolver enveloppe `buildPageManifestRegions` + généralise `mapSlotIdToShellRegion → mapSlotToRegion(slot, template)`
- validation : dupliquer le bloc `widgetProps` dans `parsePageManifestJson` ; règles additives dans `validateManifestBundle` ; overlay auto-autorisé (allowlist = registre)
- `templates/transverse` = à généraliser **et nettoyer** (cascade `pageKey` en dur → donnée)

## À trancher avant (HITL Strophe)
Q-08 (barème défaut — un défaut minimal 3 règles existe déjà, `04B` §7bis) · versioning modules publiés (`04` §6bis).

---

## Glossaire (15 termes)
- **Shell** : cadre de pièces fixes d'une page (header/nav/main/aside/footer).
- **Région** : une zone du template courant (nb libre selon template).
- **Rôle de présentation** : étiquette sur un slot (hero/body/toolbar…), résolue dans une région.
- **LayoutTemplate** : géométrie déclarée en CREOS (le moteur ne fige pas le nb de zones).
- **Overlay** : strate au-dessus du template (raccourcis clavier, modale), pas une région.
- **Profil `presentation`** : intentions de composition déclarées (emphasis/density/region…).
- **Provenance** : d'où vient chaque champ résolu (défaut/app/user/agent).
- **CompositionArbiter** : hook d'arbitrage (inerte en v0.1, place de l'âme).
- **Prise inerte** : interface/hook/mock présent mais sans effet (D-15).
- **Contrat de tokens** : slots sémantiques exposés par le moteur, remplis par le theme app.
- **Theme CREOS** : manifest app qui remplit le contrat (couleurs, identité).
- **Support profile** : form factor + input + viewport + orientation.
- **display_priority** : quoi sacrifier quand l'espace manque.
- **override_policy** : jusqu'où le user peut surcharger (déclaré par l'app).
- **AR39** : OpenAPI > ContextEnvelope > CREOS > prefs UI.

## Schéma avant/après (écran caisse)
```
NANO (aujourd'hui)                    v0.1 (cible)
RuntimeDemoApp.tsx :                   PageManifest (donnée) :
  if path==='/cash-register/sale'        slot main:
  withKioskSaleDashboard(...)              presentation:{region:hero,
  hide_register_selection_row              emphasis:primary}
  #2e7d32 en dur dans CSS                theme CREOS Recyclique: brand.6
  → décidé DANS le moteur               → déclaré, résolu PAR le moteur
```
