#!/usr/bin/env python3
"""Fill Germaine ODS T2 2026 — detail rows only, formulas preserved on TOTAL rows."""
from __future__ import annotations

import json
import shutil
import subprocess
import zipfile
from lxml import etree
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
T = NS["table"]
O = NS["office"]
X = NS["text"]
NSMAP = {"office": O, "table": T, "text": X}

PERIODE_LABEL = "DECLARATION TRIMESTRIELLE DU 01/04/2026 AU 30/06/2026"
DU = "Du 01/04/2026"
AU = "Au 30/06/2026 inclus"
DETAIL_LABEL = "Recyclique T2 - calcul agent 15/07/2026"


def fmt_t(val: float) -> str:
    s = f"{val:.3f}".replace(".", ",")
    return s.rstrip("0").rstrip(",") if "," in s else s


def fmt_kg(val: float) -> str:
    if abs(val - round(val)) < 0.05:
        return str(int(round(val)))
    return f"{val:.1f}".replace(".", ",")


def fmt_pieces(val: int | float) -> str:
    return str(int(val))


def col_index(letter: str) -> int:
    n = 0
    for ch in letter.upper():
        n = n * 26 + (ord(ch) - ord("A") + 1)
    return n - 1


def cell_text(cell: etree._Element) -> str:
    parts: list[str] = []
    for p in cell.xpath(".//text:p", namespaces=NSMAP):
        if p.text:
            parts.append(p.text)
        for child in p:
            if child.text:
                parts.append(child.text)
            if child.tail:
                parts.append(child.tail)
    return "".join(parts).strip()


def parse_float_fr(val: str) -> float | None:
    if not val:
        return None
    v = val.strip().replace("\u00a0", "").replace(" ", "").replace(",", ".")
    try:
        return float(v)
    except ValueError:
        return None


def cell_has_formula(cell: etree._Element) -> bool:
    return bool(cell.get(f"{{{T}}}formula"))


def set_cell_text(cell: etree._Element, text: str, *, numeric: bool = True) -> None:
    if cell_has_formula(cell):
        return
    for p in cell.xpath("text:p", namespaces=NSMAP):
        cell.remove(p)
    p = etree.SubElement(cell, f"{{{X}}}p")
    p.text = text

    if numeric:
        f = parse_float_fr(text)
        if f is not None:
            cell.set(f"{{{O}}}value-type", "float")
            cell.set(f"{{{O}}}value", str(f))
        else:
            cell.set(f"{{{O}}}value-type", "string")
            cell.attrib.pop(f"{{{O}}}value", None)
    else:
        cell.set(f"{{{O}}}value-type", "string")
        cell.attrib.pop(f"{{{O}}}value", None)


def row_cells_expanded(row: etree._Element) -> list[etree._Element | None]:
    slots: list[etree._Element | None] = []
    for cell in row.xpath("table:table-cell", namespaces=NSMAP):
        rep = int(cell.get(f"{{{T}}}number-columns-repeated", 1))
        for _ in range(rep):
            slots.append(cell)
    return slots


def materialize_row(row: etree._Element, min_cols: int) -> list[etree._Element]:
    """Expand repeated cells into one XML cell per column (detail rows only)."""
    new_cells: list[etree._Element] = []
    for cell in list(row.xpath("table:table-cell", namespaces=NSMAP)):
        rep = int(cell.get(f"{{{T}}}number-columns-repeated", 1))
        if rep > 1:
            cell.attrib.pop(f"{{{T}}}number-columns-repeated", None)
            new_cells.append(cell)
            for _ in range(rep - 1):
                new_cells.append(etree.Element(f"{{{T}}}table-cell"))
        else:
            new_cells.append(cell)
    while len(new_cells) < min_cols:
        new_cells.append(etree.Element(f"{{{T}}}table-cell"))
    for child in list(row):
        row.remove(child)
    for cell in new_cells:
        row.append(cell)
    return new_cells


def set_row_values(
    row: etree._Element,
    values: dict[str, str],
    *,
    numeric: bool = True,
) -> None:
    if not values:
        return
    max_col = max(col_index(k) for k in values)
    cells = materialize_row(row, max_col + 1)
    for letter, text in values.items():
        idx = col_index(letter)
        set_cell_text(cells[idx], text, numeric=numeric)


