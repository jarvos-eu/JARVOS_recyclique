# Analyse déclarations — Recyclivre (La Clique)

**Date :** 2026-07-07  
**Partenaire :** Recyclivre (cession livres ESS — **pas** éco-organisme REP)  
**Sources :** `referentiels-officiels/` (4 fichiers) — pas de `declarations-la-clique/`

---

## Résumé exécutif

Recyclivre n’est pas une filière REP type Ecologic/Ecomaison : c’est un **partenariat commercial** (cession de livres triés) avec rétrocession **10 %** (tri seul) ou **15 %** (tri + scan). Pas de grille xlsx trimestrielle côté La Clique — suivi **opérationnel + financier**. Module JARVOS = partenaire flux dédié, pas export poids REP.

---

## Obligations pour La Clique

- **Pas de déclaration REP trimestrielle** au sens eco-organismes.
- **Opérationnel :** tri selon critères art. 2, conditionnement cartons/palettes, remise régulière, exclusivité dons publics (point-livres) et scan si mode scan.
- **Financier :** percevoir rétrocession sur livres **vendus par Recyclivre** ; rapports trimestriels **envoyés par Recyclivre** (format inconnu dans le dépôt).

---

## Flux à tracer

| Flux | Détail |
|------|--------|
| Entrées | Dons point-livres, dépôts internes |
| Tri / rejet | Exclusions : dict., encyclo., manuels, sans code-barres, clubs, revues, langues étrangères ; mail ajoute **millésimés** |
| Sortie Recyclivre | Cession cartons/palettes |
| Sortie boutique | Vente locale (mode scan uniquement) |
| Recyclage | Rejets non acceptés au scan |
| Retour financier | 10–15 % ventes nettes HT Recyclivre |

**Unité :** nombre de **livres** (pas kg REP).

---

## Mapping brouillon Recyclique → Recyclivre

```
Livres (réception)
├── entrée_don_public
├── entrée_don_interne
├── tri_rejet
├── sortie_recyclivre
├── sortie_boutique      (vente caisse — LCQ-003)
├── sortie_recyclage
└── retour_financier     (hors agrégats poids)
```

---

## Cas particuliers

- Livres point-livres : **priorité Recyclivre** (art. 4) — conflit possible vente boutique.
- Livres vendus par Recyclivre mais rejetés au scan : pas de rétrocession.
- Ne pas confondre flag Paheko `LIV` (DEEE) avec filière livres.

---

## Gaps / questions La Clique

| Gap | Question |
|-----|----------|
| Mode **tri vs scan** inconnu | Convention signée ? |
| Placeholders `XXXX` dans conventions | Statut partenariat ? |
| Outil scan non documenté | API / formation ? |
| Rapports trimestriels Recyclivre absents | Format retour ? |
| Millésimés dans mail, pas conventions | Règle tri officielle ? |

---

## Pistes patch 1.4.5

Ne pas forcer le modèle 3 flux poids eco-maison. Prévoir sous-flux `recyclivre | boutique | recyclage` si mode scan ; comptage pièces + lots expédition.
