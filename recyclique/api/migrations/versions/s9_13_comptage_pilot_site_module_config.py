"""Story 9.13 — seed config pilote comptage-pieces-billets pour site La Clique.

Revision ID: s9_13_comptage_pilot_site_module_config
Revises: s9_11_cash_denomination_counts
Create Date: 2026-06-06
"""

from __future__ import annotations

import json
import os
import uuid

import sqlalchemy as sa
from alembic import op

revision = "s9_13_comptage_pilot_site_module_config"
down_revision = "s9_11_cash_denomination_counts"
branch_labels = None
depends_on = None

_MODULE_KEY = "comptage-pieces-billets"
_SCHEMA_VERSION = "1.0.0"
_PILOT_PAYLOAD = {
    "enabled": True,
    "skip_allowed": False,
    "require_denomination_grid": True,
    "show_images": True,
}


def _resolve_pilot_site_id(connection: sa.Connection) -> uuid.UUID | None:
    env_id = os.environ.get("PILOT_SITE_ID", "").strip()
    if env_id:
        try:
            return uuid.UUID(env_id)
        except ValueError as exc:
            raise ValueError(f"PILOT_SITE_ID invalide (UUID attendu) : {env_id!r}") from exc
    row = connection.execute(
        sa.text(
            "SELECT id FROM sites WHERE name ILIKE :pattern AND is_active = true ORDER BY name LIMIT 1"
        ),
        {"pattern": "%La Clique%"},
    ).fetchone()
    if row is None:
        return None
    return row[0]


def upgrade() -> None:
    connection = op.get_bind()
    site_id = _resolve_pilot_site_id(connection)
    if site_id is None:
        print(
            "s9_13_comptage_pilot_site_module_config: aucun site pilote trouvé "
            "(PILOT_SITE_ID ou nom %La Clique%) — seed ignoré ; activer via /admin/modules"
        )
        return

    payload_json = json.dumps(_PILOT_PAYLOAD)
    connection.execute(
        sa.text(
            """
            INSERT INTO site_module_configs (site_id, module_key, schema_version, payload, version)
            VALUES (:site_id, :module_key, :schema_version, CAST(:payload AS jsonb), 1)
            ON CONFLICT (site_id, module_key) DO UPDATE SET
                schema_version = EXCLUDED.schema_version,
                payload = EXCLUDED.payload,
                version = site_module_configs.version + 1
            """
        ),
        {
            "site_id": site_id,
            "module_key": _MODULE_KEY,
            "schema_version": _SCHEMA_VERSION,
            "payload": payload_json,
        },
    )


def downgrade() -> None:
    connection = op.get_bind()
    site_id = _resolve_pilot_site_id(connection)
    if site_id is None:
        print(
            "s9_13_comptage_pilot_site_module_config: aucun site pilote trouvé "
            "(PILOT_SITE_ID ou nom %La Clique%) — seed ignoré ; activer via /admin/modules"
        )
        return
    connection.execute(
        sa.text(
            "DELETE FROM site_module_configs WHERE site_id = :site_id AND module_key = :module_key"
        ),
        {"site_id": site_id, "module_key": _MODULE_KEY},
    )
