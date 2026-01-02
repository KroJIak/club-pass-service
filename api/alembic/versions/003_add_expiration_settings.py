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
    from sqlalchemy import inspect
    from sqlalchemy.engine import reflection
    
    # Check if table already exists
    conn = op.get_bind()
    inspector = inspect(conn)
    existing_tables = inspector.get_table_names()
    
    if 'expiration_settings' not in existing_tables:
    op.create_table(
        'expiration_settings',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('ticket_expiration_enabled', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('event_deactivation_enabled', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    
        # Insert default settings only if table was just created
        op.execute("""
            INSERT INTO expiration_settings (id, ticket_expiration_enabled, event_deactivation_enabled, updated_at)
            VALUES (1, true, true, NOW())
            ON CONFLICT (id) DO NOTHING
        """)
    else:
        # Table already exists, just ensure default settings exist
    op.execute("""
        INSERT INTO expiration_settings (id, ticket_expiration_enabled, event_deactivation_enabled, updated_at)
        VALUES (1, true, true, NOW())
            ON CONFLICT (id) DO NOTHING
    """)


def downgrade():
    """Drop expiration_settings table."""
    op.drop_table('expiration_settings')

