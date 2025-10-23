#!/bin/bash
echo "⚠️  This will delete all data! Press Ctrl+C to cancel..."
sleep 5
echo "🗑️  Stopping and removing all containers and volumes..."
docker compose down -v
echo "✅ All data cleared. Run ./scripts/start.sh to start fresh."
