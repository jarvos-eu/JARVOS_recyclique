# Inbox — audios terrain (non versionné sauf ce fichier)

Déposer ici les fichiers audio **avant** d’exécuter le skill **transcription-pipeline-v1.1** (scan inbox → `run_pipeline.py`).

## Formats

`.mp3`, `.wav`, `.m4a`, `.flac`, `.ogg` (voir README parent).

## Nommage recommandé

- `YYYY-MM-DD HH.MM.m4a` → le script `_queue_run_pipeline.py` déduit un `meeting_id` du type `YYYY-MM-DD-terrain-HHMM`.
- Sinon : inclure un mot-clé métier (`paheko`, etc.) ou passer `--meeting-id` explicitement lors d’un run manuel du pipeline.

## Fichiers dans ce dossier

Tout fichier audio copié ici reste **local** (gitignore `.transcription/*` sauf exceptions listées dans `.gitignore` à la racine). Ne pas committer d’audio ni de secrets.

## Run pipeline

1. Clé AssemblyAI : voir [README parent](../README.md) (ordre `.env` skill → `.transcription/.env` → `.env` racine).
2. Racine du skill : variable d’environnement `TRANSCRIPTION_SKILL_ROOT` si le skill n’est pas sous `~/.cursor/skills/transcription-pipeline-v1.1`.
3. Commande type (depuis la racine du dépôt, adapter les chemins) :

```bash
python "$TRANSCRIPTION_SKILL_ROOT/scripts/run_pipeline.py" \
  --transcription-root "$(pwd)/.transcription" \
  --meeting-id "2026-05-23-recyclique-terrain-audit-final" \
  --verbose
```

Les sorties vont sous `.transcription/meetings/<MEETING_ID>/` (non versionné).
