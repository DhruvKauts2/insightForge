#!/bin/bash
if [ -f .api.pid ]; then
    PID=$(cat .api.pid)
    kill $PID 2>/dev/null
    rm .api.pid
    echo "✅ API stopped"
else
    echo "⚠️  No API running"
fi
