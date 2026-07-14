#!/usr/bin/env python3
"""Vérifications Docker / miroir PostgreSQL — messages en français clair."""
from __future__ import annotations

import subprocess
import sys


def _run(cmd: list[str], timeout: int = 30) -> tuple[int, str, str]:
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return proc.returncode, proc.stdout.strip(), proc.stderr.strip()
    except FileNotFoundError:
        return 127, "", "commande introuvable"
    except subprocess.TimeoutExpired:
        return 124, "", "délai dépassé"


def check_docker_mirror(
    container: str = "recyclic-mirror-t2",
    database: str = "recyclic_la_clique_mirror",
    user: str = "postgres",
) -> tuple[bool, str]:
    """
    Vérifie que Docker tourne et que le miroir BDD est utilisable.
    Retourne (ok, message). Si ok=False, message = explication utilisateur + quoi faire.
    """
    code, _, err = _run(["docker", "version", "--format", "{{.Server.Version}}"])
    if code == 127:
        return False, (
            "Docker n'est pas installé ou la commande « docker » n'est pas accessible.\n"
            "→ Installe Docker Desktop (Windows) ou relance ton terminal après installation.\n"
            "→ Doc skill : .cursor/skills/interroger-eco-organismes/runbook.md"
        )
    if code != 0:
        return False, (
            "Docker est installé mais le moteur ne répond pas.\n"
            "→ Ouvre Docker Desktop et attends qu'il soit complètement démarré (icône verte).\n"
            "→ Puis relance la commande.\n"
            f"   (détail technique : {err or 'docker version a échoué'})"
        )

    code, out, err = _run(
        ["docker", "inspect", "-f", "{{.State.Running}}", container]
    )
    if code != 0:
        return False, (
            f"Le conteneur « {container} » n'existe pas sur cette machine.\n"
            "→ Il faut d'abord restaurer le dump PostgreSQL dans un miroir local.\n"
            "→ Place un fichier recyclic_db_export_*.dump dans references/_depot/\n"
            "→ Suis la section « Restauration Docker » du runbook :\n"
            "   .cursor/skills/interroger-eco-organismes/runbook.md\n"
            "→ Je n'ai pas lancé la restauration automatiquement — c'est volontaire."
        )

    if out.lower() != "true":
        return False, (
            f"Le conteneur « {container} » existe mais il est **arrêté**.\n"
            f"→ Lance : docker start {container}\n"
            "→ Attends quelques secondes, puis relance le script."
        )

    code, out, err = _run(
        [
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
            "SELECT 1",
        ]
    )
    if code != 0:
        hint = err or out or "connexion refusée"
        return False, (
            f"Le conteneur « {container} » tourne, mais la base « {database} » "
            "n'est pas accessible.\n"
            "→ Le dump n'a peut-être pas été restauré (pg_restore manquant ou incomplet).\n"
            "→ Reprends la procédure runbook.md (docker cp dump + pg_restore).\n"
            f"   (détail : {hint[:300]})"
        )

    code, out, err = _run(
        [
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
            "SELECT COUNT(*) FROM information_schema.tables "
            "WHERE table_schema='public' AND table_name IN "
            "('sale_items','ligne_depot','ticket_depot','categories','sales')",
        ]
    )
    if code != 0 or out != "5":
        return False, (
            f"La base « {database} » répond, mais les tables Recyclique attendues "
            "ne sont pas toutes là.\n"
            "→ Le dump est peut-être corrompu, incomplet, ou restauré dans une autre base.\n"
            "→ Vérifie avec : docker exec "
            f"{container} psql -U {user} -d {database} -c \"\\dt\"\n"
            "→ Si vide : refaire pg_restore depuis references/_depot/."
        )

    return True, f"OK — miroir {container} / {database} prêt."


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Vérifier miroir Docker Recyclique")
    parser.add_argument("--container", default="recyclic-mirror-t2")
    parser.add_argument("--database", default="recyclic_la_clique_mirror")
    parser.add_argument("--user", default="postgres")
    args = parser.parse_args()

    ok, msg = check_docker_mirror(args.container, args.database, args.user)
    print(msg)
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
