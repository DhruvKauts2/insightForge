#!/bin/bash
echo "🛑 Stopping LogFlow Pipeline..."
./scripts/stop-processor.sh
./scripts/stop-shipper.sh
./scripts/stop-logs.sh
echo "✅ Pipeline stopped"
