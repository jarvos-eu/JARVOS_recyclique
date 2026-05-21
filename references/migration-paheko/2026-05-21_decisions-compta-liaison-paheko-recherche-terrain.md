# Décisions compta — Liaison Paheko (recherche terrain + Perplexity 2026-05-21)

**Date :** 2026-05-21  
**Statut :** décisions **produit / brainstorm** — les points marqués **EC** restent à valider par l’expert-comptable avant figement BMAD ou implémentation.  
**Sources :** [recherche Perplexity 1re passe](../recherche/2026-05-21_liaison-paheko-caisse-compta-terrain_perplexity_reponse.md), [validation comptes 2e passe](../recherche/2026-05-21_validation-comptes-liaison-paheko_perplexity_reponse.md), [multi-caisse](2026-05-21_multi-caisse-lieux-vente-paheko-recyclique.md), [recap terrain](../artefacts/2026-05-21_02_recap-idees-paheko-reception-terrain.md), [PRD caisse-compta](2026-04-15_prd-recyclique-caisse-compta-paheko.md), arbitrages porteur produit (2026-05-21).

**Ne remplace pas** le PRD du 15/04 pour l’implémentation technique (tables, API, outbox) : ce fichier **fige l’orientation métier** après recherche.

---

## 1. Décisions figées (produit)

| # | Décision | Justification courte |
|---|----------|----------------------|
| D1 | **Priorité chantier** : fermeture caisse → Paheko (liaison), pas réception d’abord | Porteur produit — chantier en cours |
| D2 | **Clôture par session** : un récap/jour vers Paheko, **pas** une écriture par ticket | PRD §2.1 + recherche A4 + pratique asso |
| D3 | **Détail tickets** conservé dans Recyclique comme **justificatif** (export/archivage) | Condition légale de validité du récap agrégé |
| D4 | **Écriture Paheko ventilée** : lignes distinctes 7070, 7541, **53x** (espèces par poste), 511/5112/512… — **pas** une ligne « recettes du jour » | Recherche A4, B + [multi-caisse](2026-05-21_multi-caisse-lieux-vente-paheko-recyclique.md) |
| D5 | **Module comptage pièces/billets** : **obligatoire**, **module séparé** branché sur la fermeture | Porteur produit + recherche A2/A5 |
| D6 | **Fermeture** : PDF ou export feuille de clôture archivable ; écart documenté | Recherche A2 |
| D7 | **Ventes réemploi** → compte produit **`7070`** (pas 707 générique) | Terrain (C refuse 707) + PRD + recherche B1 |
| D8 | **Dons en caisse** (surplus volontaire) → **`7541`**, **séparés** des ventes dans l’écriture | PRD + recherche B |
| D9 | **Surplus volontaire** : flux **don explicite** en caisse (pas noyé dans le paiement vente) | Recherche B4 |
| D10 | **Chèque don + vente** : **une pièce, plusieurs lignes** comptables — **pas** de découpage physique du chèque | Terrain PKO-006/007 + recherche B3 |
| D11 | **Ticket mixte** (don matière -18 + ligne payante) : **fréquent** → géré **v1** | Porteur produit |
| D12 | **Ligne don matière / -18** : **aucun €** vers Paheko ; traçabilité **Recyclique** (kg, article) | Recherche C + recap PKO-016/016b |
| D13 | **Clôture Paheko** : envoyer **uniquement les totaux monétaires** du jour | Conséquence D11, D12 |
| D14 | **Pas d’envoi Paheko** des sorties matière -18 sans décision EC sur CVN (classe 8) | Recherche C2, C4 |
| D15 | **Bug « don » par défaut** en caisse : **hors priorité** brainstorm (correctif attendu v2 caisse) | Porteur produit |
| D16 | **Chèques** → compte **`5112`** (standard Paheko/PCG), pas 511 ni sous-comptes 511-205/210 | Validation 2e passe Q1, Q10 |
| D17 | **Carte bancaire** → compte **`511`** (valeurs à l’encaissement), **pas** 512 direct | Validation 2e passe Q1 |
| D18 | **511 205 / 511 210** = **comptage RecyClique uniquement**, pas des comptes du plan Paheko | Validation 2e passe D.1 |
| D19 | **Écarts de caisse** (module comptage) → **`658`** / **`758`** (gestion courante), pas 678/778 du plugin | Validation 2e passe Q5 — **EC** confirme vs plugin Paheko |
| D20 | Clôture session : **2 pièces type** — (1) ventes+dons ventilés ; (2) écart si comptage ≠ théorique | Validation 2e passe §6 |
| D21 | Oral **« 53 »** = classe, pas un compte ; **`1630`** à supprimer | Validation 2e passe Q2, Q3 |
| D22 | Compte **`58`** : **virements internes** trésorerie uniquement (solde ≈ 0), jamais achats espèces | Validation 2e passe Q7 |
| D23 | **`471` / `472`** : pas en fonctionnement normal boutique ; sortie espèces connue = **53x** → 6xx direct | Validation 2e passe Q8 + multi-caisse |
| D24 | **Multi-caisse** : **1 caisse physique = 1 compte 53x** (531, 5311, 532…) ; **530** seulement si **une** caisse dans l'asso | [multi-caisse](2026-05-21_multi-caisse-lieux-vente-paheko-recyclique.md) |
| D25 | Paheko **Lieux de vente** = alignement cible avec **`cash_registers`** RecyClique ; moyens de paiement **dupliqués par lieu** côté Paheko | Idem |
| D26 | Compte espèces Paheko : **paramétrable par poste de caisse** (`cash_registers`), pas seed global `530` unique | Idem — PRD §5.3 |
| D27 | **Module comptage** : lié au **poste / session**, pas à un compte 530 global | Idem |
| D28 | Transferts entre caisses ou caisse → banque : obligatoirement via **58** (pas 53x ↔ 53x direct) | Idem + D22 |

