"""Add is_template column to ticket_types and make event_id nullable

Revision ID: 009
Revises: 008
Create Date: 2024-12-26 15:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '009'
down_revision = '008'
branch_labels = None
depends_on = None


def upgrade():
    """Add is_template column and make event_id nullable for templates."""
    # First, make event_id nullable
    op.alter_column('ticket_types', 'event_id',
                    existing_type=sa.Integer(),
                    nullable=True)
    
    # Add is_template column
    op.add_column('ticket_types', sa.Column('is_template', sa.Boolean(), nullable=False, server_default='false'))


def downgrade():
    """Remove is_template column and make event_id not nullable."""
    # Remove is_template column
    op.drop_column('ticket_types', 'is_template')
    
    # Make event_id not nullable (this might fail if there are NULL values)
    op.alter_column('ticket_types', 'event_id',
                    existing_type=sa.Integer(),
                    nullable=False)