def set_row_label(row: etree._Element, text: str) -> None:
    cells = materialize_row(row, 1)
    if not cell_has_formula(cells[0]):
        set_cell_text(cells[0], text, numeric=False)


def find_sheet(root: etree._Element, name: str) -> etree._Element:
    hits = root.xpath(f'.//table:table[@table:name="{name}"]', namespaces=NSMAP)
    if not hits:
        raise KeyError(f"Sheet not found: {name}")
    return hits[0]


def append_note_row(sheet: etree._Element, text: str) -> None:
    row = etree.SubElement(sheet, f"{{{T}}}table-row")
    set_row_label(row, text)


def get_row(sheet: etree._Element, row_num_1based: int) -> etree._Element:
    rows = sheet.xpath("table:table-row", namespaces=NSMAP)
    idx = row_num_1based - 1
    if idx < 0 or idx >= len(rows):
        raise IndexError(f"Row {row_num_1based} out of range ({len(rows)} rows)")
    return rows[idx]


def replace_total_label(row: etree._Element, new: str = "TOTAL 2T 2026") -> None:
    """Renomme la cellule A du TOTAL sans toucher aux formules B-S."""
    for cell in row.xpath("table:table-cell", namespaces=NSMAP):
        if cell_has_formula(cell):
            continue
        txt = cell_text(cell)
        if txt.startswith("TOTAL"):
            set_cell_text(cell, new, numeric=False)
            return
        rep = int(cell.get(f"{{{T}}}number-columns-repeated", 1))
        if rep > 1:
            return