---

## 2. Aligné PRD existant (inchangé, rappel)

| Sujet | Valeur | Fichier |
|--------|--------|---------|
| Source de vérité paiements | `payment_transactions` | PRD §2.2 |
| `free` | Vente à 0 €, pas moyen de paiement | PRD §4.4 |
| Remboursement exercice clos | Compte **`672`** confirmé (pas 467 ni 772) ; **réimputation fin d’exercice** à valider EC | PRD §6.7 + validation 2e passe Q11 |
| Batch Paheko | Stratégie B : ventes+dons / remb. courant / remb. antérieur | PRD §9.2 |
| Exercice Paheko | Saisie manuelle ID (pas API liste) | Spec SuperAdmin M5 |

---

## 3. Rejeté explicitement

| Sujet | Raison |
|--------|--------|
| Agréger don + vente sur **une seule ligne** crédit en clôture | Recherche B, terrain |
| Envoyer sorties matière -18 à Paheko **sans** cadre EC (CVN / hors bilan) | Recherche C |
| Ventilation par **famille produit** en clôture (ex. 7073 textile seul) | Décision PRD + spec I1 |
| Prorata **physique** d’un chèque entre don et vente | Terrain PKO-006 |
| Compte **1630** ; oral **« 53 »** utilisé comme numéro de compte (≠ classe 53) | Validation 2e passe Q2–Q3 |
| **511 205 / 511 210** dans le plan comptable Paheko | Données module comptage RecyClique uniquement |
| **467** pour remboursement exercice clos | Validation 2e passe Q11 — utiliser **672** |
| **708**, **7041**, **7073** (seeds / erreurs) | Validation 2e passe D.3 |
| **530** unique pour toutes les caisses en multi-postes | [Multi-caisse](2026-05-21_multi-caisse-lieux-vente-paheko-recyclique.md) — 1 caisse = 1 **53x** |
| Transfert direct **531 ↔ 532** (sans 58) | Idem |

---

## 4. Paramétrage SuperAdmin figé (recherche — sans attendre EC)

| Paramètre | Valeur | Source |
|-----------|--------|--------|
| Compte ventes | **7070** | Validation §3 |
| Compte dons caisse | **7541** | Validation §3 |
| Compte chèques | **5112** | Validation §3 |
| Compte carte | **511** | Validation §3 |
| Compte espèces | **53x par poste** (530 si mono-caisse ; sinon 531, 532…) | [Multi-caisse](2026-05-21_multi-caisse-lieux-vente-paheko-recyclique.md) |
| Écarts caisse | **658** / **758** | Validation §3 — écriture auto v2 |

---

## 5. En attente expert-comptable (ne pas coder comme définitif)

