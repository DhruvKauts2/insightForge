#!/bin/bash

case "$1" in
    init)
        echo "Initializing database..."
        cat scripts/init-schema.sql | docker compose exec -T postgres psql -U logflow -d logflow
        echo "✅ Database initialized"
        ;;
    reset)
        echo "⚠️  This will DELETE ALL DATA!"
        read -p "Are you sure? (yes/no): " confirm
        if [ "$confirm" = "yes" ]; then
            echo "Dropping all tables..."
            docker compose exec -T postgres psql -U logflow -d logflow << 'EOSQL'
DROP TABLE IF EXISTS triggered_alerts CASCADE;
DROP TABLE IF EXISTS alert_rules CASCADE;
DROP TABLE IF EXISTS users CASCADE;
DROP TABLE IF EXISTS system_config CASCADE;
EOSQL
            echo "Recreating tables..."
            cat scripts/init-schema.sql | docker compose exec -T postgres psql -U logflow -d logflow
            echo "✅ Database reset complete"
        else
            echo "Cancelled"
        fi
        ;;
    shell)
        echo "Opening PostgreSQL shell..."
        docker compose exec postgres psql -U logflow -d logflow
        ;;
    backup)
        BACKUP_FILE="backups/logflow-$(date +%Y%m%d-%H%M%S).sql"
        mkdir -p backups
        echo "Creating backup: $BACKUP_FILE"
        docker compose exec -T postgres pg_dump -U logflow logflow > "$BACKUP_FILE"
        echo "✅ Backup created: $BACKUP_FILE"
        ;;
    *)
        echo "Usage: $0 {init|reset|shell|backup}"
        echo ""
        echo "Commands:"
        echo "  init   - Initialize database with tables and seed data"
        echo "  reset  - Drop and recreate all tables (DELETES ALL DATA)"
        echo "  shell  - Open PostgreSQL shell"
        echo "  backup - Create database backup"
        exit 1
        ;;
esac
