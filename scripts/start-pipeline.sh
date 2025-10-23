#!/bin/bash
echo "🚀 Starting LogFlow Pipeline..."
echo ""

echo "1. Starting log generator..."
./scripts/generate-logs.sh
sleep 2

echo "2. Starting shipper..."
./scripts/start-shipper.sh
sleep 2

echo "3. Starting processor..."
./scripts/start-processor.sh
sleep 3

echo ""
echo "✅ Pipeline started!"
echo ""
echo "📊 Check status:"
echo "   Shipper:   tail -f logs/shipper.log"
echo "   Processor: tail -f logs/processor.log"
echo ""
echo "🔍 Search logs:"
echo "   curl http://localhost:9200/logs-*/_count"
echo "   open http://localhost:5601 (Kibana)"
echo ""
echo "🛑 Stop pipeline: ./scripts/stop-pipeline.sh"
