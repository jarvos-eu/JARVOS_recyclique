#!/usr/bin/env python3
"""Boucle locale : un fichier _queue -> inbox -> run_pipeline -> vider inbox.

Chemins : relatifs à ce fichier (portable Linux/macOS/Windows).
Skill : ~/.cursor/skills/transcription-pipeline-v1.1 ou TRANSCRIPTION_SKILL_ROOT.
"""
from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
TRANSCRIPTION_ROOT = SCRIPT_DIR
REPO_ROOT = SCRIPT_DIR.parent
AUDIO_EXT = {".m4a", ".mp3", ".wav", ".flac", ".ogg"}


def skill_root() -> Path:
    env = os.environ.get("TRANSCRIPTION_SKILL_ROOT")
    if env:
        return Path(env)
    default = Path.home() / ".cursor" / "skills" / "transcription-pipeline-v1.1"
    if default.is_dir():
        return default
    legacy_win = Path(r"C:\Users\Strophe\.cursor\skills\transcription-pipeline-v1.1")
    if legacy_win.is_dir():
        return legacy_win
    return default


def meeting_id_for(filename: str) -> str:
    m = re.match(
        r"^(\d{2})-(\d{2})-(\d{4})\s+(\d+)\.(\d+)\.m4a$",
        filename,
        re.IGNORECASE,
    )
    if m:
        day, month, year, hh, mm = m.groups()
        return f"{year}-{month}-{day}-terrain-{int(hh):02d}{int(mm):02d}"
    low = filename.lower()
    if "paheko" in low:
        return "2026-05-21-recyclique-terrain-paheko"
    return "2026-05-21-recyclique-terrain-unknown"


def main() -> int:
    queue = TRANSCRIPTION_ROOT / "_queue"
    inbox = TRANSCRIPTION_ROOT / "inbox"
    inbox.mkdir(parents=True, exist_ok=True)

    if not queue.is_dir():
        print(
            f"[queue] Dossier absent : {queue} (créer _queue/ et y déposer les audios)",
            file=sys.stderr,
        )
        return 1

    files = sorted(
        (f for f in queue.iterdir() if f.is_file() and f.suffix.lower() in AUDIO_EXT),
        key=lambda p: p.name.lower(),
    )
    if not files:
        print("[queue] Aucun fichier audio dans _queue/", file=sys.stderr)
        return 1

    skill = skill_root()
    run_script = skill / "scripts" / "run_pipeline.py"
    if not run_script.is_file():
        print(
            f"[queue] Script introuvable : {run_script}\n"
            "  Définir TRANSCRIPTION_SKILL_ROOT vers transcription-pipeline-v1.1",
            file=sys.stderr,
        )
        return 1

    exit_summary: list[tuple[str, str, int, str]] = []

    for src in files:
        mid = meeting_id_for(src.name)
        dest = inbox / src.name
        shutil.copy2(src, dest)
        print(f"\n=== Run: {src.name} -> meeting_id={mid} ===\n", flush=True)
        proc = subprocess.run(
            [
                sys.executable,
                str(run_script),
                "--transcription-root",
                str(TRANSCRIPTION_ROOT),
                "--meeting-id",
                mid,
                "--verbose",
            ],
            cwd=str(REPO_ROOT),
        )
        err = ""
        if proc.returncode != 0:
            err = f"exit_code={proc.returncode}"
            print(f"[ERREUR] {src.name} ({mid}): {err}", file=sys.stderr)
        if dest.exists():
            dest.unlink()
        exit_summary.append((src.name, mid, proc.returncode, err))

    print("\n--- Résumé ---", flush=True)
    for name, mid, code, err in exit_summary:
        print(f"  {code}\t{mid}\t{name}\t{err}", flush=True)

    return 0 if all(c == 0 for _, _, c, _ in exit_summary) else 2


if __name__ == "__main__":
    raise SystemExit(main())
