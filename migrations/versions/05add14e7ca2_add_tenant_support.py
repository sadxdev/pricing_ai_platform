"""add tenant support

Revision ID: 05add14e7ca2
Revises: c6767d5634e2
Create Date: 2026-02-13 19:05:21.919796

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '05add14e7ca2'
down_revision: Union[str, Sequence[str], None] = 'c6767d5634e2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # 1️⃣ Create tenants table
    op.create_table(
        "tenants",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=255), nullable=False, unique=True),
    )

    # 2️⃣ Insert default tenant
    op.execute("INSERT INTO tenants (id, name) VALUES (1, 'default')")

    # 3️⃣ Add tenant_id as nullable first
    op.add_column("products", sa.Column("tenant_id", sa.Integer(), nullable=True))
    op.add_column("skus", sa.Column("tenant_id", sa.Integer(), nullable=True))

    # 4️⃣ Backfill existing rows
    op.execute("UPDATE products SET tenant_id = 1")
    op.execute("UPDATE skus SET tenant_id = 1")

    # 5️⃣ Make column NOT NULL
    op.alter_column("products", "tenant_id", nullable=False)
    op.alter_column("skus", "tenant_id", nullable=False)

    # 6️⃣ Add foreign key constraints
    op.create_foreign_key(
        "fk_products_tenant",
        "products",
        "tenants",
        ["tenant_id"],
        ["id"],
        ondelete="CASCADE"
    )

    op.create_foreign_key(
        "fk_skus_tenant",
        "skus",
        "tenants",
        ["tenant_id"],
        ["id"],
        ondelete="CASCADE"
    )

    # 7️⃣ Add index
    op.create_index("ix_products_tenant_id", "products", ["tenant_id"])
    op.create_index("ix_skus_tenant_id", "skus", ["tenant_id"])


def downgrade():
    op.drop_constraint("fk_skus_tenant", "skus", type_="foreignkey")
    op.drop_constraint("fk_products_tenant", "products", type_="foreignkey")

    op.drop_index("ix_skus_tenant_id", table_name="skus")
    op.drop_index("ix_products_tenant_id", table_name="products")

    op.drop_column("skus", "tenant_id")
    op.drop_column("products", "tenant_id")

    op.drop_table("tenants")
    # ### end Alembic commands ###
