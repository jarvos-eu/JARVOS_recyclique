# Prompt recherche — Validation comptes Liaison Paheko (2e passe)

**Date :** 2026-05-21  
**Dernière QA prompt :** 2026-05-21 — **GO** (rapport archivé : `artefacts/archive/2026-05-21-menage-paheko-compta-qa/`)  
**Cible :** Perplexity Pro  
**Usage :** Trancher les numéros de comptes et la conformité PCA / Paheko pour la clôture de caisse RecyClique.  
**Réponse :** coller la réponse Perplexity dans un fichier dépôt nommé `2026-05-21_validation-comptes-liaison-paheko_perplexity_reponse.md` (archivage local uniquement — Perplexity n’y a pas accès).

---

## Prompt Perplexity — copier-coller intégral (tout le texte ci-dessous)

```
# Validation comptable — RecyClique × Paheko (ressourcerie réemploi, France)

Tu es expert-comptable associations **loi 1901 non assujetties à la TVA**, plan comptable associatif (PCA), et usages du logiciel **Paheko** (extension Caisse). Réponds en **français**, avec **sources URL vérifiables**. Ne invente pas d’articles de loi. Si incertain : indique « à valider par expert-comptable sur place ».

---

## A. Contexte projet (à prendre comme données de départ)

**RecyClique** : application web **caisse** pour une ressourcerie (association loi 1901). Elle gère tickets, sessions de caisse, paiements mixtes (espèces + chèque + carte sur un même ticket), dons en caisse (surplus volontaire distinct de la vente), remboursements. Un **module comptage pièces et billets** est **obligatoire** à chaque fermeture de caisse (branché sur la clôture, pas optionnel).

**Paheko** : logiciel de **comptabilité** de la même association (écritures, plan comptable, rapprochements banque). Extension Caisse Paheko existe ; l’association n’est **pas** soumise NF525 (non-TVA).

**Flux retenu** : à la **fermeture de caisse** (fin de session / journée), RecyClique calcule un **récapitulatif ventilé** et l’envoie à Paheko — **pas** une écriture comptable par ticket. Les **tickets détaillés** restent dans RecyClique comme **justificatifs** (export / archivage). L’écriture Paheko doit ventiler **7070** (ventes), **7541** (dons), **530 / 511 / 512** (trésorerie), etc. — **pas** une seule ligne « recettes du jour ».

**Stack** : backend Python/FastAPI, front PWA ; synchronisation comptable asynchrone vers API Paheko (lot d’écritures par session).

---

## B. Synthèse d’une recherche Perplexity déjà réalisée (ne pas refaire en long — compléter / trancher les contradictions)

Cette recherche large a déjà conclu (à confirmer ou infirmer sur les points listés en section D) :

- Clôture **par session** + justificatifs tickets dans l’app = **acceptable** si écriture Paheko **ventilée**.
- Comptage espèces à chaque fermeture = **bonne pratique** ; écarts à documenter ; candidats écarts **658** (manque) / **758** (trop-perçu) — **à confirmer** vs comptes **678/778** utilisés par le plugin caisse Paheko.
- Ventes réemploi → **7070** (pas 707 générique).
- Dons caisse → **7541**, séparés des ventes ; surplus volontaire = don **explicite**, pas noyé dans le paiement vente.
- Chèque unique vente + don → **une pièce, deux lignes** comptables (7070 + 7541), sans découper le chèque physiquement.
- Lignes ticket **don matière / textiles -18 sans €** : **pas** de flux monétaire vers Paheko en v1 ; traçabilité kg dans RecyClique ; classe 8 CVN = **facultatif**, décision EC.
- Remboursement client sur **exercice comptable déjà clos** : candidat **672** (charges exercices antérieurs), pas 467 (bilan), pas 772 (produits antérieurs).
- Clôture Paheko : préférer **plusieurs sous-écritures équilibrées** par session (ex. lot ventes+dons ; lot remboursements exercice courant ; lot remboursements exercice antérieur) plutôt qu’une seule ligne fourre-tout.
- Pas de **prorata physique** d’un chèque entre don et vente : ventilation **comptable** en lignes séparées.

**Recherche remboursements caisse (avril 2026)** : association non-TVA pas NF525 ; remboursement = mouvement inverse daté du jour du remboursement ; conservation pièces comptables **10 ans** (Code de commerce L123-22) ; clôture agrégée possible avec détail conservé.

---

## C. Décisions produit déjà prises (ne pas invalider sans argument fort)

1. Priorité : **fermeture caisse → Paheko** opérationnelle.
2. **Module comptage** monnaie obligatoire, séparé de l’écran de fermeture.
3. **Tickets mixtes** fréquents (ex. habits donnés -18 + vaisselle payante) : gérer dès la v1 côté ticket ; clôture Paheko = **partie € seulement**.
4. Objectif comptes : **7070** ventes réemploi, **7541** dons manuels caisse.
5. On **remet en question tout le plan** actuel Paheko + paramètres Recyclique pour **conformité et simplicité** — pas de préservation par habitude.

---

## D. Plan comptable et paramètres ACTUELS à auditer (source : réunion terrain mai 2026 + paramétrage logiciel)

Nous reprenons **depuis zéro**. Pour **chaque** ligne ci-dessous : indiquer **Correct / À corriger / À créer / Supprimer**, le **compte PCA recommandé**, et si **validation expert-comptable obligatoire**.

### D.1 Comptes présents ou cités dans **Paheko** (instance association « La Clique » — navigation compta terrain, mai 2026)

| Compte | Usage oral / écran Paheko |
|--------|---------------------------|
| 530 | Caisse ; cumul mouvements journée ; tampon espèces clôture |
| 531 | Fond de caisse (crédit/débit entre ouvertures) |
| 511 | Tampon chèques / espèces avant banque |
| 511 205 | Versement espèces — **billets** (comptage clôture) |
| 511 210 | Retrait monnaie — **pièces** (comptage + fond de caisse) |
| 511 220 | Proposé pour virements / tampon banque |
| 512 | Banque ; parfois « chèques à encaisser » ; CB ; plusieurs 512 évoqués (virements dons, espèces dons) |
| 707 | Ventes de marchandises — utilisé **1re année comptable** |
| 7070 | Ventes de **réemploi** — **cible** métier |
| 754 | Dons (regroupement oral) |
| 754.10 | Dons manuels — compte de **synthèse** |
| 754.11 | Dons manuels — **écritures courantes** quotidiennes |
| 754.115 | Dons manuels reçus par **chèque** |
| 754.111 | Dons affectés **projet** (ex. atelier cartes 69 €) |
| 754.12 | Abandon de frais **bénévoles** (hors scope caisse v1) |
| 7541 | Dons manuels — référence PCA / doc |
| 1630 | Cité comme « espèces » dans un doc interne — **existence réelle ?** |
| 53 | Formulation « caisse » en séance comptable terrain |
| 58 | Cité dans exemples ; fin de séance : plutôt **virements internes** trésorerie |
| 471 | Compte d’**attente** — décaissements / monnaie |
| 472 | Dépenses à classer — peu utilisé |
| 678 | Erreur de caisse — **plugin** extension Caisse Paheko |
| 778 | Erreur de caisse (excédent) — **plugin** Paheko |
| 771.3 | Libéralités **exceptionnelles** (vs 754.11 habituel) |
| 754.900 | Cité oralement — sens à clarifier sur plan réel |
| 5112 | Norme PRD / seed RecyClique (chèques) — **non cité** en navigation Paheko terrain (511 + 205/210 à la place) |

### D.2 Paramétrage actuel **RecyClique** (écran SuperAdmin / seeds — peut diverger de Paheko)

**Comptes globaux :**
- Ventes par défaut : **7070** (objectif PRD) — en base / tests parfois encore **707**
- Dons par défaut : **7541** (corrigé depuis ancien **708** inadapté)
- Remboursement exercice clos : **672** (corrigé depuis ancien **467**)
- Journal caisse : à renseigner (ex. CA)
- Préfixe libellé écriture : « Z caisse »

**Moyens de paiement → comptes (seeds application) :**

| Moyen | Compte débit encaissement | Compte crédit remboursement |
|-------|---------------------------|-----------------------------|
| Espèces | 530 | 530 |
| Chèque | 5112 | 5112 |
| Carte bancaire | 511 | 511 |
| Don (surplus) | 530 | 7541 |
| Virement | 512 | 512 |

**Anciens réglages clôture (tests / legacy)** : parfois débit **512** + crédit **707** en une ligne — **incohérent** avec 7070 + ventilation par moyen de paiement.

### D.3 Comptes **obsolètes ou erreurs** (ne plus utiliser — confirmer suppression / migration)

| Compte | Problème | Remplacement cible |
|--------|----------|-------------------|
| 708 | Ancien défaut « don » (produits annexes) | **7541** |
| 467 | Ancien défaut remboursement exercice clos (bilan) | **672** |
| 7073 | Sous-compte textile en test — ventilation par famille **refusée** | **7070** unique ventes réemploi |
| 7041 | Erreur transcription audio (≈ 7541) | **7541** |

### D.4 Écarts connus Paheko ↔ RecyClique (à trancher dans ta réponse)

| Sujet | Paheko / terrain | RecyClique / PRD |
|--------|------------------|------------------|
| Ventes clôture | 707 (historique) | 7070 |
| Chèques | 511, 511 205, 511 210, parfois 512 | 5112 |
| Carte | 512 (?) | 511 |
| Écarts caisse | 678 / 778 | 658 / 758 (recherche antérieure) |
| Espèces | 530 + oral « 53 » + 1630 ? | 530 |

---

## E. Questions obligatoires (11 sections numérotées)

Pour **chaque** question : **Recommandation** | **Certitude** (fort / moyen / faible) | **Source (URL)** | **Valider EC** (oui / non)

**Q1 — Architecture trésorerie clôture**  
Pour une ressourcerie : rôles respectifs de **530**, **511**, **5112**, **512**, sous-comptes **511-205** (billets) et **511-210** (pièces) ? Faut-il **plusieurs comptes 512** ? Comment lier le **comptage monnaie** obligatoire en caisse à ces comptes ?

**Q2 — 530 vs 53**  
Le compte caisse espèces standard PCA est-il **530** ? Le « 53 » oral = classe 5 ou erreur pour 530 ?

**Q3 — Compte 1630**  
Le compte **1630** « espèces » existe-t-il dans les plans associatifs ou confusion avec **530** ?

**Q4 — Fond de caisse 531**  
**531** adapté au fond de caisse ou gestion du fond uniquement via **530** / solde de session sans compte 531 ?

**Q5 — Écarts de caisse**  
**658/758** vs **678/778** (Paheko) pour asso non-TVA ? Seuil de tolérance usuel petite structure ?

**Q6 — Dons 7541 vs sous-comptes**  
**7541** seul suffit-il ou garder **754.11** + **754.115** comme dans Paheko aujourd’hui ?

**Q7 — Compte 58**  
**58** = virements internes trésorerie **uniquement**, pas achats espèces magasin (**530** + **6xx**) ?

**Q8 — 471 / 472**  
Quand obligatoires en magasin (sortie monnaie, retour différé) vs **530 + 6xx** direct ?

**Q9 — 7070 vs 707 vs 70700**  
Numérotation PCA réemploi ; migration depuis plan déjà en **707** ?

**Q10 — Chèque vente + don**  
Confirmer : **une pièce**, lignes **7070** + **7541**, débit **511 ou 5112** ?

**Q11 — 672 remboursement exercice clos**  
Confirmer **672** vs **467** et **772** ?

---

## F. Livrable attendu (format strict)

1. **Tableau récap** des 11 questions (colonnes : Question | Recommandation | Certitude | Source | Valider EC).

2. **Plan comptable cible** — tableau pour **tous** les comptes listés en **D.1, D.2 et D.3** :  
   `Compte actuel | Où (Paheko/Recyclique) | Compte recommandé | Action | Commentaire`.

3. **5 décisions** que RecyClique peut figer en paramétrage SuperAdmin **sans** attendre l’EC.

4. **5 décisions** **réservées** à l’EC sur place.

5. **3 points de contrôle** à faire vérifier avec le comptable sur le **plan Paheko réellement créé** (libellés 511 205/210, 754.11/754.115, cohérence avec 5112 côté RecyClique).

6. **Écriture(s) type clôture de session** (exemple chiffré) — préciser si **une ou plusieurs** pièces comptables par session :  
   - 120 € ventes espèces  
   - 30 € ventes chèques  
   - 50 € ventes carte  
   - 2 € don espèces (surplus)  
   → lignes débit/crédit complètes et équilibrées selon ta recommandation.

---

## G. Hors scope (ne pas développer)

Reçu fiscal Cerfa, CVN classe 8 détaillée, bien reçu en don puis revendu, notes de frais 754.12, HelloAsso, API technique Paheko.

---

## H. Consignes finales

- Citer doc Paheko (paheko.cloud), PCA / plans associatifs, sources comptables associations France quand possible.
- Distinguer : obligation légale / bonne pratique / choix outil / périmètre EC.
- Si Paheko et RecyClique divergent, recommander **un plan unique** aligné PCA, pas deux logiques parallèles.
- Orthographe produit : **RecyClique** (logiciel caisse), **Paheko** (compta).
```

---

*Fin du prompt — tout le bloc entre les triples backticks ci-dessus est autonome pour Perplexity (aucune autre pièce du dépôt requise).*
