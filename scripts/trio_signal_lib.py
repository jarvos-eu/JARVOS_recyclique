"""Signaux trio brownfield — stdlib only, sans ledger Ombre."""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path

SCHEMA_VERSION = "0.1"
HEADLINE_MAX_LEN = 120
REPRISE_DEFAULT = "REPRISE.md"

MEMORY_CORE_KEYS = frozenset(
    {
        "schema_version",
        "project_id",
        "updated_at",
        "status",
        "headline",
        "next_action",
        "risk_level",
        "ledger_drift",
        "thread_count",
        "source_ref",
    }
)
PROGRAM_CORE_KEYS = frozenset(
    {
        "schema_version",
        "project_id",
        "updated_at",
        "status",
        "headline",
        "next_action",
        "risk_level",
        "source_ref",
    }
)
VALID_STATUS = frozenset({"active", "blocked", "idle", "closed"})
VALID_RISK = frozenset({"low", "medium", "high"})

SCRIPT_FILES = (
    "trio_signal_lib.py",
    "publish_memory_signal.py",
    "publish_program_signal.py",
)


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _mtime_iso(path: Path) -> str:
    if path.is_file():
        return datetime.fromtimestamp(
            path.stat().st_mtime, tz=timezone.utc
        ).strftime("%Y-%m-%dT%H:%M:%SZ")
    return utc_now_iso()


def _strip_markdown(text: str) -> str:
    text = re.sub(r"\*\*(.+?)\*\*", r"\1", text)
    text = re.sub(r"`([^`]+)`", r"\1", text)
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    return " ".join(text.split())


def _truncate(text: str, max_len: int = HEADLINE_MAX_LEN) -> str:
    text = text.strip()
    if len(text) <= max_len:
        return text
    return text[: max_len - 1].rstrip() + "…"


def _section_by_number(content: str, section_num: int) -> str:
    pattern = re.compile(
        rf"^##\s+{section_num}\.\s+.+?\n\n(.*?)(?=\n---\n|\n##\s+\d+\.|\Z)",
        re.MULTILINE | re.DOTALL,
    )
    match = pattern.search(content)
    return match.group(1).strip() if match else ""


def _section_by_title(content: str, *title_patterns: str) -> str:
    for pat in title_patterns:
        pattern = re.compile(
            rf"^##\s+(?:\d+\.\s+)?{pat}[^\n]*\n\n(.*?)(?=\n---\n|\n##\s|\Z)",
            re.MULTILINE | re.DOTALL | re.IGNORECASE,
        )
        match = pattern.search(content)
        if match:
            return match.group(1).strip()
    return ""


def _first_paragraph(text: str) -> str:
    for block in re.split(r"\n\s*\n", text.strip()):
        block = block.strip()
        if not block or block.startswith("|") or block.startswith("```"):
            continue
        return block
    return ""


def _p0_from_continue_table(content: str) -> str:
    section = _section_by_title(content, r"Où continuer")
    if not section:
        return ""
    for line in section.splitlines():
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if len(cells) < 2:
            continue
        if cells[0].upper() == "P0":
            return _strip_markdown(cells[1])
    return ""


def _next_action_from_numbered_section(content: str) -> str:
    for num in (5, 7, 6):
        body = _section_by_number(content, num)
        if not body:
            continue
        header_match = re.search(
            rf"^##\s+{num}\.\s+(.+)$", content, re.MULTILINE
        )
        if header_match and re.search(
            r"prochaine\s+action", header_match.group(1), re.IGNORECASE
        ):
            return _strip_markdown(_first_paragraph(body))
    return ""


