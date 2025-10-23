#!/bin/bash
echo "📊 LogFlow Pipeline Status"
echo "=========================="
echo ""

echo "🔧 Processes:"
if [ -f .log-generator.pid ]; then
    echo "  ✅ Generator running (PID: $(cat .log-generator.pid))"
else
    echo "  ❌ Generator not running"
fi

if [ -f .shipper.pid ]; then
    echo "  ✅ Shipper running (PID: $(cat .shipper.pid))"
else
    echo "  ❌ Shipper not running"
fi

if [ -f .processor.pid ]; then
    echo "  ✅ Processor running (PID: $(cat .processor.pid))"
else
    echo "  ❌ Processor not running"
fi

echo ""
echo "📈 Elasticsearch Indices:"
curl -s http://localhost:9200/_cat/indices/logs-* 2>/dev/null || echo "  No indices found"

echo ""
echo "📊 Total Logs:"
curl -s http://localhost:9200/logs-*/_count?pretty 2>/dev/null | grep count || echo "  Unable to count"

echo ""
