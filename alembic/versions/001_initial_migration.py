"""Initial migration

Revision ID: 001_initial
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '001_initial'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create materials table
    op.create_table(
        'materials',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('type', sa.Enum('GEMSTONE', 'METAL', 'OTHER', name='materialtype'), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('unit', sa.String(), nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('attributes_json', sa.JSON(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_materials_id'), 'materials', ['id'], unique=False)
    
    # Create purchases table
    op.create_table(
        'purchases',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('material_id', sa.Integer(), nullable=False),
        sa.Column('supplier_name', sa.String(), nullable=False),
        sa.Column('purchase_date', sa.DateTime(), nullable=False),
        sa.Column('qty_purchased', sa.Float(), nullable=False),
        sa.Column('qty_remaining', sa.Float(), nullable=False),
        sa.Column('unit_cost', sa.Float(), nullable=False),
        sa.Column('currency', sa.String(), nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['material_id'], ['materials.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_purchases_id'), 'purchases', ['id'], unique=False)
    
    # Create products table
    op.create_table(
        'products',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('sku', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('image_url', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('sku')
    )
    op.create_index(op.f('ix_products_id'), 'products', ['id'], unique=False)
    op.create_index(op.f('ix_products_sku'), 'products', ['sku'], unique=False)
    
    # Create product_bom table
    op.create_table(
        'product_bom',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('product_id', sa.Integer(), nullable=False),
        sa.Column('material_id', sa.Integer(), nullable=False),
        sa.Column('qty_required', sa.Float(), nullable=False),
        sa.Column('unit', sa.String(), nullable=False),
        sa.Column('note', sa.String(), nullable=True),
        sa.ForeignKeyConstraint(['material_id'], ['materials.id'], ),
        sa.ForeignKeyConstraint(['product_id'], ['products.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_product_bom_id'), 'product_bom', ['id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_product_bom_id'), table_name='product_bom')
    op.drop_table('product_bom')
    op.drop_index(op.f('ix_products_sku'), table_name='products')
    op.drop_index(op.f('ix_products_id'), table_name='products')
    op.drop_table('products')
    op.drop_index(op.f('ix_purchases_id'), table_name='purchases')
    op.drop_table('purchases')
    op.drop_index(op.f('ix_materials_id'), table_name='materials')
    op.drop_table('materials')
