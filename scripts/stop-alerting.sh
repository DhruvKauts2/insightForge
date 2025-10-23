#!/bin/bash
if [ -f .alerting.pid ]; then
    PID=$(cat .alerting.pid)
    kill $PID 2>/dev/null
    rm .alerting.pid
    echo "✅ Alert Engine stopped"
else
    echo "⚠️  No Alert Engine running"
fi
