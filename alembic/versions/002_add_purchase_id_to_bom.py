"""Add purchase_id to product_bom

Revision ID: 002_add_purchase_id
Revises: 001_initial
Create Date: 2024-01-01 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '002_add_purchase_id'
down_revision: Union[str, None] = '001_initial'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Check if column already exists (in case it was created by create_all)
    conn = op.get_bind()
    result = conn.execute(sa.text("PRAGMA table_info(product_bom)"))
    columns = [row[1] for row in result]
    
    if 'purchase_id' not in columns:
        # Add purchase_id column to product_bom table
        op.add_column('product_bom', sa.Column('purchase_id', sa.Integer(), nullable=True))
    
    # For existing BOM lines, we need to set a purchase_id
    # We'll use the most recent purchase for each material
    op.execute(sa.text("""
        UPDATE product_bom
        SET purchase_id = (
            SELECT purchases.id
            FROM purchases
            WHERE purchases.material_id = product_bom.material_id
            ORDER BY purchases.purchase_date DESC
            LIMIT 1
        )
        WHERE purchase_id IS NULL
    """))
    
    # Note: SQLite doesn't support ALTER COLUMN to change nullable constraint
    # The column will remain nullable, but we ensure all rows have values
    # Foreign keys in SQLite need to be defined at table creation, so we skip that


def downgrade() -> None:
    op.drop_constraint('fk_product_bom_purchase_id', 'product_bom', type_='foreignkey')
    op.drop_column('product_bom', 'purchase_id')
