#!/bin/bash

echo "🤖 Complete Anomaly Detection Test"
echo "=================================="
echo ""

API_URL="http://localhost:8000"

# Test 1: Log Volume Anomalies
echo "1️⃣  Testing Log Volume Anomaly Detection (60min window)..."
RESPONSE=$(curl -s "$API_URL/api/v1/anomaly/detect/log-volume?window_minutes=60")
COUNT=$(echo "$RESPONSE" | python3 -c "import sys,json; print(len(json.load(sys.stdin)))")

if [ "$COUNT" -gt 0 ]; then
    echo "   ✅ Detected $COUNT log volume anomalies"
    echo "$RESPONSE" | python3 -c "
import sys, json
anomalies = json.load(sys.stdin)
for a in anomalies[:3]:
    print(f\"      - {a['severity'].upper()}: {a['actual_value']:.0f} logs (expected {a['expected_value']:.0f}, {a['deviation_percent']:.1f}% deviation)\")
"
else
    echo "   ℹ️  No anomalies detected (data might be too old)"
fi

echo ""

# Test 2: Error Rate Anomalies
echo "2️⃣  Testing Error Rate Anomaly Detection (60min window)..."
ERROR_RESPONSE=$(curl -s "$API_URL/api/v1/anomaly/detect/error-rate?window_minutes=60")
ERROR_COUNT=$(echo "$ERROR_RESPONSE" | python3 -c "import sys,json; print(len(json.load(sys.stdin)))")

if [ "$ERROR_COUNT" -gt 0 ]; then
    echo "   ✅ Detected $ERROR_COUNT error rate anomalies"
else
    echo "   ℹ️  No error rate anomalies detected"
fi

echo ""

# Test 3: Full Report
echo "3️⃣  Getting Full Anomaly Report..."
curl -s "$API_URL/api/v1/anomaly/report?window_minutes=60" | python3 -c "
import sys, json
report = json.load(sys.stdin)
print(f\"   Period: {report['period_start'][:16]} to {report['period_end'][11:16]}\")
print(f\"   Total anomalies: {report['total_anomalies']}\")
if report['anomalies_by_severity']:
    print(f\"   By severity: {report['anomalies_by_severity']}\")
if report['anomalies_by_service']:
    print(f\"   By service: {report['anomalies_by_service']}\")
"

echo ""

# Test 4: Data Statistics
echo "4️⃣  Current Data Statistics..."
LOG_COUNT=$(curl -s "http://localhost:9200/logs/_count" -H 'Content-Type: application/json' -d '{"query": {"range": {"timestamp": {"gte": "now-60m"}}}}' | python3 -c "import sys,json; print(json.load(sys.stdin)['count'])")
echo "   Total logs (60min): $LOG_COUNT"

curl -s "http://localhost:9200/logs/_search" -H 'Content-Type: application/json' -d '{
  "query": {"range": {"timestamp": {"gte": "now-60m"}}},
  "size": 0,
  "aggs": {
    "per_minute": {"date_histogram": {"field": "timestamp", "fixed_interval": "1m"}},
    "by_level": {"terms": {"field": "level", "size": 10}}
  }
}' | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    buckets = data.get('aggregations', {}).get('per_minute', {}).get('buckets', [])
    levels = data.get('aggregations', {}).get('by_level', {}).get('buckets', [])
    
    if buckets:
        counts = [b['doc_count'] for b in buckets if b['doc_count'] > 0]
        if counts:
            print(f'   Logs per minute: min={min(counts)}, max={max(counts)}, avg={sum(counts)//len(counts)}')
            
    if levels:
        level_str = ', '.join([f'{l[\"key\"]}: {l[\"doc_count\"]}' for l in levels])
        print(f'   By level: {level_str}')
except Exception as e:
    print(f'   Could not parse stats: {e}')
" 2>/dev/null

echo ""
echo "✅ Anomaly Detection Test Complete!"
echo ""
echo "Available endpoints:"
echo "  GET /api/v1/anomaly/detect/log-volume?window_minutes=60"
echo "  GET /api/v1/anomaly/detect/error-rate?window_minutes=60"
echo "  GET /api/v1/anomaly/report?window_minutes=60"
