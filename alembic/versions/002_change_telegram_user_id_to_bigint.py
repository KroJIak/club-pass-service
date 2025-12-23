"""Change telegram_user_id to BigInteger

Revision ID: 002_change_telegram_user_id
Revises: 001_initial
Create Date: 2024-12-23 22:30:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '002_change_telegram_user_id'
down_revision = '001_initial'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Change telegram_user_id from Integer to BigInteger
    op.alter_column('users', 'telegram_user_id',
                    existing_type=sa.Integer(),
                    type_=sa.BigInteger(),
                    existing_nullable=False)


def downgrade() -> None:
    # Revert telegram_user_id back to Integer
    op.alter_column('users', 'telegram_user_id',
                    existing_type=sa.BigInteger(),
                    type_=sa.Integer(),
                    existing_nullable=False)

