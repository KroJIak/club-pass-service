"""Create admin_messages and admin_message_photos tables

Revision ID: 014
Revises: 013
Create Date: 2024-12-28 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '014'
down_revision = '013'
branch_labels = None
depends_on = None


def upgrade():
    """Create admin_messages and admin_message_photos tables."""
    # Create admin_messages table
    op.create_table(
        'admin_messages',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('message', sa.String(), nullable=True),
        sa.Column('sent_by', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_admin_messages_id'), 'admin_messages', ['id'], unique=False)
    op.create_index(op.f('ix_admin_messages_user_id'), 'admin_messages', ['user_id'], unique=False)
    op.create_index(op.f('ix_admin_messages_sent_by'), 'admin_messages', ['sent_by'], unique=False)
    op.create_index('ix_admin_messages_created_at', 'admin_messages', ['created_at'], unique=False)
    
    # Create admin_message_photos table
    op.create_table(
        'admin_message_photos',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('admin_message_id', sa.Integer(), nullable=False),
        sa.Column('file_path', sa.String(), nullable=False),
        sa.Column('file_name', sa.String(), nullable=False),
        sa.Column('file_size', sa.Integer(), nullable=False),
        sa.Column('mime_type', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['admin_message_id'], ['admin_messages.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_admin_message_photos_id'), 'admin_message_photos', ['id'], unique=False)
    op.create_index(op.f('ix_admin_message_photos_admin_message_id'), 'admin_message_photos', ['admin_message_id'], unique=False)


def downgrade():
    """Remove admin_messages and admin_message_photos tables."""
    op.drop_index(op.f('ix_admin_message_photos_admin_message_id'), table_name='admin_message_photos')
    op.drop_index(op.f('ix_admin_message_photos_id'), table_name='admin_message_photos')
    op.drop_table('admin_message_photos')
    
    op.drop_index('ix_admin_messages_created_at', table_name='admin_messages')
    op.drop_index(op.f('ix_admin_messages_sent_by'), table_name='admin_messages')
    op.drop_index(op.f('ix_admin_messages_user_id'), table_name='admin_messages')
    op.drop_index(op.f('ix_admin_messages_id'), table_name='admin_messages')
    op.drop_table('admin_messages')

