#!/usr/bin/env python3
import zipfile
from pathlib import Path
from lxml import etree

T = "urn:oasis:names:tc:opendocument:xmlns:table:1.0"
X = "urn:oasis:names:tc:opendocument:xmlns:text:1.0"
ns = {"table": T, "text": X}


def scan(path, title):
    with zipfile.ZipFile(path) as z:
        root = etree.fromstring(z.read("content.xml"))
    sheet = root.xpath('.//table:table[@table:name="Entrees-Reception"]', namespaces=ns)[0]
    rows = sheet.xpath("table:table-row", namespaces=ns)
    print(f"\n=== {title} ===")
    for ri in range(31, 79):
        row = rows[ri - 1]
        col = 0
        label = ""
        nums = []
        for cell in row.xpath("table:table-cell", namespaces=ns):
            rep = int(cell.get(f"{{{T}}}number-columns-repeated", 1))
            f = cell.get(f"{{{T}}}formula", "")
            val = "".join(p.text or "" for p in cell.xpath("text:p", namespaces=ns))
            for _ in range(rep):
                if col == 0 and val:
                    label = val[:42]
                if val and not f and col >= 1 and col <= 18:
                    if val.replace(",", ".").replace(" ", "").replace("Q:", "").strip() not in ("0", "0,0", ""):
                        ch = chr(65 + col) if col < 26 else "?"
                        nums.append(f"{ch}={val[:8]}")
                col += 1
        if label or nums:
            print(f"R{ri:2}  A={label!r:42}  {', '.join(nums[:6])}")


for p, t in [
    ("references/_depot/DeclarationESS-ECOLOGIC-ECOMAISON-EntreesSorties.ods", "Template vierge Germaine"),
    (
        "references/eco-organismes/partenaires/ecologic/declarations-la-clique/2026-T2/"
        "DeclarationESS-ECOLOGIC-ECOMAISON-EntreesSorties-REMPLI-v4.ods",
        "REMPLI v4 (agent)",
    ),
    (
        "references/eco-organismes/partenaires/ecologic/declarations-la-clique/2026-T2/"
        "DeclarationESS-ECOLOGIC-2T2026.ods",
        "Ancien T2 Germaine (2026)",
    ),
]:
    scan(Path(p), t)
