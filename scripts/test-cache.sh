#!/bin/bash
echo "🚀 Testing Redis Cache Performance"
echo ""

API_URL="http://localhost:8000"

# Test 1: Cache stats before
echo "1️⃣  Initial cache stats:"
curl -s "$API_URL/api/v1/cache/stats" | python3 -m json.tool
echo ""

# Test 2: First request (cache miss)
echo "2️⃣  First request (cache miss - should be slower):"
time curl -s "$API_URL/api/v1/metrics/overview" > /dev/null
echo ""

# Test 3: Second request (cache hit)
echo "3️⃣  Second request (cache hit - should be faster!):"
time curl -s "$API_URL/api/v1/metrics/overview" > /dev/null
echo ""

# Test 4: Multiple cached requests
echo "4️⃣  Making 10 cached requests..."
for i in {1..10}; do
    curl -s "$API_URL/api/v1/metrics/overview" > /dev/null
done
echo "   ✅ Done"
echo ""

# Test 5: Cache stats after
echo "5️⃣  Cache stats after requests:"
curl -s "$API_URL/api/v1/cache/stats" | python3 -m json.tool
echo ""

# Test 6: Service-specific caching
echo "6️⃣  Testing service-specific cache:"
time curl -s "$API_URL/api/v1/metrics/service/payment-service" > /dev/null
time curl -s "$API_URL/api/v1/metrics/service/payment-service" > /dev/null
echo ""

# Test 7: Check cache keys
echo "7️⃣  Current cache keys:"
docker compose exec redis redis-cli KEYS "metrics:*"
echo ""

echo "✅ Cache performance test complete!"
