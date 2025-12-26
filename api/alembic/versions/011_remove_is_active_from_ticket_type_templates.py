"""Remove is_active column from ticket_type_templates

Revision ID: 011
Revises: 010
Create Date: 2024-12-26 19:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '011'
down_revision = '010'
branch_labels = None
depends_on = None


def upgrade():
    """Remove is_active column from ticket_type_templates."""
    op.drop_column('ticket_type_templates', 'is_active')


def downgrade():
    """Add is_active column back to ticket_type_templates."""
    op.add_column('ticket_type_templates', sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'))

