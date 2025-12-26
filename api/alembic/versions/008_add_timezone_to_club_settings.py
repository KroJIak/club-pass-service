"""Add timezone column to club_settings

Revision ID: 008
Revises: 007
Create Date: 2024-12-26 14:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '008'
down_revision = '007'
branch_labels = None
depends_on = None


def upgrade():
    """Add timezone column to club_settings table."""
    op.add_column('club_settings', sa.Column('timezone', sa.String(), nullable=False, server_default='Europe/Moscow'))


def downgrade():
    """Remove timezone column from club_settings table."""
    op.drop_column('club_settings', 'timezone')

