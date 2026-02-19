import os
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool
from alembic import context

# Alembic Config object
config = context.config

# Logging setup
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# ---------------------------------------------------------
# Import Base and ALL models so Alembic detects them
# ---------------------------------------------------------
from app.db.base_class import Base
from app.db import models  # ensures models are registered

# Explicit imports (important for autogenerate)
from app.models.product import Product
from app.models.sku import SKU
from app.models.tenant import Tenant
from app.models.competitor_price import CompetitorPrice
from app.models.price_decision import PriceDecision
from app.models.pricing_rl_state import PricingRLState
from app.models.demand_signal import DemandSignal

target_metadata = Base.metadata

# ---------------------------------------------------------
# Helper: Get DATABASE_URL from environment
# ---------------------------------------------------------
def get_database_url():
    url = os.getenv(
        "DATABASE_URL",
        "postgresql+asyncpg://pricing_user:pricing_pass@postgres:5432/pricing_db"
    )

    if url.startswith("postgresql+asyncpg"):
        url = url.replace("postgresql+asyncpg", "postgresql")

    return url



# ---------------------------------------------------------
# OFFLINE MIGRATIONS
# ---------------------------------------------------------
def run_migrations_offline() -> None:
    """Run migrations in offline mode."""

    database_url = get_database_url()

    context.configure(
        url=database_url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


# ---------------------------------------------------------
# ONLINE MIGRATIONS
# ---------------------------------------------------------
def run_migrations_online() -> None:
    """Run migrations in online mode (Docker-safe)."""

    database_url = get_database_url()

    # 👇 Override alembic.ini DB URL
    config.set_main_option("sqlalchemy.url", database_url)

    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,          # detect column type changes
            compare_server_default=True # detect default changes
        )

        with context.begin_transaction():
            context.run_migrations()


# ---------------------------------------------------------
# ENTRY POINT
# ---------------------------------------------------------
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()