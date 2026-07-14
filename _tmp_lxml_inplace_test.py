#!/usr/bin/env python3
"""Test in-place lxml edit preserving namespaces."""
import shutil
import zipfile
from pathlib import Path
from lxml import etree

T = "urn:oasis:names:tc:opendocument:xmlns:table:1.0"
X = "urn:oasis:names:tc:opendocument:xmlns:text:1.0"
O = "urn:oasis:names:tc:opendocument:xmlns:office:1.0"

src = Path("references/_depot/DeclarationESS-ECOLOGIC-ECOMAISON-EntreesSorties.ods")
out = Path("_tmp_lxml_inplace.ods")
shutil.copy2(src, out)

with zipfile.ZipFile(out, "r") as z:
    xml = z.read("content.xml")
    other = {n: z.read(n) for n in z.namelist() if n != "content.xml"}

root = etree.fromstring(xml)
ns = {"table": T, "text": X, "office": O}
sheet = root.xpath('.//table:table[@table:name="Entrees-Reception"]', namespaces=ns)[0]
rows = sheet.xpath("table:table-row", namespaces=ns)
row13 = rows[12]

# set A1 label only - find first text:p in first cell
cell0 = row13.xpath("table:table-cell", namespaces=ns)[0]
p = cell0.xpath("text:p", namespaces=ns)
if p:
    p[0].text = "TEST LABEL"
else:
    etree.SubElement(cell0, f"{{{X}}}p").text = "TEST LABEL"

new_xml = etree.tostring(root, xml_declaration=True, encoding="UTF-8")
text = new_xml.decode("utf-8")
print("table:formula count:", text.count("table:formula"))
print("formula bare count:", text.count(' formula="of:'))
print("office:document-content" in text, "ns0:document-content" in text)
print(text[text.find("TEST LABEL") - 80 : text.find("TEST LABEL") + 40])

with zipfile.ZipFile(out, "w", compression=zipfile.ZIP_DEFLATED) as z:
    for n, d in other.items():
        z.writestr(n, d)
    z.writestr("content.xml", new_xml)
