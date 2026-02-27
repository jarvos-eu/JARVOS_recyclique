# Alembic env.py — RecyClique (Story 3.2).
# Charge la config (database_url) et les modèles pour target_metadata.

from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy.pool import NullPool
from alembic import context

from api.config import get_settings
from api.db.session import Base

# Import de tous les modèles pour enregistrement dans Base.metadata
from api.models import (  # noqa: F401
    Site,
    CashRegister,
    CashSession,
    Category,
    PresetButton,
    Group,
    Permission,
    User,
    UserSession,
    LoginHistory,
    RegistrationRequest,
    AuditEvent,
    PosteReception,
    Sale,
    SaleItem,
    PaymentTransaction,
)

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def get_url():
    settings = get_settings()
    return settings.database_url or "sqlite:///./recyclic.sqlite"


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    configuration = config.get_section(config.config_ini_section, {}) or {}
    configuration["sqlalchemy.url"] = get_url()
    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
