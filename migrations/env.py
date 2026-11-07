"""Alembic environment.

The database URL is taken from ``agent_ant_core`` settings (``DATABASE_URL``) unless a caller
sets ``sqlalchemy.url`` on the Alembic config first, which is how tests point it at a test
database without touching the environment.
"""

from alembic import context
from sqlalchemy import create_engine, pool

from agent_ant_core.config import get_settings
from agent_ant_core.db.models import Base

config = context.config
target_metadata = Base.metadata


def _url() -> str:
    return config.get_main_option("sqlalchemy.url") or get_settings().database_url


def run_migrations_offline() -> None:
    context.configure(url=_url(), target_metadata=target_metadata, literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    engine = create_engine(_url(), poolclass=pool.NullPool)
    with engine.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
