# Versioning — JARVOS Recyclique

Convention simplifiee de statut produit. Objectif : eviter les confusions liees aux versions intermediaires.

---

## Decision active (a appliquer maintenant)

Le projet **n'utilise plus** les versions intermediaires `v0.x` pour piloter le travail.

Le pilotage se fait avec :

- les **epics/stories** (`_bmad-output/planning-artifacts/epics.md`) pour le "quoi faire",
- un **statut de maturite produit** pour le "ou on en est".

---

## Statuts de maturite (source de verite)

Utiliser uniquement ces 3 statuts :

1. **alpha interne** : construction active, instable, changements frequents.
2. **beta terrain** : tests reels/operationnels, stabilisation, corrections prioritaires.
3. **v1.0 prod** : mise en production stable chez La Clique, sans rupture des usages cibles.

---

## Regles d'usage

- Ne plus creer ni annoncer de jalons `v0.1`, `v0.2`, `v0.3`, etc.
- Les anciennes mentions `v0.x` dans les docs historiques sont considerees comme des **etiquettes de phase passees**, non bloquantes.
- Les decisions de priorite se prennent via backlog/epics/stories, pas via numerotation de versions intermediaires.
- Le passage en **v1.0 prod** se decide explicitement quand la checklist de readiness prod est validee.

---

## Tags Git

- Tant que le projet n'est pas en production stable : pas d'obligation de tag de release.
- Premier tag cible recommande : `v1.0.0` (apres validation explicite).
- Ne pas creer de tag sans validation de Strophe.
