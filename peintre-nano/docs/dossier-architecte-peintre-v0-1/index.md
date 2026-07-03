# Dossier d'architecte — Peintre v0.1 (post-nano : moteur de composition agnostique de l'écosystème JARVOS)

> **Statut** : cadrage normatif, brouillon pour exécution Cursor. Promotion BMAD après HITL Strophe.
> **Audience** : agent de dev Cursor + architecte. Sans contexte projet préalable requis (le dossier est autoporteur).
> **Convention fichiers** : `NN-PEINTRE-slug.md` — code après le numéro, comme les packs `ARCH` / `MOD`.
> **Source d'autorité amont** : ne pas réécrire ; **citer** `references/peintre/`, `references/dossier-architecte-externe-v2/` (pack ARCH), `references/protocole-modules-recyclique/` (pack MOD), `_bmad-output/`.
> **Méthode de production** : passes successives, **édition inline** (jamais de v2/v3 concurrentes). Tour 1 = moteur · Tour 2 = portage Recyclique · Tour 3 = doc agents · puis addendum de révision.

---

## Le principe au-dessus de tout : agnosticité

**Peintre ne contient aucune décision propre à une application.** Couleurs, identité, libellés, priorités d'affichage, contraintes métier : **tout arrive en CREOS depuis l'application appelante**. Recyclique est *une* app de l'écosystème JARVOS, pas la référence. CREOS est l'unité de base du **bus JARVOS** (« orchestration hypothalamus ») : c'est le seul canal par lequel l'intention de présentation entre dans Peintre.

Test de l'agnosticité (à appliquer à chaque ligne du moteur) : *si un fichier du moteur connaît un nom, une couleur, une route ou une règle métier d'une app, c'est un bug.*

## Problème en une phrase

`Peintre_nano` **place** correctement les choses (liaison Recyclique→Peintre fonctionnelle, widgets au bon slot) mais ne sait pas les **composer** : il manque (a) un **langage de composition adaptatif déclaratif** porté par CREOS, (b) un **modèle d'autorité d'affichage** défaut→app→user, (c) une **adaptation au support** (desktop/tablette/téléphone/tactile) dans le moteur. De plus le shell « générique » est pollué par des **décisions Recyclique codées en dur** — violation directe de l'agnosticité. Résultat : rendu plat, non adaptatif, non réutilisable.

## Thèse directrice

L'« affichage convaincant » (court terme) et le « moteur agnostique réutilisable + intelligence d'adaptation » (cible) **sont le même chantier**. On construit un **langage de composition déclaratif** exprimé en CREOS ; l'utilisateur le surcharge dans la **même grammaire** ; et plus tard l'intelligence agentique ne fera que **produire ce même CREOS** — jamais générer du React ni toucher aux données.

**Invariants non négociables du dossier :**
1. **Agnosticité** — zéro décision applicative dans le moteur ; tout entre par CREOS.
2. **Grammaire unique** — app, user et (futur) agent s'expriment dans le même langage CREOS de composition ; la résolution superpose défaut moteur → contrat app → préférence user.
3. **AR39 inviolable** — la composition n'affiche jamais ce que les contrats de données n'autorisent pas.
4. **Place réservée à l'âme** — v0.1 pose des **hooks d'arbitrage inertes** (pass-through) pour le futur « final cut » agentique, sans le coder ni le rendre jamais impossible.

---

## Ordre de lecture

