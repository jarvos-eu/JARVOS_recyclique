# Transcription — JARVOS Recyclique (terrain)

## Déposer les audios

Copier les fichiers dans **`inbox/`** (ce dossier n'est pas versionné).

Chemin complet sur cette machine :

`JARVOS_recyclique/.transcription/inbox/`

Formats pris en charge par le skill : `.mp3`, `.wav`, `.m4a`, `.flac`, `.ogg`.

## Clé API AssemblyAI

Ordre de chargement (skill) :

1. `%USERPROFILE%\.cursor\skills\transcription-pipeline-v1.1\env\.env` (clé partagée entre projets)
2. `.transcription/.env` (projet uniquement, ignoré par git)
3. `.env` à la racine du repo (ignoré par git)

Un test de connexion a réussi (GET `https://api.assemblyai.com/v2/account`, HTTP 200) avec la clé trouvée dans le `.env` du skill.

## Profil et template

Fichier : **`transcription-profile.json`**.

- Type : `multi` (choix du template possible à chaque run).
- Template par défaut : **`brainstorming-organique`** (fiches d'idées + tags).
- Diarisation : `true`, langue : `fr`.
- Pattern `meeting_id` : `YYYY-MM-DD-recyclique-terrain` (ex. `2026-05-21-recyclique-terrain-entretien-caisses`).

Renommer les intervenants dans `speakers` après les premières transcriptions si besoin.

## Sorties

Après passage du pipeline : `.transcription/meetings/<MEETING_ID>/` (non versionné). Document final assemblé : `meetings/<MEETING_ID>/final/<MEETING_ID>.md`.

## Lancer le pipeline

Voir le skill **transcription-pipeline-v1.1** (étapes scan inbox, `run_pipeline.py`, etc.).

## Révision et QA2 (mai 2026)

**État (2026-05-21) :** révision éditoriale appliquée sur les **6** meetings (drafts + finaux). Rapports `qa2-draft-fusion.md` : **4/6** présents ; absents pour `2026-05-21-terrain-1401` et `2026-05-21-recyclique-terrain-paheko`. Recap idées : **`references/artefacts/2026-05-21_02_recap-idees-paheko-reception-terrain.md`**. Journaux de chantier archivés : `references/artefacts/archive/2026-05-21-menage-paheko-compta-qa/`.

## Notes vocales (13/06/2026)

**3** notes téléphone traitées : `2026-06-13-notes-01` (inscription/import), `2026-06-13-notes-02` (onboarding overlay), `2026-06-13-notes-03` (dashboard perso / présence). Addendum idées : **`references/artefacts/2026-06-13_01_addendum-notes-vocales-onboarding-dashboard.md`** (USR-001…012).
