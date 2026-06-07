# Conventions — révisions terrain

## Identifiants

```
REV-<DOMAINE>-<NN>
```

| Code domaine | Fichier | Exemple |
|--------------|---------|---------|
| `CAISSE` | `domaines/caisse.md` | REV-CAISSE-06 |
| `RECEPTION` | `domaines/reception.md` | REV-RECEPTION-01 |
| `ADMIN` | `domaines/admin.md` | REV-ADMIN-03 |
| `TRANSVERSE` | `domaines/transverse.md` | REV-TRANSVERSE-02 |

**NN** = numéro séquentiel **par domaine** (01, 02, …). Ne pas réutiliser un ID supprimé ; marquer « annulé » dans les notes si besoin.

---

## Types (tag obligatoire sur chaque item)

| Type | Quand l'utiliser |
|------|------------------|
| **métier** | Règle métier fausse, incompréhensible ou manquante pour l'opératrice |
| **UI/UX** | Layout, lisibilité, navigation, libellés, feedback utilisateur |
| **tech** | Bug technique, état incohérent, API, persistance, permissions |
| **parité-legacy** | Écart vs Recyclique 1.4.4 (geste ou écran attendu) |
| **cadrage-produit** | Décision PO à trancher (feature v2 vs masquer en beta) |

Un item peut porter **plusieurs types** (ex. `UI/UX` + `parité-legacy`).

**Origine (champ Signalé)** — indiquer clairement :

- `2026-06-07` seul → **revue live Strophe** ;
- `2026-05-27 (rapport parité)` ou `import audit` → écart documenté par un agent code, **pas forcément vu en terrain** ;
- ne pas mélanger pilotage dev (tags, C2b, C3…) avec des bugs terrain sans l’indiquer.

---

## Priorités

| Priorité | Signification |
|----------|---------------|
| **P0** | Bloquant quotidien (caissier / réceptionniste ne peut pas finir son geste) |
| **P1** | Fortement pénible ; contournement difficile |
| **P2** | Dette, polish, ou attente décision produit |

---

## Cases à cocher (par item)

Chaque item comporte ce bloc — **les agents cochent les trois premières** ; **Strophe coche Validé HITL** après retest terrain.

```markdown
**Suivi**
- [ ] Investigé — cause ou périmètre identifié (noter en « Notes agent »)
- [ ] Corrigé — fix livré (PR, commit ; référence en notes)
- [ ] Validé HITL — retest terrain OK (Strophe)
```

Optionnel :

```markdown
- [ ] Story / ticket — lié à une story BMAD ou issue (référence en notes)
```

---

## Structure d'un fichier domaine

1. En-tête (périmètre, liens doc, synthèse session)
2. **Tableau de bord** — tous les items du domaine avec colonnes Suivi
3. Sections thématiques (D1, D2, …) avec fiches détaillées
4. Pistes techniques transverses (si pertinent)
5. Pas de journal local — tout ajout passe par [`journal.md`](journal.md)

---

## Ajouter un problème (revue live)

1. Choisir ou **créer** `domaines/<domaine>.md` (copier la structure depuis `domaines/caisse.md`).
2. Prochain ID `REV-<DOMAINE>-NN`.
3. Copier [`_template-item.md`](_template-item.md), remplir, placer dans la bonne section thématique.
4. Ajouter une ligne au tableau de bord du domaine.
5. Ligne dans [`journal.md`](journal.md) : date, auteur, ID, une phrase.
6. Si **P0** : ajouter une ligne au tableau « Vue d'ensemble P0 » de [`index.md`](index.md).

---

## Nommage fichiers domaine

```
domaines/<slug-metier>.md
```

Slugs en minuscules, tirets : `caisse.md`, `reception.md`, `liaison-paheko.md`, `comptage-pieces-billets.md`.

Créer un nouveau fichier dès qu'un domaine a **≥ 3 items** ou une **session de revue dédiée** — pas besoin d'anticiper tous les domaines.
