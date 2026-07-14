#!/usr/bin/env python3
"""Fill Germaine ODS template with Ecologic T2 2026 agent decisions."""
from __future__ import annotations

import re
import shutil
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "references/_depot/DeclarationESS-ECOLOGIC-ECOMAISON-EntreesSorties.ods"
OUT = (
    ROOT
    / "references/eco-organismes/partenaires/ecologic/declarations-la-clique/2026-T2"
    / "DeclarationESS-ECOLOGIC-ECOMAISON-EntreesSorties-REMPLI.ods"
)

NS = {
    "office": "urn:oasis:names:tc:opendocument:xmlns:office:1.0",
    "table": "urn:oasis:names:tc:opendocument:xmlns:table:1.0",
    "text": "urn:oasis:names:tc:opendocument:xmlns:text:1.0",
}

# French decimal display (comma)
DEC_REE_ECOLOGIC = {
    "B": "0,270",  # PAM
    "C": "0,032",  # ECR
    "D": "0,060",  # GHF
    "E": "0,063",  # GEF
    "F": "0,100",  # ASL-CAT1
    "G": "0,036",  # ASL-CAT2
    "H": "0",      # ABJ-TONA
    "I": "1",      # ABJ-TONM (pièces)
    "J": "0",      # ABJ-AUT (pièces)
}

# From previous T2 manual weigh-ins (Entrees-Reception TOTAL — LIV Ecologic)
LIV_ECOLOGIC = {
    "B": "246,5",
    "C": "25,1",
    "D": "40",
    "E": "0",
    "F": "69",
    "G": "32,7",
    "H": "0",
    "I": "0",
    "J": "0",
}

# Ecomaison recyclage TOTAL 2T 2026 (old ODS row 84)
RECYCLAGE_ECOMAISON = {
    "L": "2,5",
    "M": "13,5",
    "N": "14,7",
    "O": "8,1",
    "P": "971,6",
    "Q": "560",
    "R": "1321,1",
    "S": "132",
    "T": "0",
}


def col_index(letter: str) -> int:
    n = 0
    for ch in letter.upper():
        n = n * 26 + (ord(ch) - ord("A") + 1)
    return n - 1


def col_letter(n: int) -> str:
    s = ""
    while n >= 0:
        s = chr(n % 26 + ord("A")) + s
        n = n // 26 - 1
    return s


def parse_float_fr(val: str) -> float | None:
    if not val:
        return None
    v = val.strip().replace("\u00a0", "").replace(" ", "").replace(",", ".")
    try:
        return float(v)
    except ValueError:
        return None


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


def set_cell_text(cell: ET.Element, text: str, *, numeric: bool = True) -> None:
    """Set visible text; update office:value when numeric."""
    for p in list(cell.findall("text:p", NS)):
        cell.remove(p)
    p = ET.SubElement(cell, f"{{{NS['text']}}}p")
    p.text = text

    if numeric:
        f = parse_float_fr(text)
        if f is not None:
            cell.set(f"{{{NS['office']}}}value-type", "float")
            cell.set(f"{{{NS['office']}}}value", str(f))
        else:
            cell.set(f"{{{NS['office']}}}value-type", "string")
            if f"{{{NS['office']}}}value" in cell.attrib:
                del cell.attrib[f"{{{NS['office']}}}value"]
    else:
        cell.set(f"{{{NS['office']}}}value-type", "string")
        if f"{{{NS['office']}}}value" in cell.attrib:
            del cell.attrib[f"{{{NS['office']}}}value"]

    # Drop formula so OpenOffice keeps static value (formulas would overwrite with 0)
    if f"{{{NS['office']}}}formula" in cell.attrib:
        del cell.attrib[f"{{{NS['office']}}}formula"]


def row_cells_expanded(row: ET.Element) -> list[ET.Element | None]:
    """Expand row to one slot per column (may be None for missing cells)."""
    slots: list[ET.Element | None] = []
    for cell in row.findall("table:table-cell", NS):
        rep = int(cell.get(f"{{{NS['table']}}}number-columns-repeated", 1))
        for _ in range(rep):
            slots.append(cell)
    return slots


def ensure_row_width(row: ET.Element, min_cols: int) -> list[ET.Element | None]:
    slots = row_cells_expanded(row)
    while len(slots) < min_cols:
        new_cell = ET.SubElement(row, f"{{{NS['table']}}}table-cell")
        slots.append(new_cell)
    return slots


def set_row_values(
    row: ET.Element,
    values: dict[str, str],
    *,
    numeric: bool = True,
) -> None:
    if not values:
        return
    max_col = max(col_index(k) for k in values)
    slots = ensure_row_width(row, max_col + 1)
    for letter, text in values.items():
        idx = col_index(letter)
        cell = slots[idx]
        if cell is None:
            continue
        set_cell_text(cell, text, numeric=numeric)


