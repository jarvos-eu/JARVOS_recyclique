# 07-PEINTRE — ADR : décisions structurantes

> Statuts : **Proposed** (à valider HITL), **Accepted**, **Superseded**. Toutes les décisions ci-dessous sont **Proposed** tant que Strophe n'a pas tranché.
>
> **Ordre de lecture** : le corps suit l'ordre *chronologique de décision* (fondatrices D-00, D-09→D-15 d'abord, puis D-01→D-08 issues du premier cadrage). Pour une lecture *numérique*, suivre le **journal en fin de fichier** (trié), qui donne aussi les dépendances. Les deux vues pointent les mêmes décisions.

## D-00 — Agnosticité totale du moteur (décision fondatrice)
**Statut** : Proposed (surplombe toutes les autres).
**Contexte** : `peintre-nano` contient des décisions Recyclique (couleurs, routes, libellés, surcouches) dans le moteur. Bloque la réutilisation par d'autres apps JARVOS.
**Décision** : le moteur ne contient **aucune** décision propre à une application. Tout (theme, identité, priorités, contraintes) entre par **CREOS** (bus JARVOS). Recyclique est *un consommateur*.
**Test** : si un fichier du moteur connaît un nom/couleur/route/règle d'une app → bug.
**Conséquences** : theme déplacé côté app (`03` §0) ; priorités déclarées en CREOS (`04A` §5) ; rapatriement des alias hors du shell (D-04).

## D-09 — Grammaire unique app / user / agent
**Statut** : Proposed.
**Décision** : app, utilisateur et (futur) agent expriment l'intention de présentation dans le **même** vocabulaire CREOS de composition. La résolution superpose défaut moteur → app → user par deep-merge (`04A`).
**Justification** : cohérence de fusion, et surtout l'agent futur se branche sans format supplémentaire à réconcilier.
**Alternative écartée** : *canal user séparé* → dette de pont + 4ᵉ format pour l'agent.

## D-10 — Hooks d'arbitrage inertes réservés à l'âme
**Statut** : Proposed.
**Décision** : v0.1 pose un `CompositionArbiter` **présent, appelé, mais pass-through**. Le futur « final cut » agentique s'y branchera sans refonte.
**Justification** : « poser les fondations qui ne rendent jamais l'agentique impossible » sans coder l'agent maintenant.
**Conséquence** : le pipeline (`05`) passe toujours par l'arbitre ; aucun court-circuit autorisé.

## D-11 — Theme par contrat de tokens rempli en CREOS
**Statut** : Proposed.
**Décision** : le moteur expose un **contrat de tokens** (slots sémantiques + défauts neutres) ; l'app fournit un **theme CREOS** qui le remplit (`03` §0, §10). Aucune couleur de marque dans le moteur.
**Alternative écartée** : *palette dans le moteur* → viole D-00.

## D-12 — Adaptation au support comme capacité centrale du moteur
**Statut** : Proposed.
**Décision** : le réarrangement par support (form factor / input / priorité / nature info-tactile) est une fonction **du moteur** (`04B`), pilotée par CREOS, pas un responsive par widget.
**Justification** : besoin explicite multi-support ; condition d'un rendu « dans les bons clous » desktop/tablette/téléphone/tactile.

