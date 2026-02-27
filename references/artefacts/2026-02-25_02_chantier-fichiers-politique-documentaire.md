# Chantier - Fichiers et politique documentaire

**Date :** 2026-02-25  
**Scope :** Versions futures (pas la migration immediate). Chantier a part entiere ; exploration et formalisation.

---

## Objectif

Explorer et formaliser une **politique documentaire** et un **acces unifie** aux fichiers (Paheko + services tiers), avec possibilite de **matrice vivante** selon les installations (tout local, K-Drive, Nextcloud, etc.).

## Pistes a creuser

- **Matrice** : qui depose quoi ou (compta → Paheko, partage → K-Drive ou local, etc.) ; matrice potentiellement vivante par instance.
- **Matrice « qui dépose quoi où » (mise à jour story 10.2)** :
  | Qui / Rôle        | Type de document              | Où (backend)        |
  |-------------------|-------------------------------|---------------------|
  | Compta / admin    | Factures, pièces compta       | Paheko (transaction) |
  | App RecyClique    | Statutaire, com, prise de notes | Fonds RecyClique (volume dédié / K-Drive) |
  | Membres / web     | Documents membres, pages web  | Paheko (user, web)  |
  Fonds RecyClique = distinct de Paheko ; voir `doc/fonds-documentaire-recyclique.md`.
- **Backends multiples** : local, K-Drive, Nextcloud, autres ; mutualisation et complexite.
- **Flux scans factures** : parcours scan → stockage / lien ecriture Paheko ; decision de design.
- **Upload RecyClique → Paheko** : WebDAV vs endpoint plugin (voir analyse brownfield) ; frontiere plugin Paheko / app RecyClique.
- **Volume partage Docker** (si applicable) : lecture/RAG OK ; ecriture liee compta via WebDAV ou API pour coherence metadonnees.
- **Collabora** : contexte (edition en ligne) ; self-host = container dedie + config Paheko.

## References

- Capacites fichiers Paheko : `references/artefacts/2026-02-24_11_capacites-paheko-calendrier-fichiers-communication.md`.
- API, WebDAV, upload : `references/paheko/analyse-brownfield-paheko.md`.

## Lien idees-kanban

Idee dediee : `references/idees-kanban/a-creuser/2026-02-25_chantier-fichiers-politique-documentaire.md`.
