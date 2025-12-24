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
    # Note: PostgreSQL requires new enum values to be committed in a separate transaction
    # before they can be used. We need to execute this outside of Alembic's transaction.
    # Create a separate connection with autocommit for the enum addition
    from sqlalchemy import create_engine
    from api.core.config import settings
    
    # Create a separate connection with autocommit for the enum addition
    db_url = (
        f"postgresql://{settings.DB_USER}:{settings.DB_PASSWORD}"
        f"@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"
    )
    engine = create_engine(db_url, isolation_level="AUTOCOMMIT")
    with engine.connect() as autocommit_conn:
        autocommit_conn.execute(sa.text("ALTER TYPE ticketstatus ADD VALUE IF NOT EXISTS 'USED'"))
    engine.dispose()
    
    # Now we can use the new enum value
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

