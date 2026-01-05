"""Add request_count column to music_queue table

Revision ID: 022
Revises: 021
Create Date: 2025-01-06 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '022'
down_revision = '021'
branch_labels = None
depends_on = None


def upgrade():
    """Add request_count column to music_queue table."""
    op.add_column(
        'music_queue',
        sa.Column('request_count', sa.Integer(), nullable=False, server_default='0')
    )
    op.create_index(
        op.f('ix_music_queue_request_count'),
        'music_queue',
        ['request_count'],
        unique=False
    )


def downgrade():
    """Remove request_count column from music_queue table."""
    op.drop_index(op.f('ix_music_queue_request_count'), table_name='music_queue')
    op.drop_column('music_queue', 'request_count')