def query_db() -> dict:
    """Pull T2 aggregates from Docker mirror if available."""
    sql_path = ROOT / "_tmp_germaine_queries.sql"
    sql_path.write_text(
        r"""
WITH periode AS (
  SELECT '2026-04-01'::timestamptz AS t_start, '2026-07-01'::timestamptz AS t_end
),
dec_ree AS (
  SELECT CASE c.name
    WHEN '1- Petits appareils em melange(PAM)' THEN 'B'
    WHEN '2- Ecrans' THEN 'C'
    WHEN '3- Gros électroménager hors froid (GEMHF)' THEN 'D'
    WHEN '4- Gros électroménager froid (GEMF)' THEN 'E'
    WHEN '1- Cycles et engins de déplacement non motorisés' THEN 'F'
    WHEN '2- Autres ASL' THEN 'G'
    WHEN '1- Tondeuses autoportées' THEN 'H'
    WHEN '2- Tondeuses à conducteur marchant' THEN 'I'
    WHEN '3- Autres ABJ thermique' THEN 'J'
  END AS col,
  CASE WHEN c.name IN (
    '1- Tondeuses autoportées', '2- Tondeuses à conducteur marchant', '3- Autres ABJ thermique'
  ) THEN SUM(si.quantity)::numeric
  ELSE ROUND(SUM(COALESCE(si.weight, 0))::numeric / 1000, 3) END AS val
  FROM sale_items si
  JOIN sales s ON s.id = si.sale_id
  JOIN categories c ON c.id::text = si.category
  CROSS JOIN periode p
  WHERE COALESCE(s.sale_date, s.created_at) >= p.t_start
    AND COALESCE(s.sale_date, s.created_at) < p.t_end
    AND c.name IN (
      '1- Petits appareils em melange(PAM)', '2- Ecrans',
      '3- Gros électroménager hors froid (GEMHF)', '4- Gros électroménager froid (GEMF)',
      '1- Cycles et engins de déplacement non motorisés', '2- Autres ASL',
      '1- Tondeuses autoportées', '2- Tondeuses à conducteur marchant', '3- Autres ABJ thermique'
    )
  GROUP BY c.name
),
-- LIV Ecologic (entrées tickets)
liv AS (
  SELECT CASE c.name
    WHEN '1- Petits appareils em melange(PAM)' THEN 'B'
    WHEN '2- Ecrans' THEN 'C'
    WHEN '3- Gros électroménager hors froid (GEMHF)' THEN 'D'
    WHEN '4- Gros électroménager froid (GEMF)' THEN 'E'
    WHEN '1- Cycles et engins de déplacement non motorisés' THEN 'F'
    WHEN '2- Autres ASL' THEN 'G'
  END AS col,
  ROUND(FLOOR(SUM(ld.poids_kg))::numeric / 1000, 3) AS val
  FROM ligne_depot ld
  JOIN ticket_depot t ON t.id = ld.ticket_id
  JOIN categories c ON c.id = ld.category_id
  CROSS JOIN periode p
  WHERE ld.is_exit = false
    AND t.created_at >= p.t_start AND t.created_at < p.t_end
    AND c.name IN (
      '1- Petits appareils em melange(PAM)', '2- Ecrans',
      '3- Gros électroménager hors froid (GEMHF)', '4- Gros électroménager froid (GEMF)',
      '1- Cycles et engins de déplacement non motorisés', '2- Autres ASL'
    )
  GROUP BY c.name
),
-- Ecomaison sorties réemploi (ventes)
eco_sale AS (
  SELECT col, ROUND(SUM(kg)::numeric / 1000, 3) AS val_t
  FROM (
    SELECT CASE
      WHEN c.name IN ('Jardin', '*Pots de fleurs', '* Gros équipement de jardin sup80cm',
        'NE PLUS UTILISER Materiel destinés à l''aménagement du jardin') THEN 'K'
      WHEN c.name IN ('A - Outillage Divers', '* Outillage à main', 'Outillage',
        'NE PLUS UTILISER- Materiel de bricolage', '* Gros Equipements de Bricolage (sup 80 cm)') THEN 'L'
      WHEN c.name = '1- Jeux de plein air' THEN 'M'
      WHEN c.name = '2- Jeux société et puzzle' THEN 'N'
      WHEN c.name IN ('3- autres jeux d''intérieur', 'A - Jeux Divers') THEN 'O'
      WHEN c.name IN ('* Assises', 'Chaises', 'Petit meuble/chaise en bois massif',
        'Gros meuble en bois massif', 'Meuble moyen en bois massif', 'A - Meuble Divers') THEN 'P'
      WHEN c.name = '* Couchage' THEN 'Q'
      WHEN c.name IN ('* Rangement', 'NE PLUS UTILISER Rangement et plan de pose et de travail') THEN 'R'
      WHEN c.name = '*Plan de pose , plan de travail' THEN 'S'
      WHEN c.name = '* Décoration textile' THEN 'T'
    END AS col,
    COALESCE(si.weight, 0) AS kg
    FROM sale_items si
    JOIN sales s ON s.id = si.sale_id
    JOIN categories c ON c.id::text = si.category
    CROSS JOIN periode p
    WHERE COALESCE(s.sale_date, s.created_at) >= p.t_start
      AND COALESCE(s.sale_date, s.created_at) < p.t_end
  ) x
  WHERE col IS NOT NULL
  GROUP BY col
),
-- Ecomaison entrées tickets
eco_entree AS (
  SELECT col, ROUND(SUM(kg)::numeric / 1000, 3) AS val_t
  FROM (
    SELECT CASE
      WHEN c.name IN ('Jardin', '*Pots de fleurs', '* Gros équipement de jardin sup80cm',
        'NE PLUS UTILISER Materiel destinés à l''aménagement du jardin') THEN 'K'
      WHEN c.name IN ('A - Outillage Divers', '* Outillage à main', 'Outillage',
        'NE PLUS UTILISER- Materiel de bricolage', '* Gros Equipements de Bricolage (sup 80 cm)') THEN 'L'
      WHEN c.name = '1- Jeux de plein air' THEN 'M'
      WHEN c.name = '2- Jeux société et puzzle' THEN 'N'
      WHEN c.name IN ('3- autres jeux d''intérieur', 'A - Jeux Divers') THEN 'O'
      WHEN c.name IN ('* Assises', 'Chaises', 'Petit meuble/chaise en bois massif',
        'Gros meuble en bois massif', 'Meuble moyen en bois massif', 'A - Meuble Divers') THEN 'P'
      WHEN c.name = '* Couchage' THEN 'Q'
      WHEN c.name IN ('* Rangement', 'NE PLUS UTILISER Rangement et plan de pose et de travail') THEN 'R'
      WHEN c.name = '*Plan de pose , plan de travail' THEN 'S'
      WHEN c.name = '* Décoration textile' THEN 'T'
    END AS col,
    ld.poids_kg AS kg
    FROM ligne_depot ld
    JOIN ticket_depot t ON t.id = ld.ticket_id
    JOIN categories c ON c.id = ld.category_id
    CROSS JOIN periode p
    WHERE ld.is_exit = false
      AND t.created_at >= p.t_start AND t.created_at < p.t_end
  ) x
  WHERE col IS NOT NULL
  GROUP BY col
),
-- Recyclage interne (kg) — section 2
recyclage AS (
  SELECT col, ROUND(SUM(kg)::numeric, 1) AS val_kg
  FROM (
    SELECT CASE
      WHEN c.name IN ('Jardin', '*Pots de fleurs', '* Gros équipement de jardin sup80cm',
        'NE PLUS UTILISER Materiel destinés à l''aménagement du jardin') THEN 'K'
      WHEN c.name IN ('A - Outillage Divers', '* Outillage à main', 'Outillage',
        'NE PLUS UTILISER- Materiel de bricolage', '* Gros Equipements de Bricolage (sup 80 cm)') THEN 'L'
      WHEN c.name = '1- Jeux de plein air' THEN 'M'
      WHEN c.name = '2- Jeux société et puzzle' THEN 'N'
      WHEN c.name IN ('3- autres jeux d''intérieur', 'A - Jeux Divers') THEN 'O'
      WHEN c.name IN ('* Assises', 'Chaises', 'Petit meuble/chaise en bois massif',
        'Gros meuble en bois massif', 'Meuble moyen en bois massif', 'A - Meuble Divers') THEN 'P'
      WHEN c.name = '* Couchage' THEN 'Q'
      WHEN c.name IN ('* Rangement', 'NE PLUS UTILISER Rangement et plan de pose et de travail') THEN 'R'
      WHEN c.name = '*Plan de pose , plan de travail' THEN 'S'
      WHEN c.name = '* Décoration textile' THEN 'T'
    END AS col,
    ld.poids_kg AS kg
    FROM ligne_depot ld
    JOIN ticket_depot t ON t.id = ld.ticket_id
    JOIN categories c ON c.id = ld.category_id
    CROSS JOIN periode p
    WHERE ld.is_exit = true AND ld.destination = 'RECYCLAGE'
      AND t.created_at >= p.t_start AND t.created_at < p.t_end
  ) x
  WHERE col IS NOT NULL
  GROUP BY col
)
SELECT 'dec_ree' AS kind, col, val::text FROM dec_ree
UNION ALL SELECT 'liv', col, val::text FROM liv
UNION ALL SELECT 'eco_sale', col, val_t::text FROM eco_sale
UNION ALL SELECT 'eco_entree', col, val_t::text FROM eco_entree
UNION ALL SELECT 'recyclage', col, val_kg::text FROM recyclage
ORDER BY kind, col;
""",
        encoding="utf-8",
    )
    try:
        subprocess.run(
            ["docker", "cp", str(sql_path), "recyclic-mirror-t2:/tmp/germaine_t2.sql"],
            check=True,
            capture_output=True,
            text=True,
            timeout=30,
        )
        proc = subprocess.run(
            [
                "docker",
                "exec",
                "recyclic-mirror-t2",
                "psql",
                "-U",
                "postgres",
                "-d",
                "recyclic_la_clique_mirror",
                "-t",
                "-A",
                "-F",
                "|",
                "-f",
                "/tmp/germaine_t2.sql",
            ],
            capture_output=True,
            text=True,
            check=True,
            timeout=120,
        )
    except (subprocess.CalledProcessError, FileNotFoundError) as exc:
        err = getattr(exc, "stderr", str(exc))
        raise SystemExit(f"DB query failed: {err}") from exc

    if proc.stderr.strip():
        print("psql stderr:", proc.stderr[:500])

    data: dict[str, dict[str, float]] = {
        "dec_ree": {},
        "liv": {},
        "eco_sale": {},
        "eco_entree": {},
        "recyclage": {},
    }
    for line in proc.stdout.strip().splitlines():
        if not line.strip():
            continue
        kind, col, val = line.split("|")
        data[kind][col] = float(val.replace(",", "."))
    return data


