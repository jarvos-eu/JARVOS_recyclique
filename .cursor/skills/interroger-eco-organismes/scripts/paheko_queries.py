#!/usr/bin/env python3
"""OBSOLETE — ne plus appeler pour les décla.

Décision 2026-08-18 : Paheko = compta euros. Poids / éco-organismes = Recyclique.
Saisie au poids et Caisse Paheko vont être désinstallées.
interroger_eco_org.py refuse --source paheko. Ce module n'est plus sur le chemin canon.
"""
from __future__ import annotations

import json
import math
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path

# Objets par défaut du module (atelier vélos) — HITL hors ces libellés.
# Les noms Recyclique (PAM, ECR…) sont aussi acceptés si configurés tels quels.
PAHEKO_ECOLOGIC_OBJECTS: dict[str, list[str]] = {
    "ASL-CAT1": [
        "Vélo enfant",
        "Vélo adulte",
        "Vélo",
        "Trottinette, skateboard, roller",
        "1- Cycles et engins de déplacement non motorisés",
    ],
    "ASL-CAT2": [
        "Accessoire / pièce vélo",
        "Pièce ou accessoire vélo",
        "2- Autres ASL",
    ],
}

PAHEKO_HITL_CODES = {"ASL-CAT1", "ASL-CAT2"}

# grammes (stockage module) -> kg / t
GRAMS_PER_KG = 1000
GRAMS_PER_TONNE = 1_000_000


def _connect_ro(path: Path) -> sqlite3.Connection:
    return sqlite3.connect(f"file:{path.as_posix()}?mode=ro", uri=True, timeout=10)


def period_bounds_sqlite(date_debut: str, date_fin: str) -> tuple[str, str]:
    start = datetime.strptime(date_debut, "%Y-%m-%d")
    end_exclusive = datetime.strptime(date_fin, "%Y-%m-%d") + timedelta(days=1)
    return start.strftime("%Y-%m-%d"), end_exclusive.strftime("%Y-%m-%d")


def _in_period(doc_date: str | None, t_start: str, t_end_excl: str) -> bool:
    if not doc_date:
        return False
    d = str(doc_date).replace("T", " ")[:10]
    return t_start <= d < t_end_excl


def load_movements(con: sqlite3.Connection) -> list[dict]:
    cur = con.cursor()
    rows = cur.execute(
        "SELECT id, key, document FROM module_data_saisie_poids"
    ).fetchall()
    out: list[dict] = []
    for rid, key, raw in rows:
        if not raw:
            continue
        try:
            doc = json.loads(raw)
        except json.JSONDecodeError:
            continue
        if doc.get("type") not in ("entry", "exit"):
            continue
        doc["_id"] = rid
        doc["_key"] = key
        out.append(doc)
    return out


def table_exists(con: sqlite3.Connection, name: str) -> bool:
    row = con.execute(
        "SELECT 1 FROM sqlite_master WHERE type='table' AND name=?",
        (name,),
    ).fetchone()
    return row is not None


def resolve_objects(
    row: dict,
    recyclique_ecologic: dict[str, list[str]],
    recyclique_ecomaison: dict[str, list[str]],
) -> list[str]:
    if row.get("categorie_recyclique", "").strip():
        return [row["categorie_recyclique"].strip()]
    code = row.get("code", "").strip().upper()
    partenaire = row.get("partenaire", "ecologic").strip().lower()
    names: list[str] = []
    if code in PAHEKO_ECOLOGIC_OBJECTS:
        names.extend(PAHEKO_ECOLOGIC_OBJECTS[code])
    if partenaire == "ecomaison" and code in recyclique_ecomaison:
        names.extend(recyclique_ecomaison[code])
    elif partenaire == "ecologic" and code in recyclique_ecologic:
        names.extend(recyclique_ecologic[code])
    else:
        if code in recyclique_ecologic:
            names.extend(recyclique_ecologic[code])
        if code in recyclique_ecomaison:
            names.extend(recyclique_ecomaison[code])
    # dédoublonner en conservant l'ordre
    seen: set[str] = set()
    uniq: list[str] = []
    for n in names:
        if n not in seen:
            seen.add(n)
            uniq.append(n)
    return uniq


