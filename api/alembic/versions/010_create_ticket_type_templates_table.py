"""Create ticket_type_templates table and remove is_template from ticket_types

Revision ID: 010
Revises: 009
Create Date: 2024-12-26 16:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '010'
down_revision = '009'
branch_labels = None
depends_on = None


def upgrade():
    """Create ticket_type_templates table and remove is_template from ticket_types."""
    # Create ticket_type_templates table
    op.create_table(
        'ticket_type_templates',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('price', sa.Numeric(10, 2), nullable=False),
        sa.Column('available_quantity', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('total_quantity', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_ticket_type_templates_id'), 'ticket_type_templates', ['id'], unique=False)
    
    # Remove is_template column from ticket_types
    op.drop_column('ticket_types', 'is_template')
    
    # Make event_id not nullable again (since templates are now separate)
    op.alter_column('ticket_types', 'event_id',
                    existing_type=sa.Integer(),
                    nullable=False)


def downgrade():
    """Remove ticket_type_templates table and restore is_template to ticket_types."""
    # Drop ticket_type_templates table
    op.drop_index(op.f('ix_ticket_type_templates_id'), table_name='ticket_type_templates')
    op.drop_table('ticket_type_templates')
    
    # Add is_template column back to ticket_types
    op.add_column('ticket_types', sa.Column('is_template', sa.Boolean(), nullable=False, server_default='false'))
    
    # Make event_id nullable again
    op.alter_column('ticket_types', 'event_id',
                    existing_type=sa.Integer(),
                    nullable=True)

