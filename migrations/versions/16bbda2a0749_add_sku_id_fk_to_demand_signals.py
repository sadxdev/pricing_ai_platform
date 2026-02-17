"""add sku_id fk to demand_signals

Revision ID: 16bbda2a0749
Revises: 6507f5f2ea2c
Create Date: 2026-02-17

"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

# revision identifiers
revision: str = "16bbda2a0749"
down_revision: Union[str, Sequence[str], None] = "6507f5f2ea2c"
branch_labels = None
depends_on = None


# -----------------------------------------------------
# 🔍 Utility helpers (for idempotent safe migration)
# -----------------------------------------------------
def column_exists(table: str, column: str) -> bool:
    bind = op.get_bind()
    inspector = inspect(bind)
    columns = [col["name"] for col in inspector.get_columns(table)]
    return column in columns


def index_exists(table: str, index_name: str) -> bool:
    bind = op.get_bind()
    inspector = inspect(bind)
    indexes = [idx["name"] for idx in inspector.get_indexes(table)]
    return index_name in indexes


def fk_exists(table: str, fk_name: str) -> bool:
    bind = op.get_bind()
    inspector = inspect(bind)
    fks = [fk["name"] for fk in inspector.get_foreign_keys(table)]
    return fk_name in fks


# -----------------------------------------------------
# 🚀 UPGRADE
# -----------------------------------------------------
def upgrade() -> None:

    # =====================================================
    # 1️⃣ TENANT_ID COLUMN (SAFE ADD + BACKFILL)
    # =====================================================
    if not column_exists("demand_signals", "tenant_id"):
        op.add_column(
            "demand_signals",
            sa.Column("tenant_id", sa.Integer(), nullable=True),
        )

    # Backfill tenant_id (default tenant = 1)
    op.execute(
        """
        UPDATE demand_signals
        SET tenant_id = 1
        WHERE tenant_id IS NULL
        """
    )

    # Make NOT NULL
    op.alter_column(
        "demand_signals",
        "tenant_id",
        nullable=False,
    )

    # Add FK
    if not fk_exists("demand_signals", "fk_demand_signals_tenant_id"):
        op.create_foreign_key(
            "fk_demand_signals_tenant_id",
            "demand_signals",
            "tenants",
            ["tenant_id"],
            ["id"],
            ondelete="CASCADE",
        )

    # Add index
    if not index_exists("demand_signals", "ix_demand_signals_tenant_id"):
        op.create_index(
            "ix_demand_signals_tenant_id",
            "demand_signals",
            ["tenant_id"],
            unique=False,
        )

    # =====================================================
    # 2️⃣ SKU_ID COLUMN (SAFE ADD + BACKFILL)
    # =====================================================
    if not column_exists("demand_signals", "sku_id"):
        op.add_column(
            "demand_signals",
            sa.Column("sku_id", sa.Integer(), nullable=True),
        )

    # Backfill sku_id (default sku = 1)
    op.execute(
        """
        UPDATE demand_signals
        SET sku_id = 1
        WHERE sku_id IS NULL
        """
    )

    # Make NOT NULL
    op.alter_column(
        "demand_signals",
        "sku_id",
        nullable=False,
    )

    # Add FK
    if not fk_exists("demand_signals", "fk_demand_signals_sku_id"):
        op.create_foreign_key(
            "fk_demand_signals_sku_id",
            "demand_signals",
            "skus",
            ["sku_id"],
            ["id"],
            ondelete="CASCADE",
        )

    # Add index
    if not index_exists("demand_signals", "ix_demand_signals_sku_id"):
        op.create_index(
            "ix_demand_signals_sku_id",
            "demand_signals",
            ["sku_id"],
            unique=False,
        )


# -----------------------------------------------------
# ⬇️ DOWNGRADE
# -----------------------------------------------------
def downgrade() -> None:

    # Remove SKU FK + index + column
    if index_exists("demand_signals", "ix_demand_signals_sku_id"):
        op.drop_index("ix_demand_signals_sku_id", table_name="demand_signals")

    if fk_exists("demand_signals", "fk_demand_signals_sku_id"):
        op.drop_constraint("fk_demand_signals_sku_id", "demand_signals", type_="foreignkey")

    if column_exists("demand_signals", "sku_id"):
        op.drop_column("demand_signals", "sku_id")

    # Remove TENANT FK + index + column
    if index_exists("demand_signals", "ix_demand_signals_tenant_id"):
        op.drop_index("ix_demand_signals_tenant_id", table_name="demand_signals")

    if fk_exists("demand_signals", "fk_demand_signals_tenant_id"):
        op.drop_constraint("fk_demand_signals_tenant_id", "demand_signals", type_="foreignkey")

    if column_exists("demand_signals", "tenant_id"):
        op.drop_column("demand_signals", "tenant_id")