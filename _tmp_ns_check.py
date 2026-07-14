#!/usr/bin/env python3
import zipfile
from pathlib import Path

paths = {
    "src": Path("references/_depot/DeclarationESS-ECOLOGIC-ECOMAISON-EntreesSorties.ods"),
    "v3": Path(
        "references/eco-organismes/partenaires/ecologic/declarations-la-clique/2026-T2/"
        "DeclarationESS-ECOLOGIC-ECOMAISON-EntreesSorties-REMPLI-v3.ods"
    ),
}
for label, p in paths.items():
    with zipfile.ZipFile(p) as z:
        xml = z.read("content.xml").decode("utf-8")
    print("===", label, "===")
    print("table:formula:", xml.count("table:formula"))
    print(' bare formula="of:', xml.count(' formula="of:'))
    print("office:value-type:", xml.count("office:value-type"))
    print("ns0:value-type:", xml.count("ns0:value-type"))
    print("table:table-cell:", xml.count("table:table-cell"))
    print("ns4:table-cell:", xml.count("ns4:table-cell"))
    print(xml[:200])
    print()
