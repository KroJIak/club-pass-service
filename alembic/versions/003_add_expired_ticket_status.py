"""Add EXPIRED status to tickets

Revision ID: 003_add_expired_status
Revises: 002_change_telegram_user_id
Create Date: 2024-12-23 23:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '003_add_expired_status'
down_revision = '002_change_telegram_user_id'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add EXPIRED value to ticket_status enum
    # Note: PostgreSQL requires creating a new enum type and altering the column
    op.execute("ALTER TYPE ticketstatus ADD VALUE IF NOT EXISTS 'expired'")


def downgrade() -> None:
    # Note: PostgreSQL doesn't support removing enum values easily
    # This would require recreating the enum type
    # For now, we'll leave it as is
    pass

