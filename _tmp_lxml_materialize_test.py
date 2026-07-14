#!/usr/bin/env python3
import shutil
import zipfile
from pathlib import Path
from lxml import etree

T = "urn:oasis:names:tc:opendocument:xmlns:table:1.0"
X = "urn:oasis:names:tc:opendocument:xmlns:text:1.0"
O = "urn:oasis:names:tc:opendocument:xmlns:office:1.0"
ns = {"table": T, "text": X, "office": O}

src = Path("references/_depot/DeclarationESS-ECOLOGIC-ECOMAISON-EntreesSorties.ods")
out = Path("_tmp_lxml_materialize.ods")
shutil.copy2(src, out)
with zipfile.ZipFile(out) as z:
    xml = z.read("content.xml")

root = etree.fromstring(xml)
sheet = root.xpath('.//table:table[@table:name="Entrees-Reception"]', namespaces=ns)[0]
row = sheet.xpath("table:table-row", namespaces=ns)[12]  # R13


def col_index(letter):
    n = 0
    for ch in letter.upper():
        n = n * 26 + (ord(ch) - ord("A") + 1)
    return n - 1


def materialize_row_lxml(row, min_cols):
    cells = list(row.xpath("table:table-cell", namespaces=ns))
    new_cells = []
    for cell in cells:
        rep = int(cell.get(f"{{{T}}}number-columns-repeated", "1"))
        if rep > 1:
            cell.attrib.pop(f"{{{T}}}number-columns-repeated", None)
            new_cells.append(cell)
            for _ in range(rep - 1):
                new_cells.append(etree.Element(f"{{{T}}}table-cell"))
        else:
            new_cells.append(cell)
    while len(new_cols := new_cells) and len(new_cols) < min_cols:
        new_cells.append(etree.Element(f"{{{T}}}table-cell"))
    for child in list(row):
        row.remove(child)
    for c in new_cells:
        row.append(c)
    return new_cells


def set_cell(cell, text, numeric=True):
    if cell.get(f"{{{T}}}formula"):
        return
    for p in cell.xpath("text:p", namespaces=ns):
        cell.remove(p)
    p = etree.SubElement(cell, f"{{{X}}}p")
    p.text = text
    if numeric:
        cell.set(f"{{{O}}}value-type", "float")
        cell.set(f"{{{O}}}value", str(float(text.replace(",", "."))))
    else:
        cell.set(f"{{{O}}}value-type", "string")
        if f"{{{O}}}value" in cell.attrib:
            del cell.attrib[f"{{{O}}}value"]


cells = materialize_row_lxml(row, col_index("S") + 1)
set_cell(cells[0], "TEST", numeric=False)
set_cell(cells[1], "1,136")

new_xml = etree.tostring(root, xml_declaration=True, encoding="UTF-8").decode()
print("table:formula:", new_xml.count("table:formula"))
print("ns0:", "ns0:" in new_xml)

with zipfile.ZipFile(out, "w", compression=zipfile.ZIP_DEFLATED) as z:
    with zipfile.ZipFile(src) as zin:
        for n in zin.namelist():
            if n != "content.xml":
                z.writestr(n, zin.read(n))
    z.writestr("content.xml", new_xml.encode("utf-8"))
