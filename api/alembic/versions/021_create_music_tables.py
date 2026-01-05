"""Create music_requests, music_queue, and music_request_limits tables

Revision ID: 021
Revises: 020
Create Date: 2025-01-05 19:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '021'
down_revision = '020'
branch_labels = None
depends_on = None


def upgrade():
    """Create music_requests, music_queue, and music_request_limits tables."""
    # Create music_requests table (wishlist)
    op.create_table(
        'music_requests',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('event_id', sa.Integer(), nullable=False),
        sa.Column('track_title', sa.String(), nullable=False),
        sa.Column('track_artist', sa.String(), nullable=False),
        sa.Column('yandex_music_url', sa.String(), nullable=True),
        sa.Column('other_source_url', sa.String(), nullable=True),
        sa.Column('request_count', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['event_id'], ['events.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_music_requests_id'), 'music_requests', ['id'], unique=False)
    op.create_index(op.f('ix_music_requests_user_id'), 'music_requests', ['user_id'], unique=False)
    op.create_index(op.f('ix_music_requests_event_id'), 'music_requests', ['event_id'], unique=False)
    op.create_index(op.f('ix_music_requests_request_count'), 'music_requests', ['request_count'], unique=False)
    op.create_index(op.f('ix_music_requests_is_deleted'), 'music_requests', ['is_deleted'], unique=False)
    
    # Create music_queue table
    op.create_table(
        'music_queue',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('track_title', sa.String(), nullable=False),
        sa.Column('track_artist', sa.String(), nullable=False),
        sa.Column('yandex_music_url', sa.String(), nullable=True),
        sa.Column('other_source_url', sa.String(), nullable=True),
        sa.Column('queue_order', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_music_queue_id'), 'music_queue', ['id'], unique=False)
    op.create_index(op.f('ix_music_queue_queue_order'), 'music_queue', ['queue_order'], unique=False)
    op.create_index(op.f('ix_music_queue_is_deleted'), 'music_queue', ['is_deleted'], unique=False)
    
    # Create music_request_limits table
    op.create_table(
        'music_request_limits',
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('event_id', sa.Integer(), nullable=False),
        sa.Column('last_request_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['event_id'], ['events.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('user_id', 'event_id')
    )
    op.create_index(op.f('ix_music_request_limits_user_id'), 'music_request_limits', ['user_id'], unique=False)
    op.create_index(op.f('ix_music_request_limits_event_id'), 'music_request_limits', ['event_id'], unique=False)


def downgrade():
    """Remove music_requests, music_queue, and music_request_limits tables."""
    op.drop_index(op.f('ix_music_request_limits_event_id'), table_name='music_request_limits')
    op.drop_index(op.f('ix_music_request_limits_user_id'), table_name='music_request_limits')
    op.drop_table('music_request_limits')
    
    op.drop_index(op.f('ix_music_queue_is_deleted'), table_name='music_queue')
    op.drop_index(op.f('ix_music_queue_queue_order'), table_name='music_queue')
    op.drop_index(op.f('ix_music_queue_id'), table_name='music_queue')
    op.drop_table('music_queue')
    
    op.drop_index(op.f('ix_music_requests_is_deleted'), table_name='music_requests')
    op.drop_index(op.f('ix_music_requests_request_count'), table_name='music_requests')
    op.drop_index(op.f('ix_music_requests_event_id'), table_name='music_requests')
    op.drop_index(op.f('ix_music_requests_user_id'), table_name='music_requests')
    op.drop_index(op.f('ix_music_requests_id'), table_name='music_requests')
    op.drop_table('music_requests')

