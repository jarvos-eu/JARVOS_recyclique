#!/usr/bin/env python3
"""List Recyclique PostgreSQL dumps and their inferred dates."""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

PATTERN = re.compile(
    r"recyclic_db_export_(?P<date>\d{8})_(?P<time>\d{6})\.dump$",
    re.IGNORECASE,
)


def parse_dump_name(path: Path) -> dict | None:
    m = PATTERN.match(path.name)
    if not m:
        return None
    dt = datetime.strptime(m.group("date") + m.group("time"), "%Y%m%d%H%M%S").replace(
        tzinfo=timezone.utc
    )
    return {
        "path": str(path.resolve()),
        "filename": path.name,
        "exported_at": dt.isoformat(),
        "exported_date": dt.date().isoformat(),
        "size_bytes": path.stat().st_size,
    }


def find_dumps(dump_dir: Path) -> list[dict]:
    dumps = []
    for p in sorted(dump_dir.glob("recyclic_db_export_*.dump")):
        meta = parse_dump_name(p)
        if meta:
            dumps.append(meta)
    dumps.sort(key=lambda d: d["exported_at"], reverse=True)
    return dumps


def main() -> int:
    parser = argparse.ArgumentParser(description="Manifest dumps Recyclique La Clique")
    parser.add_argument(
        "--dump-dir",
        type=Path,
        default=Path("references/_depot"),
        help="Dossier contenant les .dump",
    )
    parser.add_argument("--json", action="store_true", help="Sortie JSON")
    parser.add_argument(
        "--check-date",
        type=str,
        default=None,
        help="Date fin requête YYYY-MM-DD — exit 1 si dump trop ancien",
    )
    args = parser.parse_args()

    if not args.dump_dir.is_dir():
        print(f"Dossier introuvable: {args.dump_dir}", file=sys.stderr)
        return 2

    dumps = find_dumps(args.dump_dir)
    if not dumps:
        print(f"Aucun dump recyclic_db_export_*.dump dans {args.dump_dir}", file=sys.stderr)
        return 1

    latest = dumps[0]
    if args.json:
        print(json.dumps({"latest": latest, "all": dumps}, indent=2, ensure_ascii=False))
    else:
        print(f"Dernier dump: {latest['filename']}")
        print(f"  Exporté le: {latest['exported_date']}")
        print(f"  Chemin: {latest['path']}")
        print(f"  Taille: {latest['size_bytes']:,} octets")
        if len(dumps) > 1:
            print(f"\nArchives ({len(dumps) - 1}):")
            for d in dumps[1:]:
                print(f"  - {d['filename']} ({d['exported_date']})")

    if args.check_date:
        req = datetime.strptime(args.check_date, "%Y-%m-%d").date()
        dump_date = datetime.strptime(latest["exported_date"], "%Y-%m-%d").date()
        if req > dump_date:
            print(
                f"\nBLOQUANT: période demandée jusqu'au {req} > dump {dump_date}. "
                "Demander un export frais dans references/_depot/.",
                file=sys.stderr,
            )
            return 1
        print(f"\nOK: dump {dump_date} couvre la période jusqu'au {req}.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
