"""Add end_date and end_time to events table

Revision ID: 006
Revises: 005
Create Date: 2024-12-26 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '006'
down_revision = '005'
branch_labels = None
depends_on = None


def upgrade():
    """Add end_date and end_time columns to events table."""
    # Add columns as nullable first
    op.add_column(
        'events',
        sa.Column('end_date', sa.String(), nullable=True)
    )
    op.add_column(
        'events',
        sa.Column('end_time', sa.String(), nullable=True)
    )
    
    # Fill existing events with default values (copy from date and time)
    op.execute("""
        UPDATE events 
        SET end_date = date, end_time = time 
        WHERE end_date IS NULL OR end_time IS NULL
    """)
    
    # Make columns non-nullable
    op.alter_column('events', 'end_date', nullable=False)
    op.alter_column('events', 'end_time', nullable=False)


def downgrade():
    """Remove end_date and end_time columns from events table."""
    op.drop_column('events', 'end_time')
    op.drop_column('events', 'end_date')

