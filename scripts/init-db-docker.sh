#!/bin/bash
echo "Waiting for PostgreSQL to be ready..."
sleep 10

echo "Initializing database..."
docker compose exec -T postgres psql -U logflow -d logflow < scripts/init-schema.sql

echo "✅ Database initialized!"
