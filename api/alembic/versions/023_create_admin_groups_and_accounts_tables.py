"""Create admin_groups, admin_accounts, and admin_permissions tables

Revision ID: 023
Revises: 022
Create Date: 2025-01-07 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '023'
down_revision = '022'
branch_labels = None
depends_on = None


def upgrade():
    """Create admin_groups, admin_accounts, and admin_permissions tables."""
    # Create admin_groups table
    op.create_table(
        'admin_groups',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_admin_groups_id'), 'admin_groups', ['id'], unique=False)
    op.create_index(op.f('ix_admin_groups_name'), 'admin_groups', ['name'], unique=True)
    op.create_index(op.f('ix_admin_groups_is_deleted'), 'admin_groups', ['is_deleted'], unique=False)
    
    # Create admin_accounts table
    op.create_table(
        'admin_accounts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('group_id', sa.Integer(), nullable=False),
        sa.Column('username', sa.String(), nullable=False),
        sa.Column('password_hash', sa.String(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['group_id'], ['admin_groups.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_admin_accounts_id'), 'admin_accounts', ['id'], unique=False)
    op.create_index(op.f('ix_admin_accounts_username'), 'admin_accounts', ['username'], unique=True)
    op.create_index(op.f('ix_admin_accounts_group_id'), 'admin_accounts', ['group_id'], unique=False)
    op.create_index(op.f('ix_admin_accounts_is_deleted'), 'admin_accounts', ['is_deleted'], unique=False)
    
    # Create admin_permissions table
    op.create_table(
        'admin_permissions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('group_id', sa.Integer(), nullable=False),
        sa.Column('resource', sa.String(), nullable=False),
        sa.Column('can_read', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('can_write', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('can_delete', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['group_id'], ['admin_groups.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('group_id', 'resource', name='uq_admin_permissions_group_resource')
    )
    op.create_index(op.f('ix_admin_permissions_id'), 'admin_permissions', ['id'], unique=False)
    op.create_index(op.f('ix_admin_permissions_group_id'), 'admin_permissions', ['group_id'], unique=False)
    op.create_index(op.f('ix_admin_permissions_resource'), 'admin_permissions', ['resource'], unique=False)


def downgrade():
    """Remove admin_groups, admin_accounts, and admin_permissions tables."""
    op.drop_index(op.f('ix_admin_permissions_resource'), table_name='admin_permissions')
    op.drop_index(op.f('ix_admin_permissions_group_id'), table_name='admin_permissions')
    op.drop_index(op.f('ix_admin_permissions_id'), table_name='admin_permissions')
    op.drop_table('admin_permissions')
    
    op.drop_index(op.f('ix_admin_accounts_is_deleted'), table_name='admin_accounts')
    op.drop_index(op.f('ix_admin_accounts_group_id'), table_name='admin_accounts')
    op.drop_index(op.f('ix_admin_accounts_username'), table_name='admin_accounts')
    op.drop_index(op.f('ix_admin_accounts_id'), table_name='admin_accounts')
    op.drop_table('admin_accounts')
    
    op.drop_index(op.f('ix_admin_groups_is_deleted'), table_name='admin_groups')
    op.drop_index(op.f('ix_admin_groups_name'), table_name='admin_groups')
    op.drop_index(op.f('ix_admin_groups_id'), table_name='admin_groups')
    op.drop_table('admin_groups')

