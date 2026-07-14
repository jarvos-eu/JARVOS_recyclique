#!/usr/bin/env python3
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

T = "{urn:oasis:names:tc:opendocument:xmlns:table:1.0}"
O = "{urn:oasis:names:tc:opendocument:xmlns:office:1.0}"
X = "{urn:oasis:names:tc:opendocument:xmlns:text:1.0}"


def dump_formula_row(path: Path, sheet_name: str, row_num: int) -> None:
    print(f"\n=== {path.name} / {sheet_name} R{row_num} ===")
    with zipfile.ZipFile(path) as z:
        raw = z.read("content.xml")
    root = ET.fromstring(raw)
    sheet = [t for t in root.findall(f".//{T}table") if t.get(f"{T}name") == sheet_name][0]
    row = sheet.findall(f"{T}table-row")[row_num - 1]
    col = 0
    for cell in row.findall(f"{T}table-cell"):
        rep = int(cell.get(f"{T}number-columns-repeated", 1))
        formula = cell.get(f"{T}formula", "")
        vtype = cell.get(f"{O}value-type", "")
        value = cell.get(f"{O}value", "")
        txt = "".join(p.text or "" for p in cell.findall(f".//{X}p"))
        for _ in range(rep):
            if formula or (col == 1 and (txt or vtype)):
                print(
                    f"  col{col}: formula={formula!r} "
                    f"value-type={vtype!r} value={value!r} text={txt!r}"
                )
            col += 1


for p in [
    Path("references/_depot/DeclarationESS-ECOLOGIC-ECOMAISON-EntreesSorties.ods"),
    Path(
        "references/eco-organismes/partenaires/ecologic/declarations-la-clique/2026-T2/"
        "DeclarationESS-ECOLOGIC-ECOMAISON-EntreesSorties-REMPLI-v3.ods"
    ),
]:
    dump_formula_row(p, "Entrees-Reception", 33)
    dump_formula_row(p, "Sortie-VenteDonsReemploi", 21)

# show raw bytes snippet around first formula in each file
print("\n=== RAW XML prefix sample ===")
for p in [
    Path("references/_depot/DeclarationESS-ECOLOGIC-ECOMAISON-EntreesSorties.ods"),
    Path(
        "references/eco-organismes/partenaires/ecologic/declarations-la-clique/2026-T2/"
        "DeclarationESS-ECOLOGIC-ECOMAISON-EntreesSorties-REMPLI-v3.ods"
    ),
]:
    with zipfile.ZipFile(p) as z:
        xml = z.read("content.xml").decode("utf-8")
    idx = xml.find("table:formula")
    if idx < 0:
        idx = xml.find("formula=")
    print(p.name, "...", xml[idx : idx + 120].replace("\n", " "))
