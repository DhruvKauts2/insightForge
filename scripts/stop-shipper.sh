#!/bin/bash
if [ -f .shipper.pid ]; then
    PID=$(cat .shipper.pid)
    kill $PID 2>/dev/null
    rm .shipper.pid
    echo "✅ Shipper stopped"
else
    echo "⚠️  No shipper running"
fi
