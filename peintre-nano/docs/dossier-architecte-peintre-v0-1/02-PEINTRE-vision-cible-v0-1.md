# 02-PEINTRE — Vision cible Peintre v0.1 (post-nano)

## 1. Définition de Peintre v0.1

**Peintre v0.1** = le passage de `peintre-nano` (frontend *de* Recyclique, présentation implicite et décisions métier dans le moteur) à un **moteur de composition UI agnostique** : il ne contient **aucune** décision propre à une application ; toute intention de présentation entre par **CREOS** (bus JARVOS). Recyclique devient *un consommateur* du moteur, au même titre que n'importe quelle future app de l'écosystème.

v0.1 = la **première version où le langage racine bas niveau et le moteur sont posés** : assez complets pour recoder Peintre proprement *et* reporter Recyclique dessus, mais sans préjuger de l'avenir agentique (dont les fondations sont réservées, pas codées).

Ce qui distingue v0.1 de nano :

| Axe | nano (aujourd'hui) | v0.1 (cible) |
|-----|--------------------|-----------| 
| Autorité métier | dans le moteur (alias, surcouches, couleurs en dur) | **hors moteur** : tout en CREOS depuis l'app |
| Composition | implicite, CSS modules par widget + surcouches runtime | **langage déclaratif CREOS** résolu en tokens + layout |
| Tokens | squelette de 6 couleurs, codés dans le moteur | **contrat de tokens** rempli par le theme CREOS de l'app |
| Autorité d'affichage | indistincte | **3 couches en grammaire unique** : défaut moteur → app → user (`04A`) |
| Support | responsive bricolé par widget | **adaptation au support centrale** : réarrangement, priorité, nature info/tactile (`04B`) |
| Layout | `if/else` + alias legacy dans le shell | **`LayoutResolver`** : merge des couches + résolution support |
| Avenir agentique | impossible | **hooks d'arbitrage inertes** réservés (`04A` §6) |
| Réutilisabilité | Recyclique only | **agnostique, multi-applications** |

## 2. Les trois couches de Peintre v0.1

```
   ENTRÉES (tout en CREOS — bus JARVOS) ─────────────────────┐
   • theme/tokens app   • profil composition app             │
   • prefs user (voix, poignées)  • ContextEnvelope (AR39)    │
   • support détecté (form factor / input / viewport)        │
└───────────────────────┬──────────────────────────────────┘
                        ▼
┌──────────────────────────────────────────────────────────┐
│  MODÈLE D'AUTORITÉ (04A) — grammaire unique               │
│  merge par champ : défaut moteur → app → user             │
│  + invariants AR39/required + override_policy             │
│  + CompositionArbiter (HOOK INERTE, réservé à l'âme)      │
└───────────────────────┬──────────────────────────────────┘
                        │ profil de composition effectif (+ provenance)
┌───────────────────────▼──────────────────────────────────┐
│  RÉSOLUTION (05 LayoutResolver) + ADAPTATION SUPPORT (04B)│
│  régions, colonnes, priorités, réarrangement, ergonomie  │
│  tactile, sacrifice par priorité — résolus en tokens (03)│
└───────────────────────┬──────────────────────────────────┘
                        │ régions + classes/tokens résolus
┌───────────────────────▼──────────────────────────────────┐
│  MOTEUR DE RENDU (existant, à durcir)                    │
│  shell, registry, slots, fallbacks, PageRenderer         │
│  rend des widgets APPLICATIFS (agnostique de leur métier)│
└──────────────────────────────────────────────────────────┘
        ▲ plus tard : l'INTELLIGENCE (08) se branche sur le
          hook d'arbitrage inerte et émet le MÊME CREOS
```

Tout entre **par le haut, en CREOS**. Le moteur ne *décide* rien de métier : il *résout* une superposition d'intentions. L'intelligence future ne remplace aucune couche — elle se branche sur le hook d'arbitrage (`04A` §6) et produit le même type de profil que l'app et le user. C'est ce qui rend l'ambition réaliste *et* sûre : personne ne génère de React, tout le monde parle composition CREOS.

## 3. Principe directeur unique

> **Toute intention de présentation entre par CREOS et s'exprime en intentions (pas en pixels). Le moteur ne décide rien d'applicatif : il résout défaut→app→user, adapte au support, et rend. Ce qu'un humain peut surcharger, un agent le pourra demain, dans la même grammaire.**

Corollaires :
- Un widget ne décide plus *comment* il est composé — l'app **déclare** l'intention, le user la surcharge, le moteur résout.
- Le moteur ne contient aucun nom de route, couleur, libellé ou règle d'une app (test d'agnosticité, index).
- Aucune valeur visuelle en dur hors le **contrat de tokens** (rempli par le theme CREOS de l'app, `03`).
- Le futur arbitre agentique a déjà sa place (hook inerte) ; v0.1 ne la comble pas mais ne la ferme jamais.

## 4. Frontière moteur / métier (condition de l'agnosticité)

Reprise et durcissement de `peintre-nano/docs/05-monorepo-et-extraction.md`.

**Appartient au MOTEUR (générique, agnostique)** :
- shell, providers, `RootShell`, régions ;
- `registry` (résolution `widget_type → composant`) ;
- modèle d'autorité (`04A`), LayoutResolver + adaptation support (`04B`, `05`), résolveur de tokens (`03`) ;
- `CompositionArbiter` (hook inerte), validation des manifests, AR39, mode dégradé.

**Appartient à l'APPLICATION (Recyclique = un consommateur, `domains/**`)** :
- widgets métier (caisse, réception, admin…) ;
- clients API, bindings `operation_id` ;
- **le theme CREOS** (couleurs, identité) et **les profils de composition** (priorités, emphase, per_support) ;
- autorité métier, permissions, parcours ;
- les manifests CREOS reviewables (writer = Recyclique).

**Règle de tranchage** : si un fichier du shell connaît un nom de route métier (`/cash-register/...`), un `module_key` métier, ou un libellé métier → il est mal placé. Il doit migrer vers un manifest (donnée) ou un domaine (code applicatif).

## 5. Trajectoire (rappel phasage / tours)

1. **Phase 1 — noyau langage agnostique** *(Tour 1 moteur)* : contrat tokens (`03`) → langage composition (`04`) → modèle d'autorité (`04A`) → adaptation support (`04B`) → templates & overlays (`04C`) → LayoutResolver (`05`) → rapatriement des décisions Recyclique hors du moteur. *Livre l'affichage convaincant ET l'agnosticité.*
2. **Phase 2 — portage Recyclique** *(Tour 2)* : Recyclique réécrit comme **consommateur** (theme CREOS + profils de composition + widgets), zéro décision dans le moteur. *Prouve l'agnosticité sur une vraie app.*
3. **Phase 3 — intelligence** *(branchée sur les hooks inertes de `04A`)* : palier règles (3a) puis génératif (3b). *Livre le « semblant d'intelligence » puis l'arbitre vivant.*

## 6. Critères de succès v0.1

- **Agnosticité prouvée** : zéro couleur/route/libellé/règle d'une app dans le moteur (lint + revue). Le theme et les priorités viennent *uniquement* du CREOS app.
- Contrat de tokens rempli par un theme CREOS ; zéro valeur visuelle en dur hors résolution de tokens.
- Profil de composition CREOS (composition + autorité + adaptation) validé par schéma, résolu par le LayoutResolver.
- Modèle d'autorité défaut→app→user opérationnel en **grammaire unique** ; user surcharge ce qu'`override_policy` autorise ; invariants AR39 tenus.
- **Adaptation support réelle** : le même écran se réarrange desktop/tablette/téléphone, respecte priorités + nature info/tactile, sans code par écran.
- `CompositionArbiter` inerte branché et testé (la place de l'âme existe).
- Le pilote caisse rendu **convaincant** et **adaptatif**, **sans** surcouche runtime ni alias dans le shell.
- Surface publique moteur documentée → une 2ᵉ app fictive pourrait le consommer en ne fournissant que du CREOS.
