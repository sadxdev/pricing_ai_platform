"""add tenant_id to products

Revision ID: 5291a893827c
Revises: 05add14e7ca2
Create Date: 2026-02-17 11:35:50.314456
"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


# revision identifiers
revision: str = '5291a893827c'
down_revision: Union[str, Sequence[str], None] = '05add14e7ca2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    # -------------------------------------------------------
    # 1. Add column ONLY if not exists
    # -------------------------------------------------------
    op.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1
                FROM information_schema.columns
                WHERE table_name='products'
                AND column_name='tenant_id'
            ) THEN
                ALTER TABLE products ADD COLUMN tenant_id INTEGER;
            END IF;
        END $$;
    """)

    # -------------------------------------------------------
    # 2. Backfill existing rows
    # -------------------------------------------------------
    op.execute("UPDATE products SET tenant_id = 1 WHERE tenant_id IS NULL")

    # -------------------------------------------------------
    # 3. Set NOT NULL
    # -------------------------------------------------------
    op.execute("""
        ALTER TABLE products
        ALTER COLUMN tenant_id SET NOT NULL
    """)

    # -------------------------------------------------------
    # 4. Add FK constraint if not exists
    # -------------------------------------------------------
    op.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM pg_constraint
                WHERE conname = 'fk_products_tenant_id'
            ) THEN
                ALTER TABLE products
                ADD CONSTRAINT fk_products_tenant_id
                FOREIGN KEY (tenant_id)
                REFERENCES tenants(id)
                ON DELETE CASCADE;
            END IF;
        END $$;
    """)

    # -------------------------------------------------------
    # 5. Add index if not exists
    # -------------------------------------------------------
    op.execute("""
        CREATE INDEX IF NOT EXISTS ix_products_tenant_id
        ON products (tenant_id);
    """)


def downgrade() -> None:
    """Downgrade schema."""

    # Drop indexes
    op.drop_index(op.f('ix_products_tenant_id'), table_name='products')
    op.drop_constraint("fk_products_tenant_id", "products", type_="foreignkey")

    op.drop_index(op.f('ix_tenants_id'), table_name='tenants')
    op.drop_index(op.f('ix_competitor_prices_competitor_price'), table_name='competitor_prices')
    op.drop_index(op.f('ix_competitor_prices_competitor_name'), table_name='competitor_prices')

    # Drop column
    op.drop_column("products", "tenant_id")