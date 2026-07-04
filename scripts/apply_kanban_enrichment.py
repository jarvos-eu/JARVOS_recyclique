#!/usr/bin/env python3
"""Applique enrichment-pass JSON sur les fiches kanban v2 puis sync."""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

_SCRIPTS = Path(r"C:\Users\Strophe\.cursor\skills\idees-kanban\scripts")
sys.path.insert(0, str(_SCRIPTS))

from kanban_lib import (  # noqa: E402
    dump_frontmatter,
    publish_signal,
    scan_cards,
    split_frontmatter,
    sync_kanban,
    write_index,
    VALID_MATURITY,
    VALID_PRIORITY,
)

REPO = Path(r"d:\users\Strophe\Documents\1-IA\La Clique Qui Recycle\JARVOS_recyclique")
KANBAN_DIR = REPO / "docs" / "ideas" / "kanban"
ENRICHMENT = KANBAN_DIR / "enrichment-pass-2026-07-04.json"
PROJECT_ID = "jarvos-recyclique"


def apply() -> int:
    data = json.loads(ENRICHMENT.read_text(encoding="utf-8"))
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    applied = 0
    for idea_id, patch in sorted(data.items()):
        path = KANBAN_DIR / f"{idea_id}.md"
        if not path.is_file():
            print(f"SKIP missing {idea_id}", file=sys.stderr)
            continue
        text = path.read_text(encoding="utf-8")
        meta, body = split_frontmatter(text)
        maturity = patch.get("maturity", meta.get("maturity", "raw"))
        if maturity not in VALID_MATURITY:
            raise ValueError(f"{idea_id}: maturity invalide {maturity!r}")
        meta["maturity"] = maturity
        meta["domain"] = list(patch.get("domain") or [])
        meta["tags"] = list(patch.get("tags") or [])
        meta["routes_suggested"] = list(patch.get("routes_suggested") or [])
        priority = patch.get("priority")
        if priority in VALID_PRIORITY:
            meta["priority"] = priority
        elif "priority" in meta:
            del meta["priority"]
        meta["updated_at"] = now
        path.write_text(dump_frontmatter(meta, body), encoding="utf-8")
        applied += 1
        print(f"OK {idea_id} maturity={maturity} tags={len(meta['tags'])} routes={len(meta['routes_suggested'])}")
    cards, index_path, sig_path = sync_kanban(REPO, PROJECT_ID)
    print(f"SYNC {len(cards)} fiches index={index_path} signal={sig_path}")
    return applied


if __name__ == "__main__":
    n = apply()
    if n != 24:
        raise SystemExit(f"expected 24 applied, got {n}")
    print("done")
