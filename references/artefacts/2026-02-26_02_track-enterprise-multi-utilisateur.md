# Track BMAD Enterprise - multi-utilisateur, une instance par ressourcerie

Date : 2026-02-26

## Décision projet

- **Track BMAD : Enterprise** (sécurité, conformité, DevOps).
- **Modèle** : **multi-utilisateur** (plusieurs rôles par instance) ; **une instance par ressourcerie** (pas de multi-tenant).

## Livrables Enterprise

D'après la doc BMAD, le track Enterprise produit : PRD + Architecture + Security + DevOps. Dans l'install actuelle, il n'y a pas de workflow dédié « Create Security » ou « Create DevOps » - ces thèmes sont couverts dans le PRD (NFR Security, Compliance) et dans le workflow **Create Architecture** (catégories Authentication & Security, Infrastructure & Deployment). L'architecture et le PRD doivent les traiter explicitement.

## Référence

- Plan : passage du projet en mode entreprise (track BMAD Enterprise).
- `references/ou-on-en-est.md` : section Track BMAD.
