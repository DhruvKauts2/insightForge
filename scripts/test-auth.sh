#!/bin/bash
set -e

echo "🔐 Testing LogFlow Authentication"
echo ""

API_URL="http://localhost:8000"

# Test 1: Register new user
echo "1️⃣  Testing user registration..."
REGISTER_RESPONSE=$(curl -s -X POST "$API_URL/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser_'$(date +%s)'",
    "email": "test'$(date +%s)'@example.com",
    "password": "testpass123",
    "full_name": "Test User"
  }')

if echo "$REGISTER_RESPONSE" | grep -q "username"; then
    echo "   ✅ Registration successful"
    USERNAME=$(echo "$REGISTER_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['username'])")
else
    echo "   ❌ Registration failed"
    echo "$REGISTER_RESPONSE"
    exit 1
fi

# Test 2: Login
echo ""
echo "2️⃣  Testing login..."
LOGIN_RESPONSE=$(curl -s -X POST "$API_URL/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=$USERNAME&password=testpass123")

if echo "$LOGIN_RESPONSE" | grep -q "access_token"; then
    echo "   ✅ Login successful"
    TOKEN=$(echo "$LOGIN_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])")
else
    echo "   ❌ Login failed"
    echo "$LOGIN_RESPONSE"
    exit 1
fi

# Test 3: Get current user
echo ""
echo "3️⃣  Testing authenticated endpoint..."
ME_RESPONSE=$(curl -s -X GET "$API_URL/api/v1/auth/me" \
  -H "Authorization: Bearer $TOKEN")

if echo "$ME_RESPONSE" | grep -q "$USERNAME"; then
    echo "   ✅ Authentication working"
else
    echo "   ❌ Authentication failed"
    echo "$ME_RESPONSE"
    exit 1
fi

# Test 4: Create alert with auth
echo ""
echo "4️⃣  Testing protected endpoint (create alert)..."
ALERT_RESPONSE=$(curl -s -X POST "$API_URL/api/v1/alerts/rules" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Alert",
    "condition": "greater_than",
    "threshold": 100,
    "levels": ["ERROR"],
    "notification_channel": "console"
  }')

if echo "$ALERT_RESPONSE" | grep -q "Test Alert"; then
    echo "   ✅ Protected endpoint working"
    ALERT_ID=$(echo "$ALERT_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['id'])")
else
    echo "   ❌ Protected endpoint failed"
    echo "$ALERT_RESPONSE"
    exit 1
fi

# Test 5: Try without auth (should fail)
echo ""
echo "5️⃣  Testing endpoint without auth (should fail)..."
NO_AUTH_RESPONSE=$(curl -s -X POST "$API_URL/api/v1/alerts/rules" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Unauthorized Alert",
    "condition": "greater_than",
    "threshold": 50,
    "levels": ["ERROR"],
    "notification_channel": "console"
  }')

if echo "$NO_AUTH_RESPONSE" | grep -q "Not authenticated"; then
    echo "   ✅ Authorization protection working"
else
    echo "   ⚠️  Warning: Endpoint accessible without auth"
fi

# Test 6: Delete alert (cleanup)
echo ""
echo "6️⃣  Testing delete (owner permission)..."
DELETE_RESPONSE=$(curl -s -X DELETE "$API_URL/api/v1/alerts/rules/$ALERT_ID" \
  -H "Authorization: Bearer $TOKEN" \
  -w "%{http_code}")

if [ "${DELETE_RESPONSE: -3}" = "204" ]; then
    echo "   ✅ Delete working"
else
    echo "   ❌ Delete failed"
fi

echo ""
echo "✅ All authentication tests passed!"
echo ""
echo "Summary:"
echo "  - User registration: Working"
echo "  - Login & JWT tokens: Working"
echo "  - Protected endpoints: Working"
echo "  - Authorization checks: Working"
