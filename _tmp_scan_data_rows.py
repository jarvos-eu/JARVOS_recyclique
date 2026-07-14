#!/usr/bin/env python3
import zipfile
from pathlib import Path
from lxml import etree

T = "urn:oasis:names:tc:opendocument:xmlns:table:1.0"
X = "urn:oasis:names:tc:opendocument:xmlns:text:1.0"
ns = {"table": T, "text": X}


def is_number(s):
    try:
        float(s.replace(",", ".").strip())
        return True
    except ValueError:
        return False


def scan_data_rows(path):
    with zipfile.ZipFile(path) as z:
        root = etree.fromstring(z.read("content.xml"))
    sheet = root.xpath('.//table:table[@table:name="Entrees-Reception"]', namespaces=ns)[0]
    rows = sheet.xpath("table:table-row", namespaces=ns)
    print(f"\n{path.name} ({len(rows)} lignes XML)")
    for ri, row in enumerate(rows, 1):
        col = 0
        label = ""
        nums = []
        for cell in row.xpath("table:table-cell", namespaces=ns):
            rep = int(cell.get(f"{{{T}}}number-columns-repeated", 1))
            f = cell.get(f"{{{T}}}formula", "")
            val = "".join(p.text or "" for p in cell.xpath("text:p", namespaces=ns))
            for _ in range(rep):
                if col == 0 and val:
                    label = val
                if val and not f and 1 <= col <= 18 and is_number(val):
                    nums.append((col, val))
                col += 1
        if nums:
            print(f"  R{ri:2} [{label[:35]:35}] {nums[:6]}")


base = Path("references/eco-organismes/partenaires/ecologic/declarations-la-clique/2026-T2")
scan_data_rows(Path("references/_depot/DeclarationESS-ECOLOGIC-ECOMAISON-EntreesSorties.ods"))
scan_data_rows(base / "DeclarationESS-ECOLOGIC-ECOMAISON-EntreesSorties-REMPLI-v4.ods")
scan_data_rows(base / "DeclarationESS-ECOLOGIC-2T2026.ods")
