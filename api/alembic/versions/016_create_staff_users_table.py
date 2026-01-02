"""Create staff_users table

Revision ID: 016
Revises: 015
Create Date: 2025-01-03 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '016'
down_revision = '015'
branch_labels = None
depends_on = None


def upgrade():
    """Create staff_users table."""
    op.create_table(
        'staff_users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('telegram_user_id', sa.BigInteger(), nullable=False),
        sa.Column('first_name', sa.String(), nullable=True),
        sa.Column('last_name', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('telegram_user_id')
    )
    op.create_index(op.f('ix_staff_users_id'), 'staff_users', ['id'], unique=False)
    op.create_index(op.f('ix_staff_users_telegram_user_id'), 'staff_users', ['telegram_user_id'], unique=True)
    op.create_index('idx_staff_users_telegram_user_id', 'staff_users', ['telegram_user_id'], unique=False)


def downgrade():
    """Remove staff_users table."""
    op.drop_index('idx_staff_users_telegram_user_id', table_name='staff_users')
    op.drop_index(op.f('ix_staff_users_telegram_user_id'), table_name='staff_users')
    op.drop_index(op.f('ix_staff_users_id'), table_name='staff_users')
    op.drop_table('staff_users')

