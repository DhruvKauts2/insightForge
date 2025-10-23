#!/bin/bash

# Automated test script
echo "Running pipeline tests..."
echo ""

PASSED=0
FAILED=0

# Test 1: Infrastructure running
echo -n "Test 1: Docker services running... "
if docker compose ps | grep -q "Up"; then
    echo "✓ PASSED"
    ((PASSED++))
else
    echo "✗ FAILED"
    ((FAILED++))
fi

# Test 2: Elasticsearch responding
echo -n "Test 2: Elasticsearch responding... "
if curl -s http://localhost:9200 > /dev/null; then
    echo "✓ PASSED"
    ((PASSED++))
else
    echo "✗ FAILED"
    ((FAILED++))
fi

# Test 3: Kafka topic exists
echo -n "Test 3: Kafka topic exists... "
if docker compose exec -T kafka kafka-topics --list --bootstrap-server localhost:9092 2>/dev/null | grep -q "logs-raw"; then
    echo "✓ PASSED"
    ((PASSED++))
else
    echo "✗ FAILED"
    ((FAILED++))
fi

# Test 4: Logs in Elasticsearch
echo -n "Test 4: Logs indexed in Elasticsearch... "
COUNT=$(curl -s 'http://localhost:9200/logs-*/_count' 2>/dev/null | grep -o '"count":[0-9]*' | cut -d: -f2)
if [ "$COUNT" -gt 0 ] 2>/dev/null; then
    echo "✓ PASSED ($COUNT logs)"
    ((PASSED++))
else
    echo "✗ FAILED (0 logs)"
    ((FAILED++))
fi

# Test 5: All components have PIDs
echo -n "Test 5: Pipeline components running... "
RUNNING=0
[ -f .log-generator.pid ] && ((RUNNING++))
[ -f .shipper.pid ] && ((RUNNING++))
[ -f .processor.pid ] && ((RUNNING++))

if [ $RUNNING -eq 3 ]; then
    echo "✓ PASSED (3/3 components)"
    ((PASSED++))
else
    echo "✗ FAILED ($RUNNING/3 components)"
    ((FAILED++))
fi

echo ""
echo "========================"
echo "Test Results: $PASSED passed, $FAILED failed"
echo "========================"

if [ $FAILED -eq 0 ]; then
    echo "✓ All tests passed!"
    exit 0
else
    echo "✗ Some tests failed"
    exit 1
fi
