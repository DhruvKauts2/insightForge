#!/bin/bash

echo "=========================================="
echo "   LogFlow - Complete Pipeline Demo"
echo "=========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}Step 1: Checking infrastructure...${NC}"
docker compose ps | grep -E "logflow-kafka|logflow-elasticsearch|logflow-postgres|logflow-redis"
echo ""

echo -e "${BLUE}Step 2: Cleaning up old data...${NC}"
./scripts/stop-pipeline.sh 2>/dev/null
rm -f sample_logs/app.log
rm -f .*.pid
curl -X DELETE "http://localhost:9200/logs-*" 2>/dev/null
echo -e "${GREEN}✓ Cleaned up${NC}"
echo ""

echo -e "${BLUE}Step 3: Starting log generator...${NC}"
./scripts/generate-logs.sh
sleep 2
echo -e "${GREEN}✓ Generator started${NC}"
echo ""

echo -e "${BLUE}Step 4: Starting shipper...${NC}"
./scripts/start-shipper.sh
sleep 2
echo -e "${GREEN}✓ Shipper started${NC}"
echo ""

echo -e "${BLUE}Step 5: Starting processor...${NC}"
./scripts/start-processor.sh
sleep 3
echo -e "${GREEN}✓ Processor started${NC}"
echo ""

echo -e "${YELLOW}Waiting 30 seconds for data to flow through pipeline...${NC}"
for i in {30..1}; do
    echo -ne "\rTime remaining: $i seconds... "
    sleep 1
done
echo ""
echo ""

echo -e "${BLUE}Step 6: Checking results...${NC}"
echo ""

# Check Kafka
echo -e "${BLUE}📊 Kafka Topic Messages:${NC}"
KAFKA_COUNT=$(docker compose exec -T kafka kafka-run-class kafka.tools.GetOffsetShell \
  --broker-list localhost:9092 \
  --topic logs-raw 2>/dev/null | awk -F: '{sum += $2} END {print sum}')
echo "  Messages in Kafka: $KAFKA_COUNT"
echo ""

# Check Elasticsearch
echo -e "${BLUE}📊 Elasticsearch Indices:${NC}"
curl -s 'http://localhost:9200/_cat/indices?v' | grep logs
echo ""

echo -e "${BLUE}📊 Total Logs in Elasticsearch:${NC}"
ES_COUNT=$(curl -s 'http://localhost:9200/logs-*/_count' | grep -o '"count":[0-9]*' | cut -d: -f2)
echo "  Total logs indexed: $ES_COUNT"
echo ""

# Sample logs
echo -e "${BLUE}📋 Sample Logs (last 3):${NC}"
curl -s -X GET "http://localhost:9200/logs-*/_search" -H 'Content-Type: application/json' -d'
{
  "query": { "match_all": {} },
  "size": 3,
  "sort": [{"timestamp": "desc"}]
}
' | python3 -c "
import sys, json
data = json.load(sys.stdin)
for hit in data['hits']['hits']:
    src = hit['_source']
    print(f\"  [{src['timestamp']}] {src['level']} [{src['service']}] {src['message']}\")
" 2>/dev/null || echo "  (Install python3 to see formatted logs)"
echo ""

# Log level distribution
echo -e "${BLUE}📊 Log Level Distribution:${NC}"
curl -s -X GET "http://localhost:9200/logs-*/_search" -H 'Content-Type: application/json' -d'
{
  "size": 0,
  "aggs": {
    "by_level": {
      "terms": { "field": "level" }
    }
  }
}
' | python3 -c "
import sys, json
data = json.load(sys.stdin)
for bucket in data['aggregations']['by_level']['buckets']:
    print(f\"  {bucket['key']}: {bucket['doc_count']}\")
" 2>/dev/null || echo "  (Install python3 to see distribution)"
echo ""

echo -e "${GREEN}=========================================="
echo "   ✓ Pipeline Demo Complete!"
echo "==========================================${NC}"
echo ""
echo "Next steps:"
echo "  • Open Kibana: http://localhost:5601"
echo "  • View logs in Discover with data view: logs-*"
echo "  • Stop pipeline: ./scripts/stop-pipeline.sh"
echo ""

