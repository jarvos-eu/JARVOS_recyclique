# Synthèse — validation comptes Perplexity (2e passe, 2026-05-21)

**Source :** [réponse Perplexity](../recherche/2026-05-21_validation-comptes-liaison-paheko_perplexity_reponse.md)  
**Pour :** Strophe — langage plancher, avant EC / Carole  
**QA ventilation :** [rapport 10](2026-05-21_10_qa-ventilation-compta-paheko-2026-05-21.md)

---

## En 10 lignes

1. **RecyClique peut figer** : 7070 ventes, 7541 dons, **5112** chèques, **511** carte, écarts **658/758**.
2. **Espèces** : **530** si **une seule** caisse ; sinon **un compte 53x par poste** (531, 532…) — voir [multi-caisse](../migration-paheko/2026-05-21_multi-caisse-lieux-vente-paheko-recyclique.md).
3. **511 205 / 511 210** = module comptage RecyClique uniquement, **pas** le plan Paheko.
4. **1630** à oublier ; oral « 53 » = **classe**, pas un compte à saisir.
5. Aligner Paheko terrain : chèques → **5112** (pas 511-205).
6. Clôture = **T1** ventes+dons + **T3** écart (+ **T2** remb.) — voir [procédure](../migration-paheko/2026-05-21_procedure-cloture-liaison-paheko-recyclique.md) ; dépôt chèques plus tard (5112 → 512).
7. **EC** : grille 53x, fusion 754.xx, réimputation 672, journaux Paheko — détail [synthèse 11](2026-05-21_11_synthese-trous-perplexity-liaison-paheko.md).
8. **3e passe faite** — [réponse](../recherche/2026-05-21_liaison-paheko-trous-recherche_perplexity_reponse.md) ventilée ; synchro Paheko caisse **off**, seuil écart **±2 €**.
9. Réunion EC / Carole : checklist [répertoire §8](../migration-paheko/2026-05-21_repertoire-comptes-terrain-audio-recyclique.md).
10. Ensuite : brainstorm fermeture + param SuperAdmin (compte **par poste**).

---

## Paramétrage RecyClique cible (figé recherche, sauf EC)

| Rôle | Compte | Note |
|------|--------|------|
| Ventes réemploi | **7070** | |
| Dons caisse | **7541** | |
| Espèces | **53x** (ou **530** mono-caisse) | Par `cash_registers` |
| Chèques | **5112** | |
| Carte | **511** | |
| Virement / banque | **512** | |
| Écart manque | **658** | |
| Écart trop-perçu | **758** | |
| Remb. exercice clos | **672** | |

**À ne plus utiliser :** 708, 467, 7073, 7041, 1630, 707 (nouvelles écritures).

---

## Ce qui reste ouvert (post 3e passe)

| Sujet | Qui | Statut |
|--------|-----|--------|
| Grille **53x** (7 postes) | EC | [multi-caisse](../migration-paheko/2026-05-21_multi-caisse-lieux-vente-paheko-recyclique.md) |
| Réimputation **672**, fusion **754.xx**, journaux | EC | [synthèse 11](2026-05-21_11_synthese-trous-perplexity-liaison-paheko.md) |
| **754.900**, arborescence 754 | Carole | Plan réel |
| Implémentation T1/T2/T3 + désactiver synchro Paheko | Dev | [procédure](../migration-paheko/2026-05-21_procedure-cloture-liaison-paheko-recyclique.md) |
| Cerfa, CVN -18, bien revendu | EC | Hors clôture v1 |

*Tranché en 3e passe : 678/778 (non), T1/T2/T3, 7541 seul v1, pas de migration 707 N-1, 709 (non), fond sans écriture ouverture.*

---

## Exemple clôture — mono-caisse (1 poste, 530)

**Pièce 1 — ventes + dons**

- Débit 530 : 122 € (120 ventes + 2 don espèces)
- Débit 5112 : 30 € · Débit 511 : 50 € (CB)
- Crédit 7070 : 200 € · Crédit 7541 : 2 €

**Pièce 2 — écart** : 658 ou 758 ↔ **530** du poste.

**Dépôt chèques :** Débit 512 / Crédit 5112.

> Multi-postes : remplacer **530** par le **53x** du poste (ex. 531 pour établ. A caisse 1) — même structure.

---

## Liens

- [Décisions](../migration-paheko/2026-05-21_decisions-compta-liaison-paheko-recherche-terrain.md) · [Répertoire](../migration-paheko/2026-05-21_repertoire-comptes-terrain-audio-recyclique.md) · [Multi-caisse](../migration-paheko/2026-05-21_multi-caisse-lieux-vente-paheko-recyclique.md)
