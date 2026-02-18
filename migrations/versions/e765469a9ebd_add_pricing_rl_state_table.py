"""add pricing rl state table

Revision ID: e765469a9ebd
Revises: 2d68c5beecf1
Create Date: 2026-02-17 19:10:12.972669
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers
revision: str = 'e765469a9ebd'
down_revision: Union[str, Sequence[str], None] = '2d68c5beecf1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# =========================================================
#  UPGRADE
# =========================================================
def upgrade() -> None:
    """Create pricing RL state table"""

    op.create_table(
        "pricing_rl_state",
        sa.Column("id", sa.Integer(), primary_key=True),

        sa.Column("tenant_id", sa.Integer(), nullable=False),
        sa.Column("sku_id", sa.Integer(), nullable=False),

        sa.Column("avg_reward", sa.Float(), nullable=False, server_default="0"),
        sa.Column("total_trials", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("epsilon", sa.Float(), nullable=False, server_default="0.1"),

        sa.ForeignKeyConstraint(
            ["tenant_id"],
            ["tenants.id"],
            ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["sku_id"],
            ["skus.id"],
            ondelete="CASCADE"
        ),
    )

    op.create_index(
        "ix_pricing_rl_state_tenant_sku",
        "pricing_rl_state",
        ["tenant_id", "sku_id"],
        unique=True
    )


# =========================================================
#  DOWNGRADE
# =========================================================
def downgrade() -> None:
    """Drop pricing RL state table"""

    op.drop_index("ix_pricing_rl_state_tenant_sku", table_name="pricing_rl_state")
    op.drop_table("pricing_rl_state")