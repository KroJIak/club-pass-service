"""Add language column to admin_accounts table

Revision ID: 025
Revises: 024
Create Date: 2025-01-07 20:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '025'
down_revision = '024'
branch_labels = None
depends_on = None


def upgrade():
    """Add language column to admin_accounts table."""
    op.add_column(
        'admin_accounts',
        sa.Column('language', sa.String(2), nullable=False, server_default='ru')
    )


def downgrade():
    """Remove language column from admin_accounts table."""
    op.drop_column('admin_accounts', 'language')

