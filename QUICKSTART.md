# LogFlow - Quick Start Guide

Get the log aggregation pipeline running in 5 minutes!

## Prerequisites

- Docker Desktop running
- Python 3.11+
- 8GB RAM
- 10GB disk space

## 1. Clone and Setup (2 minutes)
```bash
# Clone repository
git clone <your-repo-url>
cd logflow

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## 2. Start Infrastructure (2 minutes)
```bash
# Start all Docker services
docker compose up -d

# Wait for services to be healthy (~60 seconds)
./scripts/status.sh
```

## 3. Run Complete Demo (1 minute)
```bash
# Run automated demo
./scripts/demo.sh
```

This will:
- Start log generator (creates realistic logs)
- Start shipper (sends logs to Kafka)
- Start processor (indexes to Elasticsearch)
- Show statistics and sample logs

## 4. View Logs in Kibana

1. Open http://localhost:5601
2. Go to Menu → Discover
3. Create data view: `logs-*` with timestamp field `timestamp`
4. Explore your logs!

## 5. Stop Everything
```bash
./scripts/stop-pipeline.sh
docker compose down
```

---

## Architecture
```
[Log Files] → [Shipper] → [Kafka] → [Processor] → [Elasticsearch] → [Kibana]
```

## Key Services

| Service | Port | Purpose |
|---------|------|---------|
| Kafka | 9092 | Message streaming |
| Elasticsearch | 9200 | Log storage & search |
| Kibana | 5601 | Visualization |
| PostgreSQL | 5432 | Metadata (future) |
| Redis | 6379 | Caching (future) |

## Manual Control
```bash
# Start components individually
./scripts/generate-logs.sh    # Generate sample logs
./scripts/start-shipper.sh    # Ship logs to Kafka
./scripts/start-processor.sh  # Process logs to Elasticsearch

# Stop components
./scripts/stop-logs.sh
./scripts/stop-shipper.sh
./scripts/stop-processor.sh

# Or stop all at once
./scripts/stop-pipeline.sh
```

## Troubleshooting

**Services not starting?**
```bash
docker compose ps
docker compose logs <service-name>
```

**Elasticsearch not responding?**
```bash
curl http://localhost:9200
# Wait 60 seconds for Elasticsearch to start
```

**No logs appearing?**
```bash
# Check each component
tail -f logs/shipper.log
tail -f logs/processor.log
tail -f sample_logs/app.log
```

## Next Steps

- Add alerting (Step 7-9)
- Build REST API (Step 10-12)
- Add authentication (Step 13)
- Deploy to Kubernetes (Step 19)

## Support

For issues, check the main README.md or component-specific documentation.
