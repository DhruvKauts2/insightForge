-- This runs after PostgreSQL starts
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_user WHERE usename = 'logflow') THEN
        CREATE USER logflow WITH PASSWORD 'logflow123' SUPERUSER CREATEDB;
    END IF;
END
$$;

CREATE DATABASE IF NOT EXISTS logflow OWNER logflow;
ALTER DATABASE logflow OWNER TO logflow;