def set_row_label(row: ET.Element, text: str) -> None:
    slots = ensure_row_width(row, 1)
    cell = slots[0]
    if cell is not None:
        set_cell_text(cell, text, numeric=False)


def find_sheet(root: ET.Element, name: str) -> ET.Element:
    for table in root.findall(".//table:table", NS):
        if table.get(f"{{{NS['table']}}}name") == name:
            return table
    raise KeyError(f"Sheet not found: {name}")


def get_row(sheet: ET.Element, row_num_1based: int) -> ET.Element:
    rows = sheet.findall("table:table-row", NS)
    idx = row_num_1based - 1
    if idx < 0 or idx >= len(rows):
        raise IndexError(f"Row {row_num_1based} out of range ({len(rows)} rows)")
    return rows[idx]


def replace_in_row_label(row: ET.Element, old: str, new: str) -> None:
    slots = row_cells_expanded(row)
    if not slots:
        return
    cell = slots[0]
    if cell is None:
        return
    txt = cell_text(cell)
    if old in txt:
        set_cell_text(cell, txt.replace(old, new), numeric=False)


def fill_workbook() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(SRC, OUT)

    with zipfile.ZipFile(OUT, "r") as zin:
        content = zin.read("content.xml")
        other = {name: zin.read(name) for name in zin.namelist() if name != "content.xml"}

    root = ET.fromstring(content)

    # --- Sortie-VenteDonsReemploi ---
    sorties = find_sheet(root, "Sortie-VenteDonsReemploi")
    set_row_label(get_row(sorties, 1), "DECLARATION TRIMESTRIELLE DU 01/04/2026 AU 30/06/2026")
    set_row_label(get_row(sorties, 7), "Du 01/04/2026")
    set_row_label(get_row(sorties, 8), "Au 30/06/2026 inclus")
    # TOTAL sorties réemploi Ecologic (ligne consolidée — les lignes période B-J restent vides)
    total_sorties = get_row(sorties, 21)
    replace_in_row_label(total_sorties, "TOTAL 4T 2025", "TOTAL 2T 2026")
    set_row_values(total_sorties, DEC_REE_ECOLOGIC)

    # --- Entrees-Reception — section 1 LES ENTREES (LIV) ---
    entrees = find_sheet(root, "Entrees-Reception")
    set_row_label(get_row(entrees, 1), "DECLARATION TRIMESTRIELLE DU 01/04/2026 AU 30/06/2026")
    set_row_label(get_row(entrees, 11), "Du 01/04/2026")
    set_row_label(get_row(entrees, 12), "Au 30/06/2026 inclus")
    total_entrees = get_row(entrees, 17)
    replace_in_row_label(total_entrees, "TOTAL 4T 2025", "TOTAL 2T 2026")
    set_row_values(total_entrees, LIV_ECOLOGIC)

    # --- Section 2 RECYCLAGES — Ecomaison TOTAL (reprise ancien T2) ---
    total_recyclage = get_row(entrees, 33)
    replace_in_row_label(total_recyclage, "TOTAL 4T 2025", "TOTAL 2T 2026")
    set_row_values(total_recyclage, RECYCLAGE_ECOMAISON)

    # --- Section 3 AUTRES — libellé seulement ---
    total_autres = get_row(entrees, 49)
    replace_in_row_label(total_autres, "TOTAL 4T 2025", "TOTAL 2T 2026")

    new_content = ET.tostring(root, encoding="utf-8", xml_declaration=True)

    with zipfile.ZipFile(OUT, "w", compression=zipfile.ZIP_DEFLATED) as zout:
        for name, data in other.items():
            zout.writestr(name, data)
        zout.writestr("content.xml", new_content)

    print(f"Written: {OUT}")


def verify() -> None:
    with zipfile.ZipFile(OUT) as z:
        root = ET.fromstring(z.read("content.xml"))

    def show(sheet_name: str, row_num: int, cols: str) -> None:
        sheet = find_sheet(root, sheet_name)
        row = get_row(sheet, row_num)
        slots = row_cells_expanded(row)
        out = {}
        for ch in cols:
            i = col_index(ch)
            if i < len(slots) and slots[i] is not None:
                out[ch] = cell_text(slots[i])
        print(f"{sheet_name} R{row_num}: {out}")

    show("Sortie-VenteDonsReemploi", 13, "BCDEFGHIJ")
    show("Sortie-VenteDonsReemploi", 21, "ABCDEFGHIJ")
    show("Entrees-Reception", 17, "ABCDEFGHIJ")
    show("Entrees-Reception", 33, "LMNOPQRST")


if __name__ == "__main__":
    if not SRC.exists():
        raise SystemExit(f"Source missing: {SRC}")
    fill_workbook()
    verify()