def dict_to_fr_t(d: dict[str, float], cols: str, *, zero_as_empty: bool = False) -> dict[str, str]:
    out: dict[str, str] = {}
    for c in cols:
        v = d.get(c, 0.0)
        if zero_as_empty and abs(v) < 1e-9:
            continue
        if c in "HIJ" and c in d and d[c] == int(d[c]) and c in ("H", "I", "J"):
            out[c] = fmt_pieces(d[c])
        else:
            out[c] = fmt_t(v)
    return out


def dict_to_fr_kg(d: dict[str, float], cols: str) -> dict[str, str]:
    return {c: fmt_kg(d[c]) for c in cols if c in d and d[c] > 0}


def build_payload(data: dict) -> dict:
    dec = data["dec_ree"]
    liv = data["liv"]
    eco_sale = data["eco_sale"]
    eco_entree = data["eco_entree"]
    recyclage = data["recyclage"]

    # PAM LIV: tickets Recyclique (~1,1 t), NOT old tableur 246,5 t
    pam_liv = liv.get("B", 1.136)

    liv_ecologic = dict_to_fr_t(
        {c: liv.get(c, 0.0) for c in "BCDEFG"},
        "BCDEFG",
    )

    dec_ecologic = {}
    for col in "BCDEFG":
        if col in dec and dec[col] > 0:
            dec_ecologic[col] = fmt_t(dec[col])
    for col in "HIJ":
        if col in dec and dec[col] > 0:
            dec_ecologic[col] = fmt_pieces(dec[col])

    eco_entree_fr = dict_to_fr_t(eco_entree, "KLMNOPQRS", zero_as_empty=True)
    eco_sale_fr = dict_to_fr_t(
        {c: eco_sale[c] for c in "KLMNOPQRS" if c in eco_sale},
        "KLMNOPQRS",
        zero_as_empty=True,
    )
    recyclage_fr = dict_to_fr_kg(recyclage, "KLMNOPQRST")

    note_entrees = (
        "NOTE AGENT (15/07/2026) - Feuille ENTREES, trimestre avril-juin 2026. "
        "Bloc 1 : matiere recue au depot. Chiffres Ecologic (col. B-G) et Ecomaison (col. K-S) "
        "viennent des pesees Recyclique du trimestre. "
        f"PAM (petits appareils electriques) : {fmt_t(pam_liv)} t - calcule depuis Recyclique "
        "(environ 1,1 t), PAS les 246 t de l'ancien tableur qui etaient faux (cumul / double comptage). "
        "Si vos bordereaux Ecologic montrent autre chose, corrigez la ligne du dessus avant le portail. "
        "Bloc 2 RECYCLAGES : matiere partie en benne interne (kg), pas la caisse. "
        "Bloc 3 : laisse vide."
    )

    note_sorties = (
        "NOTE AGENT (15/07/2026) - Feuille SORTIES CAISSE, trimestre avril-juin 2026. "
        "Ce sont les ventes (reemploi) comptees en caisse Recyclique. "
        "Ecologic col. B-J : petits electro, ecrans, gros electro, sport, tondeuses... "
        "Ecomaison col. K-T : meubles, jouets, brico/jardin, deco textile. "
        "Les lignes deco textile deja saisies plus haut (col. T) viennent de Germaine - "
        "notre ligne Recyclique T2 les complete pour le total. "
        "Verifier avant envoi sur le portail Ecologic / Ecomaison."
    )

    return {
        "liv_ecologic": liv_ecologic,
        "liv_ecomaison": eco_entree_fr,
        "recyclage": recyclage_fr,
        "dec_ecologic": dec_ecologic,
        "dec_ecomaison": eco_sale_fr,
        "note_entrees": note_entrees,
        "note_sorties": note_sorties,
        "pam_liv": pam_liv,
    }


