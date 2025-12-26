"""Create support_messages table

Revision ID: 012
Revises: 011
Create Date: 2024-12-26 20:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = '012'
down_revision = '011'
branch_labels = None
depends_on = None


def upgrade():
    """Create support_messages table."""
    # Create enum type for status
    op.execute("CREATE TYPE supportmessagestatus AS ENUM ('new', 'responded', 'closed')")
    
    op.create_table(
        'support_messages',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('message', sa.String(), nullable=False),
        sa.Column('status', postgresql.ENUM('new', 'responded', 'closed', name='supportmessagestatus', create_type=False), nullable=False, server_default='new'),
        sa.Column('admin_response', sa.String(), nullable=True),
        sa.Column('responded_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('responded_by', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_support_messages_id'), 'support_messages', ['id'], unique=False)
    op.create_index(op.f('ix_support_messages_user_id'), 'support_messages', ['user_id'], unique=False)
    op.create_index(op.f('ix_support_messages_status'), 'support_messages', ['status'], unique=False)
    op.create_index('ix_support_messages_created_at', 'support_messages', ['created_at'], unique=False)


def downgrade():
    """Remove support_messages table."""
    op.drop_index('ix_support_messages_created_at', table_name='support_messages')
    op.drop_index(op.f('ix_support_messages_status'), table_name='support_messages')
    op.drop_index(op.f('ix_support_messages_user_id'), table_name='support_messages')
    op.drop_index(op.f('ix_support_messages_id'), table_name='support_messages')
    op.drop_table('support_messages')
    op.execute("DROP TYPE supportmessagestatus")

