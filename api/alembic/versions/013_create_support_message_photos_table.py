"""Create support_message_photos table

Revision ID: 013
Revises: 012
Create Date: 2024-12-27 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '013'
down_revision = '012'
branch_labels = None
depends_on = None


def upgrade():
    """Create support_message_photos table."""
    op.create_table(
        'support_message_photos',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('support_message_id', sa.Integer(), nullable=False),
        sa.Column('file_path', sa.String(), nullable=False),
        sa.Column('file_name', sa.String(), nullable=False),
        sa.Column('file_size', sa.Integer(), nullable=False),
        sa.Column('mime_type', sa.String(), nullable=False),
        sa.Column('is_admin_photo', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['support_message_id'], ['support_messages.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_support_message_photos_id'), 'support_message_photos', ['id'], unique=False)
    op.create_index(op.f('ix_support_message_photos_support_message_id'), 'support_message_photos', ['support_message_id'], unique=False)
    op.create_index(op.f('ix_support_message_photos_is_admin_photo'), 'support_message_photos', ['is_admin_photo'], unique=False)


def downgrade():
    """Remove support_message_photos table."""
    op.drop_index(op.f('ix_support_message_photos_is_admin_photo'), table_name='support_message_photos')
    op.drop_index(op.f('ix_support_message_photos_support_message_id'), table_name='support_message_photos')
    op.drop_index(op.f('ix_support_message_photos_id'), table_name='support_message_photos')
    op.drop_table('support_message_photos')


