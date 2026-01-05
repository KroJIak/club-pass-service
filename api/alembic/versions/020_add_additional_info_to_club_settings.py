"""Add additional_info column to club_settings

Revision ID: 020
Revises: 019
Create Date: 2026-01-05 18:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '020'
down_revision = '019'
branch_labels = None
depends_on = None


def upgrade():
    """Add additional_info column to club_settings table."""
    op.add_column('club_settings', sa.Column('additional_info', sa.String(), nullable=True))


def downgrade():
    """Remove additional_info column from club_settings table."""
    op.drop_column('club_settings', 'additional_info')

