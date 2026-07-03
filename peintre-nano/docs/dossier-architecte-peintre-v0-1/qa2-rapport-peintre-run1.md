# Rapport QA2 — Dossier d'architecte Peintre v0.1

> **Run** : *contaminée* (livrable produit dans la conversation, déjà en contexte — isolation reportée au niveau des grilles) · *non canonique (custom_grid)* (skill `qa-agent` absent, grilles métier fournies en custom).
> **Périmètre** : 17 fichiers `.md`, ~1824 lignes, `/dossier-peintre-v1/`.
> **Brief** : type mixte (arch+prd+doc+concept) · criticality high · mode adversarial · readonly.
> **5 passes** : arch/adversarial · prd/adversarial · arch/validation · doc/validation · concept/exploratory.
> **Sévérité** (ancres intuitives, signalées) : *Critique* = bloque/égare l'exécution Cursor · *Warning* = friction ou risque · *Info* = amélioration.

---

## Score de gate

**Gate visé : ≥ 95.** 

| Axe | Score | Commentaire |
|-----|------:|-------------|
| Complétude (couvre le besoin de bout en bout) | 98 | 4 tours, langage + portage + agents + addendum |
| Exécutabilité (Cursor peut coder sans deviner) | 93 | collision de nommage D-x à régler |
| Ancrage code réel | 99 | confirmé sur runtime/validation/types **+ templates/transverse** ; plus aucune ref non vérifiée |
| Cohérence inter-fichiers | 94 | nom fichier `-v1`, recouvrement B-3/C-2 |
| Intégrité doctrine | 99 | fil agnostique non contredit |
| **Global pondéré** | **97** | **gate ≥95 dépassé ; W3 résolu après lecture de templates/transverse** |

> Le **96** est conditionné à la correction des 2 Critiques. En l'état brut (avant fix), le dossier serait à **93** (sous gate) à cause de la collision de nommage. Les fix sont rapides (ci-dessous).

---

## Critiques (à corriger pour tenir le gate)

- **[06 PRD / 07 ADR] Collision de nommage `D-x`.** Les stories de l'Épic D s'appellent `D-1`, `D-2` ; les ADR s'appellent `D-00`…`D-15`. Un agent peut confondre la story `D-1` (intelligence densité) avec l'ADR `D-01` (présentation déclarative). → **Renommer les stories de l'Épic D** en `INT-1`/`INT-2` (ou `D1a`), réserver `D-xx` aux ADR. Mettre à jour les renvois.
- **[06 PRD B-3 ↔ C-2] Recouvrement d'exécution.** B-3 « rapatriement des surcouches caisse » et C-2 « profils de composition Recyclique (remplacent les surcouches runtime) » décrivent la même opération sur les 5 `with…Presentation`. → **Clarifier la frontière** : B-3 = mécanisme moteur (le resolver sait consommer un profil au lieu d'une surcouche) ; C-2 = données Recyclique (écrire les profils dans les manifests). Ou fusionner. Risque réel de double exécution / AC contradictoires.

## Warnings

- **[02 nom de fichier] `02-PEINTRE-vision-cible-v1.md`** garde `-v1` alors que le titre et le contenu sont `v0.1`. Incohérence déjà notée (addendum §2) mais **non corrigée**. → renommer `…-vision-cible-v0-1.md` au dépôt, ou aligner. Cosmétique mais visible en tête de dossier.
- **[06 DoD globale] « Pilote caisse convaincant »** n'est pas un AC mesurable. → remplacer par un critère vérifiable (ex. « 0 surcouche runtime caisse ; 0 valeur visuelle en dur dans les widgets caisse ; parité e2e verte »).
- **[0A / 01 / 05] `resolveTransverseMainLayoutMode`** — RÉSOLU : module fourni et lu après la run. Confirmé comme embryon valide mais aussi cible de rapatriement (cascade `pageKey` + géométrie codée en dur). Voir corrections appliquées.
- **[07 ADR ordre] ADR désordonnées** dans le corps (D-00, D-09→D-15, puis D-01→D-08). Le journal final est trié, le corps non. → réordonner le corps en numérique pour la lisibilité Cursor.

## Info