| # | Fichier | Rôle | Pour qui |
|---|---------|------|----------|
| 01 | `01-PEINTRE-audit-etat-reel.md` | Audit de vérité terrain, preuves chiffrées, anti-patterns nommés | architecte + agent |
| 0A | `0A-PEINTRE-ancrage-code-reel.md` | **Ancrage code réel** : points d'injection exacts (types/registry/PageRenderer/runtime) | agent |
| 02 | `02-PEINTRE-vision-cible-v0-1.md` | Cible Peintre v0.1 : agnosticité, 3 couches, frontière moteur/métier, trajectoire | architecte |
| 03 | `03-PEINTRE-design-tokens-spec.md` | Système de tokens sémantiques — **contrat** rempli par le theme CREOS de l'app | agent |
| 04 | `04-PEINTRE-creos-presentation-profile.md` | Langage CREOS de composition : profil `presentation` déclaratif (schéma + sémantique) | architecte + agent |
| 04A | `04A-PEINTRE-modele-autorite-affichage.md` | **Modèle d'autorité défaut→app→user** en grammaire unique CREOS ; hooks d'arbitrage inertes | architecte + agent |
| 04B | `04B-PEINTRE-adaptation-support-spec.md` | **Adaptation au support** : breakpoints, réarrangement, priorité, nature info/tactile | architecte + agent |
| 04C | `04C-PEINTRE-templates-et-overlays.md` | **Templates à géométrie variable** (le moteur ne fige pas le nb de zones) + **couche overlays** (pilote raccourcis clavier) | architecte + agent |
| 05 | `05-PEINTRE-layout-resolver-spec.md` | `LayoutResolver` : pipeline de résolution, superposition des couches, rapatriement des alias | agent |
| 06 | `06-PEINTRE-prd-chantier.md` | PRD du chantier : épics, stories, AC, séquençage, definition of done | agent + PO |
| 07 | `07-PEINTRE-adr-decisions.md` | ADR : décisions structurantes (D-01…D-0x), statuts, alternatives | architecte |
| 08 | `08-PEINTRE-intelligence-roadmap.md` | Brique d'intelligence : palier règles (3a) puis génératif (3b), garde-fous | architecte |
| 09 | `09-PEINTRE-risques-et-questions-hitl.md` | Risques, dette assumée, questions ouvertes nécessitant arbitrage Strophe | architecte + PO |
| 10 | `10-PEINTRE-portage-recyclique.md` | **Tour 2** : guide concret de portage Recyclique sur le langage (theme CREOS, migration surcouches, alias) | agent |
| 11 | `11-PEINTRE-doc-agents.md` | **Tour 3** : surface d'outils exposée à un agent (l'outillage de l'âme future) | agent + architecte |
| 12 | `12-PEINTRE-veille-page-agent.md` | Veille : principes agent à intégrer (hooks inertes, DOM-texte) | architecte |
| 98 | `98-PEINTRE-revue-senior.md` | Revue architecte senior : findings & plan | architecte |
| 99 | `99-PEINTRE-addendum-revision.md` | **Addendum** : trous comblés, bilan de complétude | architecte + agent |
| — | `prompt-agent-chantier-peintre.md` | Prompt d'entrée agent Cursor (quoi lire, quelles règles) | agent |
| — | `qa2-rapport-peintre-run1/run2.md` | QA2 du pack (gate 98) | architecte |

> **Pack PEINTRE** = 3ᵉ pack de la doc Recyclique v2 (à côté de ARCH et MOD), même convention `NN-PEINTRE-slug`. Chantier de **Piste A** (Peintre, mocks OK) : pas besoin d'attendre l'API Recyclique (Piste B) pour l'exécuter.

**Prérequis de lecture** : `01` (état) + `0A` (ancrage code) + `02` (cible) avant tout code. Le **noyau langage v0.1** = `03` (tokens-contrat) + `04` (composition) + `04A` (autorité) + `04B` (support), résolus par `05` (LayoutResolver). `0A` donne les points d'injection exacts dans le code réel.

---

## Phasage global

- **Phase 0 — Audit** *(fait dans ce dossier, à confirmer sur repo vivant)* → `01`
- **Phase 1 — Noyau langage agnostique** *(Tour 1 moteur)* → `03` (tokens-contrat) + `04` (composition) + `04A` (autorité défaut/app/user) + `04B` (support) + `05` (LayoutResolver)
- **Phase 2 — Portage Recyclique sur le langage** *(Tour 2)* → `06` Épics de portage ; Recyclique devient un *consommateur* du moteur, plus un *propriétaire*
- **Phase 3 — Intelligence** *(palier règles puis génératif, branché sur les hooks inertes de `04A`)* → `08`

**Ordre non négociable** : tokens-contrat → langage composition → modèle d'autorité → adaptation support → LayoutResolver → rapatriement des décisions Recyclique hors du moteur → portage → intelligence. Sauter une étape = dette.

## Tours de production (méthode d'édition)

| Tour | Périmètre | Fichiers travaillés |
|------|-----------|---------------------|
| **1 — Moteur** *(livré)* | Langage + résolution agnostiques | `02`, `03`, `04`, `04A`, `04B`, `04C`, `05`, `07`, `08`, `09`, `0A` |
| **2 — Portage** *(livré)* | Recyclique réécrit comme consommateur | `10-PEINTRE-portage-recyclique.md` + `06` Épic C |
| **3 — Doc agents** *(livré)* | Outillage de l'âme future | `11-PEINTRE-doc-agents.md` |
| **Final — Addendum** *(livré)* | Trous, oublis, rectificatifs | `99-PEINTRE-addendum-revision.md` |
