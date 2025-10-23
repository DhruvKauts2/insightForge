#!/bin/bash
if [ -f .log-generator.pid ]; then
    PID=$(cat .log-generator.pid)
    kill $PID 2>/dev/null
    rm .log-generator.pid
    echo "✅ Log generator stopped"
else
    echo "⚠️  No log generator running"
fi
