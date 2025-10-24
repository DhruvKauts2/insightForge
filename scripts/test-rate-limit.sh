#!/bin/bash
echo "🚦 Testing Rate Limiting"
echo ""

API_URL="http://localhost:8000"

# Test 1: Normal requests (within limit)
echo "1️⃣  Making 5 requests (should succeed):"
for i in {1..5}; do
    RESPONSE=$(curl -s -w "\nHTTP Code: %{http_code}" "$API_URL/" 2>&1)
    HTTP_CODE=$(echo "$RESPONSE" | grep "HTTP Code" | cut -d' ' -f3)
    
    # Extract rate limit headers
    HEADERS=$(curl -s -I "$API_URL/" 2>&1)
    LIMIT=$(echo "$HEADERS" | grep -i "x-ratelimit-limit" | cut -d' ' -f2 | tr -d '\r')
    REMAINING=$(echo "$HEADERS" | grep -i "x-ratelimit-remaining" | cut -d' ' -f2 | tr -d '\r')
    
    if [ "$HTTP_CODE" = "200" ]; then
        echo "   ✅ Request $i: OK (Remaining: $REMAINING/$LIMIT)"
    else
        echo "   ❌ Request $i: Failed (HTTP $HTTP_CODE)"
    fi
    sleep 0.5
done
echo ""

# Test 2: Rapid requests (test rate limiting)
echo "2️⃣  Making 70 rapid requests (should hit limit at 60):"
SUCCESS=0
RATE_LIMITED=0

for i in {1..70}; do
    HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "$API_URL/")
    
    if [ "$HTTP_CODE" = "200" ]; then
        ((SUCCESS++))
    elif [ "$HTTP_CODE" = "429" ]; then
        ((RATE_LIMITED++))
    fi
done

echo "   ✅ Successful: $SUCCESS"
echo "   🚫 Rate Limited: $RATE_LIMITED"
echo ""

# Test 3: Check rate limit headers
echo "3️⃣  Checking rate limit headers:"
curl -I "$API_URL/" 2>&1 | grep -i "x-ratelimit"
echo ""

# Test 4: Test specific endpoint limits
echo "4️⃣  Testing search endpoint (50/minute limit):"
for i in {1..3}; do
    HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "$API_URL/api/v1/logs/recent?limit=10")
    echo "   Request $i: HTTP $HTTP_CODE"
done
echo ""

echo "✅ Rate limit tests complete!"
echo ""
echo "Summary:"
echo "  - Default limit: 60 requests/minute"
echo "  - Search limit: 50 requests/minute"
echo "  - Auth endpoints: 10-20 requests/hour"
echo "  - Rate limits enforced: $([ $RATE_LIMITED -gt 0 ] && echo 'Yes ✅' || echo 'No ❌')"
