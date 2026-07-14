#!/usr/bin/env python3
"""Execute eco-organismes interrogation template against Recyclique mirror DB."""
from __future__ import annotations

import argparse
import csv
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path

from docker_mirror import check_docker_mirror

# Ecologic code -> categories.name (see mapping-reference.md)
ECOLOGIC_CATEGORIES: dict[str, list[str]] = {
    "PAM": ["1- Petits appareils em melange(PAM)"],
    "ECR": ["2- Ecrans"],
    "GHF": ["3- Gros électroménager hors froid (GEMHF)"],
    "GEF": ["4- Gros électroménager froid (GEMF)"],
    "ASL-CAT1": ["1- Cycles et engins de déplacement non motorisés"],
    "ASL-CAT2": ["2- Autres ASL"],
    "ABJ-TONA": ["1- Tondeuses autoportées"],
    "ABJ-TONM": ["2- Tondeuses à conducteur marchant"],
    "ABJ-AUT": ["3- Autres ABJ thermique"],
}

# Ecomaison colonnes tableur K–T (session T2)
ECOMAISON_CATEGORIES: dict[str, list[str]] = {
    "K": [
        "Jardin",
        "*Pots de fleurs",
        "* Gros équipement de jardin sup80cm",
        "NE PLUS UTILISER Materiel destinés à l'aménagement du jardin",
    ],
    "L": [
        "A - Outillage Divers",
        "* Outillage à main",
        "Outillage",
        "NE PLUS UTILISER- Materiel de bricolage",
        "* Gros Equipements de Bricolage (sup 80 cm)",
    ],
    "M": ["1- Jeux de plein air"],
    "N": ["2- Jeux société et puzzle"],
    "O": ["3- autres jeux d'intérieur", "A - Jeux Divers"],
    "P": [
        "* Assises",
        "Chaises",
        "Petit meuble/chaise en bois massif",
        "Gros meuble en bois massif",
        "Meuble moyen en bois massif",
        "A - Meuble Divers",
    ],
    "Q": ["* Couchage"],
    "R": [
        "* Rangement",
        "NE PLUS UTILISER Rangement et plan de pose et de travail",
    ],
    "S": ["*Plan de pose , plan de travail"],
    "T": ["* Décoration textile"],
}

HITL_CODES = {"ASL-CAT1", "ASL-CAT2", "ABJ-TONM", "T"}

FLUX_SUPPORTES = frozenset(
    {"DEC_REE", "LIV", "RECYCLAGE", "COUNT", "SORTIES_DEPOT_KG"}
)


def sql_escape(s: str) -> str:
    return s.replace("'", "''")


def period_bounds(date_debut: str, date_fin: str) -> tuple[str, str]:
    start = datetime.strptime(date_debut, "%Y-%m-%d")
    end_exclusive = datetime.strptime(date_fin, "%Y-%m-%d") + timedelta(days=1)
    return (
        start.strftime("%Y-%m-%d 00:00:00+00"),
        end_exclusive.strftime("%Y-%m-%d 00:00:00+00"),
    )


def resolve_categories(row: dict) -> list[str]:
    if row.get("categorie_recyclique", "").strip():
        return [row["categorie_recyclique"].strip()]
    code = row.get("code", "").strip().upper()
    partenaire = row.get("partenaire", "ecologic").strip().lower()
    if partenaire == "ecomaison" and code in ECOMAISON_CATEGORIES:
        return ECOMAISON_CATEGORIES[code]
    if partenaire == "ecologic" and code in ECOLOGIC_CATEGORIES:
        return ECOLOGIC_CATEGORIES[code]
    # rétrocompat : code seul si partenaire absent ou ambigu
    if code in ECOLOGIC_CATEGORIES:
        return ECOLOGIC_CATEGORIES[code]
    if code in ECOMAISON_CATEGORIES:
        return ECOMAISON_CATEGORIES[code]
    return []


def depot_base_sql(t_start: str, t_end: str, cat_list: str) -> str:
    return f"""
FROM ligne_depot ld
JOIN ticket_depot t ON t.id = ld.ticket_id
JOIN categories c ON c.id = ld.category_id
WHERE t.created_at >= '{t_start}'
  AND t.created_at < '{t_end}'
  AND c.name IN ({cat_list})
""".strip()


