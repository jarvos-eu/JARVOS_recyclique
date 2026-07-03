# Rapport QA2 — Run 2 (vérification post-correction) — Dossier Peintre v0.1

> **Nature** : 2ᵉ boucle QA2, **run de vérification post-fix**. Objectif : confirmer que les 6 corrections de la run 1 ont tenu sans régression, traquer les effets de bord des édits, et balayer un angle neuf (testabilité réelle des AC).
> **Run** : *contaminée* (dossier en contexte → isolation au niveau des grilles) · *non canonique (custom_grid)* (skill `qa-agent` absent).
> **Périmètre** : 18 fichiers `.md` + rapport run 1.
> **5 passes** : non-régression (doc) · séquençage post-renommage (prd/adversarial) · ADR post-édits (arch) · ancrage transverse (arch) · testabilité réelle des AC (concept, angle neuf).
> **Ancres de sévérité** : *Critique* = bloque/égare Cursor · *Warning* = friction · *Info* = polish.

---

## Score de gate

| Axe | Run 1 | Run 2 | Commentaire |
|-----|------:|------:|-------------|
| Complétude | 98 | 98 | inchangé |
| Exécutabilité | 96 | 97 | parité B-4 rendue testable (N1) |
| Ancrage code réel | 99 | 99 | transverse confirmé, cohérent sur 3 emplacements |
| Cohérence inter-fichiers | 94 | 98 | régression de séquence (R1) corrigée |
| Intégrité doctrine | 99 | 99 | fil non contredit |
| **Global pondéré** | **97** | **98** | **gate ≥95 tenu et amélioré** |

---

## Régression introduite par la run 1 (trouvée et corrigée)

- **[R1 — 06 PRD] Séquence d'épics A→B→C→E + en-tête obsolète.** Le fix C1 (renommage Épic D→E pour éviter la collision avec les ADR `D-xx`) avait laissé : (a) la règle de séquençage en tête disant encore « A → B → C → **D** », (b) un saut alphabétique inexpliqué A/B/C/E déroutant. → **Corrigé** : en-tête mis à « A → B → C → E » + note explicite que le saut « D » est volontaire (identifiant réservé aux ADR). C'est le type même de défaut qu'une 2ᵉ boucle doit attraper : un fix qui en crée un autre.

## Finding neuf (angle non couvert run 1)

- **[N1 — 06 PRD B-4 AC3] « Parité visuelle » non vérifiable telle quelle.** Un agent ne peut pas tester « parité visuelle » sans méthode. → **Corrigé** : méthode ajoutée (snapshot DOM sur les testids `data-transverse-*` déjà présents dans le code réel, ou screenshot-diff). Réutilise un actif identifié à l'ancrage (`0A`).

## Non-régression confirmée (les 6 corrections run 1 tiennent)

| Fix run 1 | État run 2 |
|-----------|-----------|
| C1 collision `D-x` → `INT-x`/Épic E | tenu (corps du dossier propre ; seul effet de bord = R1, corrigé) |
| C2 frontière B-3/C-2 | tenu, distinction nette (mécanisme moteur vs données Recyclique + fixture agnostique) |
| W1 renommage fichier `02` | tenu (aucune réf à l'ancien nom hors rapport run 1 descriptif) |
| W2 DoD caisse mesurable | tenu |
| W4 note navigation ADR | tenue ; journal D-00→D-15 complet et tracé |
| Info garde-fou D-15 | présent (« préparer ≠ construire ») |

## Ancrage transverse — vérifié cohérent

L'intégration post-run-1 de `templates/transverse` est **cohérente sur ses 3 emplacements** (`01` §4bis, `0A`, `05` DoD) : même diagnostic (cascade `pageKey` + géométrie en dur = cible de rapatriement), même renvoi `04B`/`04C`, même actif préservé (testids). Aucune contradiction.

## Manquant / Risques

- Aucun trou fonctionnel neuf.
- Seul point de fond ouvert (inchangé) : **Q-08** (barème « affichage par défaut »), non bloquant pour démarrer A-1, à trancher avant l'Épic E.

## Confiance par passe

| Passe | Confiance | Raison |
|-------|-----------|--------|
| 1 non-régression | haute | corrections tenues, 1 effet de bord trouvé |
| 2 séquençage post-renommage | haute | régression R1 identifiée précisément |
| 3 ADR post-édits | haute | journal complet, dépendances cohérentes |
| 4 ancrage transverse | haute | 3 emplacements cohérents |
| 5 testabilité AC (neuf) | haute | 1 AC non testable trouvée et corrigée |

---

## Verdict

**GO — gate ≥95 tenu et amélioré (98).** La 2ᵉ boucle a fait son travail : elle a attrapé **une régression que le premier fix avait introduite** (R1, séquence d'épics) et **un défaut neuf** sur un angle non sondé avant (N1, parité visuelle non testable). Les deux sont corrigés dans cette run. Les 6 corrections de la run 1 tiennent toutes. Le dossier est stable, cohérent, entièrement ancré sur le code réel, et ses critères d'acceptation sont vérifiables par un agent.

**Recommandation** : geler le dossier ici. Une 3ᵉ boucle aurait un rendement marginal faible (les passes 3/4 n'ont rien trouvé ; seules les passes ciblant les édits récents ont produit des findings — signe de convergence). Prochain mouvement utile = exécution Cursor (Épic A-1) + arbitrage Q-08, pas davantage de QA.

<details><summary>Annexe — plan de passes run 2</summary>

```yaml
planner_done: true
routing_rationale: "Run de vérif post-fix : passes recentrées sur non-régression + effets de bord des édits (séquence, ADR, ancrage transverse), plus un angle neuf (testabilité réelle des AC) non couvert en run 1."
passes:
  - { id: r2-1, type: doc,     mode: validation,  objective: "non-régression des 6 corrections run 1" }
  - { id: r2-2, type: prd,     mode: adversarial, objective: "séquençage/renvois après renommage Épic D→E" }
  - { id: r2-3, type: arch,    mode: validation,  objective: "journal ADR + garde-fou D-15" }
  - { id: r2-4, type: arch,    mode: validation,  objective: "cohérence intégration transverse sur 3 emplacements" }
  - { id: r2-5, type: concept, mode: exploratory, objective: "testabilité réelle des AC par un agent (angle neuf)" }
```
</details>
