"""Remove promocodes table and promocode column from orders

Revision ID: 015
Revises: 014
Create Date: 2025-01-02 20:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '015'
down_revision = '014'
branch_labels = None
depends_on = None


def upgrade():
    # Drop promocode column from orders table
    op.drop_column('orders', 'promocode')
    
    # Drop promocodes table
    op.drop_table('promocodes')


def downgrade():
    # Recreate promocodes table (simplified structure)
    op.create_table(
        'promocodes',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('code', sa.String(), nullable=False),
        sa.Column('discount_percent', sa.Numeric(5, 2), nullable=True),
        sa.Column('discount_amount', sa.Numeric(10, 2), nullable=True),
        sa.Column('valid_from', sa.DateTime(), nullable=False),
        sa.Column('valid_until', sa.DateTime(), nullable=False),
        sa.Column('usage_limit', sa.Integer(), nullable=True),
        sa.Column('usage_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_promocodes_id'), 'promocodes', ['id'], unique=False)
    op.create_index(op.f('ix_promocodes_code'), 'promocodes', ['code'], unique=True)
    
    # Recreate promocode column in orders table
    op.add_column('orders', sa.Column('promocode', sa.String(), nullable=True))

