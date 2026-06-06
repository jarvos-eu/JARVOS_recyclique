# Décisions HITL — module comptage pièces/billets (pilote La Clique)

**Date :** 2026-06-06  
**Statut :** figé PO Strophe — entrée stories **9.11–9.13** (Epic 9, cible **v2.0.2**)  
**Sources :** recherche Perplexity [`2026-06-06_comptage-pieces-billets-fermeture-caisse-ux-terrain_perplexity_reponse.md`](../recherche/2026-06-06_comptage-pieces-billets-fermeture-caisse-ux-terrain_perplexity_reponse.md) · fiche protocole [`08-MOD-exemple-pilote-comptage-pieces-billets.md`](../protocole-modules-recyclique/08-MOD-exemple-pilote-comptage-pieces-billets.md)

---

## Décisions produit (langage terrain)

| # | Sujet | Décision |
|---|--------|----------|
| D-CPT-01 | Gros billets | **500 € seul** dans la section « coupures rares » (masqué par défaut). Les **200 €** restent dans la grille principale. |
| D-CPT-02 | Soirée sans ventes espèces | On **compte quand même** tout le tiroir (fond inclus) — pas de raccourci sans grille. |
| D-CPT-03 | Mémoire / historique | **Chaque fermeture** reste consultable dans Recyclique (détail comptage conservé). Pas de PDF systématique. |
| D-CPT-04 | PDF | PDF feuille de clôture **uniquement en cas d’anomalie** (écart, seuil, coupure rare signalée, etc.). |
| D-CPT-05 | Relecture | Écran de **relecture obligatoire** avant validation (même si tout colle). |
| D-CPT-06 | Images pièces/billets | **Oui en V1** — pictos **stylisés** (pas de photos réalistes de billets). Option module **`show_images`** : afficher ou masquer. **Plus tard** : personnalisation des visuels par dénomination. |
| D-CPT-07 | Comptage obligatoire pilote | Module activé → **`skip_allowed: false`**, grille complète requise. |
| D-CPT-08 | Vérité comptée | **Seul le total de la grille** fait foi — pas de second montant global saisi à la main quand le module est actif. |
| D-CPT-09 | Fond de caisse | **Tout compter dans la grille** (fond inclus) ; le logiciel calcule fond à laisser / à retirer. |
| D-CPT-10 | Poids (balance) | **Hors V1** — comptage **unitaire** d’abord ; poids = phase ultérieure (recherche optionnelle). |
| D-CPT-11 | Paheko | **Aucune** écriture par dénomination — snapshot enrichi seulement ; chaîne T1/T2/T3 **9.10** inchangée. |

---

## Rangement BMAD

| Story | Objet |
|-------|--------|
| **9.11** | Back + contrats + persistance + snapshot |
| **9.12** | Wizard clôture (grille, relecture, pictos, PDF anomalie) |
| **9.13** | Schéma module-config, activation admin, recette on/off |

**Epic :** 9 (module métier incrémental post-9.10). **Hôte UX :** wizard clôture Epic 6 / story 6.7 (done, extension seulement).

---

## Visuels (D-CPT-06)

- Créer un pack **SVG stylisé** in-repo (`peintre-nano/public/assets/cash-denominations/`) : forme générique + libellé valeur — **pas** de reproduction photographique de billets (règles BCE : risque de confusion avec vraie monnaie).
- Sources externes : pictos génériques type UXWing / Noun Project **si licence commerciale sans attribution** ; documenter dans `README` du dossier assets.
- **Pas de téléchargement** d’images BCE haute résolution sans marquage SPECIMEN.
