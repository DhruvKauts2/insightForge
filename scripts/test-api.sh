#!/bin/bash

echo "🧪 Testing LogFlow API..."
echo ""

API_URL="http://localhost:8000"

# Test 1: Health check
echo "Test 1: Health check"
curl -s "$API_URL/health" | python3 -m json.tool
echo ""

# Test 2: Root endpoint
echo "Test 2: Root endpoint"
curl -s "$API_URL/" | python3 -m json.tool
echo ""

# Test 3: Recent logs
echo "Test 3: Recent logs (5)"
curl -s "$API_URL/api/v1/logs/recent?limit=5" | python3 -c "
import sys, json
data = json.load(sys.stdin)
print(f'Total: {data[\"total\"]}')
print(f'Returned: {len(data[\"logs\"])}')
for log in data['logs'][:3]:
    print(f'  [{log[\"timestamp\"]}] {log[\"level\"]} - {log[\"message\"][:50]}')
"
echo ""

# Test 4: Search ERROR logs
echo "Test 4: Search ERROR logs"
curl -s -X POST "$API_URL/api/v1/logs/search" \
  -H "Content-Type: application/json" \
  -d '{"levels": ["ERROR"], "limit": 3}' | python3 -c "
import sys, json
data = json.load(sys.stdin)
print(f'Total errors: {data[\"total\"]}')
print(f'Query time: {data[\"query_time_ms\"]:.2f}ms')
if 'aggregations' in data and data['aggregations']:
    print('Aggregations:', data['aggregations'])
"
echo ""

# Test 5: Full-text search
echo "Test 5: Full-text search for 'timeout'"
curl -s -X POST "$API_URL/api/v1/logs/search" \
  -H "Content-Type: application/json" \
  -d '{"query": "timeout", "limit": 3}' | python3 -c "
import sys, json
data = json.load(sys.stdin)
print(f'Matches: {data[\"total\"]}')
for log in data['logs']:
    print(f'  [{log[\"level\"]}] {log[\"message\"]}')
"
echo ""

echo "✅ API tests complete!"
