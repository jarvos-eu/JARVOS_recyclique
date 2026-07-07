#!/usr/bin/env python3
"""Extract Ecologic ODS structure for mode d'emploi T2 2026."""
from __future__ import annotations

import json
import re
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

NS = {
    "office": "urn:oasis:names:tc:opendocument:xmlns:office:1.0",
    "table": "urn:oasis:names:tc:opendocument:xmlns:table:1.0",
    "text": "urn:oasis:names:tc:opendocument:xmlns:text:1.0",
}

ROOT = Path(__file__).resolve().parent
T2_ODS = ROOT / "references/eco-organismes/partenaires/ecologic/declarations-la-clique/2026-T2/DeclarationESS-ECOLOGIC-2T2026.ods"
T4_ENTREES = ROOT / "references/eco-organismes/partenaires/ecologic/declarations-la-clique/2025-T4/DeclarationEcologic-EntreesDepot-4T2025-1.ods"
T4_SORTIES = ROOT / "references/eco-organismes/partenaires/ecologic/declarations-la-clique/2025-T4/DeclarationEcologic-Sorties-4T2025-1.ods"
OUT_JSON = ROOT / "log/cursor-agent/ecologic-t2-2026-ods-extract.json"

# Official column mapping T4 -> pro forma T1
COL_MAP = {
    "PAM": ("PAM", "t"),
    "ECRANS": ("ECR", "t"),
    "GHF": ("GHF", "t"),
    "GF": ("GEF", "t"),
    "ASL-CAT1 o-o": ("ASL-CAT1", "t"),
    "ASL-CAT2": ("ASL-CAT2", "t"),
    "ABJ-TON Auto": ("ABJ-TONA", "t"),
    "ABJ-TON Marchant": ("ABJ-TONM", "t"),
    "ABJ-AUTres": ("ABJ-AUT", "pieces"),
}


def col_letter(n: int) -> str:
    s = ""
    while n >= 0:
        s = chr(n % 26 + ord("A")) + s
        n = n // 26 - 1
    return s


def cell_text(cell: ET.Element) -> str:
    parts: list[str] = []
    for p in cell.findall(".//text:p", NS):
        if p.text:
            parts.append(p.text)
        for child in p:
            if child.text:
                parts.append(child.text)
            if child.tail:
                parts.append(child.tail)
    return "".join(parts).strip()


def parse_ods(path: Path) -> dict:
    with zipfile.ZipFile(path, "r") as z:
        content = z.read("content.xml")
    root = ET.fromstring(content)
    sheets = []
    for table in root.findall(".//table:table", NS):
        name = table.get(f"{{{NS['table']}}}name", "")
        rows_data = []
        for ri, row in enumerate(table.findall("table:table-row", NS)):
            cells = []
            col_idx = 0
            for cell in row.findall("table:table-cell", NS):
                rep = int(cell.get(f"{{{NS['table']}}}number-columns-repeated", 1))
                val = cell_text(cell)
                for _ in range(rep):
                    cells.append(
                        {
                            "col": col_idx,
                            "col_letter": col_letter(col_idx),
                            "value": val,
                        }
                    )
                    col_idx += 1
            while cells and cells[-1]["value"] == "":
                cells.pop()
            if any(c["value"] for c in cells):
                rows_data.append({"row": ri + 1, "cells": cells})
        sheets.append({"name": name, "rows": rows_data, "row_count": len(rows_data)})
    return {"file": str(path), "filename": path.name, "sheets": sheets}


def find_header_row(sheet: dict) -> dict | None:
    for row in sheet["rows"]:
        vals = [c["value"] for c in row["cells"]]
        joined = " ".join(vals).upper()
        if "PAM" in joined and ("ECR" in joined or "ECRANS" in joined):
            return row
    return None


def build_column_index(header_row: dict) -> dict[str, dict]:
    idx: dict[str, dict] = {}
    for c in header_row["cells"]:
        label = c["value"].strip()
        if label:
            idx[label] = {"col": c["col"], "col_letter": c["col_letter"]}
    return idx


def is_numeric(val: str) -> bool:
    if not val:
        return False
    v = val.replace(",", ".").strip()
    return bool(re.match(r"^-?\d+(\.\d+)?$", v))


