# Transcription — JARVOS Recyclique (terrain)

## Déposer les audios

Copier les fichiers dans **`inbox/`** (contenu local non versionné ; seul `inbox/README.md` peut être suivi par Git).

Chemin type : **`<racine-repo>/.transcription/inbox/`** (voir aussi [inbox/README.md](inbox/README.md)).

Formats pris en charge par le skill : `.mp3`, `.wav`, `.m4a`, `.flac`, `.ogg`.

### File d’attente `_queue/` (optionnel)

Le script versionné **`_queue_run_pipeline.py`** lit **`_queue/`** (à créer à la racine de `.transcription/`), copie chaque audio vers `inbox/`, lance `run_pipeline.py`, puis retire la copie dans `inbox/`. Chemins **portables** (Linux / macOS / Windows). Racine du skill : variable d’environnement **`TRANSCRIPTION_SKILL_ROOT`** si le skill n’est pas dans `~/.cursor/skills/transcription-pipeline-v1.1`.

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

**Compte rendu structurant (2026-05-23) :** synthèse directions + dépendances + intégration futurs audios — [`references/artefacts/2026-05-23_01_compte-rendu-audit-terrain-directions-futures.md`](../references/artefacts/2026-05-23_01_compte-rendu-audit-terrain-directions-futures.md). Dossier **`inbox/`** documenté : [`inbox/README.md`](inbox/README.md).
