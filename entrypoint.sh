#!/bin/bash
set -e

echo "Starting container..."

# Wait for database to be ready
echo "Waiting for database to be ready..."
until pg_isready -h "$DB_HOST" -p 5432 -U "$POSTGRES_USER"; do
  echo "Database not ready yet, waiting..."
  sleep 2
done

echo "Database is ready!"

# Run migrations
echo "Running Alembic migrations..."
alembic upgrade head

echo "Migrations completed!"

# Start the application
echo "Starting FastAPI application..."
exec "$@" 