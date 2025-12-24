"""Add USED status to tickets and remove is_used column

Revision ID: 004_add_used_status_remove_is_used
Revises: 003_add_expired_status
Create Date: 2024-12-24 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '004_add_used_status_remove_is_used'
down_revision = '003_add_expired_status'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add USED value to ticketstatus enum
    # Note: Initial migration created enum with uppercase values (ACTIVE, REFUNDED, CANCELLED)
    # The model uses lowercase, but TypeDecorator handles conversion
    # We'll add both uppercase and lowercase to be safe, or just uppercase to match existing
    op.execute("ALTER TYPE ticketstatus ADD VALUE IF NOT EXISTS 'USED'")
    
    # Update existing tickets: if is_used is True, set status to USED
    # Must use uppercase 'ACTIVE' to match the enum value from initial migration
    op.execute("""
        UPDATE tickets 
        SET status = 'USED'::ticketstatus
        WHERE is_used = true AND status = 'ACTIVE'::ticketstatus
    """)
    
    # Drop the is_used column
    op.drop_column('tickets', 'is_used')


def downgrade() -> None:
    # Add back the is_used column
    op.add_column('tickets', 
        sa.Column('is_used', sa.Boolean(), nullable=False, server_default='false')
    )
    
    # Update is_used based on status
    op.execute("""
        UPDATE tickets 
        SET is_used = true 
        WHERE status = 'used'
    """)
    
    # Note: PostgreSQL doesn't support removing enum values easily
    # The 'used' value will remain in the enum type
    pass

