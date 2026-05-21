# Décisions compta — Liaison Paheko (recherche terrain + Perplexity 2026-05-21)

**Date :** 2026-05-21  
**Statut :** décisions **produit / brainstorm** — les points marqués **EC** restent à valider par l’expert-comptable avant figement BMAD ou implémentation.  
**Sources :** [1re passe](../recherche/2026-05-21_liaison-paheko-caisse-compta-terrain_perplexity_reponse.md) · [2e passe validation](../recherche/2026-05-21_validation-comptes-liaison-paheko_perplexity_reponse.md) · [3e passe trous](../recherche/2026-05-21_liaison-paheko-trous-recherche_perplexity_reponse.md) · [multi-caisse](2026-05-21_multi-caisse-lieux-vente-paheko-recyclique.md) · [procédure clôture](2026-05-21_procedure-cloture-liaison-paheko-recyclique.md) · [recap terrain](../artefacts/2026-05-21_02_recap-idees-paheko-reception-terrain.md) · [PRD](2026-04-15_prd-recyclique-caisse-compta-paheko.md).

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
| D20 | Clôture session : **T1** ventes+dons + **T3** écart si besoin ; **T2** remboursements si présents (voir D29) | 3e passe R2 — [procédure](2026-05-21_procedure-cloture-liaison-paheko-recyclique.md) |
| D29 | **3 transactions API** max par session : T1 (toujours), T2 (remb.), T3 (écart) — `ADVANCED`, `id_year: current` | 3e passe R2, C.2 |
| D30 | **Désactiver synchro auto** extension Caisse Paheko (exercice vide) — RecyClique = seul producteur d’écritures | 3e passe R1 |
| D31 | Remboursement **exercice courant** → débit **7070** (pas **709**) | 3e passe R2 |
| D32 | Remboursement **exercice clos** → débit **672** ; **une pièce API par remboursement** | 3e passe R5 |
| D33 | Écart caisse : seuil **±2 €** ; au-delà → **bloquer** clôture ; en deçà → T3 auto 658/758 | 3e passe R7 |
| D34 | **7541 seul** en v1 ; **7542** si dons affectés projet ; fusion **754.xx** → début N+1 avec EC | 3e passe R3 |
| D35 | **Ne pas reclasser** historique **707 → 7070** ; créer 7070, note N-1 au rapport | 3e passe R4 |
| D36 | **Pas d’écriture Paheko** à l’ouverture de session ; fond = solde permanent **53x** (gestion RecyClique) | 3e passe R8 |
| D37 | Libellé écriture API **≤ 200 car.** ; format `Z SESSION {id} – {type} – {date}` | 3e passe R7 |
| D38 | Logger **toute réponse API ≠ 200** ; archiver `id` pièces Paheko sur la session | 3e passe C.2, C.7 |
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
| Batch Paheko | **T1** ventes+dons · **T2** remb. (7070 ou 672) · **T3** écart — voir [procédure](2026-05-21_procedure-cloture-liaison-paheko-recyclique.md) | PRD §9.2 (à aligner) |
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
| **709** pour remboursements après coup | 3e passe R2 — utiliser **7070** débit |
| **531** en **mono-caisse** (une seule caisse) | 3e passe R8 — utiliser **530** |
| Synchro auto Paheko caisse **+** API RecyClique en parallèle | 3e passe R1 — doublon écritures |

---

## 4. Paramétrage SuperAdmin figé (recherche — sans attendre EC)

| Paramètre | Valeur | Source |
|-----------|--------|--------|
| Compte ventes | **7070** | Validation §3 |
| Compte dons caisse | **7541** | Validation §3 |
| Compte chèques | **5112** | Validation §3 |
| Compte carte | **511** | Validation §3 |
| Compte espèces | **53x par poste** (530 si mono-caisse ; sinon 531, 532…) | [Multi-caisse](2026-05-21_multi-caisse-lieux-vente-paheko-recyclique.md) |
| Écarts caisse | **658** / **758** | Validation §3 — T3 si \|écart\| ≤ 2 € |
| Seuil écart | **±2 €** (blocage au-delà) | 3e passe R7 |
| API exercice | **`id_year: current`** | 3e passe R7 |
| Synchro Paheko caisse | **Désactivée** (exercice config vide) | 3e passe R1 |

---

## 5. En attente expert-comptable (ne pas coder comme définitif)

