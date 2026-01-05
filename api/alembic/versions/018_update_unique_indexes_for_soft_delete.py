"""Update unique indexes for soft delete support

Revision ID: 018
Revises: 017
Create Date: 2025-01-03 12:30:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '018'
down_revision = '017'
branch_labels = None
depends_on = None


def upgrade():
    """Update unique indexes to support soft delete using partial indexes."""
    # Drop existing unique constraints and indexes
    # Note: SQLAlchemy creates unique constraints which may have different names
    # We'll drop constraints first, then recreate as partial indexes
    
    # For users.telegram_user_id
    try:
        op.drop_constraint('users_telegram_user_id_key', 'users', type_='unique')
    except Exception:
        pass
    try:
        op.drop_index('ix_users_telegram_user_id', table_name='users')
    except Exception:
        pass
    
    # For staff_users.telegram_user_id
    try:
        op.drop_constraint('staff_users_telegram_user_id_key', 'staff_users', type_='unique')
    except Exception:
        pass
    try:
        op.drop_index('ix_staff_users_telegram_user_id', table_name='staff_users')
    except Exception:
        pass
    
    # For tickets.token
    try:
        op.drop_constraint('tickets_token_key', 'tickets', type_='unique')
    except Exception:
        pass
    try:
        op.drop_index('ix_tickets_token', table_name='tickets')
    except Exception:
        pass
    
    # For orders.order_id
    try:
        op.drop_constraint('orders_order_id_key', 'orders', type_='unique')
    except Exception:
        pass
    try:
        op.drop_index('ix_orders_order_id', table_name='orders')
    except Exception:
        pass
    
    # For payments.yookassa_payment_id
    try:
        op.drop_constraint('payments_yookassa_payment_id_key', 'payments', type_='unique')
    except Exception:
        pass
    try:
        op.drop_index('ix_payments_yookassa_payment_id', table_name='payments')
    except Exception:
        pass
    
    # Create partial unique indexes (only for non-deleted records)
    # PostgreSQL partial indexes using WHERE clause
    op.execute("""
        CREATE UNIQUE INDEX ix_users_telegram_user_id_active 
        ON users(telegram_user_id) 
        WHERE is_deleted = FALSE
    """)
    
    op.execute("""
        CREATE UNIQUE INDEX ix_staff_users_telegram_user_id_active 
        ON staff_users(telegram_user_id) 
        WHERE is_deleted = FALSE
    """)
    
    op.execute("""
        CREATE UNIQUE INDEX ix_tickets_token_active 
        ON tickets(token) 
        WHERE is_deleted = FALSE
    """)
    
    op.execute("""
        CREATE UNIQUE INDEX ix_orders_order_id_active 
        ON orders(order_id) 
        WHERE is_deleted = FALSE
    """)
    
    # For payments, yookassa_payment_id is nullable, so we need to handle NULLs
    op.execute("""
        CREATE UNIQUE INDEX ix_payments_yookassa_payment_id_active 
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

