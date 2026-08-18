#!/usr/bin/env python3
"""List Recyclique PostgreSQL dumps and Paheko SQLite dumps with inferred dates."""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

from check_paheko_dump import find_paheko_dumps

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


def print_recyclique(dumps: list[dict]) -> dict | None:
    if not dumps:
        print("Aucun dump recyclic_db_export_*.dump", file=sys.stderr)
        return None
    latest = dumps[0]
    print(f"Dernier dump Recyclique: {latest['filename']}")
    print(f"  Exporté le: {latest['exported_date']}")
    print(f"  Chemin: {latest['path']}")
    print(f"  Taille: {latest['size_bytes']:,} octets")
    if len(dumps) > 1:
        print(f"\nArchives Recyclique ({len(dumps) - 1}):")
        for d in dumps[1:]:
            print(f"  - {d['filename']} ({d['exported_date']})")
    return latest


def print_paheko(dumps: list[dict]) -> dict | None:
    if not dumps:
        print("Aucun dump Paheko (.sqlite) dans le dossier", file=sys.stderr)
        return None
    latest = dumps[0]
    print(f"Dernier dump Paheko: {latest['filename']}")
    print(f"  Date: {latest['exported_date']}")
    print(f"  Chemin: {latest['path']}")
    print(f"  Taille: {latest['size_bytes']:,} octets")
    if len(dumps) > 1:
        print(f"\nAutres SQLite ({len(dumps) - 1}):")
        for d in dumps[1:]:
            print(f"  - {d['filename']} ({d['exported_date']})")
    return latest


def check_freshness(latest: dict | None, check_date: str, label: str) -> int:
    if latest is None:
        print(
            f"\nBLOQUANT: aucun dump {label} pour contrôler la date {check_date}.",
            file=sys.stderr,
        )
        return 1
    req = datetime.strptime(check_date, "%Y-%m-%d").date()
    dump_date = datetime.strptime(latest["exported_date"], "%Y-%m-%d").date()
    if req > dump_date:
        print(
            f"\nBLOQUANT: période demandée jusqu'au {req} > dump {label} {dump_date}. "
            "Demander un export frais dans references/_depot/.",
            file=sys.stderr,
        )
        return 1
    print(f"\nOK: dump {label} {dump_date} couvre la période jusqu'au {req}.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Manifest dumps Recyclique (PostgreSQL) et/ou Paheko (SQLite)"
    )
    parser.add_argument(
        "--dump-dir",
        type=Path,
        default=Path("references/_depot"),
        help="Dossier contenant les .dump / .sqlite",
    )
    parser.add_argument(
        "--source",
        choices=["recyclique", "paheko", "all"],
        default="recyclique",
        help="recyclique = volumes décla ; paheko = fichier compta € (pas de poids)",
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

    rec = find_dumps(args.dump_dir) if args.source in ("recyclique", "all") else []
    pah = find_paheko_dumps(args.dump_dir) if args.source in ("paheko", "all") else []

    empty = (
        (args.source == "recyclique" and not rec)
        or (args.source == "paheko" and not pah)
        or (args.source == "all" and not rec and not pah)
    )

    if args.json:
        payload: dict = {}
        if args.source in ("recyclique", "all"):
            payload["recyclique"] = {"latest": rec[0] if rec else None, "all": rec}
        if args.source in ("paheko", "all"):
            payload["paheko"] = {"latest": pah[0] if pah else None, "all": pah}
        # rétrocompat --source recyclique --json : même forme qu'avant
        if args.source == "recyclique":
            payload = {"latest": rec[0] if rec else None, "all": rec}
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    else:
        if args.source in ("recyclique", "all"):
            print_recyclique(rec)
            if args.source == "all" and pah:
                print()
        if args.source in ("paheko", "all"):
            print_paheko(pah)

    if empty:
        return 1

    if args.check_date:
        code = 0
        if args.source in ("recyclique", "all") and rec:
            code = max(code, check_freshness(rec[0], args.check_date, "Recyclique"))
        if args.source in ("paheko", "all") and pah:
            code = max(code, check_freshness(pah[0], args.check_date, "Paheko"))
        return code

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
