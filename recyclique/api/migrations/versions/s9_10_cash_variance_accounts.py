"""Story 9.10 — comptes globaux écart caisse 658/758 (T3 clôture Paheko).

Revision ID: s9_10_cash_variance_accounts
Revises: t_mod_3_site_module_configs
Create Date: 2026-05-27
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "s9_10_cash_variance_accounts"
down_revision = "t_mod_3_site_module_configs"
branch_labels = None
depends_on = None


def _has_column(inspector: sa.Inspector, table: str, column: str) -> bool:
    return any(c["name"] == column for c in inspector.get_columns(table))


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if "global_accounting_settings" not in inspector.get_table_names():
        return
    if not _has_column(inspector, "global_accounting_settings", "cash_shortage_account"):
        op.add_column(
            "global_accounting_settings",
            sa.Column("cash_shortage_account", sa.String(length=32), nullable=False, server_default="658"),
        )
    inspector = sa.inspect(bind)
    if not _has_column(inspector, "global_accounting_settings", "cash_surplus_account"):
        op.add_column(
            "global_accounting_settings",
            sa.Column("cash_surplus_account", sa.String(length=32), nullable=False, server_default="758"),
        )
    bind.execute(
        sa.text(
            """
            UPDATE global_accounting_settings
            SET cash_shortage_account = COALESCE(NULLIF(TRIM(cash_shortage_account), ''), '658'),
                cash_surplus_account = COALESCE(NULLIF(TRIM(cash_surplus_account), ''), '758')
            """
        )
    )


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if "global_accounting_settings" not in inspector.get_table_names():
        return
    inspector = sa.inspect(bind)
    if _has_column(inspector, "global_accounting_settings", "cash_surplus_account"):
        op.drop_column("global_accounting_settings", "cash_surplus_account")
    inspector = sa.inspect(bind)
    if _has_column(inspector, "global_accounting_settings", "cash_shortage_account"):
        op.drop_column("global_accounting_settings", "cash_shortage_account")
