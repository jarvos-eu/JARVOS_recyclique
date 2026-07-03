# 12-PEINTRE — Veille : principes à intégrer (réf. externe page-agent)

> Source d'inspiration analysée : un agent GUI in-page open-source (pilotage d'UI en langage naturel). **Verdict : s'inspirer, ne pas intégrer.** Les principes ci-dessous sont agnostiques (aucune dépendance au projet source) et se branchent sur `11` (doc agents), pas sur le moteur v0.1.

## 1. Distinction structurante à acter

Deux couches d'agent, à ne pas confondre :
- **Compositeur** (Peintre) : *décide* l'affichage, déclaratif CREOS. C'est le dossier actuel.
- **Conducteur** (réf. externe) : *actionne* une UI déjà rendue (clique, remplit, navigue) en langage naturel.

→ Complémentaires. Le conducteur est un **candidat pour la couche exécution de l'âme** (`11`), au-dessus du compositeur. À réserver comme hook, pas à construire en v0.1.

## 2. Principes à reprendre (agnostiques)

| Principe | Ce qu'on en fait |
|----------|------------------|
| **Conscience d'écran par DOM-texte** (pas screenshots) : léger, déterministe, testable | Aligne avec nos testids `data-*`. La surface de lecture agent (`11` §2.1) expose un **arbre sémantique texte** de l'écran résolu, pas une image. Moins cher, plus sûr. |
| **BYO-LLM** : le modèle n'est pas figé dans le produit | La surface agent (`11`) reste **agnostique du fournisseur LLM** : on expose des outils, on n'impose pas un modèle. |
| **Exposition via MCP Server** | Modèle propre pour publier la surface d'outils agent (`11` §2). À retenir comme forme d'exposition quand l'âme sera branchée. |
| **Actions bornées + confirmation** (l'agent propose, un garde valide) | Renforce notre invariant : l'agent **propose du CREOS**, le moteur valide/arbitre (`04A` §6, `11` §3). Même discipline côté *actions* : toute action passe un garde AR39. |

## 3. Ce qu'on NE reprend pas

- Le pilotage d'UI arbitraire (notre UI est composée par nous, pas « subie »).
- Toute dépendance runtime au projet source (on garde le principe, pas le code — licence permissive vérifiée si réutilisation future de bouts DOM-parsing).

## 4. Où ça se branche

- `11-PEINTRE-doc-agents` : ajouter une **sous-couche « exécution/conduite »** (inerte en v0.1) à côté de la sous-couche « composition ». Hook réservé, cohérent avec D-15.
- Rien dans le moteur v0.1. Rien dans le portage Recyclique.

## 5. Action

- [ ] Ajouter à `11` un hook inerte `AgentActionSurface` (conduite d'UI) distinct de la surface composition, documenté comme « réservé, principe validé par veille externe ».
- [ ] Noter DOM-texte comme format canonique de conscience d'écran agent (vs screenshots).
