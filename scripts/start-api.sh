#!/bin/bash
echo "🚀 Starting LogFlow API..."
python api/main.py > logs/api.log 2>&1 &
echo $! > .api.pid
echo "✅ API started (PID: $(cat .api.pid))"
echo "📁 Logs: logs/api.log"
echo "📖 API docs: http://localhost:8000/docs"
echo ""
echo "To stop: ./scripts/stop-api.sh"
