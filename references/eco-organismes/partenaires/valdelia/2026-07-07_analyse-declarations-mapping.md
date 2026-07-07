# Analyse déclarations — Valdelia (La Clique)

**Date :** 2026-07-07  
**Partenaire :** Valdelia — **DEA mobilier professionnel** (pas REP emballages)  
**Sources :** 3 fichiers `referentiels-officiels/` — pas de `declarations-la-clique/`

---

## Résumé exécutif

Valdelia couvre le **mobilier professionnel** (bureau, scolaire, hospitalier, restauration, hébergement), distinct de l’**ameublement ménager EA** (Ecomaison). La Clique a déposé une **demande de conventionnement** le 26/11/2025 via le RNRR ; **aucune déclaration xlsx** dans le dépôt. Format attendu : **Annexe 3 Excel** (valdelia.org), envoi trimestriel par e-mail.

---

## Obligations déclaration

- Déclaration **trimestrielle** des tonnages réemployés/réutilisés + justificatifs.
- Envoi sous **30 jours** après clôture trimestre → `reemploi@valdelia.org`.
- Dons/ventes **entre structures ESS conventionnées** : ne pas déclarer chez Valdelia (le bénéficiaire déclare).
- Cohérence entrants / sortants / stock ; protocoles pour collectes coordonnées.

**Statut La Clique :** ~5 t/an estimées, conventionnement **en cours** (non signée dans le dépôt).

---

## Inventaire dépôt

| Fichier | Nature |
|---------|--------|
| `Annexe 1 – Barème de soutien (1).pdf` | Barème (170 €/t REE/REU, 250 €/trim traçabilité, FAC 60 €/t, etc.) |
| `Annexe 2 – Demande de conventionnement (1).docx` | Formulaire **rempli** 26/11/2025 — L’ÉCO de LA CLIQUE, SIREN 98905144600015 |
| `e2d0ce23-….pdf` | Attestation **RNRR** (Broceliande CARNIEL), pas contrat Valdelia |

**Manquant :** Guide partenariat, **Annexe 3** Excel, convention signée, MO déclarations.

---

## Mapping brouillon

| Type mobilier | Sorties possibles |
|---------------|-------------------|
| Bureau / scolaire / hospitalier / restauration / hébergement | Vente, don, utilisation interne, remise filière (FAC) |
| Collecte coordonnée | SSCC (plafond 1 000 €/opération) |

**Critère critique Recyclique :** distinguer **ménager (Ecomaison)** vs **professionnel (Valdelia)** sur les catégories ameublement.

---

## Cas particuliers

- **> 15 t/trimestre** réemployées → justificatifs de sortie obligatoires.
- MO Ecomaison mentionne ligne « Tonnes DEA » — risque **chevauchement** si non séparé métier.
- La Clique déclare déjà Ecomaison + Ecologic ; **zéro Valdelia** en terrain.

---

## Gaps / questions

1. Télécharger Annexe 3 + Guide depuis valdelia.org.
2. Statut conventionnement post 26/11/2025 ?
3. Règle métier ménager vs pro dans Recyclique ?
4. Aucun mapping Valdelia dans le code (Epic 9).

---

## Pistes patch 1.4.5

Hors scope immédiat patch stats La Clique (priorité Ecomaison). Prévoir flag `mobilier_pro` sur catégories ameublement avant export Valdelia.
