#!/bin/bash
echo "📊 LogFlow Infrastructure Status"
echo "================================"
docker compose ps
echo ""
echo "🔍 Quick Health Checks:"
echo -n "Elasticsearch: "
curl -s http://localhost:9200/_cluster/health | grep -o '"status":"[^"]*"' || echo "❌ Not responding"
echo ""
echo -n "Redis: "
docker compose exec -T redis redis-cli ping 2>/dev/null || echo "❌ Not responding"
echo -n "PostgreSQL: "
docker compose exec -T postgres pg_isready -U logflow 2>/dev/null || echo "❌ Not responding"
