"""add tenant_id to competitor_prices

Revision ID: 6507f5f2ea2c
Revises: 5291a893827c
Create Date: 2026-02-17 12:15:53.493919

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6507f5f2ea2c'
down_revision: Union[str, Sequence[str], None] = '5291a893827c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:

    #  Add column as NULLABLE first
    op.add_column(
        'competitor_prices',
        sa.Column('tenant_id', sa.Integer(), nullable=True)
    )

    # Set default tenant for existing data
    op.execute("UPDATE competitor_prices SET tenant_id = 1")

    # Make column NOT NULL
    op.alter_column(
        'competitor_prices',
        'tenant_id',
        nullable=False
    )

    #  Add foreign key constraint
    op.create_foreign_key(
        'fk_competitor_prices_tenant',
        'competitor_prices',
        'tenants',
        ['tenant_id'],
        ['id'],
        ondelete='CASCADE'
    )

    # Add index
    op.create_index(
        'ix_competitor_prices_tenant_id',
        'competitor_prices',
        ['tenant_id']
    )


def downgrade() -> None:
    op.drop_index('ix_competitor_prices_tenant_id', table_name='competitor_prices')
    op.drop_constraint('fk_competitor_prices_tenant', 'competitor_prices', type_='foreignkey')
    op.drop_column('competitor_prices', 'tenant_id')
