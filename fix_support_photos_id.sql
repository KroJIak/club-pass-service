-- Fix support_message_photos.id to be auto-increment
-- First, create a sequence
CREATE SEQUENCE IF NOT EXISTS support_message_photos_id_seq;

-- Set the default value for id column to use the sequence
ALTER TABLE support_message_photos 
    ALTER COLUMN id SET DEFAULT nextval('support_message_photos_id_seq');

-- Set the sequence to start from the current max id + 1
SELECT setval('support_message_photos_id_seq', COALESCE((SELECT MAX(id) FROM support_message_photos), 0) + 1, false);

-- Make the sequence owned by the column (so it gets dropped if column is dropped)
ALTER SEQUENCE support_message_photos_id_seq OWNED BY support_message_photos.id;

