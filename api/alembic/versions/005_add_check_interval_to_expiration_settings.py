"""Add check_interval_minutes to expiration_settings

Revision ID: 005
Revises: 004_add_used_status_remove_is_used
Create Date: 2024-12-24 03:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '005'
down_revision = '003'  # Ссылается на миграцию 003 из api/alembic/versions/
branch_labels = None
depends_on = None


def upgrade():
    """Add check_interval_minutes column to expiration_settings table."""
    op.add_column(
        'expiration_settings',
        sa.Column('check_interval_minutes', sa.Integer(), nullable=False, server_default='30')
    )


def downgrade():
    """Remove check_interval_minutes column from expiration_settings table."""
    op.drop_column('expiration_settings', 'check_interval_minutes')

