from logging.config import fileConfig
import os
import sys

from alembic import context
from sqlalchemy import create_engine, pool

# --- path setup ---
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# --- Alembic config ---
config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# --- import models ---
from app.db.base import Base
from app.db.models import (
    tenant,
    user,
    project,
    sdlc_job,
    sdlc_step,
    agent_execution,
)

target_metadata = Base.metadata

# --- DATABASE URL ---
DATABASE_URL = os.environ.get("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL environment variable is not set")


def run_migrations_offline():
    context.configure(
        url=DATABASE_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    engine = create_engine(
        DATABASE_URL,
        poolclass=pool.NullPool,
    )

    with engine.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
from app.db.models import (
    tenant,
    user,
    project,
    sdlc_job,
    sdlc_step,
    agent_execution,
    refresh_token,   # 👈 ADD THIS
)
