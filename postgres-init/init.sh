#!/bin/bash
set -e

echo "Creating logflow user and database..."

psql -v ON_ERROR_STOP=1 --username "postgres" --dbname "postgres" <<-EOSQL
    CREATE USER logflow WITH PASSWORD 'logflow123' CREATEDB;
    CREATE DATABASE logflow OWNER logflow;
    GRANT ALL PRIVILEGES ON DATABASE logflow TO logflow;
EOSQL

echo "User and database created successfully"