def parse_reprise_heuristic(content: str) -> tuple[str, str]:
    """Extrait headline et next_action depuis REPRISE.md (formats variés)."""
    headline = ""
    next_action = ""

    s1 = _section_by_number(content, 1)
    if s1:
        headline = _truncate(_strip_markdown(_first_paragraph(s1)))

    if not headline:
        for title in (r"En une phrase", r"Où on en est"):
            body = _section_by_title(content, title)
            if body:
                headline = _truncate(_strip_markdown(_first_paragraph(body)))
                if headline:
                    break

    next_action = _next_action_from_numbered_section(content)
    if not next_action:
        body = _section_by_title(content, r"Prochaine action")
        if body:
            next_action = _strip_markdown(_first_paragraph(body))
    if not next_action:
        next_action = _p0_from_continue_table(content)

    return headline, next_action


def _prochaine_etape_from_table(content: str) -> str:
    for line in content.splitlines():
        if "**Prochaine étape**" in line and "|" in line:
            cells = [c.strip() for c in line.strip("|").split("|")]
            if len(cells) >= 2:
                return _strip_markdown(cells[1])
    return ""


def parse_program_heuristic(content: str) -> tuple[str, str]:
    """Extrait headline et next_action depuis amont programme."""
    headline = ""
    next_action = ""

    m = re.search(
        r"\*\*Prochaine action unique\*\*\s*:\s*(.+)",
        content,
        re.IGNORECASE,
    )
    if m:
        next_action = _strip_markdown(m.group(1))

    s1 = _section_by_number(content, 1)
    if s1:
        headline = _truncate(_strip_markdown(_first_paragraph(s1)))

    if not headline:
        for title in (
            r"En une phrase",
            r"Vision courte",
            r"Où on en est",
            r"État programme",
        ):
            body = _section_by_title(content, title)
            if body:
                headline = _truncate(_strip_markdown(_first_paragraph(body)))
                if headline:
                    break

    if not next_action:
        next_action = _prochaine_etape_from_table(content)
    if not next_action:
        body = _section_by_title(
            content, r"Prochaine action programme", r"Prochaine action"
        )
        if body:
            next_action = _strip_markdown(_first_paragraph(body))
    if not next_action:
        next_action = _p0_from_continue_table(content)

    if not headline:
        body = _section_by_title(content, r"État actuel")
        if body:
            headline = _truncate(_strip_markdown(_first_paragraph(body)))

    return headline, next_action


def find_program_upstream(root: Path) -> Path | None:
    """Cherche l'amont programme : docs/programme/*_REPRISE.md puis fallback."""
    programme_dir = root / "docs" / "programme"
    if programme_dir.is_dir():
        candidates = sorted(
            programme_dir.glob("*_REPRISE.md"),
            key=lambda p: p.stat().st_mtime,
            reverse=True,
        )
        if candidates:
            return candidates[0]

    fallback = root / "references" / "ou-on-en-est.md"
    if fallback.is_file():
        return fallback
    return None


def _status_for(*, ledger_drift: bool, thread_count: int) -> str:
    if ledger_drift:
        return "blocked"
    if thread_count == 0:
        return "idle"
    return "active"


def _risk_for(*, ledger_drift: bool, thread_count: int) -> str:
    if ledger_drift:
        return "high"
    if thread_count == 0:
        return "medium"
    return "low"


def _merge_extra_keys(existing: dict | None, payload: dict, core: frozenset[str]) -> dict:
    if not existing:
        return payload
    merged = dict(payload)
    for key, value in existing.items():
        if key not in core:
            merged[key] = value
    return merged


def _load_existing_signal(path: Path) -> dict | None:
    if not path.is_file():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None
    return data if isinstance(data, dict) else None


