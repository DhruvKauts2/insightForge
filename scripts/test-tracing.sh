#!/bin/bash
echo "🔍 Testing Request Tracing"
echo ""

API_URL="http://localhost:8000"

# Test 1: Make request and check for trace headers
echo "1️⃣  Testing trace headers..."
RESPONSE=$(curl -s -i "$API_URL/")

REQUEST_ID=$(echo "$RESPONSE" | grep -i "x-request-id" | cut -d' ' -f2 | tr -d '\r')
CORRELATION_ID=$(echo "$RESPONSE" | grep -i "x-correlation-id" | cut -d' ' -f2 | tr -d '\r')

if [ -n "$REQUEST_ID" ]; then
    echo "   ✅ Request ID: $REQUEST_ID"
else
    echo "   ❌ No Request ID found"
fi

if [ -n "$CORRELATION_ID" ]; then
    echo "   ✅ Correlation ID: $CORRELATION_ID"
else
    echo "   ❌ No Correlation ID found"
fi

# Test 2: Get trace context
echo ""
echo "2️⃣  Getting trace context..."
curl -s "$API_URL/api/v1/trace/context" | python3 -m json.tool

# Test 3: Test with custom correlation ID
echo ""
echo "3️⃣  Testing custom correlation ID..."
CUSTOM_CORR_ID="test-correlation-$(date +%s)"
RESPONSE=$(curl -s -i -H "X-Correlation-ID: $CUSTOM_CORR_ID" "$API_URL/")
RETURNED_CORR_ID=$(echo "$RESPONSE" | grep -i "x-correlation-id" | cut -d' ' -f2 | tr -d '\r')

if [ "$RETURNED_CORR_ID" = "$CUSTOM_CORR_ID" ]; then
    echo "   ✅ Custom correlation ID preserved: $CUSTOM_CORR_ID"
else
    echo "   ❌ Correlation ID mismatch"
fi

# Test 4: Test health with tracing
echo ""
echo "4️⃣  Testing traced health endpoint..."
curl -s "$API_URL/api/v1/trace/health-traced" | python3 -m json.tool

# Test 5: Multiple requests with same correlation ID
echo ""
echo "5️⃣  Testing request chain with correlation ID..."
CHAIN_ID="chain-$(date +%s)"
echo "   Making 3 requests with correlation ID: $CHAIN_ID"

for i in {1..3}; do
    RESP=$(curl -s -H "X-Correlation-ID: $CHAIN_ID" "$API_URL/api/v1/trace/context")
    REQ_ID=$(echo "$RESP" | python3 -c "import sys, json; print(json.load(sys.stdin)['request_id'])")
    echo "   Request $i - Request ID: $REQ_ID"
done

echo ""
echo "✅ Request tracing tests complete!"
echo ""
echo "Features tested:"
echo "  - Request ID generation"
echo "  - Correlation ID propagation"
echo "  - Custom correlation ID support"
echo "  - Trace context retrieval"
echo "  - Request chaining"