## D-13 — Géométrie de layout par templates déclarés (le moteur ne fige pas le nombre de zones)
**Statut** : Proposed.
**Contexte** : les 5 régions sont aujourd'hui une **constante du moteur**. Figer ce nombre fermerait la porte au plein écran, dashboards variables, tactile localisé.
**Décision** : la géométrie devient un **LayoutTemplate déclaré en CREOS** (`04C`). v0.1 **livre 1 template** (`standard-5`, identique à l'actuel) mais le moteur résout un template de longueur libre. « 5 » = choix de livraison, pas loi du moteur.
**Alternative écartée** : *garder 5 régions en dur* → rigide, anti-agnostique, bloque les supports futurs.
**Conséquence** : `mapSlotIdToShellRegion` → `mapSlotToRegion(slotId, template)` ; `buildPageManifestRegions` itère sur `template.regions`.

## D-14 — Overlays = strate au-dessus du template (pas des régions)
**Statut** : Proposed.
**Décision** : les overlays (raccourcis clavier, onboarding IA, modales) vivent dans une **couche `OverlayHost`** au-dessus du template, gérés en pile (focus trap, capture). v0.1 = squelette + **1 pilote** (`keyboard-shortcuts`) + **hook inerte** `ShortcutEditor` pour l'édition live future (façon Ableton).
**Justification** : besoins overlays déjà identifiés ; un overlay n'est pas une zone de fond. Cohérent avec la doctrine « fondations sans construction spéculative ».
**Conséquence** : overlay = widget registry standard (AR39 respecté) ; `remap()` réservé en v0.1.

## D-15 — Tout branchement futur est préparé dans le code, pas seulement documenté (principe transversal)
**Statut** : Proposed (surplombe tous les « plus tard » du dossier).
**Contexte** : Strophe — *« tous les branchements futurs, il faut qu'ils soient annoncés, préparés, moqués, peu importe »*.
**Décision** : chaque capacité repoussée à « plus tard » doit exister en v0.1 comme **prise inerte concrète dans le code** (interface posée, hook pass-through, ou mock data), **jamais** comme simple intention dans un doc. Activer la capacité = remplacer l'implémentation inerte, sans toucher au reste.
**Application aux « plus tard » du dossier** :
- intelligence générative 3b → hook `CompositionArbiter` inerte (`04A` §6) ✓
- édition live raccourcis → `ShortcutEditor.remap` no-op réservé (`04C` §6) ✓
- agent-âme + mémoire → surface tools posée, `ArbitrationContext` extensible (`11`) ✓
- **themes multiples (Q-10)** → le résolveur accepte une **pile** de themes ; v0.1 n'en empile qu'un, mais l'API et un **mock à 2 themes** prouvent l'empilage (`03`)
- **templates additionnels (Q9)** → mécanisme template + `standard-5` livré ; un **2ᵉ template mocké** (non monté) prouve la géométrie variable (`04C`)
- prefs multi-device (Q-07) → champ `pref_scope` présent même si un seul niveau câblé
**Justification** : évite la dette « on verra » ; garantit qu'aucune porte n'est fermée *en pratique*, pas seulement *en principe*.
**Conséquence** : chaque story « réservée » porte un AC « prise inerte + test prouvant qu'elle est appelée/réservée ».
**Garde-fou (préparer ≠ construire)** : une prise inerte est *minimale* — une interface, un hook pass-through, ou un mock data non monté. Si « préparer » exige plus de quelques heures ou un sous-système réel, ce n'est plus une prise inerte : re-trancher en HITL plutôt que gonfler le scope v0.1.

---

## D-01 — La présentation devient déclarative (profil CREOS), pas impérative
**Statut** : Proposed.
**Contexte** : aujourd'hui la présentation vit dans les CSS modules par widget + 5 surcouches `widgetProps` patchées au runtime. Non extractible, incohérent.
**Décision** : introduire un profil `presentation` CREOS (vocabulaire fermé d'intentions) résolu par le moteur. Les widgets déclarent des intentions, pas des styles.
**Alternatives écartées** :
- *Theming Mantine seul* : ne couvre pas le layout ni la composition par contexte ; resterait du code par widget.
- *Tailwind* : interdit par ADR P1 (`references/peintre/2026-04-01_adr-p1-p2…`).
**Conséquences** : nouveau schéma à maintenir ; CI CREOS à étendre ; gain = extractibilité + cohérence + pont vers l'intelligence.

## D-02 — Tokens à deux niveaux (primitif / sémantique)
**Statut** : Proposed.
**Décision** : `tokens.css` séparé en primitifs (palette) et sémantiques (usage). Widgets consomment **uniquement** le niveau sémantique.
**Justification** : permet theming futur (mode sombre, theme par app de l'écosystème) sans toucher aux widgets ; condition de réutilisabilité v1.
**Conséquence** : lint interdisant la consommation de primitifs par les widgets.

## D-03 — Un seul vocabulaire de tokens côté widgets ; Mantine remappé
**Statut** : Proposed.
**Contexte** : 7 fichiers fuient `--mantine-*`, double système.
**Décision** : mapper le thème Mantine sur `--pn-*` ; interdire `--mantine-*` dans les CSS modules.
**Alternative écartée** : *adopter `--mantine-*` comme vocabulaire* → couplerait Peintre à Mantine, contraire à la réutilisabilité moteur.

## D-04 — Le shell générique ne connaît aucune route ni libellé métier
**Statut** : Proposed.
**Contexte** : `RuntimeDemoApp` contient ~15 constantes de routes caisse + cascade de routage manuel.
**Décision** : routage déclaratif (`aliases[]`/`path_pattern` dans le NavigationManifest) + LayoutResolver générique. Toute connaissance métier dans le shell = bug.
**Conséquence** : migration des alias en données ; règle de revue : « le shell ne doit jamais matcher un nom de route métier ».

## D-05 — L'intelligence produit du profil présentation, jamais du React ni de la donnée
**Statut** : Proposed (cœur de la trajectoire).
**Décision** : la couche intelligence (règles puis générative) **émet un profil `presentation` CREOS** validé par schéma avant rendu. Elle ne génère pas de composants, ne touche pas aux `operation_id`, ne contourne pas AR39.
**Justification** : rend l'ambition « adaptation à la volée » réaliste et sûre — l'IA choisit des intentions dans un vocabulaire fermé déjà rendu par le moteur ; le mode dégradé garantit qu'elle ne casse jamais le métier.
**Alternative écartée** : *IA générant du JSX/CSS à la volée* → ingouvernable, non validable, casse l'extractibilité et la sécurité métier.

## D-06 — Palier règles avant palier génératif
**Statut** : Proposed.
**Décision** : livrer d'abord l'intelligence **déterministe par règles** (densité/emphase/réorg selon viewport+contexte), avant tout LLM.
**Justification** : c'est le « semblant d'intelligence » demandé en premier ; déterministe, testable, zéro coût d'inférence, zéro risque. Le palier génératif réutilise exactement le même point de sortie (le profil présentation).

## D-07 — `presentation` strict (`additionalProperties:false`) dès le départ
**Statut** : Proposed.
**Contexte** : `widget-declaration.schema.json` est `additionalProperties:true` (absorbe l'évolution) — c'est précisément ce qui a permis la dérive `widgetProps`.
**Décision** : le profil présentation est **fermé** dès v1. Étendre = PR explicite sur le schéma.
**Justification** : empêcher la reconstitution d'un bricolage ad hoc.

## D-08 — Extraction physique reportée ; frontières durcies maintenant
**Statut** : Proposed (aligné `docs/05-monorepo-et-extraction.md`).
**Décision** : pas de split repo en v1. On durcit la frontière moteur/métier et on documente la surface publique. L'extraction reste une évolution de packaging future.
**Justification** : éviter coûts de versioning/sync prématurés tant que contrats et frontend évoluent à la même cadence.

## Journal
| ID | Décision | Statut | Dépend de |
|----|----------|--------|-----------|
| **D-00** | **Agnosticité totale du moteur** | Proposed | — (fondatrice) |
| D-01 | Présentation déclarative | Proposed | D-00 |
| D-02 | Tokens 2 niveaux | Proposed | D-00 |
| D-03 | Vocabulaire unique, Mantine remappé | Proposed | D-02 |
| D-04 | Shell sans métier | Proposed | D-00, D-01 |
| D-05 | IA → profil présentation only | Proposed | D-01, D-07, D-09 |
| D-06 | Règles avant génératif | Proposed | D-05 |
| D-07 | Profil strict | Proposed | D-01 |
| D-08 | Extraction reportée | Proposed | D-04 |
| **D-09** | **Grammaire unique app/user/agent** | Proposed | D-00, D-01 |
| **D-10** | **Hooks d'arbitrage inertes (âme)** | Proposed | D-09 |
| **D-11** | **Theme par contrat de tokens CREOS** | Proposed | D-00, D-02 |
| **D-12** | **Adaptation support centrale** | Proposed | D-00 |
| **D-13** | **Géométrie par templates (nb zones libre)** | Proposed | D-00, D-12 |
| **D-14** | **Overlays = strate + hook édition live inerte** | Proposed | D-00, D-10 |
| **D-15** | **Tout futur préparé/moqué dans le code (pas que doc)** | Proposed | D-10 (généralise) |