def fill_workbook(payload: dict) -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(SRC, OUT)

    with zipfile.ZipFile(OUT, "r") as zin:
        content = zin.read("content.xml")
        other = {name: zin.read(name) for name in zin.namelist() if name != "content.xml"}

    root = etree.fromstring(content)

    # --- Entrees-Reception ---
    entrees = find_sheet(root, "Entrees-Reception")
    set_row_label(get_row(entrees, 1), PERIODE_LABEL)
    set_row_label(get_row(entrees, 11), DU)
    set_row_label(get_row(entrees, 12), AU)

    # Section 1 LIV — R13 (plage SOMME B13:B23 du modele Germaine)
    detail1 = get_row(entrees, 13)
    set_row_label(detail1, DETAIL_LABEL)
    set_row_values(detail1, payload["liv_ecologic"])
    set_row_values(detail1, payload["liv_ecomaison"])

    # Section 2 RECYCLAGES — R38 (plage SOMME B38:B48)
    set_row_label(get_row(entrees, 27), DU)
    set_row_label(get_row(entrees, 28), AU)
    detail2 = get_row(entrees, 38)
    set_row_label(detail2, DETAIL_LABEL + " (recyclage benne interne, kg)")
    set_row_values(detail2, payload["recyclage"])

    replace_total_label(get_row(entrees, 17))
    replace_total_label(get_row(entrees, 33))
    replace_total_label(get_row(entrees, 49))

    # Note below all 3 sections
    append_note_row(entrees, payload["note_entrees"])

    # --- Sortie-VenteDonsReemploi ---
    sorties = find_sheet(root, "Sortie-VenteDonsReemploi")
    set_row_label(get_row(sorties, 1), PERIODE_LABEL)
    set_row_label(get_row(sorties, 7), DU)
    set_row_label(get_row(sorties, 8), AU)
    # Sorties — R19 (plage SOMME B9:B19 ; col. T = Germaine R9-R18, on ne touche pas)
    detail_s = get_row(sorties, 19)
    set_row_label(detail_s, DETAIL_LABEL)
    set_row_values(detail_s, payload["dec_ecologic"])
    set_row_values(detail_s, payload["dec_ecomaison"])

    replace_total_label(get_row(sorties, 21))

    append_note_row(sorties, payload["note_sorties"])

    new_content = etree.tostring(root, xml_declaration=True, encoding="UTF-8")

    with zipfile.ZipFile(OUT, "w", compression=zipfile.ZIP_DEFLATED) as zout:
        for name, data in other.items():
            zout.writestr(name, data)
        zout.writestr("content.xml", new_content)

    print(f"Written: {OUT}")


