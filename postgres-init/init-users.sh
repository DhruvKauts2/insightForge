#!/bin/sh
set -e

psql -v ON_ERROR_STOP=1 --username "postgres" <<-EOSQL
    CREATE USER logflow WITH PASSWORD 'logflow123' SUPERUSER;
    CREATE DATABASE logflow OWNER logflow;
EOSQL
