-- Migration 009: Add is_template column to ticket_types and make event_id nullable
-- This can be run manually if Alembic migration fails

-- First, make event_id nullable
ALTER TABLE ticket_types ALTER COLUMN event_id DROP NOT NULL;

-- Add is_template column with default value
ALTER TABLE ticket_types ADD COLUMN IF NOT EXISTS is_template BOOLEAN NOT NULL DEFAULT false;

