"""Add soft delete fields to all tables

Revision ID: 017
Revises: 016
Create Date: 2025-01-03 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime


# revision identifiers, used by Alembic.
revision = '017'
down_revision = '016'
branch_labels = None
depends_on = None


def upgrade():
    """Add is_deleted and deleted_at columns to all tables."""
    tables = [
        'users',
        'events',
        'ticket_types',
        'ticket_type_templates',
        'tickets',
        'orders',
        'payments',
        'support_messages',
        'admin_messages',
        'staff_users',
        'support_message_photos',
        'admin_message_photos',
    ]
    
    for table_name in tables:
        # Add is_deleted column
        op.add_column(
            table_name,
            sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='false')
        )
        # Add deleted_at column
        op.add_column(
            table_name,
            sa.Column('deleted_at', sa.DateTime(), nullable=True)
        )
        # Create index on is_deleted for performance
        op.create_index(
            f'ix_{table_name}_is_deleted',
            table_name,
            ['is_deleted'],
            unique=False
        )


def downgrade():
    """Remove is_deleted and deleted_at columns from all tables."""
    tables = [
        'users',
        'events',
        'ticket_types',
        'ticket_type_templates',
        'tickets',
        'orders',
        'payments',
        'support_messages',
        'admin_messages',
        'staff_users',
        'support_message_photos',
        'admin_message_photos',
    ]
    
    for table_name in tables:
        # Drop index
        op.drop_index(f'ix_{table_name}_is_deleted', table_name=table_name)
        # Drop columns
        op.drop_column(table_name, 'deleted_at')
        op.drop_column(table_name, 'is_deleted')

