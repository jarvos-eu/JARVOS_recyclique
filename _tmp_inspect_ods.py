#!/usr/bin/env python3
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

T = "{urn:oasis:names:tc:opendocument:xmlns:table:1.0}"
X = "{urn:oasis:names:tc:opendocument:xmlns:text:1.0}"
path = Path("references/_depot/DeclarationESS-ECOLOGIC-ECOMAISON-EntreesSorties.ods")
with zipfile.ZipFile(path) as z:
    root = ET.fromstring(z.read("content.xml"))

for sname in ["Entrees-Reception", "Sortie-VenteDonsReemploi"]:
    sheet = [t for t in root.findall(f".//{T}table") if t.get(f"{T}name") == sname][0]
    print("===", sname, "===")
    for ri, row in enumerate(sheet.findall(f"{T}table-row"), 1):
        col = 0
        parts = []
        for cell in row.findall(f"{T}table-cell"):
            rep = int(cell.get(f"{T}number-columns-repeated", 1))
            formula = cell.get(f"{T}formula", "")
            val = "".join(p.text or "" for p in cell.findall(f".//{X}p"))
            for _ in range(rep):
                if col == 0 and val:
                    parts.append(f"A={val[:40]}")
                if formula:
                    letter = chr(ord("A") + col) if col < 26 else "?"
                    parts.append(f"{letter}={formula}")
                col += 1
        if parts:
            print(f"R{ri:2}", " | ".join(parts[:8]))
