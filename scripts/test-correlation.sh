#!/bin/bash
echo "🔗 Testing Log Correlation"
echo ""

API_URL="http://localhost:8000"

# Test 1: Get service dependencies
echo "1️⃣  Getting service dependencies..."
curl -s "$API_URL/api/v1/correlation/dependencies?time_window=24" | python3 -m json.tool
echo ""

# Test 2: Find correlation IDs for a service
echo "2️⃣  Finding correlation IDs for payment-service..."
RESPONSE=$(curl -s "$API_URL/api/v1/correlation/service/payment-service/traces?limit=5")
echo "$RESPONSE" | python3 -m json.tool

# Extract first correlation ID
CORRELATION_ID=$(echo "$RESPONSE" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data['correlation_ids'][0] if data['correlation_ids'] else '')" 2>/dev/null)

if [ -n "$CORRELATION_ID" ]; then
    echo ""
    echo "3️⃣  Tracing correlation ID: $CORRELATION_ID"
    curl -s "$API_URL/api/v1/correlation/trace/$CORRELATION_ID" | python3 -m json.tool
    echo ""
else
    echo "   ⚠️  No correlation IDs found"
fi

# Test 4: Search for a log and get related logs
echo ""
echo "4️⃣  Finding related logs..."
LOG_RESPONSE=$(curl -s "$API_URL/api/v1/logs/recent?limit=1")
LOG_ID=$(echo "$LOG_RESPONSE" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data['logs'][0]['id'] if data['logs'] else '')" 2>/dev/null)

if [ -n "$LOG_ID" ]; then
    echo "   Log ID: $LOG_ID"
    curl -s "$API_URL/api/v1/correlation/related/$LOG_ID?time_window=60" | python3 -m json.tool | head -30
else
    echo "   ⚠️  No logs found"
fi

echo ""
echo "✅ Log correlation tests complete!"
echo ""
echo "Available endpoints:"
echo "  GET /api/v1/correlation/trace/{correlation_id}     - Full request trace"
echo "  GET /api/v1/correlation/related/{log_id}           - Related logs"
echo "  GET /api/v1/correlation/dependencies               - Service dependency graph"
echo "  GET /api/v1/correlation/service/{name}/traces      - Service correlation IDs"
