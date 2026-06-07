# Index — Révisions terrain HITL

**Rôle :** registre **vivant** des problèmes constatés en test terrain (revue live, beta bénévoles). Un fichier par **domaine métier** ; suivi par **cases à cocher** pour agents et PO.

> **Agents — point d'entrée.** Charger ce fichier, puis **un seul** `domaines/<domaine>.md` selon la session. Ne pas charger tous les domaines.

**Démarré :** 2026-06-07 (première passe : caisse).

---

## Domaines actifs

| Domaine | Fichier | Items | P0 ouverts | Dernière maj |
|---------|---------|-------|------------|--------------|
| **Caisse** | [domaines/caisse.md](domaines/caisse.md) | 23 | 0 | 2026-06-07 |
| **Transverse** | [domaines/transverse.md](domaines/transverse.md) | 5 | 0 | 2026-06-07 |
| **Admin** | [domaines/admin.md](domaines/admin.md) | 10 | 0 | 2026-06-07 |
| **Réception** | [domaines/reception.md](domaines/reception.md) | 8 | 0 | 2026-06-07 |

**Journal global des ajouts :** [journal.md](journal.md)  
**Conventions (IDs, types, checkboxes) :** [CONVENTIONS.md](CONVENTIONS.md)  
**Modèle pour nouvel item :** [_template-item.md](_template-item.md)

---

## Vue d'ensemble P0 (tous domaines)

| ID | Domaine | Titre court | Investigé | Corrigé | HITL |
|----|---------|-------------|-----------|---------|------|
| REV-CAISSE-02 | Caisse | Fermeture sans effet | [x] | [x] | [ ] |
| REV-CAISSE-05 | Caisse | Montant OK, actions KO | [x] | [x] | [ ] |
| REV-CAISSE-06 | Caisse | Finalisation grisée | [x] | [x] | [ ] |
| REV-CAISSE-10 | Caisse | Held sale vs encaissement | [x] | [x] | [ ] |
| REV-CAISSE-12 | Caisse | Virtuel bloqué par réel | [x] | [x] | [ ] |
| REV-RECEPTION-02 | Réception | PWA sans retour menu | [x] | [x] | [ ] |

