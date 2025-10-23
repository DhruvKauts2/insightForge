#!/bin/bash
set -e

echo "🚀 Starting LogFlow (Full Docker Deployment)"
echo ""

# Stop any running containers
echo "1. Stopping existing containers..."
docker compose down

# Start infrastructure
echo "2. Starting infrastructure (Kafka, ES, PostgreSQL, Redis)..."
docker compose up -d zookeeper kafka elasticsearch postgres redis

# Wait for services
echo "3. Waiting for services to be ready..."
sleep 30

# Initialize database
echo "4. Initializing database..."
./scripts/init-db-docker.sh

# Build and start API and alerting
echo "5. Building and starting API and alerting engine..."
docker compose up -d --build api alerting

# Wait for API
echo "6. Waiting for API to be ready..."
sleep 10

# Check health
echo "7. Checking service health..."
curl -s http://localhost:8000/health | python3 -m json.tool

echo ""
echo "✅ LogFlow is running!"
echo ""
echo "📊 Services:"
echo "  - API:           http://localhost:8000"
echo "  - API Docs:      http://localhost:8000/docs"
echo "  - Elasticsearch: http://localhost:9200"
echo "  - Kibana:        http://localhost:5601"
echo ""
echo "🔍 Check logs:"
echo "  docker compose logs -f api"
echo "  docker compose logs -f alerting"
echo ""
echo "🛑 Stop all:"
echo "  docker compose down"
