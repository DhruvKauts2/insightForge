#!/bin/bash
echo "🚀 Starting LogFlow infrastructure..."
docker compose up -d
echo "⏳ Waiting for services to be healthy..."
sleep 10
docker compose ps
echo "✅ Infrastructure is up!"
echo ""
echo "📍 Service URLs:"
echo "   Elasticsearch: http://localhost:9200"
echo "   Kibana: http://localhost:5601"
echo "   PostgreSQL: localhost:5432"
echo "   Kafka: localhost:9092"
echo "   Redis: localhost:6379"
