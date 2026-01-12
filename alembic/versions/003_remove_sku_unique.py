"""Remove SKU unique constraint

Revision ID: 003_remove_sku_unique
Revises: 002_add_purchase_id
Create Date: 2024-01-01 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '003_remove_sku_unique'
down_revision: Union[str, None] = '002_add_purchase_id'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Remove unique constraint from sku column
    # In SQLite, we need to recreate the table to remove a unique constraint
    # This is a simplified approach - in production you might want to use a table copy method
    
    # Drop the unique index if it exists
    try:
        op.drop_index('ix_products_sku', table_name='products')
    except:
        pass
    
    # Drop the unique constraint (SQLite stores it as an index)
    # Check if there's a unique constraint index
    conn = op.get_bind()
    result = conn.execute(sa.text("""
        SELECT name FROM sqlite_master 
        WHERE type='index' 
        AND tbl_name='products' 
        AND sql LIKE '%UNIQUE%'
    """))
    unique_indexes = result.fetchall()
    for idx in unique_indexes:
        if 'sku' in idx[0].lower():
            op.execute(sa.text(f"DROP INDEX IF EXISTS {idx[0]}"))
    
    # Recreate index without unique constraint
    op.create_index('ix_products_sku', 'products', ['sku'], unique=False)


def downgrade() -> None:
    # Recreate unique constraint
    op.drop_index('ix_products_sku', table_name='products')
    op.create_index('ix_products_sku', 'products', ['sku'], unique=True)
