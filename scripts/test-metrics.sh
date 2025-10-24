#!/bin/bash
echo "📊 Testing Prometheus Metrics"
echo ""

API_URL="http://localhost:8000"

# Test 1: Check metrics endpoint exists
echo "1️⃣  Checking metrics endpoint..."
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "$API_URL/metrics")
if [ "$HTTP_CODE" = "200" ]; then
    echo "   ✅ Metrics endpoint accessible"
else
    echo "   ❌ Metrics endpoint returned HTTP $HTTP_CODE"
    exit 1
fi

# Test 2: Generate some traffic
echo ""
echo "2️⃣  Generating traffic for metrics..."
for i in {1..10}; do
    curl -s "$API_URL/" > /dev/null
    curl -s "$API_URL/health" > /dev/null
    curl -s "$API_URL/api/v1/metrics/overview" > /dev/null
done
echo "   ✅ Generated 30 requests"

# Test 3: Check metrics content
echo ""
echo "3️⃣  Checking metrics content..."
METRICS=$(curl -s "$API_URL/metrics")

# Check for HTTP metrics
if echo "$METRICS" | grep -q "http_requests_total"; then
    echo "   ✅ HTTP request counter found"
else
    echo "   ⚠️  HTTP request counter not found"
fi

# Check for duration metrics
if echo "$METRICS" | grep -q "http_request_duration_seconds"; then
    echo "   ✅ HTTP duration histogram found"
else
    echo "   ⚠️  HTTP duration histogram not found"
fi

# Check for Elasticsearch metrics
if echo "$METRICS" | grep -q "elasticsearch_queries_total"; then
    echo "   ✅ Elasticsearch metrics found"
else
    echo "   ⚠️  Elasticsearch metrics not found"
fi

# Test 4: Show sample metrics
echo ""
echo "4️⃣  Sample metrics:"
echo "$METRICS" | grep -E "http_requests_total|http_request_duration_seconds_count" | head -5

echo ""
echo "✅ Metrics test complete!"
echo ""
echo "View metrics at: $API_URL/metrics"
