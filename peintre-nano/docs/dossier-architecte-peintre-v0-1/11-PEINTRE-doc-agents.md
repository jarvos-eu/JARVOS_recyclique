# 11-PEINTRE — Doc agents : outillage de l'âme future (Tour 3)

> **But** : décrire la **surface que Peintre expose à un agent** pour piloter l'affichage — le squelette d'outils que « l'âme » (final cut agentique) utilisera. v0.1 **n'implémente pas l'agent** ; il garantit que la surface existe, est stable, et que tout passe par les mêmes canaux sûrs que l'app et le user (grammaire unique, `04A` / `D-09`).
> **Public** : agents (Cursor en dev, puis l'agent Peintre incarné) + architecte.
> **Invariant** : un agent ne fait **rien de plus** qu'un humain via l'UI. Il émet du CREOS de composition, validé par schéma, borné par AR39. Pas de React, pas de données, pas de contournement.

## 1. Ce qu'un agent peut faire (et ne peut pas)

| L'agent PEUT | L'agent NE PEUT PAS |
|--------------|---------------------|
| lire le profil de composition effectif + provenance (`04A` §3) | générer du React / CSS |
| lire le `support_profile`, le ContextEnvelope (autorisations) | afficher un slot non autorisé par AR39 |
| proposer un fragment de profil `presentation` (mêmes champs que l'app/user) | écrire dans les contrats / OpenAPI |
| proposer un `LayoutTemplate` ou un `overlay` (validé par schéma) | inventer un `operation_id` ou une donnée |
| s'exprimer via le hook `CompositionArbiter` (`04A` §6) | court-circuiter la validation ou le mode dégradé |

L'agent est un **émetteur de CREOS de composition de plus**, à côté de l'app et du user. Rien de neuf dans le pipeline : il se branche sur le hook déjà posé.

## 2. La surface d'outils (tools exposés à l'agent)

Décrits en intention ; l'implémentation viendra avec l'agent. v0.1 garantit que ces lectures/écritures *existent* et sont sûres.

### 2.1 Lecture (sans effet de bord) — disponibles dès v0.1
```
peintre.readEffectiveProfile(pageKey) → CompositionProfile + provenance
peintre.readSupport()               → support_profile (form factor/input/viewport)
peintre.readContext()               → marqueurs ContextEnvelope autorisés (lecture AR39)
peintre.readTemplate(pageKey)       → LayoutTemplate courant
peintre.listOverlays()              → overlays disponibles + état
peintre.listShortcuts()            → bindings (réutilise ShortcutEditor.list, 04C §6)
```

### 2.2 Proposition (écriture bornée) — interface posée, effet réservé en v0.1
```
peintre.proposeProfile(scope, fragment) → ProposalResult
   scope = page | slot | widget ; fragment validé contre le schéma 04/04A/04B
peintre.proposeTemplate(template)       → ProposalResult   (validé contre layout_template)
peintre.proposeOverlay(overlay)         → ProposalResult   (validé contre overlay)
peintre.remapShortcut(actionId, binding)→ réservé (no-op v0.1, 04C §6)
```

Toute proposition passe par : **validation schéma → invariants AR39/required (`04A` §4) → `CompositionArbiter`**. En v0.1 l'arbitre est pass-through, donc une proposition d'agent est *acceptée syntaxiquement mais sans effet* (réservation). Quand l'âme s'allume, on remplace l'arbitre inerte par l'arbitre vivant, et ces mêmes tools deviennent effectifs — **zéro changement de surface**.

## 3. Le contrat de l'agent : émettre, pas agir

Un agent ne « manipule pas l'écran ». Il **propose un profil**, le moteur **résout**. C'est la même discipline que l'app (qui déclare) et le user (qui surcharge). Conséquence : tout ce qu'un agent produit est **inspectable, validable, réversible, traçable** (provenance `agent` dans le merge `04A` §3).

```
agent → proposeProfile(...) → [valide schéma] → [AR39] → [arbiter] → profil effectif → rendu
                                   │ rejet           │ rejet
                                   ▼                  ▼
                            profil inchangé (jamais d'écran cassé)
```

## 4. Préparation des sous-équipes d'agents (vision Strophe)

La vision : un agent Peintre « âme/visionnaire » orchestrant des sous-agents spécialisés (« édition, curation, exposition… »). v0.1 ne les crée pas, mais la surface §2 est **conçue pour être déléguée** :
- chaque sous-agent opère sur un **scope** (page/slot/widget) → délégation naturelle ;
- la **provenance** distingue les contributions (quel sous-agent a proposé quoi) ;
- le `CompositionArbiter` est le point où l'agent-âme **arbitre** entre propositions concurrentes (app vs user vs sous-agents) — c'est *là* que vivra le « final cut ».

→ v0.1 livre le **lieu** de l'arbitrage (le hook) et le **langage** de la délégation (scope + provenance), pas les agents.

## 5. Mémoire & soul (hors v0.1, place réservée)

L'agent vivant aura mémoire et continuité (« incarné dans son code, ses données, sa mémoire »). v0.1 ne persiste rien d'agentique, mais :
- le profil effectif + provenance est **sérialisable** → un futur agent peut journaliser ses décisions ;
- le hook `CompositionArbiter` reçoit un `ArbitrationContext` **extensible** → on y branchera la mémoire sans changer la signature.

C'est le strict minimum pour « ne jamais rendre l'âme impossible », sans la coder.

## 6. Doc d'usage pour agents Cursor (dev, immédiat)

Pendant le dev (avant l'âme), Cursor **est** l'agent qui écrit les manifests/themes. Cette doc lui dit :
- **toujours** déclarer l'intention de présentation en CREOS (jamais en CSS module ou surcouche runtime) ;
- **toujours** valider contre les schémas (`04`/`04A`/`04B`/`04C`) via la chaîne `validation/` ;
- **jamais** réintroduire d'alias de route ou de couleur dans le moteur (test d'agnosticité, index) ;
- utiliser `readEffectiveProfile` pour comprendre la provenance avant de modifier (qui a déjà décidé quoi).

## 7. Definition of Done (doc agents)

- [ ] Surface de lecture (§2.1) documentée et **disponible** (lectures pures, sans effet).
- [ ] Surface de proposition (§2.2) **interface posée**, effet réservé (validation OK, arbitre pass-through).
- [ ] Provenance `agent` supportée dans le merge (`04A` §3).
- [ ] `ArbitrationContext` extensible (mémoire future branchable sans rupture de signature).
- [ ] Doc Cursor (§6) intégrée aux références agent (`references/` pour consommation).