def format_number(value: float, decimals: int) -> str:
    s = f"{value:.{decimals}f}"
    return s


def grams_to_result(sum_grams: float, unite: str, flux: str) -> str:
    unite = unite.lower()
    if unite in ("pieces", "piece", "pc", "u"):
        return str(int(sum_grams))  # caller passes qty instead
    if flux == "RECYCLAGE" or flux == "SORTIES_DEPOT_KG":
        if unite in ("t", "tonne", "tonnes"):
            return format_number(sum_grams / GRAMS_PER_TONNE, 3)
        return format_number(round(sum_grams / GRAMS_PER_KG, 1), 1)
    if flux == "LIV":
        kg_floor = math.floor(sum_grams / GRAMS_PER_KG)
        return format_number(round(kg_floor / GRAMS_PER_KG, 3), 3)
    # DEC_REE t
    return format_number(round(sum_grams / GRAMS_PER_TONNE, 3), 3)


def aggregate_saisie(
    movements: list[dict],
    row: dict,
    objects: list[str],
) -> tuple[str | None, str]:
    flux = row.get("flux", "").strip().upper()
    unite = row.get("unite", "t").strip().lower()
    t_start, t_end = period_bounds_sqlite(row["date_debut"], row["date_fin"])
    destination = (row.get("destination") or "").strip()
    obj_set = set(objects)

    matched: list[dict] = []
    for doc in movements:
        if not _in_period(doc.get("date"), t_start, t_end):
            continue
        obj = doc.get("object") or ""
        if obj_set and obj not in obj_set:
            continue
        dtype = doc.get("type")
        eco = doc.get("ecologic")
        cat = doc.get("category") or ""

        if flux == "DEC_REE":
            if dtype == "exit" and eco == "DEC_REE":
                matched.append(doc)
        elif flux == "LIV":
            if dtype == "entry" and eco == "LIV":
                matched.append(doc)
        elif flux == "PRE":
            if dtype == "entry" and eco == "PRE":
                matched.append(doc)
        elif flux == "RECYCLAGE":
            if dtype != "exit":
                continue
            if destination:
                if cat == destination:
                    matched.append(doc)
            elif eco is None:
                matched.append(doc)
        elif flux == "SORTIES_DEPOT_KG":
            if dtype == "exit":
                matched.append(doc)
        elif flux == "COUNT":
            if dtype == "exit" and eco == "DEC_REE":
                matched.append(doc)
        else:
            return None, f"flux Paheko non supporté : {flux}"

    if flux == "COUNT":
        return str(len(matched)), f"{len(matched)} ligne(s) saisie_poids"
    if unite in ("pieces", "piece", "pc", "u"):
        qty = sum(int(d.get("qty") or 0) for d in matched)
        return str(qty), f"{len(matched)} ligne(s) saisie_poids"

    total_g = sum(int(d.get("total_weight") or 0) for d in matched)
    n_pos = sum(1 for d in matched if d.get("pos_session_id") is not None)
    comment = f"{len(matched)} ligne(s) saisie_poids"
    if n_pos:
        comment += f" dont {n_pos} import caisse (pos_session_id)"
    return grams_to_result(total_g, unite, flux), comment


