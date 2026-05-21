# Multi-caisse RecyClique × Paheko — Lieux de vente et comptes 53x

**Date :** 2026-05-21  
**Statut :** doctrine **produit + compta** — numérotation exacte des comptes **53x** à valider EC.  
**Sources :** doc Paheko [Lieux de vente](https://paheko.cloud/caisse-lieux-de-vente), PCG classe 53, validation comptes 2e passe (mono-caisse), recherche terrain mai 2026.

**Liens :** [décisions compta](2026-05-21_decisions-compta-liaison-paheko-recherche-terrain.md) · [répertoire comptes](2026-05-21_repertoire-comptes-terrain-audio-recyclique.md) · [PRD caisse-compta](2026-04-15_prd-recyclique-caisse-compta-paheko.md) · [PRD multisite](2026-04-19_prd-recyclique-architecture-permissions-multisite-kiosques-bmad.md) (vision `references/vision-projet/`).

---

## 1. Principe comptable

| Règle | Détail |
|--------|--------|
| **1 caisse physique = 1 compte 53x** | Chaque fonds de caisse distinct a son compte de classe **53** (sous-compte PCA/PCG). |
| **530** | Caisse générique — OK si **une seule** caisse dans toute l'asso ; **à éviter** comme compte terminal si plusieurs caisses. |
| **531, 5311, 532, 5321…** | Subdivisions libres dans la classe 53, cohérentes et documentées (format court Paheko ou long type AssoConnect — **EC** tranche). |
| **Oral « 53 »** | Raccourci de **classe**, pas un compte à créer — toujours saisir le **53x** du lieu. |

---

## 2. RecyClique ↔ Paheko — correspondance entités

| RecyClique (appli) | Paheko (compta / extension Caisse) | Compte(s) typiques |
|--------------------|-------------------------------------|-------------------|
| **`sites`** (établissement : fixe, nomade, externe) | Regroupement analytique / projet ; **pas** un compte 53x seul | 7070, 7541 (globaux ventes/dons) |
| **`cash_registers`** (poste de caisse) | **Lieu de vente** Paheko | **Un 53x** par poste (espèces) |
| **`cash_sessions`** (session ouverte/fermée) | Session de caisse Paheko (1:1 par poste, voir PRD canon) | Écriture de clôture → 53x du poste |
| **Module comptage** (pièces/billets) | Comptage clôture native (hors plan 511-205/210) | Lié au **poste**, pas à un 530 global |
| **`payment_methods`** (référentiel) | Moyens de paiement Paheko | Comptes **511**, **5112**, **512** selon règles ci-dessous |

**Conséquence Paheko (doc officielle)** : si plusieurs lieux de vente, chaque moyen de paiement dupliqué **par lieu** — ex. 4 lieux × N moyens = **N×4** entrées dans la config Paheko.

**Conséquence RecyClique** : le compte espèces (`paheko_debit_account` pour `cash`) ne peut plus être **une seule valeur globale** (`530` en seed) ; il doit être **configurable par poste de caisse** (`cash_registers`), avec repli documenté si mono-caisse.

---

## 3. Plan comptable type — 7 caisses espèces (exemple La Clique)

Scénario cible : **2 établissements × (2 + 3) caisses** + **2 stands mobiles**.

| Compte | Lieu RecyClique | Nature |
|--------|-----------------|--------|
| **531** | Établissement A — Caisse 1 | Boutique fixe |
| **5311** | Établissement A — Caisse 2 | Boutique fixe |
| **532** | Établissement B — Caisse 1 | Boutique fixe |
| **5321** | Établissement B — Caisse 2 | Boutique fixe |
| **5322** | Établissement B — Caisse 3 | Boutique fixe |
| **533** | Stand forain — Caisse mobile 1 | Nomade |
| **5331** | Stand forain — Caisse mobile 2 | Nomade |

> Numérotation **libre** tant que cohérente ; Paheko cite l'exemple ressourcerie : *531 Caisse magasin sud*, *532 Caisse magasin nord*.

---

## 4. Chèques, CB, banque (multi-lieux)

| Moyen | Règle multi-sites |
|--------|-------------------|
| **5112** (chèques) | **Un seul 5112** si tous les chèques sont déposés sur le **même** compte bancaire ; sinon sous-comptes **5112.x** par lieu ou par banque de dépôt. |
| **511** (CB) | **Un seul 511** si un contrat TPE unique ; sinon **511x** par terminal / banque de crédit. |
| **512** | **Un 512 par compte bancaire réel**, indépendamment du nombre de caisses. |

Les comptes **7070** (ventes) et **7541** (dons caisse) restent en principe **globaux** à la clôture ; seuls les **débits trésorerie** se ventilent par 53x / 511 / 5112.

---

## 5. Virements internes (compte 58)

**Jamais** de transfert direct **531 ↔ 532** (ou entre deux 53x).

| Opération | Écritures type |
|-----------|----------------|
| Dépôt espèces caisse → banque | Débit **58** / Crédit **53x** puis Débit **512** / Crédit **58** |
| Approvisionnement stand depuis caisse principale | Idem via **58** (transit, solde 58 ≈ 0) |
| Achat espèces magasin | Débit **53x** / Crédit **6xx** — **pas** le compte 58 |

Voir [décisions D22](2026-05-21_decisions-compta-liaison-paheko-recherche-terrain.md) (compte 58).

---

## 6. Clôture de session (multi-poste)

Pour **chaque** `cash_session` clôturée :

1. Identifier le **`cash_register_id`** (lieu de vente).
2. Charger le **compte 53x** configuré sur ce poste.
3. Pièce 1 — ventes + dons : débit **53x du poste** + 5112/511 selon moyens ; crédit 7070 + 7541.
4. Pièce 2 — écart comptage (si besoin) : 658/758 ↔ **53x du poste**.
5. Outbox Paheko : libellé incluant **site + poste + session** (ex. `Z caisse — {site} — {register} — SESSION {id}`).

**Rappel PRD :** stratégie B = transactions séparées ventes+dons / remb. courant / remb. antérieur — **par session**, donc **par poste** en multi-caisses.

---

## 7. Paramétrage Paheko (Lieux de vente)

Checklist admin (Carole / EC) :

- [ ] Créer les comptes **53x** dans le plan comptable Paheko (libellés explicites).
- [ ] Créer un **Lieu de vente** par poste physique (aligné `cash_registers` RecyClique).
- [ ] Dupliquer les **moyens de paiement** par lieu (espèces → 53x du lieu ; chèque/CB selon §4).
- [ ] Vérifier que la clôture native Paheko (si encore utilisée) ne contredit pas les écritures API RecyClique.
- [ ] Documenter le tableau **poste RecyClique → compte 53x → lieu Paheko** (annexe EC).

---

## 8. RecyClique — évolutions produit attendues

| Zone | Avant (mono-caisse) | Cible multi-caisse |
|------|---------------------|-------------------|
| **Seeds / SuperAdmin** | `paheko_debit_account: "530"` global | Compte espèces **par `cash_registers`** |
| **Clôture / snapshot** | Totaux agrégés | `cash_register_id` + compte 53x dans snapshot / outbox |
| **Module comptage** | — | Obligatoire **par session de poste** |
| **Admin** | `/admin/cash-registers` | Champ **compte Paheko espèces** (+ aide 53x) par poste |
| **Moyens paiement** | Liste globale | Option : comptes 511/5112 par poste ou règle globale documentée §4 |

**Hors scope immédiat :** migration automatique du plan Paheko ; API liste exercices ; HelloAsso.

---

## 9. Questions expert-comptable (multi-caisse)

1. Valider la **grille 531–5331** (ou format long 531001…) pour les 7 caisses prévues.
2. **5112** unique ou ventilé par établissement / banque ?
3. **511** unique ou par terminal CB ?
4. Fond de caisse : mouvement **53x** à chaque ouverture RecyClique ou solde permanent sans écriture d'ouverture ?
5. Cohérence avec **projets analytiques** Paheko par site (PRD vision multisite).

---

## 10. Mono-caisse vs multi-caisse (rappel)

| Contexte | Compte espèces |
|----------|----------------|
| **Une seule** caisse boutique | **530** suffit (fond = solde permanent sur 530) |
| **Plusieurs** caisses physiques | **Un 53x par caisse** ; ne pas tout passer en 530 |

Ceci **affine** la validation 2e passe (Q4 « 530 ou 531 ») : le débat 531 n'est pertinent que pour la **2e caisse du même établissement** ou le passage au **multi-caisse**.
