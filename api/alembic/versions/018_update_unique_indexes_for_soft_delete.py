"""Update unique indexes for soft delete support

Revision ID: 018
Revises: 017
Create Date: 2025-01-03 12:30:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import text


# revision identifiers, used by Alembic.
revision = '018'
down_revision = '017'
branch_labels = None
depends_on = None


def upgrade():
    """Update unique indexes to support soft delete using partial indexes."""
    # Use raw SQL with IF EXISTS to avoid transaction errors
    # Drop existing unique constraints and indexes
    conn = op.get_bind()
    
    # Drop constraints and indexes using IF EXISTS
    drop_statements = [
        "ALTER TABLE users DROP CONSTRAINT IF EXISTS users_telegram_user_id_key",
        "DROP INDEX IF EXISTS ix_users_telegram_user_id",
        "ALTER TABLE staff_users DROP CONSTRAINT IF EXISTS staff_users_telegram_user_id_key",
        "DROP INDEX IF EXISTS ix_staff_users_telegram_user_id",
        "ALTER TABLE tickets DROP CONSTRAINT IF EXISTS tickets_token_key",
        "DROP INDEX IF EXISTS ix_tickets_token",
        "ALTER TABLE orders DROP CONSTRAINT IF EXISTS orders_order_id_key",
        "DROP INDEX IF EXISTS ix_orders_order_id",
        "ALTER TABLE payments DROP CONSTRAINT IF EXISTS payments_yookassa_payment_id_key",
        "DROP INDEX IF EXISTS ix_payments_yookassa_payment_id",
    ]
    
    for stmt in drop_statements:
        conn.execute(text(stmt))
    
    # Create partial unique indexes (only for non-deleted records)
    # PostgreSQL partial indexes using WHERE clause
    op.execute("""
        CREATE UNIQUE INDEX IF NOT EXISTS ix_users_telegram_user_id_active 
        ON users(telegram_user_id) 
        WHERE is_deleted = FALSE
    """)
    
    op.execute("""
        CREATE UNIQUE INDEX IF NOT EXISTS ix_staff_users_telegram_user_id_active 
        ON staff_users(telegram_user_id) 
        WHERE is_deleted = FALSE
    """)
    
    op.execute("""
        CREATE UNIQUE INDEX IF NOT EXISTS ix_tickets_token_active 
        ON tickets(token) 
        WHERE is_deleted = FALSE
    """)
    
    op.execute("""
        CREATE UNIQUE INDEX IF NOT EXISTS ix_orders_order_id_active 
        ON orders(order_id) 
        WHERE is_deleted = FALSE
    """)
    
    # For payments, yookassa_payment_id is nullable, so we need to handle NULLs
    op.execute("""
        CREATE UNIQUE INDEX IF NOT EXISTS ix_payments_yookassa_payment_id_active 
        ON payments(yookassa_payment_id) 
        WHERE is_deleted = FALSE AND yookassa_payment_id IS NOT NULL
    """)


def downgrade():
    """Revert unique indexes to original state."""
    # Drop partial indexes
    op.execute("DROP INDEX IF EXISTS ix_users_telegram_user_id_active")
    op.execute("DROP INDEX IF EXISTS ix_staff_users_telegram_user_id_active")
    op.execute("DROP INDEX IF EXISTS ix_tickets_token_active")
    op.execute("DROP INDEX IF EXISTS ix_orders_order_id_active")
    op.execute("DROP INDEX IF EXISTS ix_payments_yookassa_payment_id_active")
    
    # Recreate original unique constraints/indexes
    op.create_index('ix_users_telegram_user_id', 'users', ['telegram_user_id'], unique=True)
    op.create_index('ix_staff_users_telegram_user_id', 'staff_users', ['telegram_user_id'], unique=True)
    op.create_index('ix_tickets_token', 'tickets', ['token'], unique=True)
    op.create_index('ix_orders_order_id', 'orders', ['order_id'], unique=True)
    op.create_index('ix_payments_yookassa_payment_id', 'payments', ['yookassa_payment_id'], unique=True)

