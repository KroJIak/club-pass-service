"""Rename date and time columns to start_date and start_time

Revision ID: 007
Revises: 006
Create Date: 2024-12-26 13:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '007'
down_revision = '006'
branch_labels = None
depends_on = None


def upgrade():
    """Rename date to start_date and time to start_time."""
    # Rename columns
    op.alter_column('events', 'date', new_column_name='start_date')
    op.alter_column('events', 'time', new_column_name='start_time')
    
    # Update end_date and end_time for existing events if they were set to start values
    # This ensures end_date/end_time are different from start_date/start_time
    op.execute("""
        UPDATE events 
        SET end_date = start_date, end_time = start_time 
        WHERE end_date IS NULL OR end_time IS NULL
    """)


def downgrade():
    """Rename start_date back to date and start_time back to time."""
    op.alter_column('events', 'start_date', new_column_name='date')
    op.alter_column('events', 'start_time', new_column_name='time')

