"""Add count field to products

Revision ID: 004_add_count_to_products
Revises: 003_remove_sku_unique
Create Date: 2024-01-01 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '004_add_count_to_products'
down_revision: Union[str, None] = '003_remove_sku_unique'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add count column to products table
    # Check if column already exists
    conn = op.get_bind()
    result = conn.execute(sa.text("PRAGMA table_info(products)"))
    columns = [row[1] for row in result.fetchall()]
    
    if 'count' not in columns:
        op.add_column('products', sa.Column('count', sa.Integer(), nullable=False, server_default='1'))


def downgrade() -> None:
    # Remove count column
    op.drop_column('products', 'count')
