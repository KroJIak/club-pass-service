"""Add expiration_settings table

Revision ID: 003
Revises: 002
Create Date: 2024-01-01 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime


# revision identifiers, used by Alembic.
revision = '003'
down_revision = None  # Первая миграция в api/alembic/versions/
branch_labels = None
depends_on = None


def upgrade():
    """Create expiration_settings table."""
    op.create_table(
        'expiration_settings',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('ticket_expiration_enabled', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('event_deactivation_enabled', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Insert default settings
    op.execute("""
        INSERT INTO expiration_settings (id, ticket_expiration_enabled, event_deactivation_enabled, updated_at)
        VALUES (1, true, true, NOW())
    """)


def downgrade():
    """Drop expiration_settings table."""
    op.drop_table('expiration_settings')

