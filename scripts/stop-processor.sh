#!/bin/bash
if [ -f .processor.pid ]; then
    PID=$(cat .processor.pid)
    kill $PID 2>/dev/null
    rm .processor.pid
    echo "✅ Processor stopped"
else
    echo "⚠️  No processor running"
fi
