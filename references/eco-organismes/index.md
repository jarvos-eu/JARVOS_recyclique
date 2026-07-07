# Index — references/eco-organismes/

Matière **module déclarations éco-organismes** : référentiels partenaires, déclarations terrain **La Clique Qui Recycle**, contrats et exports — source pour mapping Recyclique → catégories officielles et patch **1.4.5**.

> Charger si : cadrage Epic 9, mapping catégories, patch stats/décla La Clique, ou préparation déclarations trimestrielles.

**Source dépôt :** K-Drive La Clique, zip `references/_depot/EcoOrganismes.zip` (ventilé le **2026-07-07**).  
**Inventaire détaillé :** [artefacts/2026-07-07_01_inventaire-depot-eco-organismes-la-clique.md](../artefacts/2026-07-07_01_inventaire-depot-eco-organismes-la-clique.md).  
**Calendrier déclarations (2026-07-07) :** [2026-07-07_calendrier-declarations-partenaires.md](2026-07-07_calendrier-declarations-partenaires.md) — échéances trimestrielles par partenaire, vue consolidée juil.–déc. 2026.  
**Grilles déclaration finale (2026-07-07) :** [2026-07-07_grilles-declaration-finale-champs-a-remplir.md](2026-07-07_grilles-declaration-finale-champs-a-remplir.md) — cases à remplir par partenaire (Ecomaison, Ecologic, Refashion), exemples T4/T1, gaps Recyclique.

**Liens projet :**
- Vision module : [vision-projet/vision-module-decla-eco-organismes.md](../vision-projet/vision-module-decla-eco-organismes.md)
- Filières REP (générique) : [migration-paheko/categories-decla-eco-organismes.md](../migration-paheko/categories-decla-eco-organismes.md)
- Pack brownfield specs : `recyclique-1.4.4/docs/eco-organismes/`
- Retour terrain dashboard : [artefacts/2026-07-05_01_feedback-la-clique-dashboard-stats-eco-organismes.md](../artefacts/2026-07-05_01_feedback-la-clique-dashboard-stats-eco-organismes.md)

---

## Structure

```
eco-organismes/
  partenaires/
    ecomaison/          ← priorité patch La Clique
    ecologic/           ← déclarations EEE déjà faites (ASL, écrans, etc.)
    refashion/
    valdelia/
    recyclivre/
  transverse/           ← synthèse filières, fonds réemploi FDF
```

Chaque partenaire :

| Sous-dossier | Contenu |
|--------------|---------|
| `referentiels-officiels/` | Modes opératoires, guides tri, schémas bennes, partenariat ESS |
| `referentiels-officiels/contrats-referencement/` | Contrats, annexes, dossiers référencement (Ecologic) |
| `declarations-la-clique/YYYY-Tn/` | Feuilles Excel/PDF/CSV **déjà remplies** par l'équipe (entrées, sorties, factures) |
| `divers/` | Reste non classé (ex. Refashion) |
| `2026-07-07_analyse-declarations-mapping.md` | **Analyse mapping** (workers 07/07) — obligations, matrice brouillon, gaps |

**Analyses partenaires (2026-07-07) :**

| Partenaire | Rapport |
|------------|---------|
| Ecomaison | [partenaires/ecomaison/2026-07-07_analyse-declarations-mapping.md](partenaires/ecomaison/2026-07-07_analyse-declarations-mapping.md) — **P0 patch** |
| Ecologic | [partenaires/ecologic/2026-07-07_analyse-declarations-mapping.md](partenaires/ecologic/2026-07-07_analyse-declarations-mapping.md) |
| Refashion | [partenaires/refashion/2026-07-07_analyse-declarations-mapping.md](partenaires/refashion/2026-07-07_analyse-declarations-mapping.md) |
| Valdelia | [partenaires/valdelia/2026-07-07_analyse-declarations-mapping.md](partenaires/valdelia/2026-07-07_analyse-declarations-mapping.md) |
| Recyclivre | [partenaires/recyclivre/2026-07-07_analyse-declarations-mapping.md](partenaires/recyclivre/2026-07-07_analyse-declarations-mapping.md) |

---

## Fichiers clés — eco-maison (mapping patch)

**Déclarations T4 2025** (`partenaires/ecomaison/declarations-la-clique/2025-T4/`) — **matière première mapping** (noms « RECYCLIC ») :

| Fichier | Intérêt |
|---------|---------|
| `ECO MAISON ENTREES * RECYCLIC.xlsx` (4 filières) | Entrées par catégorie officielle eco-maison |
| `SORTIES RECYCLIC *.xlsx` | Sorties ameublement / brico |
| `ECO MAISON SORTIES *.xlsx` | Sorties jouets, jardin |

**Déclarations T1 2026** (`.../2026-T1/`) — déclaration **en cours** : entrées/sorties par filière + factures + soutiens REP.

**Référentiels** (`partenaires/ecomaison/referentiels-officiels/`) :

- Modes opératoires déclarations ESS (juillet 2025, février 2026)
- Guides partenariat réemploi DEA / ABJ
- Schémas collecte, listes acceptés / interdits (PNG)

---

## Fichiers clés — Ecologic (autre partenaire déjà déclaré)

`partenaires/ecologic/declarations-la-clique/` — T4 2025 (ODS/XLSX entrées/sorties), **T1 2026** (exports par filière + pro forma validé), **T2 2026** (en cours).

| Trimestre | Fichier / doc clé |
|-----------|-------------------|
| T4 2025 | `2025-T4/DeclarationEcologic-EntreesDepot-4T2025-1.ods` + sorties |
| T1 2026 | Exports xlsx par filière + `pro forma déclaration T1 2026.csv` (218,87 € HT) |
| **T2 2026** | [`2026-T2/DeclarationESS-ECOLOGIC-2T2026_MODE-EMPLOI.md`](partenaires/ecologic/declarations-la-clique/2026-T2/DeclarationESS-ECOLOGIC-2T2026_MODE-EMPLOI.md) — **fiche mode d'emploi** ; ODS : `DeclarationESS-ECOLOGIC-2T2026.ods` · **mission urgence** : [`2026-07-07_mission-assistance-decla-ecologic-t2-2026.md`](partenaires/ecologic/declarations-la-clique/2026-T2/2026-07-07_mission-assistance-decla-ecologic-t2-2026.md) |

**Analyse mapping (2026-07-07) :** [partenaires/ecologic/2026-07-07_analyse-declarations-mapping.md](partenaires/ecologic/2026-07-07_analyse-declarations-mapping.md) — grilles T4, exports T1, codes pro forma, gaps.

---

## Suite recommandée (patch 1.4.5)

1. Extraire les **grilles Excel RECYCLIC T4 2025** → table de mapping catégories boutique La Clique → catégories eco-maison (artefact ou YAML config pilote).
2. Croiser avec les agrégats stats LCQ-001…003 (dashboard / export décla).
3. Ne pas dupliquer les PDF déjà dans `recyclique-1.4.4/docs/eco-organismes/eco-maison/` — **référencer** depuis cet index.
