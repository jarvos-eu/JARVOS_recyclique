#!/usr/bin/env python3
"""Vérifications dump Paheko SQLite (compta euros) — messages en français clair.

Paheko n'est pas une source de volumes éco-organismes.
Saisie au poids / Caisse : alerte si encore présentes (désinstallation prévue).
"""
from __future__ import annotations

import argparse
import json
import re
import sqlite3
import sys
from datetime import datetime
from pathlib import Path

REQUIRED_SAISIE_TABLE = "module_data_saisie_poids"
REQUIRED_POS_TABLES = (
    "plugin_pos_sessions",
    "plugin_pos_tabs",
    "plugin_pos_tabs_items",
    "plugin_pos_categories",
)

DATE_ISO = re.compile(r"(20\d{2}-\d{2}-\d{2})")
DATE_COMPACT = re.compile(r"(20\d{6})")
PAHEKO_HINT = re.compile(r"paheko", re.IGNORECASE)


def _connect_ro(path: Path) -> sqlite3.Connection:
    uri = f"file:{path.as_posix()}?mode=ro"
    con = sqlite3.connect(uri, uri=True, timeout=10)
    con.row_factory = sqlite3.Row
    return con


def parse_dump_date(path: Path) -> str | None:
    name = path.name
    m = DATE_ISO.search(name)
    if m:
        return m.group(1)
    m = DATE_COMPACT.search(name)
    if m:
        raw = m.group(1)
        return f"{raw[:4]}-{raw[4:6]}-{raw[6:8]}"
    return None


def find_paheko_dumps(dump_dir: Path) -> list[dict]:
    """Liste les .sqlite Paheko d'un dossier (nom + signature modules)."""
    if not dump_dir.is_dir():
        return []
    found: list[dict] = []
    seen: set[str] = set()
    for p in sorted(dump_dir.glob("*.sqlite")) + sorted(dump_dir.glob("*.sqlite3")):
        key = str(p.resolve())
        if key in seen:
            continue
        seen.add(key)
        exported = parse_dump_date(p)
        meta = {
            "path": str(p.resolve()),
            "filename": p.name,
            "exported_date": exported or datetime.fromtimestamp(p.stat().st_mtime).date().isoformat(),
            "date_from_filename": bool(exported),
            "size_bytes": p.stat().st_size,
            "name_hint_paheko": bool(PAHEKO_HINT.search(p.name)),
        }
        found.append(meta)
    found.sort(key=lambda d: d["exported_date"], reverse=True)
    return found


def resolve_sqlite_path(explicit: Path | None, dump_dir: Path) -> tuple[Path | None, str]:
    if explicit:
        if not explicit.is_file():
            return None, (
                f"Le fichier SQLite indiqué n'existe pas :\n  {explicit}\n"
                "-> Place une sauvegarde Paheko (association.sqlite) dans references/_depot/\n"
                "   ou passe --sqlite avec le chemin complet."
            )
        return explicit, ""
    dumps = find_paheko_dumps(dump_dir)
    if not dumps:
        return None, (
            f"Aucun fichier .sqlite dans {dump_dir}.\n"
            "-> Exporte une sauvegarde Paheko (Données -> Sauvegarde) et dépose-la dans\n"
            "   references/_depot/ (ex. paheko_association_YYYYMMDD.sqlite)."
        )
    hinted = [d for d in dumps if d["name_hint_paheko"]]
    chosen = hinted[0] if hinted else dumps[0]
    return Path(chosen["path"]), ""


def _table_exists(cur: sqlite3.Cursor, name: str) -> bool:
    row = cur.execute(
        "SELECT 1 FROM sqlite_master WHERE type='table' AND name=?",
        (name,),
    ).fetchone()
    return row is not None


def _module_row(cur: sqlite3.Cursor, name: str) -> dict | None:
    if not _table_exists(cur, "modules"):
        return None
    row = cur.execute(
        "SELECT name, label, enabled, config FROM modules WHERE name=?",
        (name,),
    ).fetchone()
    return dict(row) if row else None