def aggregate_caisse(
    con: sqlite3.Connection,
    row: dict,
    objects: list[str],
) -> tuple[str | None, str]:
    flux = row.get("flux", "").strip().upper()
    if flux not in ("DEC_REE", "COUNT"):
        return None, (
            f"flux « {flux} » indisponible depuis la caisse Paheko "
            "(uniquement DEC_REE / COUNT). Utiliser Saisie au poids pour LIV / PRE / RECYCLAGE."
        )
    if not objects:
        return None, "aucune catégorie caisse à matcher"
    t_start, t_end = period_bounds_sqlite(row["date_debut"], row["date_fin"])
    placeholders = ",".join("?" * len(objects))
    sql = f"""
SELECT
  COALESCE(SUM(ti.qty * COALESCE(ti.weight, 0)), 0),
  COALESCE(SUM(ti.qty), 0),
  COUNT(*)
FROM plugin_pos_tabs_items ti
JOIN plugin_pos_tabs t ON t.id = ti.tab
JOIN plugin_pos_sessions s ON s.id = t.session
LEFT JOIN plugin_pos_products p ON p.id = ti.product
LEFT JOIN plugin_pos_categories c ON c.id = p.category
WHERE s.closed IS NOT NULL
  AND s.closed >= ?
  AND s.closed < ?
  AND COALESCE(ti.weight, 0) > 0
  AND (
    c.name IN ({placeholders})
    OR ti.category_name IN ({placeholders})
  )
"""
    params = [t_start, t_end, *objects, *objects]
    grams, qty, n = con.execute(sql, params).fetchone()
    unite = row.get("unite", "t").strip().lower()
    if flux == "COUNT":
        return str(int(n or 0)), f"{int(n or 0)} ligne(s) caisse (sessions clôturées)"
    if unite in ("pieces", "piece", "pc", "u"):
        return str(int(qty or 0)), f"{int(n or 0)} ligne(s) caisse (sessions clôturées)"
    return (
        grams_to_result(float(grams or 0), unite, "DEC_REE"),
        f"{int(n or 0)} ligne(s) caisse (sessions clôturées)",
    )


def choose_backend(
    requested: str,
    has_saisie: bool,
    has_caisse: bool,
) -> tuple[str | None, str]:
    if requested == "saisie_poids":
        if has_saisie:
            return "saisie_poids", ""
        return None, (
            "Backend demandé : Saisie au poids, mais la table "
            "module_data_saisie_poids est absente de ce dump."
        )
    if requested == "caisse":
        if has_caisse:
            return "caisse", ""
        return None, (
            "Backend demandé : caisse, mais les tables plugin_pos_* sont absentes."
        )
    # auto
    if has_saisie:
        return "saisie_poids", ""
    if has_caisse:
        return "caisse", (
            "Saisie au poids absente : repli sur la caisse (DEC_REE seulement). "
            "Ne pas additionner les deux sources."
        )
    return None, "ni Saisie au poids ni Caisse sur ce dump"


def run_paheko_row(
    sqlite_path: Path,
    row: dict,
    objects: list[str],
    backend: str,
    movements_cache: list[dict] | None = None,
) -> tuple[bool, str, str, str]:
    """
    Retourne (ok, resultat, commentaire, sql_audit).
    """
    flux = row.get("flux", "").strip().upper()
    con = _connect_ro(sqlite_path)
    try:
        has_saisie = table_exists(con, "module_data_saisie_poids")
        has_caisse = table_exists(con, "plugin_pos_tabs_items")
        chosen, note = choose_backend(backend, has_saisie, has_caisse)
        if not chosen:
            return False, "", note, ""

        if chosen == "saisie_poids":
            mov = movements_cache if movements_cache is not None else load_movements(con)
            value, comment = aggregate_saisie(mov, row, objects)
            sql = (
                f"-- {row.get('id')} source=paheko backend=saisie_poids "
                f"flux={flux} objects={objects!r}\n"
                "-- parse JSON module_data_saisie_poids (Python, pas SQL naïf)\n"
            )
        else:
            value, comment = aggregate_caisse(con, row, objects)
            sql = (
                f"-- {row.get('id')} source=paheko backend=caisse "
                f"flux={flux} categories={objects!r}\n"
            )
        if value is None:
            return False, "", comment, sql
        if note:
            comment = f"{note} {comment}".strip()
        return True, value, comment, sql
    finally:
        con.close()
