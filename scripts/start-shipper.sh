#!/bin/bash
echo "📤 Starting log shipper..."
python shipper/shipper.py --log-file sample_logs/app.log > logs/shipper.log 2>&1 &
echo $! > .shipper.pid
echo "✅ Shipper started (PID: $(cat .shipper.pid))"
echo "📁 Logs: logs/shipper.log"
echo ""
echo "To stop: ./scripts/stop-shipper.sh"