def inspect_saisie_poids(cur: sqlite3.Cursor) -> dict:
    info: dict = {
        "table_exists": _table_exists(cur, REQUIRED_SAISIE_TABLE),
        "module": _module_row(cur, "saisie_poids"),
        "counts_by_type": {},
        "objects": [],
        "ecologic_flags": [],
        "date_min": None,
        "date_max": None,
        "n_entry_exit": 0,
    }
    if not info["table_exists"]:
        return info
    n = cur.execute(f"SELECT COUNT(*) FROM {REQUIRED_SAISIE_TABLE}").fetchone()[0]
    info["n_documents"] = n
    for row in cur.execute(f"SELECT document FROM {REQUIRED_SAISIE_TABLE}"):
        raw = row[0]
        if not raw:
            continue
        try:
            doc = json.loads(raw)
        except json.JSONDecodeError:
            continue
        dtype = doc.get("type")
        info["counts_by_type"][dtype] = info["counts_by_type"].get(dtype, 0) + 1
        if dtype in ("entry", "exit"):
            info["n_entry_exit"] += 1
            d = str(doc.get("date") or "")[:10]
            if d:
                if info["date_min"] is None or d < info["date_min"]:
                    info["date_min"] = d
                if info["date_max"] is None or d > info["date_max"]:
                    info["date_max"] = d
            eco = doc.get("ecologic")
            if eco and eco not in info["ecologic_flags"]:
                info["ecologic_flags"].append(eco)
            obj = doc.get("object")
            if obj and obj not in info["objects"]:
                info["objects"].append(obj)
    info["objects"].sort()
    info["ecologic_flags"].sort()
    return info


def inspect_caisse(cur: sqlite3.Cursor) -> dict:
    present = [t for t in REQUIRED_POS_TABLES if _table_exists(cur, t)]
    missing = [t for t in REQUIRED_POS_TABLES if t not in present]
    info: dict = {
        "tables_present": present,
        "tables_missing": missing,
        "usable": not missing,
        "n_plugins": 0,
        "n_sessions": None,
        "n_sessions_closed": None,
        "closed_min": None,
        "closed_max": None,
        "categories": [],
    }
    if _table_exists(cur, "plugins"):
        info["n_plugins"] = cur.execute("SELECT COUNT(*) FROM plugins").fetchone()[0]
    if not info["usable"]:
        return info
    info["n_sessions"] = cur.execute(
        "SELECT COUNT(*) FROM plugin_pos_sessions"
    ).fetchone()[0]
    info["n_sessions_closed"] = cur.execute(
        "SELECT COUNT(*) FROM plugin_pos_sessions WHERE closed IS NOT NULL"
    ).fetchone()[0]
    row = cur.execute(
        "SELECT MIN(closed), MAX(closed) FROM plugin_pos_sessions WHERE closed IS NOT NULL"
    ).fetchone()
    info["closed_min"] = row[0]
    info["closed_max"] = row[1]
    if _table_exists(cur, "plugin_pos_categories"):
        cats = cur.execute(
            "SELECT name FROM plugin_pos_categories ORDER BY name"
        ).fetchall()
        info["categories"] = [c[0] for c in cats if c[0]]
    return info


