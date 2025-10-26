#!/bin/bash
echo "🌊 Testing WebSocket Streaming"
echo ""

API_URL="http://localhost:8000"
WS_URL="ws://localhost:8000"

# Test 1: Check WebSocket stats endpoint
echo "1️⃣  Checking WebSocket stats..."
curl -s "$API_URL/ws/stats" | python3 -m json.tool
echo ""

# Test 2: Test with websocat (if available)
if command -v websocat &> /dev/null; then
    echo "2️⃣  Testing WebSocket connection (10 seconds)..."
    timeout 10 websocat "$WS_URL/ws/logs" &
    WS_PID=$!
    sleep 2
    
    if ps -p $WS_PID > /dev/null; then
        echo "   ✅ WebSocket connection established"
        kill $WS_PID 2>/dev/null
    else
        echo "   ❌ WebSocket connection failed"
    fi
else
    echo "2️⃣  Skipping WebSocket test (websocat not installed)"
    echo "   Install with: brew install websocat"
fi

echo ""
echo "3️⃣  Testing with Python..."

python3 << 'PYTHON'
import asyncio
import websockets
import json

async def test_websocket():
    uri = "ws://localhost:8000/ws/logs"
    
    try:
        async with websockets.connect(uri) as websocket:
            print("   ✅ Connected to WebSocket")
            
            # Receive connection message
            message = await asyncio.wait_for(websocket.recv(), timeout=5.0)
            data = json.loads(message)
            print(f"   📨 Received: {data.get('message')}")
            
            # Receive a few log messages
            for i in range(3):
                try:
                    message = await asyncio.wait_for(websocket.recv(), timeout=2.0)
                    data = json.loads(message)
                    if data.get('type') == 'log':
                        log = data.get('data', {})
                        print(f"   📝 Log: [{log.get('level')}] {log.get('service')} - {log.get('message', '')[:50]}")
                except asyncio.TimeoutError:
                    print("   ⏱️  No more messages (timeout)")
                    break
            
            print("   ✅ WebSocket test successful!")
            
    except Exception as e:
        print(f"   ❌ WebSocket test failed: {e}")

asyncio.run(test_websocket())
PYTHON

echo ""
echo "✅ WebSocket tests complete!"
echo ""
echo "Available WebSocket endpoints:"
echo "  - ws://localhost:8000/ws/logs      - Real-time log stream"
echo "  - ws://localhost:8000/ws/metrics   - Live metrics updates"
echo "  - ws://localhost:8000/ws/alerts    - Alert notifications"
echo ""
echo "Test manually:"
echo "  websocat ws://localhost:8000/ws/logs"
echo "  websocat 'ws://localhost:8000/ws/logs?service=payment-service&level=ERROR'"
