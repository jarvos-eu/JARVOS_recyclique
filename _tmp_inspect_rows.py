#!/usr/bin/env python3
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

T = "{urn:oasis:names:tc:opendocument:xmlns:table:1.0}"
X = "{urn:oasis:names:tc:opendocument:xmlns:text:1.0}"
path = Path("references/_depot/DeclarationESS-ECOLOGIC-ECOMAISON-EntreesSorties.ods")
with zipfile.ZipFile(path) as z:
    root = ET.fromstring(z.read("content.xml"))
sheet = [t for t in root.findall(f".//{T}table") if t.get(f"{T}name") == "Entrees-Reception"][0]
for ri in range(1, 55):
    row = sheet.findall(f"{T}table-row")[ri - 1]
    val_a = ""
    for cell in row.findall(f"{T}table-cell"):
        rep = int(cell.get(f"{T}number-columns-repeated", 1))
        v = "".join(p.text or "" for p in cell.findall(f".//{X}p"))
        if v and not val_a:
            val_a = v[:50]
            break
        if rep > 1 and not v:
            break
    print(f"R{ri:2} {val_a!r}")