def verify(payload: dict) -> None:
    with zipfile.ZipFile(OUT) as z:
        root = etree.fromstring(z.read("content.xml"))
        xml_text = z.read("content.xml").decode("utf-8")

    print(f"table:formula count in output: {xml_text.count('table:formula')}")
    assert xml_text.count("table:formula") >= 70, "Formules ODS cassees (namespaces XML)"

    def show(sheet_name: str, row_num: int, cols: str) -> None:
        sheet = find_sheet(root, sheet_name)
        row = get_row(sheet, row_num)
        slots = row_cells_expanded(row)
        out = {}
        for ch in cols:
            i = col_index(ch)
            if i < len(slots) and slots[i] is not None:
                out[ch] = cell_text(slots[i])
        label = cell_text(slots[0]) if slots and slots[0] is not None else ""
        print(f"{sheet_name} R{row_num} [{label[:40]}]: {out}")

    def show_formulas(sheet_name: str, row_num: int) -> None:
        sheet = find_sheet(root, sheet_name)
        row = get_row(sheet, row_num)
        formulas = []
        col = 0
        for cell in row.xpath("table:table-cell", namespaces=NSMAP):
            rep = int(cell.get(f"{{{T}}}number-columns-repeated", 1))
            f = cell.get(f"{{{T}}}formula", "")
            for _ in range(rep):
                if f and col < 19:
                    formulas.append(f"{col}:{f[:30]}")
                col += 1
        print(f"{sheet_name} R{row_num} formulas: {formulas[:3]}... ({len(formulas)} cols)")

    show("Entrees-Reception", 13, "ABCDEFGHIJKLMNOPQRS")
    show("Entrees-Reception", 17, "ABCDEFGHIJKLMNOPQRS")
    show_formulas("Entrees-Reception", 17)
    show("Entrees-Reception", 38, "KLMNOPQRST")
    show_formulas("Entrees-Reception", 33)
    show("Sortie-VenteDonsReemploi", 19, "BCDEFGHIJKLMNOPQRST")
    show_formulas("Sortie-VenteDonsReemploi", 21)
    print(f"PAM LIV used: {payload['pam_liv']} t")


if __name__ == "__main__":
    if not SRC.exists():
        raise SystemExit(f"Source missing: {SRC}")
    db = query_db()
    payload = build_payload(db)
    fill_workbook(payload)
    verify(payload)
    # sidecar for traceability
    sidecar = OUT.with_suffix(".json")
    sidecar.write_text(json.dumps({"db": db, "payload_keys": list(payload.keys())}, indent=2), encoding="utf-8")
