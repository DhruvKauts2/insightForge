#!/bin/bash
echo "🚀 Starting log generator in background..."
python shipper/generate_logs.py --rate 5 --burst-interval 30 > /dev/null 2>&1 &
echo $! > .log-generator.pid
echo "✅ Log generator started (PID: $(cat .log-generator.pid))"
echo "📁 Logs writing to: sample_logs/app.log"
echo ""
echo "To stop: ./scripts/stop-logs.sh"
