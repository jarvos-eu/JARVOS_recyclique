# Procédure — Clôture caisse RecyClique → Paheko

**Date :** 2026-05-21  
**Statut :** cible produit v1 — après recherche Perplexity (3 passes).  
**Sources :** [réponse 3e passe](../recherche/2026-05-21_liaison-paheko-trous-recherche_perplexity_reponse.md), [décisions](2026-05-21_decisions-compta-liaison-paheko-recherche-terrain.md), [PRD](2026-04-15_prd-recyclique-caisse-compta-paheko.md).

---

## 1. Modèle API — 3 transactions par session (stratégie B affinée)

| Transaction | Contenu | Quand |
|-------------|---------|--------|
| **T1** | Ventes + dons (débits 53x/5112/511, crédits 7070/7541) | **Toujours** à la clôture |
| **T2** | Remboursements (débit **7070** ou **672**, crédit trésorerie) | Si remboursements dans la session — **une pièce API par remboursement** |
| **T3** | Écart caisse (658/758 ↔ 53x) | Si module comptage ≠ 0 et \|écart\| ≤ 2 € |

**Ordre :** Z de clôture → **T1** → **T2** (si besoin) → **T3** (si besoin).

**API :** `POST /accounting/transaction`, `type: ADVANCED`, `id_year: current`, libellé ≤ 200 car. (`Z SESSION {id} – {type} – {date}`)

> Les « 2 pièces » de la validation 2e passe = **T1 + T3** sans remboursement. Pas de contradiction avec le PRD.

---

## 2. Procédure opérationnelle (bénévole → banque)

1. Fermeture session → **module comptage** obligatoire.
2. Saisie **fond de caisse** (ex. 50 €) — pas d’écriture Paheko à l’ouverture.
3. Comptage physique → calcul écart (espèces session − fond).
4. Si \|écart\| **> 2 €** → **bloquer** clôture, alerte responsable.
5. Génération **Z** (totaux ventes, dons, CB, chèques, remboursements).
6. **T1** API → ventes + dons.
7. **T2** API (par remboursement) → 7070 ou 672 + trésorerie.
8. **T3** API si écart ≤ 2 € → 658 ou 758.
9. Archiver les `id` pièces Paheko dans la session ; logger toute réponse API ≠ 200.
10. **Chèques** (J+0 à J+3) : Paheko → compte **5112** → bordereau → **5112 → 512** ([doc Paheko](https://paheko.cloud/depot-banque-cheque)).
11. **CB** (J+1/J+2) : écriture **511 → 512** à la date du crédit bancaire.
12. **Mensuel** : rapprochement compte **512**.

---

## 3. Écritures types (référence rapide)

### T1 — ventes + dons

| Débit | Crédit |
|-------|--------|
| 53x (espèces net) | |
| 5112 (chèques) | |
| 511 (CB) | |
| | 7070 (ventes) |
| | 7541 (dons) |

Chèque mixte vente + don : un débit **5112**, deux crédits **7070** + **7541**.

### T3 — écart

| Cas | Débit | Crédit |
|-----|-------|--------|
| Manque | 658 | 53x |
| Surplus | 53x | 758 |

### T2a — remboursement exercice courant

| Débit | Crédit |
|-------|--------|
| 7070 | 53x ou 5112 |

### T2b — remboursement exercice clos

| Débit | Crédit |
|-------|--------|
| 672 | 53x ou 5112 |

Fin d’exercice (EC) : OD **débit 658 / crédit 672** pour solder le 672.

### Post-clôture banque

| Opération | Débit | Crédit |
|-----------|-------|--------|
| Dépôt chèques | 512 | 5112 |
| Crédit CB | 512 | 511 |
| Retrait banque → caisse | 58 puis 53x / 512 puis 58 | (2 écritures) |

### Fond initial (une fois)

| Débit | Crédit |
|-------|--------|
| 53x | 512 |

---

## 4. Prérequis Paheko (avant go-live)

1. Exécuter les **3 contrôles** plan comptable (511-205/210, 5112, 754.xx) — voir [répertoire §8](2026-05-21_repertoire-comptes-terrain-audio-recyclique.md).
2. Créer comptes manquants : **7070, 5112, 658, 758, 672, 58**.
3. **Désactiver synchro auto** caisse Paheko (Configuration → exercice **vide**).
4. Activer extension **Bordereau de remise de chèques**.
5. Revue **EC** avec pièces de test T1/T2/T3.

---

## 5. Risques résiduels (top 5)

| # | Risque | Mitigation |
|---|--------|------------|
| 1 | Doublon si synchro auto Paheko active | Exercice vide en config caisse |
| 2 | Mauvais exercice API | `id_year = current` + `GET /accounting/years` |
| 3 | 672 non réimputé fin d’exercice | Alerte + OD EC |
| 4 | Double compta dons 754.xx + 7541 | Contrôle C.6 + fusion N+1 |
| 5 | Erreur API silencieuse | Logger tout HTTP ≠ 200 |
