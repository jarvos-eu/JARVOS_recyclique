"""Story 27.8 — ancrage brouillon réception sur poste partagé enrôlé.

Revision ID: s27_8_poste_reception_registered_device
Revises: s27_4_enrollment_credentials
Create Date: 2026-05-30

"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "s27_8_poste_reception_registered_device"
down_revision = "s27_4_enrollment_credentials"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "poste_reception",
        sa.Column("registered_device_id", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.create_foreign_key(
        "fk_poste_reception_registered_device_id",
        "poste_reception",
        "registered_devices",
        ["registered_device_id"],
        ["id"],
    )
    op.create_index(
        "ix_poste_reception_registered_device_open",
        "poste_reception",
        ["registered_device_id"],
        postgresql_where=sa.text("status = 'opened'"),
    )


def downgrade() -> None:
    op.drop_index("ix_poste_reception_registered_device_open", table_name="poste_reception")
    op.drop_constraint(
        "fk_poste_reception_registered_device_id",
        "poste_reception",
        type_="foreignkey",
    )
    op.drop_column("poste_reception", "registered_device_id")
