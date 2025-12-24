#!/bin/bash
set -e

echo "Waiting for database to be ready..."
# Wait for database to be ready
until PGPASSWORD=$DB_PASSWORD psql -h "$DB_HOST" -U "$DB_USER" -d "$DB_NAME" -c '\q' 2>/dev/null; do
  >&2 echo "Database is unavailable - sleeping"
  sleep 1
done

echo "Database is ready. Running migrations..."
# Run migrations
alembic upgrade head

echo "Migrations completed. Starting API server..."
# Start the API server
exec uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload

