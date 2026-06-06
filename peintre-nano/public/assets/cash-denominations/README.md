# Pictos dénominations — comptage pièces/billets (Story 9.12)

Pack **SVG stylisé** pour le wizard de clôture Recyclique (`comptage-pieces-billets`).

## Convention de nommage

| Fichier | Code API | Exemple |
|---------|----------|---------|
| `{code}.svg` | `EUR_2000` | `EUR_2000.svg` (20 €) |

Les 15 codes correspondent au référentiel backend `GET /v1/cash-denominations`.

## Style

- Formes **génériques** (rectangle billets, cercle pièces) + libellé valeur.
- **Pas** de reproduction photographique de billets BCE (règle D-CPT-06 / conformité monnaie).

## Sources / licences

Assets générés in-repo (formes géométriques + texte système). Aucune image BCE ni photo réaliste.

Pour extensions futures, privilégier des pictos génériques sous licence commerciale sans attribution obligatoire (ex. UXWing, Noun Project) — documenter ici toute source externe ajoutée.

## Option module

`module-config.payload.show_images: false` masque les pictos ; le libellé texte (`label_fr`) reste affiché.
