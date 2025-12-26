#!/bin/bash
# Script to apply migration 009 manually

echo "Applying migration 009: Add is_template to ticket_types..."

# Get database credentials from environment or use defaults
DB_USER=${DB_USER:-postgres}
DB_PASSWORD=${DB_PASSWORD:-postgres}
DB_NAME=${DB_NAME:-club_pass}
DB_HOST=${DB_HOST:-db}
DB_PORT=${DB_PORT:-5432}

# Apply migration via SQL
docker compose exec -T db psql -U "$DB_USER" -d "$DB_NAME" <<EOF
-- Make event_id nullable
ALTER TABLE ticket_types ALTER COLUMN event_id DROP NOT NULL;

-- Add is_template column
ALTER TABLE ticket_types ADD COLUMN IF NOT EXISTS is_template BOOLEAN NOT NULL DEFAULT false;

-- Verify migration
SELECT column_name, data_type, is_nullable, column_default 
FROM information_schema.columns 
WHERE table_name = 'ticket_types' AND column_name = 'is_template';
EOF

echo "Migration applied successfully!"

