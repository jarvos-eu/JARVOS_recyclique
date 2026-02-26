# Parcours ouverture caisse, postes et accès PIN

---

## 2026-02-26 — Strophe

Idée : le **parcours d'ouverture de caisse** et la gestion des **postes** (réception vs caisse) et des **niveaux d'accès par PIN**.

- **Modes poste** : distinguer un mode « poste de réception » et un mode « poste de caisse ». Idéalement pouvoir ouvrir **plusieurs caisses** et **plusieurs postes de réception** — pas encore bien géré en 1.4.4.
- **Ouverture poste caisse** : pour accéder à tout l'espace d'administration, etc., il faut rentrer son **code PIN**. Le PIN détermine le **niveau d'accès** dans Recyclique.
  - Ex. caisse en veille → on rentre le PIN → si habilité caisse uniquement : accès caisse, pas les autres menus.
  - Si administrateur : accès à plus de parties (annuler des tickets, etc.).
- **Niveaux d'utilisateurs et groupes** : prévus partiellement en Recyclique 1.4.4 ; il faudra brainstormer, affiner et **rechercher les meilleures pratiques** (autres POS, autres logiciels).
- **Moment** : à creuser / rechercher probablement **avant l'architecture** (et donc avant le PRD détaillé sur ce point).

Intention : a-conceptualiser (puis a-rechercher pour benchmark POS, puis affiner avant architecture).