def _rel_path(root: Path, path: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def build_memory_payload(
    root: Path,
    reprise_path: Path,
    content: str,
    *,
    project_id: str,
    ledger_drift: bool = False,
    thread_count: int = 0,
    updated_at: str | None = None,
) -> dict:
    headline, next_action = parse_reprise_heuristic(content)
    if not headline:
        headline = "Reprise sans headline détectable — enrichir REPRISE.md."
    if not next_action:
        next_action = "Enrichir REPRISE.md (section Prochaine action ou P0)."

    rel = _rel_path(root, reprise_path)
    now = updated_at or utc_now_iso()
    return {
        "schema_version": SCHEMA_VERSION,
        "project_id": project_id,
        "updated_at": now,
        "status": _status_for(ledger_drift=ledger_drift, thread_count=thread_count),
        "headline": headline,
        "next_action": next_action,
        "risk_level": _risk_for(ledger_drift=ledger_drift, thread_count=thread_count),
        "ledger_drift": ledger_drift,
        "thread_count": thread_count,
        "source_ref": {
            "path": rel,
            "updated_at": _mtime_iso(reprise_path),
        },
    }


def build_program_payload(
    root: Path,
    upstream_path: Path,
    content: str,
    *,
    project_id: str,
    updated_at: str | None = None,
) -> dict:
    headline, next_action = parse_program_heuristic(content)
    if not headline:
        headline = "Programme sans headline détectable — enrichir amont programme."
    if not next_action:
        next_action = "Enrichir amont programme (prochaine action unique ou P0)."

    rel = _rel_path(root, upstream_path)
    now = updated_at or utc_now_iso()
    return {
        "schema_version": SCHEMA_VERSION,
        "project_id": project_id,
        "updated_at": now,
        "status": "active",
        "headline": headline,
        "next_action": next_action,
        "risk_level": "medium",
        "source_ref": {
            "path": rel,
            "updated_at": _mtime_iso(upstream_path),
        },
    }


def write_signal(
    root: Path,
    filename: str,
    payload: dict,
    *,
    dry_run: bool = False,
) -> Path:
    out_dir = root.resolve() / "_bmad" / "signals"
    out_path = out_dir / filename
    text = json.dumps(payload, indent=2, ensure_ascii=False) + "\n"
    if dry_run:
        return out_path
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path.write_text(text, encoding="utf-8")
    return out_path


def publish_memory_signal(
    repo_root: Path,
    *,
    reprise_path: Path | None = None,
    project_id: str | None = None,
    dry_run: bool = False,
) -> tuple[dict, Path | None, str | None]:
    root = repo_root.resolve()
    pid = project_id or root.name
    reprise = reprise_path or (root / REPRISE_DEFAULT)
    if not reprise.is_file():
        return {}, None, f"REPRISE absent: {reprise}"

    content = reprise.read_text(encoding="utf-8")
    payload = build_memory_payload(
        root, reprise, content, project_id=pid, ledger_drift=False, thread_count=0
    )
    existing = _load_existing_signal(root / "_bmad" / "signals" / "project-memory-signal.json")
    if existing and isinstance(existing.get("project_id"), str) and existing["project_id"]:
        payload["project_id"] = existing["project_id"]
    payload = _merge_extra_keys(existing, payload, MEMORY_CORE_KEYS)

    out_path = write_signal(
        root, "project-memory-signal.json", payload, dry_run=dry_run
    )
    return payload, out_path, None


def publish_program_signal(
    repo_root: Path,
    *,
    upstream_path: Path | None = None,
    project_id: str | None = None,
    dry_run: bool = False,
) -> tuple[dict, Path | None, str | None]:
    root = repo_root.resolve()
    pid = project_id or root.name
    upstream = upstream_path or find_program_upstream(root)
    if upstream is None or not upstream.is_file():
        return {}, None, "Amont programme introuvable (docs/programme/*_REPRISE.md ou references/ou-on-en-est.md)"

    content = upstream.read_text(encoding="utf-8")
    payload = build_program_payload(root, upstream, content, project_id=pid)
    existing = _load_existing_signal(root / "_bmad" / "signals" / "project-program-signal.json")
    if existing and isinstance(existing.get("project_id"), str) and existing["project_id"]:
        payload["project_id"] = existing["project_id"]
    payload = _merge_extra_keys(existing, payload, PROGRAM_CORE_KEYS)

    out_path = write_signal(
        root, "project-program-signal.json", payload, dry_run=dry_run
    )
    return payload, out_path, None
