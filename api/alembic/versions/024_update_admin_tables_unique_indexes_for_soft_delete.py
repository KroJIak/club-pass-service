"""Update unique indexes for admin_groups and admin_accounts to support soft delete

Revision ID: 024
Revises: 023
Create Date: 2025-01-07 13:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import text


# revision identifiers, used by Alembic.
revision = '024'
down_revision = '023'
branch_labels = None
depends_on = None


def upgrade():
    """Update unique indexes to support soft delete using partial indexes."""
    conn = op.get_bind()
    
    # Drop existing unique constraints and indexes
    drop_statements = [
        "DROP INDEX IF EXISTS ix_admin_groups_name",
        "DROP INDEX IF EXISTS ix_admin_accounts_username",
    ]
    
    for stmt in drop_statements:
        conn.execute(text(stmt))
    
    # Create partial unique indexes (only for non-deleted records)
    op.execute("""
        CREATE UNIQUE INDEX IF NOT EXISTS ix_admin_groups_name_active 
        ON admin_groups(name) 
        WHERE is_deleted = FALSE
    """)
    
    op.execute("""
        CREATE UNIQUE INDEX IF NOT EXISTS ix_admin_accounts_username_active 
        ON admin_accounts(username) 
        WHERE is_deleted = FALSE
    """)


def downgrade():
    """Revert unique indexes to original state."""
    # Drop partial indexes
    op.execute("DROP INDEX IF EXISTS ix_admin_groups_name_active")
    op.execute("DROP INDEX IF EXISTS ix_admin_accounts_username_active")
    
    # Recreate original unique indexes
    op.create_index('ix_admin_groups_name', 'admin_groups', ['name'], unique=True)
    op.create_index('ix_admin_accounts_username', 'admin_accounts', ['username'], unique=True)

