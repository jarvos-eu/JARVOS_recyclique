# Story 10.2: (Post-MVP) Fonds documentaire RecyClique

Status: done

<!-- Story post-MVP. Validation optionnelle avant dev-story. -->

## Story

En tant qu'**organisation**,
je veux **gérer un fonds documentaire RecyClique (statutaire, com, prise de notes) distinct de la compta/factures Paheko**,
afin de **centraliser la doc et préparer l'évolution JARVOS Nano/Mini**.

## Acceptance Criteria

1. **Étant donné** la politique fichiers (artefact 2026-02-25_02) et le périmètre post-MVP  
   **Quand** le fonds documentaire est implémenté  
   **Alors** le stockage (volume dédié ou K-Drive) et la frontière avec Paheko sont définis (FR27)  
   **Et** la story est post-MVP.

2. **Étant donné** le fonds documentaire RecyClique  
   **Quand** un responsable consulte ou dépose des documents (statutaire, com, prise de notes)  
   **Alors** ces documents restent dans le périmètre RecyClique (pas de mélange avec compta/factures Paheko)  
   **Et** la matrice « qui dépose quoi où » (artefact 2026-02-25_02) est respectée ou mise à jour.

## Tasks / Subtasks

- [x] Task 1 — Définir le périmètre et la frontière avec Paheko (AC: #1)
  - [x] Documenter ce qui relève du fonds RecyClique vs compta/factures Paheko
  - [x] S'appuyer sur `references/artefacts/2026-02-25_02_chantier-fichiers-politique-documentaire.md`
- [x] Task 2 — Choisir et documenter le stockage (AC: #1)
  - [x] Volume dédié (Docker) ou K-Drive (ou autre backend selon politique)
  - [x] Critères : lecture/RAG possible ; écriture cohérente avec frontière Paheko
- [x] Task 3 — Implémenter ou spécifier l'accès au fonds (AC: #2)
  - [x] API ou interface de dépôt/consultation selon périmètre post-MVP (si report : documenter l'API cible)
  - [x] Mise à jour de la matrice « qui dépose quoi où » si nécessaire (artefact 2026-02-25_02)

## Dev Notes

- **Post-MVP** : cette story ne bloque pas la livraison MVP ; elle peut être planifiée après les epics 1–9.
- **Référence politique fichiers** : `references/artefacts/2026-02-25_02_chantier-fichiers-politique-documentaire.md` — matrice vivante, backends multiples (local, K-Drive, Nextcloud), frontière plugin Paheko / app RecyClique, volume partage Docker.
- **FR27** : (Post-MVP) Le système peut gérer un fonds documentaire RecyClique distinct de la compta/factures Paheko.
- Pas de migration 1.4.4 spécifique fonds documentaire ; alignement avec chantier fichiers et évolution JARVOS Nano/Mini.
- **Frontière Paheko** : compta/factures = Paheko ; statutaire, com, prise de notes = fonds RecyClique (stockage défini dans cette story). Ne pas dupliquer la gestion fichiers Paheko ; le fonds RecyClique reste distinct.
- Si implémentation backend : respecter `api/config/settings.py` pour la config et les conventions API/BDD (epics.md, architecture.md).

### Project Structure Notes

- Stockage : à placer selon décision (volume dédié, chemin configurable, ou intégration K-Drive/backends).
- Aucun impact sur les modules existants (loader, slots) sauf si un module dédié « fonds documentaire » est ajouté ; à préciser en implémentation.

### References

- [Source: _bmad-output/planning-artifacts/epics.md] Epic 10, Story 10.2, FR27
- [Source: references/artefacts/2026-02-25_02_chantier-fichiers-politique-documentaire.md] Politique documentaire, matrice qui dépose quoi où, backends (K-Drive, volume Docker)
- [Source: references/artefacts/2026-02-24_11_capacites-paheko-calendrier-fichiers-communication.md] Capacités fichiers Paheko (lien depuis artefact 02)
- [Source: references/paheko/analyse-brownfield-paheko.md] API, WebDAV, upload — frontière Paheko

## Dev Agent Record

### Agent Model Used

- bmad-dev (story 10.2)

### Debug Log References

-

### Completion Notes List

- **Task 1** : Périmètre et frontière documentés dans `doc/fonds-documentaire-recyclique.md` (§1) : fonds RecyClique = statutaire, com, prise de notes ; Paheko = compta/factures, documents membres, web. Référence à l’artefact 2026-02-25_02.
- **Task 2** : Stockage documenté (§2) : volume dédié Docker (config `FONDS_DOCUMENTAIRE_ROOT` / section settings), K-Drive ou autre backend selon politique ; critères lecture/RAG et écriture cohérente avec frontière Paheko.
- **Task 3** : API cible spécifiée (§3) : endpoints REST listage/dépôt/téléchargement par catégorie ; matrice « qui dépose quoi où » ajoutée dans `references/artefacts/2026-02-25_02_chantier-fichiers-politique-documentaire.md` et référencée depuis le doc. Pas d’implémentation code (story post-MVP, spécification livrée).

### File List

- doc/fonds-documentaire-recyclique.md (nouveau)
- doc/index.md (modifié — entrée fonds documentaire)
- references/artefacts/2026-02-25_02_chantier-fichiers-politique-documentaire.md (modifié — matrice qui dépose quoi où)
- _bmad-output/implementation-artifacts/10-2-post-mvp-fonds-documentaire-recyclique.md (modifié — tasks, Dev Agent Record, File List, Status)

## Senior Developer Review (AI)

- **Date :** 2026-02-27  
- **Reviewer :** bmad-qa (code review adversarial)  
- **Résultat :** Approved  
- **Vérifications :** Story post-MVP, livrable = spec + documentation (pas de code). Les trois livrables ont été lus et validés : `doc/fonds-documentaire-recyclique.md` (périmètre §1, stockage §2, API cible §3), `doc/index.md` (entrée fonds documentaire), `references/artefacts/2026-02-25_02_chantier-fichiers-politique-documentaire.md` (matrice « qui dépose quoi où »). AC1 et AC2 implémentés au sens spec ; toutes les tasks [x] réalisées. Aucun écart File List. Amélioration mineure possible : date en en-tête du doc fonds-documentaire (non bloquante).

## Change Log

- 2026-02-27 : Code review (bmad-qa) : approved. Livrables doc et matrice validés ; story post-MVP sans code, AC1/AC2 et tasks conformes. Status → done, epic-10 → done.
- 2026-02-27 : Story 10.2 implémentée (spec uniquement, post-MVP). Ajout doc fonds documentaire, matrice dans artefact politique fichiers, API cible documentée.
