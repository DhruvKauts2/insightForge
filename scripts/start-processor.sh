#!/bin/bash
echo "⚙️  Starting log processor..."
python processor/processor.py > logs/processor.log 2>&1 &
echo $! > .processor.pid
echo "✅ Processor started (PID: $(cat .processor.pid))"
echo "📁 Logs: logs/processor.log"
echo ""
echo "To stop: ./scripts/stop-processor.sh"