Voir [questions consolidées](#7-questions-expert-comptable-et-suite-porteur), [répertoire comptes](2026-05-21_repertoire-comptes-terrain-audio-recyclique.md), [prompt trous Perplexity](../recherche/2026-05-21_liaison-paheko-trous-recherche_perplexity_prompt.md).

| Thème | Candidat / constat | Bloquant v1 ? |
|--------|-------------------|---------------|
| **Numérotation 53x** (531–5331 vs format long) | Grille 7 caisses proposée — doc multi-caisse | **EC** + param postes |
| **5112 / 511** unique ou par lieu / banque / TPE | Selon nombre de banques et contrats | **EC** |
| **7541** unique ou sous-comptes **754.11 / 754.115 / 754.111** | 7541 seul OK réglementairement | Non — granularité reporting |
| **Migration historique 707 → 7070** | Ne pas reclasser sans accord EC | Non pour nouvelles écritures |
| **672** : conditions + **réimputation obligatoire** fin d’exercice (PCG 2025) | Confirmé bon compte | Remboursements antérieurs |
| **Plugin Paheko 678/778** vs RecyClique **658/758** | Cohabitation ou correction manuelle ? | Écarts si plugin utilisé en parallèle |
| **754.900**, arborescence **754.10 / 754.11** double | Vérifier plan Paheko réel (Carole) | Risque double compta dons |
| Classe 8 CVN textiles -18 | Recherche 1re passe | Non clôture v1 |
| Bien don revendu, Cerfa boutique | Recherche 1re passe | Hors clôture v1 |

**3 contrôles sur plan Paheko réel** (validation §5) : libellés 511-205/210 ; cohérence **5112** RecyClique vs 511-x terrain ; arborescence 754 sans doublon.

---

## 6. Écarts documentés (à harmoniser)

| Sujet | PRD / RecyClique cible | Terrain / Paheko existant | Action |
|--------|------------------------|---------------------------|--------|
| Compte vente clôture | **7070** | Historique **707** (1re année) | EC migration ; nouvelles écritures → 7070 |
| Chèques | **5112** | Tampon **511** + 511-205/210 | Aligner plan Paheko ; comptage hors plan |
| Carte | **511** | Parfois en **512** | Corriger param Paheko |
| Écarts caisse | **658/758** | Plugin **678/778** | EC + [recherche trous R1](../recherche/2026-05-21_liaison-paheko-trous-recherche_perplexity_prompt.md) |
| Lots clôture | PRD : 3 lots (ventes+dons / remb. courant / remb. ant.) | Validation : 2 pièces session + écart | [recherche trous R2](../recherche/2026-05-21_liaison-paheko-trous-recherche_perplexity_prompt.md) |
| Fond de caisse | Session RecyClique | Audio **531** ; multi-caisse → 53x par poste | [Multi-caisse](2026-05-21_multi-caisse-lieux-vente-paheko-recyclique.md) |
| 511 220 virements | — | Tampon terrain | **512** ou **58** selon cas |

---

## 7. Questions expert-comptable et suite porteur

### 7.1 Liste pour EC (après 2 passes Perplexity)

1. **Grille 53x** pour N postes (ex. 531–5331) : valider avec EC — voir [multi-caisse](2026-05-21_multi-caisse-lieux-vente-paheko-recyclique.md).
2. **5112** et **511** : comptes uniques ou ventilés par établissement / banque / TPE (multi-caisse) ?
3. **7541** seul ou sous-comptes **754.11 / 754.115 / 754.111** (volume dons, subventionneurs) ?
4. **Migration 707 → 7070** sur exercices passés : oui/non, impact tableaux N-1 ?
5. **672** : procédure réimputation fin d’exercice pour l’asso ?
6. **658/758** (RecyClique) vs **678/778** (plugin Paheko) : un seul jeu acceptable ?
7. Chèque vente + don : confirmer **2 lignes crédit** (7070 + 7541) sur **5112** débit — **confirmé recherche**, signature EC ?
8. Seuil tolérance écart caisse (±1 à 2 € proposé) — règlement intérieur ?
9. Textiles **-18**, Cerfa, bien don revendu : inchangé (hors clôture v1).

### 7.2 Suite porteur produit (hors EC)

| Étape | Action |
|-------|--------|
| 1 | **3e passe Perplexity** — trous restants → [prompt](../recherche/2026-05-21_liaison-paheko-trous-recherche_perplexity_prompt.md) |
| 2 | Synthèses : [06](../artefacts/2026-05-21_06_synthese-recherche-liaison-paheko-brainstorm.md) · [09](../artefacts/2026-05-21_09_synthese-validation-comptes-perplexity.md) |
| 3 | Réunion EC / Carole — [checklist répertoire §8](2026-05-21_repertoire-comptes-terrain-audio-recyclique.md) + plan Paheko exporté |
| 4 | Brainstorm **atelier fermeture** + module comptage |
| 5 | Epic BMAD « Liaison Paheko v1 » quand stable |

---

## 8. Liens

- Répertoire comptes : [2026-05-21_repertoire-comptes-terrain-audio-recyclique.md](2026-05-21_repertoire-comptes-terrain-audio-recyclique.md)
- Perplexity 1re passe : [prompt](../recherche/2026-05-21_liaison-paheko-caisse-compta-terrain_perplexity_prompt.md) · [réponse](../recherche/2026-05-21_liaison-paheko-caisse-compta-terrain_perplexity_reponse.md)
- Perplexity 2e passe (validation) : [prompt](../recherche/2026-05-21_validation-comptes-liaison-paheko_perplexity_prompt.md) · [réponse](../recherche/2026-05-21_validation-comptes-liaison-paheko_perplexity_reponse.md)
- Perplexity 3e passe (trous) : [prompt](../recherche/2026-05-21_liaison-paheko-trous-recherche_perplexity_prompt.md)
- Multi-caisse / lieux de vente : [2026-05-21_multi-caisse-lieux-vente-paheko-recyclique.md](2026-05-21_multi-caisse-lieux-vente-paheko-recyclique.md)
