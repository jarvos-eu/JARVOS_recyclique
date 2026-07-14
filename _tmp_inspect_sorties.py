#!/usr/bin/env python3
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

T = "{urn:oasis:names:tc:opendocument:xmlns:table:1.0}"
X = "{urn:oasis:names:tc:opendocument:xmlns:text:1.0}"
path = Path("references/_depot/DeclarationESS-ECOLOGIC-ECOMAISON-EntreesSorties.ods")
with zipfile.ZipFile(path) as z:
    root = ET.fromstring(z.read("content.xml"))
sheet = [t for t in root.findall(f".//{T}table") if t.get(f"{T}name") == "Sortie-VenteDonsReemploi"][0]
for ri in range(7, 22):
    row = sheet.findall(f"{T}table-row")[ri - 1]
    col = 0
    b_val = t_val = ""
    for cell in row.findall(f"{T}table-cell"):
        rep = int(cell.get(f"{T}number-columns-repeated", 1))
        v = "".join(p.text or "" for p in cell.findall(f".//{X}p"))
        for _ in range(rep):
            if col == 1 and v:
                b_val = v
            if col == 19 and v:
                t_val = v
            col += 1
    print(f"R{ri:2} B={b_val!r} T={t_val!r}")