**P1 suivi (hors tableau P0) :** REV-CAISSE-01 — session orpheline : fix partiel 28.1 (`opened_at` + recollage) ; gap résiduel caissier / fond de caisse → voir [caisse.md §01](domaines/caisse.md#rev-caisse-01--session-orpheline-reprise-sans-date-claire).

*(Mettre à jour cette table quand un domaine est ajouté ou qu'un P0 change de statut.)*

---

## Workflow

### Strophe (revue live)

1. Explorer l'app à voix haute.
2. Dire le problème + le domaine approximatif (caisse, réception, etc.).
3. L'agent ajoute un item dans le bon `domaines/*.md` + une ligne dans `journal.md`.

### Agent (prise en charge)

1. Lire `CONVENTIONS.md` si premier passage.
2. Ouvrir le fichier domaine concerné.
3. Sur l'item : cocher **Investigé** quand la cause est identifiée ; **Corrigé** quand le fix est mergé ; laisser **Validé HITL** à Strophe.
4. Mettre à jour le tableau P0 de ce fichier `index.md` si pertinent.

### Lancer une vague de corrections

1. Trier par **P0** puis **type** (bloquant métier avant polish UI).
2. Croiser avec [checklist parité beta](../artefacts/2026-05-30_01_checklist-chantier-parite-v2-beta-1.4.4.md) et epics BMAD si story dédiée.

---

## Inventaire — ce que Strophe a dit en live (2026-06-07)

*Priorité pour la beta : ces items viennent de ta revue vocale, pas d’un autre agent.*

| Passage (ordre session) | Domaine | Items |
|-------------------------|---------|-------|
| Caisse : session, ticket, finalisation, fermeture, virtuel, remboursement | Caisse | REV-CAISSE-01…13 |
| Menu bandeau : manque « Mon profil » / PIN | Transverse + Admin | REV-TRANSVERSE-01 · REV-ADMIN-01 |
| Réception : hub vide, PWA coincée, layout, clavier, clôture ticket | Réception | REV-RECEPTION-01…06 |
| PWA : barre titre bleue, plier/déplier | Transverse | REV-TRANSVERSE-02, 03 |
| UUID, pavés dev, modules (erreur F5), KPI/comptage OK | Transverse + Admin | REV-TRANSVERSE-04, 05 · REV-ADMIN-02, 03 |
| Dashboard admin : Activité & Logs, super-admin repliable | Admin | REV-ADMIN-04 |
| Santé et signaux : langage humain | Admin | REV-ADMIN-05 |
| Sites & caisses : hub, CRUD sites, édition manquante, archiver ? | Admin | REV-ADMIN-06…10 |

**Total live Strophe :** 34 items (caisse 13 + transverse 5 + admin 10 + réception 6).

---

## Import rapport audit (collage autre session — pas une todo Strophe)

Le collage « plan post-9.6 », **C2b**, **C3**, **commit jalon 9.10**, tags `v2.0.0`… venait d’**un autre chat agent** (coordination dev). **Tu ne l’as pas demandé** — tu peux l’ignorer pour la revue terrain.

Écarts ajoutés depuis [`2026-05-26_03`](../artefacts/2026-05-26_03_rapport-parite-plancher-v2-gestes-terrain.md) **non vus en live** :

| Domaine | Items | Source |
|---------|-------|--------|
| Caisse | REV-CAISSE-14…22 | Rapport parité Agent A (code / spec) |
| Caisse | REV-CAISSE-23 | Référence checklist clavier audit — **optionnel**, pas bloquant ta revue |
| Réception | REV-RECEPTION-07, 08 | Rapport parité |

Contexte dev (info seulement) : agents A/B parité + Paheko **clos** côté code (mai 2026) — voir artefacts QA2 si besoin ; **pas d’action requise** de ta part.

---

## Recoupement audit parité ↔ revue live (2026-06-07)

Écarts du [rapport plancher](../artefacts/2026-05-26_03_rapport-parite-plancher-v2-gestes-terrain.md) **déjà couverts** par la session live :

| Rapport / thème | Item revision |
|-----------------|---------------|
| Grille catégories AZERTY 26 touches | **OK** — non itemisé |
| Raccourcis réception poids / destination | REV-RECEPTION-06 (partiel) |
| Hub réception sans liste | REV-RECEPTION-01 |
| Finalisation / encaissement bloqué | REV-CAISSE-05, 06, 10 |
| Fermeture caisse sans effet | REV-CAISSE-02 |
| Ticket étroit, panneaux session/tags | REV-CAISSE-04, 09, 13 |
| Admin sites/postes sans édition | REV-ADMIN-07, 08 |
| UUID partout | REV-TRANSVERSE-04 |
| D33 ±2 €, T3 batch | **Clos dev** story 9.10 — pas d’item P0 ouvert |

**Importés depuis l’audit** (non vus en live) : REV-CAISSE-14…22, REV-RECEPTION-07, 08. REV-CAISSE-23 = référence optionnelle seulement.

---

## Liens utiles (hors revision/)

- Checklist parité v2 / 1.4.4 : [`artefacts/2026-05-30_01_checklist-chantier-parite-v2-beta-1.4.4.md`](../artefacts/2026-05-30_01_checklist-chantier-parite-v2-beta-1.4.4.md)
- Rapport parité gestes terrain : [`artefacts/2026-05-26_03_rapport-parite-plancher-v2-gestes-terrain.md`](../artefacts/2026-05-26_03_rapport-parite-plancher-v2-gestes-terrain.md)
- Matrice pilotes : [`artefacts/2026-04-10_03_matrice-parite-ui-pilotes-peintre.md`](../artefacts/2026-04-10_03_matrice-parite-ui-pilotes-peintre.md)
- Besoins terrain Discord : [`besoins-terrains.md`](../besoins-terrains.md)

---

## Différence avec `artefacts/`

| | `references/revision/` | `references/artefacts/` |
|--|------------------------|-------------------------|
| **Usage** | Backlog terrain vivant, cochable, par domaine | Handoff ponctuel entre agents (mission, QA, brief) |
| **Durée** | Longue — jusqu'à beta stable | Court — archivable après traitement |
| **Format** | `domaines/<nom>.md` + journal | `YYYY-MM-DD_NN_titre.md` |
