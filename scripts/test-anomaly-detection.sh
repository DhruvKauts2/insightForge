#!/bin/bash
echo "🤖 Testing Anomaly Detection"
echo ""

API_URL="http://localhost:8000"

# Test 1: Check baseline data
echo "1️⃣  Checking baseline log volume..."
BASELINE=$(curl -s "http://localhost:9200/logs/_count" -H 'Content-Type: application/json' -d '{
  "query": {"range": {"timestamp": {"gte": "now-10m"}}}
}' | python3 -c "import sys,json; print(json.load(sys.stdin)['count'])")

echo "   Logs in last 10 minutes: $BASELINE"
echo ""

# Test 2: Generate anomaly spike
echo "2️⃣  Generating anomaly spike (100 logs/sec for 30 seconds)..."

python3 << 'PYTHON'
import sys, json, time
from kafka import KafkaProducer
from datetime import datetime

producer = KafkaProducer(
    bootstrap_servers='localhost:9092',
    value_serializer=lambda x: json.dumps(x).encode('utf-8')
)

# Generate spike - 100 logs per second for 30 seconds
for i in range(30):
    for _ in range(100):
        log = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": "INFO",
            "service": "test-service",
            "message": f"Anomaly test spike log {i}"
        }
        producer.send('logs-raw', value=log)
    if i % 10 == 0:
        print(f"   Generated {(i+1) * 100} logs...")
    time.sleep(1)

producer.close()
print("   ✅ Spike generated (3000 logs)")
PYTHON

echo ""
echo "3️⃣  Waiting 10 seconds for processing..."
sleep 10

# Test 3: Detect anomalies
echo ""
echo "4️⃣  Detecting log volume anomalies..."
curl -s "$API_URL/api/v1/anomaly/detect/log-volume?window_minutes=10" | python3 -m json.tool

echo ""
echo "5️⃣  Getting anomaly report..."
curl -s "$API_URL/api/v1/anomaly/report?window_minutes=10" | python3 -m json.tool | head -40

echo ""
echo "✅ Anomaly detection test complete!"
