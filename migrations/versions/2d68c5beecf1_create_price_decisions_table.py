"""create price_decisions table

Revision ID: 2d68c5beecf1
Revises: 16bbda2a0749
Create Date: 2026-02-17 16:46:42.320566
"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers
revision: str = "2d68c5beecf1"
down_revision: Union[str, Sequence[str], None] = "16bbda2a0749"
branch_labels = None
depends_on = None


# ============================================================
# UPGRADE
# ============================================================
def upgrade() -> None:
    # ----------------------------------------------------------
    # COMPETITOR PRICE INDEXES
    # ----------------------------------------------------------
    op.create_index(
        "ix_competitor_prices_competitor_name",
        "competitor_prices",
        ["competitor_name"],
        unique=False,
    )

    op.create_index(
        "ix_competitor_prices_competitor_price",
        "competitor_prices",
        ["competitor_price"],
        unique=False,
    )

    # ----------------------------------------------------------
    # DEMAND SIGNALS -> created_at (SAFE)
    # ----------------------------------------------------------
    op.add_column(
        "demand_signals",
        sa.Column("created_at", sa.DateTime(), nullable=True),
    )

    op.execute("""
        UPDATE demand_signals
        SET created_at = NOW()
        WHERE created_at IS NULL
    """)

    op.alter_column("demand_signals", "created_at", nullable=False)

    op.drop_index("ix_demand_signals_captured_at", table_name="demand_signals")

    op.create_index(
        "ix_demand_signals_created_at",
        "demand_signals",
        ["created_at"],
        unique=False,
    )

    op.drop_column("demand_signals", "captured_at")

    # ----------------------------------------------------------
    # PRICE DECISIONS -> TENANT (SAFE)
    # ----------------------------------------------------------
    op.add_column(
        "price_decisions",
        sa.Column("tenant_id", sa.Integer(), nullable=True),
    )

    op.execute("""
        UPDATE price_decisions
        SET tenant_id = 1
        WHERE tenant_id IS NULL
    """)

    op.alter_column("price_decisions", "tenant_id", nullable=False)

    op.create_foreign_key(
        "fk_price_decisions_tenant_id",
        "price_decisions",
        "tenants",
        ["tenant_id"],
        ["id"],
        ondelete="CASCADE",
    )

    op.create_index(
        "ix_price_decisions_tenant_id",
        "price_decisions",
        ["tenant_id"],
        unique=False,
    )

    # ----------------------------------------------------------
    # PRICE DECISIONS -> BASE PRICE (SAFE)
    # ----------------------------------------------------------
    op.add_column(
        "price_decisions",
        sa.Column("base_price", sa.Numeric(10, 2), nullable=True),
    )

    op.execute("""
        UPDATE price_decisions
        SET base_price = 0
        WHERE base_price IS NULL
    """)

    op.alter_column("price_decisions", "base_price", nullable=False)

    # ----------------------------------------------------------
    # COST PRICE (SAFE)
    # ----------------------------------------------------------
    op.add_column(
        "price_decisions",
        sa.Column("cost_price", sa.Numeric(10, 2), nullable=True),
    )

    op.execute("""
        UPDATE price_decisions
        SET cost_price = 0
        WHERE cost_price IS NULL
    """)

    op.alter_column("price_decisions", "cost_price", nullable=False)

    # ----------------------------------------------------------
    # PREDICTED DEMAND (SAFE)
    # ----------------------------------------------------------
    op.add_column(
        "price_decisions",
        sa.Column("predicted_demand", sa.Numeric(10, 2), nullable=True),
    )

    op.execute("""
        UPDATE price_decisions
        SET predicted_demand = 0
        WHERE predicted_demand IS NULL
    """)

    op.alter_column("price_decisions", "predicted_demand", nullable=False)

    # ----------------------------------------------------------
    # OPTIONAL FIELDS -> NULLABLE
    # ----------------------------------------------------------
    op.alter_column(
        "price_decisions",
        "reason",
        existing_type=sa.VARCHAR(length=255),
        nullable=True,
    )

    op.alter_column(
        "price_decisions",
        "model_version",
        existing_type=sa.VARCHAR(length=50),
        nullable=True,
    )

    # ----------------------------------------------------------
    # FIX TENANT FK IN PRODUCTS (cleaned)
    # ----------------------------------------------------------
    op.drop_constraint("fk_products_tenant", "products", type_="foreignkey")
    op.create_foreign_key(
        "fk_products_tenant",
        "products",
        "tenants",
        ["tenant_id"],
        ["id"],
        ondelete="CASCADE",
    )

    # ----------------------------------------------------------
    # TENANT TABLE CLEANUP
    # ----------------------------------------------------------
    op.drop_constraint("tenants_name_key", "tenants", type_="unique")

    op.create_index(
        "ix_tenants_id",
        "tenants",
        ["id"],
        unique=False,
    )


# ============================================================
# DOWNGRADE
# ============================================================
def downgrade() -> None:

    # --- TENANTS ---
    op.drop_index("ix_tenants_id", table_name="tenants")
    op.create_unique_constraint("tenants_name_key", "tenants", ["name"])

    # --- PRODUCTS FK ---
    op.drop_constraint("fk_products_tenant", "products", type_="foreignkey")
    op.create_foreign_key(
        "fk_products_tenant",
        "products",
        "tenants",
        ["tenant_id"],
        ["id"],
        ondelete="CASCADE",
    )

    # --- PRICE DECISIONS ---
    op.drop_column("price_decisions", "predicted_demand")
    op.drop_column("price_decisions", "cost_price")
    op.drop_column("price_decisions", "base_price")

    op.drop_constraint("fk_price_decisions_tenant_id", "price_decisions", type_="foreignkey")
    op.drop_index("ix_price_decisions_tenant_id", table_name="price_decisions")
    op.drop_column("price_decisions", "tenant_id")

    # --- DEMAND SIGNALS ---
    op.add_column(
        "demand_signals",
        sa.Column("captured_at", sa.TIMESTAMP(), nullable=False),
    )

    op.drop_index("ix_demand_signals_created_at", table_name="demand_signals")
    op.create_index(
        "ix_demand_signals_captured_at",
        "demand_signals",
        ["captured_at"],
        unique=False,
    )

    op.drop_column("demand_signals", "created_at")

    # --- COMPETITOR INDEXES ---
    op.drop_index("ix_competitor_prices_competitor_price", table_name="competitor_prices")
    op.drop_index("ix_competitor_prices_competitor_name", table_name="competitor_prices")