"""Create superadmin_settings table

Revision ID: 026
Revises: 025
Create Date: 2025-01-07 21:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '026'
down_revision = '025'
branch_labels = None
depends_on = None


def upgrade():
    """Create superadmin_settings table."""
    op.create_table(
        'superadmin_settings',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('username', sa.String(), nullable=False),
        sa.Column('language', sa.String(2), nullable=False, server_default='ru'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_superadmin_settings_id'), 'superadmin_settings', ['id'], unique=False)
    op.create_index(op.f('ix_superadmin_settings_username'), 'superadmin_settings', ['username'], unique=True)


def downgrade():
    """Drop superadmin_settings table."""
    op.drop_index(op.f('ix_superadmin_settings_username'), table_name='superadmin_settings')
    op.drop_index(op.f('ix_superadmin_settings_id'), table_name='superadmin_settings')
    op.drop_table('superadmin_settings')

