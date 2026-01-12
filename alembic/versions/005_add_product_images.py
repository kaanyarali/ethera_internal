"""Add product_images table

Revision ID: 005_add_product_images
Revises: 004_add_count_to_products
Create Date: 2024-01-01 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '005_add_product_images'
down_revision: Union[str, None] = '004_add_count_to_products'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create product_images table
    # Check if table already exists (may have been created by SQLAlchemy's create_all)
    conn = op.get_bind()
    result = conn.execute(sa.text("SELECT name FROM sqlite_master WHERE type='table' AND name='product_images'"))
    table_exists = result.fetchone() is not None
    
    if not table_exists:
        op.create_table(
            'product_images',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('product_id', sa.Integer(), nullable=False),
            sa.Column('image_url', sa.String(), nullable=False),
            sa.Column('order', sa.Integer(), nullable=False, server_default='0'),
            sa.Column('created_at', sa.DateTime(), nullable=False),
            sa.ForeignKeyConstraint(['product_id'], ['products.id'], ),
            sa.PrimaryKeyConstraint('id')
        )
        op.create_index(op.f('ix_product_images_id'), 'product_images', ['id'], unique=False)
    else:
        # Table exists, check if index exists
        result = conn.execute(sa.text("SELECT name FROM sqlite_master WHERE type='index' AND name='ix_product_images_id'"))
        index_exists = result.fetchone() is not None
        if not index_exists:
            op.create_index(op.f('ix_product_images_id'), 'product_images', ['id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_product_images_id'), table_name='product_images')
    op.drop_table('product_images')