def check_paheko_dump(
    sqlite_path: Path | None = None,
    dump_dir: Path = Path("references/_depot"),
) -> tuple[bool, str, dict]:
    """
    Vérifie qu'un dump Paheko est lisible (compta euros).
    Retourne (ok_sqlite_paheko, message, meta).
    ok=True si le fichier est une base Paheko lisible — pas si les tables poids existent.
    """
    path, err = resolve_sqlite_path(sqlite_path, dump_dir)
    if path is None:
        return False, err, {}

    try:
        con = _connect_ro(path)
        cur = con.cursor()
        cur.execute("SELECT 1")
    except sqlite3.Error as e:
        return False, (
            f"Le fichier existe mais n'est pas un SQLite lisible :\n  {path}\n"
            f"   (détail : {e})\n"
            "-> Vérifie que c'est bien une sauvegarde Paheko (association.sqlite), "
            "pas un export CSV/PDF."
        ), {"path": str(path)}

    if not _table_exists(cur, "modules"):
        con.close()
        return False, (
            f"Le SQLite « {path.name} » n'a pas l'air d'être une base Paheko "
            "(table « modules » absente).\n"
            "-> Utilise une sauvegarde Paheko (Données -> Sauvegarde), pas un dump Recyclique."
        ), {"path": str(path)}

    org = None
    if _table_exists(cur, "config"):
        row = cur.execute(
            "SELECT value FROM config WHERE key='org_name'"
        ).fetchone()
        org = row[0] if row else None

    saisie = inspect_saisie_poids(cur)
    caisse = inspect_caisse(cur)
    exported = parse_dump_date(path)
    con.close()

    meta = {
        "path": str(path.resolve()),
        "filename": path.name,
        "org_name": org,
        "exported_date": exported
        or datetime.fromtimestamp(path.stat().st_mtime).date().isoformat(),
        "date_from_filename": bool(exported),
        "size_bytes": path.stat().st_size,
        "saisie_poids": saisie,
        "caisse": caisse,
    }

    lines = [
        f"Dump Paheko trouvé : {path.name}",
        f"  Association : {org or '(nom non renseigné)'}",
        f"  Date (nom de fichier) : {meta['exported_date']}"
        + (" (lue dans le nom)" if exported else " (date de modification du fichier)"),
        f"  Chemin : {path}",
        f"  Taille : {path.stat().st_size:,} octets".replace(",", " "),
        "",
    ]

    mod = saisie.get("module")
    if mod is None:
        lines.append("Module « Saisie au poids » : plus dans la table modules (cible).")
    else:
        etat = "activé" if mod.get("enabled") else "encore listé, désactivé"
        lines.append(
            f"Module « Saisie au poids » : {etat} — à désinstaller "
            "(les volumes sont dans Recyclique)."
        )

    poids_encore_la = bool(
        saisie["table_exists"]
        or (saisie.get("module") and saisie["module"].get("enabled"))
        or caisse["usable"]
    )
    if saisie["table_exists"]:
        n_doc = saisie.get("n_documents", 0)
        n_mv = saisie.get("n_entry_exit", 0)
        lines.append(
            f"ALERTE — table {REQUIRED_SAISIE_TABLE} encore présente "
            f"({n_doc} document(s), {n_mv} mouvement(s)). "
            "À désinstaller : les volumes vivent dans Recyclique."
        )
    else:
        lines.append(
            f"Table {REQUIRED_SAISIE_TABLE} : absente (attendu — pas de volumes dans Paheko)."
        )

    lines.append("")
    if caisse["usable"]:
        lines.append(
            f"ALERTE — plugin Caisse (plugin_pos_*) encore présent "
            f"({caisse['n_sessions']} session(s)). À désinstaller."
        )
    else:
        lines.append("Plugin Caisse (plugin_pos_*) : absent (attendu).")
        if caisse["n_plugins"] == 0:
            lines.append("  Aucun plugin installé sur ce dump.")

    lines.append("")
    lines.append(
        "Périmètre : ce dump sert à la COMPTA en euros (écritures, exercices, bilans)."
    )
    lines.append(
        "  Poids / éco-organismes : Recyclique uniquement "
        "(skill interroger-eco-organismes, sans --source paheko)."
    )
    if poids_encore_la:
        lines.append(
            "  Action : désinstaller Saisie au poids et/ou Caisse dans Paheko, "
            "puis nouvelle sauvegarde."
        )
    else:
        lines.append(
            "OK — dump Paheko lisible pour la compta ; pas d'extension poids/caisse active."
        )

    return True, "\n".join(lines), meta


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Vérifier un dump Paheko SQLite (compta euros, pas les volumes)"
    )
    parser.add_argument("--sqlite", type=Path, default=None, help="Chemin du .sqlite")
    parser.add_argument(
        "--dump-dir",
        type=Path,
        default=Path("references/_depot"),
        help="Dossier si --sqlite omis",
    )
    parser.add_argument("--json", action="store_true", help="Sortie JSON (meta)")
    args = parser.parse_args()

    ok, msg, meta = check_paheko_dump(args.sqlite, args.dump_dir)
    if args.json:
        print(
            json.dumps(
                {"ok": ok, "message": msg, "meta": meta},
                indent=2,
                ensure_ascii=False,
            )
        )
    else:
        print(msg)
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
