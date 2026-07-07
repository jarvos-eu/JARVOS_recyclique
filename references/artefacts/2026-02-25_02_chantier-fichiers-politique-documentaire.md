# Chantier — Fichiers et politique documentaire

**Date :** 2026-02-25  
**Scope :** Versions futures (pas la migration immediate). Chantier a part entiere ; exploration et formalisation.

---

## Objectif

Explorer et formaliser une **politique documentaire** et un **acces unifie** aux fichiers (Paheko + services tiers), avec possibilite de **matrice vivante** selon les installations (tout local, K-Drive, Nextcloud, etc.).

## Pistes a creuser

- **Matrice** : qui depose quoi ou (compta → Paheko, partage → K-Drive ou local, etc.) ; matrice potentiellement vivante par instance.
- **Backends multiples** : local, K-Drive, Nextcloud, autres ; mutualisation et complexite.
- **Flux scans factures** : parcours scan → stockage / lien ecriture Paheko ; decision de design.
- **Upload Recyclic → Paheko** : WebDAV vs endpoint plugin (voir analyse brownfield) ; frontiere plugin Paheko / app Recyclic.
- **Volume partage Docker** (si applicable) : lecture/RAG OK ; ecriture liee compta via WebDAV ou API pour coherence metadonnees.
- **Collabora** : contexte (edition en ligne) ; self-host = container dedie + config Paheko.

## References

- Capacites fichiers Paheko : `references/artefacts/2026-02-24_11_capacites-paheko-calendrier-fichiers-communication.md`.
- API, WebDAV, upload : `references/paheko/analyse-brownfield-paheko.md`.
- **K-Drive headless VPS** (version intermediaire, kSuite gratuit) : [`2026-07-07_08_installation-kdrive-headless-vps.md`](2026-07-07_08_installation-kdrive-headless-vps.md) — clone local sur VPS pour agents ; lien bot Discord [`2026-07-05_02`](2026-07-05_02_cadrage-bot-discord-la-clique-pilote.md).

## Lien idees-kanban

Idee dediee : `references/idees-kanban/a-creuser/2026-02-25_chantier-fichiers-politique-documentaire.md`.
