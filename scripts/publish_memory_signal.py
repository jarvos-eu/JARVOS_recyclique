#!/usr/bin/env python3
"""CLI brownfield — publie project-memory-signal.json depuis REPRISE.md."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from trio_signal_lib import publish_memory_signal


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Publie project-memory-signal.json (brownfield, stdlib)."
    )
    parser.add_argument(
        "--project-root",
        type=Path,
        default=Path.cwd(),
        help="Racine du repo projet",
    )
    parser.add_argument(
        "--reprise",
        type=Path,
        default=None,
        help="Chemin REPRISE (défaut: {project-root}/REPRISE.md)",
    )
    parser.add_argument("--project-id", default=None, help="ID registre Mentor")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Affiche le JSON sans écrire",
    )
    args = parser.parse_args()

    payload, out_path, err = publish_memory_signal(
        args.project_root,
        reprise_path=args.reprise,
        project_id=args.project_id,
        dry_run=args.dry_run,
    )
    if err:
        print(err, file=sys.stderr)
        return 1

    text = json.dumps(payload, indent=2, ensure_ascii=False)
    if args.dry_run:
        sys.stdout.buffer.write((text + "\n").encode("utf-8"))
    else:
        print(f"OK {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
