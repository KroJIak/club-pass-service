"""Create menu_photos table

Revision ID: 019
Revises: 018
Create Date: 2025-01-03 13:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '019'
down_revision = '018'
branch_labels = None
depends_on = None


def upgrade():
    """Create menu_photos table."""
    op.create_table(
        'menu_photos',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('file_path', sa.String(), nullable=False),
        sa.Column('file_name', sa.String(), nullable=False),
        sa.Column('file_size', sa.Integer(), nullable=False),
        sa.Column('mime_type', sa.String(), nullable=False),
        sa.Column('display_order', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_menu_photos_id'), 'menu_photos', ['id'], unique=False)
    op.create_index(op.f('ix_menu_photos_display_order'), 'menu_photos', ['display_order'], unique=False)
    op.create_index(op.f('ix_menu_photos_is_deleted'), 'menu_photos', ['is_deleted'], unique=False)


def downgrade():
    """Remove menu_photos table."""
    op.drop_index(op.f('ix_menu_photos_is_deleted'), table_name='menu_photos')
    op.drop_index(op.f('ix_menu_photos_display_order'), table_name='menu_photos')
    op.drop_index(op.f('ix_menu_photos_id'), table_name='menu_photos')
    op.drop_table('menu_photos')