def build_sql(row: dict) -> str | None:
    flux = row.get("flux", "").strip().upper()
    if flux not in FLUX_SUPPORTES:
        return None

    unite = row.get("unite", "t").strip().lower()
    cats = resolve_categories(row)
    if not cats:
        return None

    t_start, t_end = period_bounds(row["date_debut"], row["date_fin"])
    excl_recyclage = row.get("exclure_recyclage", "oui").strip().lower() in (
        "oui",
        "yes",
        "1",
        "true",
    )
    cat_list = ", ".join(f"'{sql_escape(c)}'" for c in cats)
    recyclage_filter = (
        "AND (si.notes IS NULL OR si.notes NOT ILIKE '%recyclage%')"
        if excl_recyclage
        else ""
    )
    destination = (row.get("destination") or "RECYCLAGE").strip() or "RECYCLAGE"
    dest_sql = sql_escape(destination)

    if flux == "DEC_REE":
        if unite in ("pieces", "piece", "pc", "u"):
            return f"""
SELECT COALESCE(SUM(si.quantity), 0)::text AS result
FROM sale_items si
JOIN sales s ON s.id = si.sale_id
JOIN categories c ON c.id::text = si.category
WHERE COALESCE(s.sale_date, s.created_at) >= '{t_start}'
  AND COALESCE(s.sale_date, s.created_at) < '{t_end}'
  AND c.name IN ({cat_list})
  {recyclage_filter};
""".strip()
        return f"""
SELECT COALESCE(ROUND(SUM(COALESCE(si.weight, 0))::numeric / 1000, 3), 0)::text AS result
FROM sale_items si
JOIN sales s ON s.id = si.sale_id
JOIN categories c ON c.id::text = si.category
WHERE COALESCE(s.sale_date, s.created_at) >= '{t_start}'
  AND COALESCE(s.sale_date, s.created_at) < '{t_end}'
  AND c.name IN ({cat_list})
  {recyclage_filter};
""".strip()

    if flux == "LIV":
        return f"""
SELECT COALESCE(ROUND(FLOOR(SUM(ld.poids_kg))::numeric / 1000, 3), 0)::text AS result
{depot_base_sql(t_start, t_end, cat_list)}
  AND ld.is_exit = false;
""".strip()

    if flux == "RECYCLAGE":
        if unite in ("t", "tonne", "tonnes"):
            return f"""
SELECT COALESCE(ROUND(SUM(ld.poids_kg)::numeric / 1000, 3), 0)::text AS result
{depot_base_sql(t_start, t_end, cat_list)}
  AND ld.is_exit = true
  AND ld.destination = '{dest_sql}';
""".strip()
        return f"""
SELECT COALESCE(ROUND(SUM(ld.poids_kg)::numeric, 1), 0)::text AS result
{depot_base_sql(t_start, t_end, cat_list)}
  AND ld.is_exit = true
  AND ld.destination = '{dest_sql}';
""".strip()

    if flux == "SORTIES_DEPOT_KG":
        # Toutes sorties dépôt is_exit=true pour les catégories (toute destination)
        return f"""
SELECT COALESCE(ROUND(SUM(ld.poids_kg)::numeric, 1), 0)::text AS result
{depot_base_sql(t_start, t_end, cat_list)}
  AND ld.is_exit = true;
""".strip()

    if flux == "COUNT":
        return f"""
SELECT COUNT(*)::text AS result
FROM sale_items si
JOIN sales s ON s.id = si.sale_id
JOIN categories c ON c.id::text = si.category
WHERE COALESCE(s.sale_date, s.created_at) >= '{t_start}'
  AND COALESCE(s.sale_date, s.created_at) < '{t_end}'
  AND c.name IN ({cat_list})
  {recyclage_filter};
""".strip()

    return None


def run_psql(sql: str, container: str, database: str, user: str) -> tuple[bool, str]:
    cmd = [
        "docker",
        "exec",
        container,
        "psql",
        "-U",
        user,
        "-d",
        database,
        "-t",
        "-A",
        "-c",
        sql,
    ]
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    except FileNotFoundError:
        return False, "docker non trouvé"
    except subprocess.TimeoutExpired:
        return False, "timeout psql (>60s)"
    if proc.returncode != 0:
        return False, (proc.stderr or proc.stdout or "erreur psql").strip()
    return True, proc.stdout.strip()


def load_template(path: Path) -> tuple[list[str], list[dict]]:
    with path.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f, delimiter=";")
        if not reader.fieldnames:
            raise ValueError("Template CSV vide ou sans en-têtes")
        rows = list(reader)
        return list(reader.fieldnames), rows


