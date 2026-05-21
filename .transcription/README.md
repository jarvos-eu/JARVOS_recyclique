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

Révision consolidée des fichiers nécessaires (draft, final, rapports QA2, lacunes) : **`references/artefacts/2026-05-21_03_revision-transcriptions-terrain-qa2.md`**. **Révision éditoriale appliquée** (drafts corrigés + finaux régénérés) : **`references/artefacts/2026-05-21_04_revision-editoriale-transcriptions-appliquee.md`**. Les rapports adversariaux draft par meeting : `meetings/<MEETING_ID>/qa2-draft-fusion.md` lorsqu'ils existent.
