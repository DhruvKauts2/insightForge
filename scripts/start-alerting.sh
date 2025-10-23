#!/bin/bash
echo "🚨 Starting Alert Engine..."
python -m alerting.engine --interval 60 > logs/alerting.log 2>&1 &
echo $! > .alerting.pid
echo "✅ Alert Engine started (PID: $(cat .alerting.pid))"
echo "📁 Logs: logs/alerting.log"
echo ""
echo "To stop: ./scripts/stop-alerting.sh"
