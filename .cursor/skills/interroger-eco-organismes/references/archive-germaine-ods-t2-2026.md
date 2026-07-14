# Archive — tableur Germaine T2 2026 (ODS Ecologic + Ecomaison)

> **Lookup uniquement.** Le prochain trimestre ou partenaire peut envoyer un format **totalement différent**.  
> Ne charger ce fichier **que si** le tableur reçu ressemble à `DeclarationESS-ECOLOGIC-ECOMAISON-EntreesSorties.ods`.

**Artefacts session :**

- Template vierge : `references/_depot/DeclarationESS-ECOLOGIC-ECOMAISON-EntreesSorties.ods`
- Rempli validé T2 : `references/eco-organismes/.../2026-T2/DeclarationESS-ECOLOGIC-ECOMAISON-EntreesSorties-REMPLI.ods`
- Mode d'emploi structure : `…/2026-T2/DeclarationESS-ECOLOGIC-2T2026_MODE-EMPLOI.md`
- Script one-shot : `_tmp_fill_germaine_ods_v2.py` (racine repo)

---

## Résumé technique (si même format)

| Feuille | Ligne détail agent | Contenu |
|---------|-------------------|---------|
| `Entrees-Reception` | R13 | LIV Ecologic B–G + Ecomaison K–S |
| `Entrees-Reception` | R38 | Recyclage benne (kg) K–T |
| `Sortie-VenteDonsReemploi` | R19 | DEC_REE B–J + Ecomaison K–S |

**Ne jamais écrire** dans les lignes TOTAL (formules `table:formula` : R17, R33, R49, R21).

**ODS XML :** éditer avec **lxml** ; vérifier `table:formula` count ≥ 70 après écriture. ElementTree stdlib casse les namespaces.

**Col. T sorties :** si Germaine a déjà saisi T9–T18, ne pas réécrire T sur R19 (double comptage).

---

## Leçon métier (transposable)

Le rejet **PAM 246,5 t** (pesées tableur cumulées) vs **~1,1 t** (tickets Recyclique) est documenté dans [bdd-metier.md](bdd-metier.md) §5–§6 — **indépendant** du format Germaine.

---

## Brouillon agent d'origine

Détail complet session : [`../_brainstorm/2026-07-15_runbook-session-T2-learnings.md`](../_brainstorm/2026-07-15_runbook-session-T2-learnings.md) (non maintenu — préférer ce fichier + `bdd-metier.md`).