def extract_fillable_cells(data: dict) -> list[dict]:
    """Identify data cells in matrix sheets (entrées/sorties style)."""
    cells: list[dict] = []
    for sheet in data["sheets"]:
        header = find_header_row(sheet)
        if not header:
            continue
        col_idx = build_column_index(header)
        header_row_num = header["row"]
        sheet_role = "inconnu"
        sn = sheet["name"].lower()
        if "entree" in sn or "entr" in sn or "depot" in sn or "dépôt" in sn:
            sheet_role = "entrees_depot"
        elif "sortie" in sn:
            sheet_role = "sorties"
        else:
            # infer from filename
            fn = data["filename"].lower()
            if "entree" in fn or "depot" in fn:
                sheet_role = "entrees_depot"
            elif "sortie" in fn:
                sheet_role = "sorties"

        for row in sheet["rows"]:
            if row["row"] <= header_row_num:
                continue
            row_label = ""
            if row["cells"]:
                row_label = row["cells"][0]["value"].strip()
            if not row_label:
                continue
            row_upper = row_label.upper()
            if row_upper.startswith("TOTAL"):
                for c in row["cells"][1:]:
                    hdr = None
                    for h, meta in col_idx.items():
                        if meta["col"] == c["col"]:
                            hdr = h
                            break
                    if not hdr or hdr not in COL_MAP:
                        continue
                    code, unit = COL_MAP[hdr]
                    cells.append(
                        {
                            "sheet": sheet["name"],
                            "sheet_role": sheet_role,
                            "row": row["row"],
                            "col": c["col_letter"],
                            "libelle_officiel": hdr,
                            "code_proforma": code,
                            "ligne_periode": row_label,
                            "flux": "sortie_total" if sheet_role == "sorties" else "entree_total",
                            "operation": None,
                            "unite": unit,
                            "valeur": c["value"] if c["value"] else None,
                            "etat": "rempli" if c["value"] else "vide",
                            "type_ligne": "TOTAL",
                        }
                    )
                continue

            # Regular period rows
            for c in row["cells"][1:]:
                hdr = None
                for h, meta in col_idx.items():
                    if meta["col"] == c["col"]:
                        hdr = h
                        break
                if not hdr or hdr not in COL_MAP:
                    continue
                code, unit = COL_MAP[hdr]
                cells.append(
                    {
                        "sheet": sheet["name"],
                        "sheet_role": sheet_role,
                        "row": row["row"],
                        "col": c["col_letter"],
                        "libelle_officiel": hdr,
                        "code_proforma": code,
                        "ligne_periode": row_label,
                        "flux": "entree_depot" if sheet_role == "entrees_depot" else "sortie",
                        "operation": "LIV" if sheet_role == "entrees_depot" else "DEC_REE",
                        "unite": unit,
                        "valeur": c["value"] if c["value"] else None,
                        "etat": "rempli" if c["value"] else "vide",
                        "type_ligne": "periode",
                    }
                )
    return cells


def sheet_inventory(data: dict) -> list[dict]:
    inv = []
    for sh in data["sheets"]:
        header = find_header_row(sh)
        headers = []
        if header:
            headers = [c["value"] for c in header["cells"] if c["value"]]
        inv.append(
            {
                "name": sh["name"],
                "non_empty_rows": sh["row_count"],
                "header_row": header["row"] if header else None,
                "columns": headers,
            }
        )
    return inv


def compare_structures(t2: dict, t4: dict) -> dict:
    t2_inv = sheet_inventory(t2)
    t4_inv = sheet_inventory(t4)
    return {
        "t2_sheets": [s["name"] for s in t2["sheets"]],
        "t4_sheets": [s["name"] for s in t4["sheets"]],
        "t2_columns": t2_inv[0]["columns"] if t2_inv else [],
        "t4_columns": t4_inv[0]["columns"] if t4_inv else [],
        "columns_identical": (
            t2_inv[0]["columns"] == t4_inv[0]["columns"]
            if t2_inv and t4_inv
            else False
        ),
        "sheet_count_t2": len(t2["sheets"]),
        "sheet_count_t4": len(t4["sheets"]),
    }


def main() -> None:
    results = {"generated": "2026-07-07", "files": {}}
    t2 = parse_ods(T2_ODS)
    results["files"]["t2_2026"] = {
        "path": str(T2_ODS),
        "inventory": sheet_inventory(t2),
        "fillable_cells": extract_fillable_cells(t2),
        "all_rows_preview": {
            sh["name"]: sh["rows"] for sh in t2["sheets"]
        },
    }

    if T4_ENTREES.exists():
        t4e = parse_ods(T4_ENTREES)
        results["files"]["t4_2025_entrees"] = {
            "path": str(T4_ENTREES),
            "inventory": sheet_inventory(t4e),
            "fillable_cells_count": len(extract_fillable_cells(t4e)),
        }
        results["comparison_entrees"] = compare_structures(t2, t4e)

    if T4_SORTIES.exists():
        t4s = parse_ods(T4_SORTIES)
        results["files"]["t4_2025_sorties"] = {
            "path": str(T4_SORTIES),
            "inventory": sheet_inventory(t4s),
            "fillable_cells_count": len(extract_fillable_cells(t4s)),
        }

    # Stats
    cells = results["files"]["t2_2026"]["fillable_cells"]
    filled = [c for c in cells if c["etat"] == "rempli"]
    empty = [c for c in cells if c["etat"] == "vide"]
    results["stats"] = {
        "total_cells": len(cells),
        "filled": len(filled),
        "empty": len(empty),
        "filled_values": {f"{c['sheet']}!{c['col']}{c['row']}": c["valeur"] for c in filled},
    }

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")

    print(json.dumps(results["stats"], ensure_ascii=False, indent=2))
    print("\n--- INVENTORY T2 ---")
    for inv in results["files"]["t2_2026"]["inventory"]:
        print(f"Sheet: {inv['name']} | rows={inv['non_empty_rows']} | header_row={inv['header_row']}")
        print(f"  Columns: {inv['columns']}")
    print("\n--- ALL ROWS T2 ---")
    for sh in t2["sheets"]:
        print(f"\n## {sh['name']}")
        for row in sh["rows"]:
            vals = " | ".join(f"{c['col_letter']}:{c['value']}" for c in row["cells"] if c["value"])
            print(f"  R{row['row']}: {vals}")


if __name__ == "__main__":
    main()