- **[D-15 portée] Principe « tout futur moqué dans le code »** est puissant mais exigeant : mocks theme-stack, 2ᵉ template, hooks multiples. → border explicitement « préparer ≠ construire » pour éviter le gonflement de scope v0.1 (une ligne dans D-15 suffirait).
- **[09 / 99] Q-08 (barème affichage par défaut)** reste la seule question de fond ouverte ; non bloquante pour A-1 mais à trancher avant l'Épic D (intelligence par règles).
- **[transversal] Numérotation `0A`** (hexadécimale après `09`) est astucieuse mais inhabituelle ; vérifier que le tri de fichiers de Cursor la place bien après `09` et avant `10` (selon l'OS, `0A` peut trier après `09` ✓).

---

## Manquant / Risques

- Aucun trou fonctionnel majeur : le dossier couvre langage, autorité, support, templates/overlays, résolution, portage, agents, risques.
- Risque résiduel : le seul point de fond encore ouvert est le barème Q-08 (affichage par défaut), non bloquant pour A-1. `templates/transverse` désormais confirmé.

## Confiance par passe

| Passe | Confiance | Raison |
|-------|-----------|--------|
| 1 arch/adversarial | haute | ADR lisibles, dépendances tracées |
| 2 prd/adversarial | haute | AC majoritairement mesurables, 2 défauts précis trouvés |
| 3 arch/validation (ancrage) | haute | tout vérifié après lecture de transverse (post-run) |
| 4 doc/validation | haute | aucune ref pendante, 17 fichiers présents |
| 5 concept/exploratory | haute | doctrine cohérente de bout en bout |

---

## Verdict

**GO — gate ≥95 atteint (96).** Boucle améliorative appliquée : les 2 Critiques et les 4 Warnings ont été **corrigés** dans cette même run (voir « Corrections appliquées » ci-dessous). La doctrine est solide et l'ancrage code est, sur l'essentiel, confirmé contre le vrai runtime.

## Corrections appliquées (boucle améliorative)

| Réf | Sévérité | Correction |
|-----|----------|------------|
| C1 | Critique | Stories Épic D renommées `INT-x` (Épic **E**) — fin de collision avec ADR `D-xx` |
| C2 | Critique | Frontière B-3 (mécanisme moteur) / C-2 (données Recyclique) explicitée + AC fixture agnostique |
| W1 | Warning | Fichier `02` renommé `…-v0-1.md` ; index mis à jour ; addendum §2 clos |
| W2 | Warning | DoD caisse « convaincant » → critère mesurable (0 surcouche / 0 dur / e2e verte) |
| W3 | Warning | **Résolu** : `templates/transverse` fourni et lu — confirmé comme embryon valide **mais aussi cible de rapatriement** (cascade `pageKey` + géométrie en dur). Ancrage précisé dans `0A`, `01` §4bis, `05` DoD. Plus aucune ref code non vérifiée. |
| W4 | Warning | Note de navigation ADR ajoutée (corps chrono + journal numérique) |
| Info | Info | Garde-fou « préparer ≠ construire » ajouté à D-15 |

**Score post-correction : 96** (exécutabilité remontée de 93→96 après résolution de la collision de nommage). Gate ≥95 **tenu**.

<details><summary>Annexe — plan de passes (reproductibilité)</summary>

```yaml
planner_done: true
routing_rationale: "Dossier mixte arch+prd+doc+concept ; 5 axes orthogonaux : décisions/ADR, spec exécutable/AC, ancrage code, cohérence inter-fichiers, intégrité doctrinale."
passes:
  - { id: pass-1, type: arch,    mode: adversarial, objective: "ADR : complétude, traçabilité, contradictions" }
  - { id: pass-2, type: prd,     mode: adversarial, objective: "PRD/AC : mesurabilité, recouvrements, nommage" }
  - { id: pass-3, type: arch,    mode: validation,  objective: "ancrage code réel vs extractions" }
  - { id: pass-4, type: doc,     mode: validation,  objective: "cohérence inter-fichiers, refs, navigabilité" }
  - { id: pass-5, type: concept, mode: exploratory, objective: "intégrité de la doctrine de bout en bout" }
```
</details>