Voir [questions consolidées](#7-questions-expert-comptable-et-suite-porteur), [répertoire comptes](2026-05-21_repertoire-comptes-terrain-audio-recyclique.md), [prompt trous Perplexity](../recherche/2026-05-21_liaison-paheko-trous-recherche_perplexity_prompt.md).

| Thème | Candidat / constat | Bloquant v1 ? |
|--------|-------------------|---------------|
| **Numérotation 53x** (531–5331 vs format long) | Grille 7 caisses proposée — doc multi-caisse | **EC** + param postes |
| **5112 / 511** unique ou par lieu / banque / TPE | Selon nombre de banques et contrats | **EC** |
| **672** : compte cible **réimputation** fin d’exercice (658 vs 671) | OD **débit 658 / crédit 672** proposée | **EC** — avant clôture exercice |
| **Fusion 754.xx → 7541** | OD début **N+1** | **EC** |
| **Journaux** Paheko (Recettes / OD / Banque) pour T1–T3 | À confirmer sur instance | **EC** |
| **Caisse native Paheko** en parallèle (buvette, stand) | Procédure anti-doublon | **EC** si cas existant |
| **7542** (dons affectés projet) | Créer seulement si subventionneur l’exige | **EC** / reporting |
| **754.900** | Compte local non normé — identifier | Carole + **EC** |
| Arborescence **754.xx** double | Contrôle C.6 avant go-live | Carole |
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
| Écarts caisse | **658/758** (T3) | Ancienne hypothèse plugin 678/778 | **Résolu** — pas de 678/778 caisse native ; désactiver synchro auto |
| Lots clôture | **T1/T2/T3** | PRD §9.2 ancien libellé T3=672 | **Résolu** — [procédure](2026-05-21_procedure-cloture-liaison-paheko-recyclique.md) ; aligner PRD |
| Fond de caisse | Pas d’écriture ouverture ; fond hors T1 | Audio 531 / multi 53x | [Multi-caisse](2026-05-21_multi-caisse-lieux-vente-paheko-recyclique.md) + R8 |
| Migration 707→7070 | Ne pas reclasser N-1 | Historique 707 | **Résolu** 3e passe — note annexe |
| Remb. courant | **7070** débit | Recherche 04-02 citait 709 | **Résolu** 3e passe |
| 511 220 virements | — | Tampon terrain | **512** ou **58** selon cas |

---

## 7. Questions expert-comptable et suite porteur

### 7.1 Liste pour EC (après 3 passes Perplexity)

1. **Grille 53x** multi-postes — [multi-caisse](2026-05-21_multi-caisse-lieux-vente-paheko-recyclique.md).
2. **Réimputation 672** fin d’exercice : compte cible (658 ou 671) et date OD.
3. **Fusion 754.xx → 7541** : OD début N+1.
4. **Journaux** exacts pour écritures importées RecyClique.
5. **Caisse native Paheko** en parallèle : procédure anti-doublon si applicable.
6. Chèque vente + don : **2 lignes crédit** sur **5112** — signature EC (déjà confirmé recherche).
7. **7542** : créer ou non selon subventionneurs.
8. Textiles **-18**, Cerfa, bien don revendu : hors clôture v1.

### 7.2 Suite porteur produit (hors EC)

| Étape | Action |
|-------|--------|
| 1 | Synthèses : [06](../artefacts/2026-05-21_06_synthese-recherche-liaison-paheko-brainstorm.md) · [09](../artefacts/2026-05-21_09_synthese-validation-comptes-perplexity.md) · [11](../artefacts/2026-05-21_11_synthese-trous-perplexity-liaison-paheko.md) |
| 2 | Implémenter [procédure clôture](2026-05-21_procedure-cloture-liaison-paheko-recyclique.md) (T1/T2/T3, outbox, seuil 2 €) |
| 3 | Aligner **PRD §9.2** (T3 = écart, T2 = remb. courant + 672) |
| 4 | Réunion EC / Carole — [checklist répertoire §8](2026-05-21_repertoire-comptes-terrain-audio-recyclique.md) + checklist prod §4 procédure |
| 5 | Brainstorm écran fermeture + epic BMAD « Liaison Paheko v1 » |

---

## 8. Liens

- Répertoire comptes : [2026-05-21_repertoire-comptes-terrain-audio-recyclique.md](2026-05-21_repertoire-comptes-terrain-audio-recyclique.md)
- Perplexity 1re passe : [prompt](../recherche/2026-05-21_liaison-paheko-caisse-compta-terrain_perplexity_prompt.md) · [réponse](../recherche/2026-05-21_liaison-paheko-caisse-compta-terrain_perplexity_reponse.md)
- Perplexity 2e passe (validation) : [prompt](../recherche/2026-05-21_validation-comptes-liaison-paheko_perplexity_prompt.md) · [réponse](../recherche/2026-05-21_validation-comptes-liaison-paheko_perplexity_reponse.md)
- Perplexity 3e passe : [prompt](../recherche/2026-05-21_liaison-paheko-trous-recherche_perplexity_prompt.md) · [réponse](../recherche/2026-05-21_liaison-paheko-trous-recherche_perplexity_reponse.md)
- Procédure clôture : [2026-05-21_procedure-cloture-liaison-paheko-recyclique.md](2026-05-21_procedure-cloture-liaison-paheko-recyclique.md)
- Multi-caisse : [2026-05-21_multi-caisse-lieux-vente-paheko-recyclique.md](2026-05-21_multi-caisse-lieux-vente-paheko-recyclique.md)