def write_output(path: Path, fieldnames: list[str], rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=";", extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def max_date_fin(rows: list[dict]) -> str | None:
    dates = [r.get("date_fin", "").strip() for r in rows if r.get("date_fin", "").strip()]
    return max(dates) if dates else None


def check_dump_freshness(dump_dir: Path, date_fin: str) -> tuple[bool, str]:
    script = Path(__file__).resolve().parent / "dump_manifest.py"
    proc = subprocess.run(
        [sys.executable, str(script), "--dump-dir", str(dump_dir), "--check-date", date_fin],
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        msg = (proc.stderr or proc.stdout or "dump insuffisant").strip()
        return False, (
            f"Le dump dans {dump_dir} est trop ancien pour la période demandée (fin {date_fin}).\n"
            f"→ Demande un export frais pré-prod et dépose-le dans references/_depot/\n"
            f"   ({msg})"
        )
    return True, proc.stdout.strip()


def mark_all_rows(rows: list[dict], statut: str, commentaire: str) -> None:
    for row in rows:
        row["statut"] = statut
        row["commentaire"] = commentaire


def main() -> int:
    parser = argparse.ArgumentParser(description="Interroger dump Recyclique pour éco-organismes")
    parser.add_argument("--template", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--dump-dir", type=Path, default=Path("references/_depot"))
    parser.add_argument("--container", default="recyclic-mirror-t2")
    parser.add_argument("--database", default="recyclic_la_clique_mirror")
    parser.add_argument("--user", default="postgres")
    parser.add_argument("--dry-run", action="store_true", help="Génère SQL sans exécuter")
    parser.add_argument(
        "--skip-docker-check",
        action="store_true",
        help="Ne pas vérifier Docker/miroir (dry-run ou debug)",
    )
    parser.add_argument("--save-sql", type=Path, default=None, help="Fichier audit SQL")
    args = parser.parse_args()

    fieldnames, rows = load_template(args.template)
    for col in ("resultat", "statut", "commentaire"):
        if col not in fieldnames:
            fieldnames.append(col)

    date_fin = max_date_fin(rows)
    if date_fin:
        ok, msg = check_dump_freshness(args.dump_dir, date_fin)
        if not ok:
            mark_all_rows(rows, "dump_insuffisant", msg)
            write_output(args.output, fieldnames, rows)
            print(msg, file=sys.stderr)
            return 1

    if not args.dry_run and not args.skip_docker_check:
        ok, msg = check_docker_mirror(args.container, args.database, args.user)
        if not ok:
            mark_all_rows(rows, "docker_indisponible", msg.replace("\n", " "))
            write_output(args.output, fieldnames, rows)
            print(msg, file=sys.stderr)
            return 1
        print(msg, file=sys.stderr)

    sql_log: list[str] = []
    errors = 0

    for row in rows:
        row_id = row.get("id", "?")
        sql = build_sql(row)
        if not sql:
            flux = row.get("flux", "?")
            row["statut"] = "erreur"
            row["commentaire"] = (
                f"flux « {flux} » ou code/categorie non résolu — "
                f"flux supportés : {', '.join(sorted(FLUX_SUPPORTES))}"
            )
            errors += 1
            continue

        sql_log.append(f"-- {row_id}\n{sql}\n")

        if args.dry_run:
            row["statut"] = "dry_run"
            row["commentaire"] = "SQL généré, non exécuté"
            continue

        ok, value = run_psql(sql, args.container, args.database, args.user)
        if not ok:
            row["statut"] = "erreur"
            row["commentaire"] = f"requête SQL échouée : {value[:400]}"
            errors += 1
            continue

        row["resultat"] = value
        row["statut"] = "ok"
        code = row.get("code", "").strip().upper()
        if code in HITL_CODES:
            extra = "mapping_hitl — valider terrain si décla officielle"
            base = (row.get("commentaire") or "").strip()
            row["commentaire"] = f"{base} {extra}".strip() if base else extra

    if args.save_sql:
        args.save_sql.parent.mkdir(parents=True, exist_ok=True)
        args.save_sql.write_text("\n".join(sql_log), encoding="utf-8")

    write_output(args.output, fieldnames, rows)
    print(f"Écrit: {args.output} ({len(rows)} lignes, {errors} erreur(s))")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
