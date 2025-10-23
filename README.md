# LogFlow - Distributed Log Aggregation System

A real-time log aggregation, processing, and analysis platform built with modern backend technologies.

## 🎯 Features

- **Real-time Log Ingestion**: Collect logs from multiple sources
- **Stream Processing**: Process logs with Kafka for scalability
- **Full-Text Search**: Search logs instantly with Elasticsearch
- **Smart Alerting**: Configure threshold-based alerts
- **REST API**: Query and manage logs programmatically
- **Monitoring**: Built-in metrics with Prometheus

## 🏗️ Architecture
```
[Log Sources] → [Shipper] → [Kafka] → [Processor] → [Elasticsearch]
                                                            ↓
                                                       [Query API]
                                                            ↓
                                                    [Alerting Engine]
```

## 🛠️ Tech Stack

- **Languages**: Python 3.11+
- **Message Queue**: Apache Kafka
- **Search Engine**: Elasticsearch
- **API Framework**: FastAPI
- **Database**: PostgreSQL
- **Cache**: Redis
- **Containerization**: Docker, Docker Compose
- **Orchestration**: Kubernetes (optional)

## 📋 Prerequisites

- Python 3.11+
- Docker & Docker Compose
- 8GB RAM minimum
- 20GB disk space

## 🚀 Quick Start

### 1. Clone and Setup
```bash
git clone <your-repo>
cd logflow
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Start Infrastructure
```bash
docker-compose up -d
```

### 3. Verify Services

- Elasticsearch: http://localhost:9200
- Kibana: http://localhost:5601
- API Docs: http://localhost:8000/docs

### 4. Run Components
```bash
# Terminal 1: Start API
python api/main.py

# Terminal 2: Start Processor
python processor/processor.py

# Terminal 3: Start Shipper
python shipper/shipper.py
```

## 📁 Project Structure
```
logflow/
├── shipper/          # Log collection agents
├── processor/        # Stream processing
├── api/              # REST API
├── alerting/         # Alert engine
├── tests/            # Test suite
├── docs/             # Documentation
└── docker-compose.yml
```

## 🧪 Testing
```bash
pytest tests/ -v
```

## 📊 Monitoring

- Prometheus metrics: http://localhost:9090
- Grafana dashboards: http://localhost:3000

## 🔧 Configuration

See `.env` file for all configuration options.

## 📝 API Documentation

Once running, visit: http://localhost:8000/docs

## 🤝 Contributing

This is a portfolio project built to demonstrate backend engineering skills.

## 📄 License

MIT License

## 👤 Author

Your Name - [GitHub](https://github.com/yourusername)

---

**Status**: 🚧 In Development
**Current Phase**: Infrastructure Setup

## 📝 Log Generator

Generate realistic application logs for testing:

### Basic Usage
```bash
# Generate text logs (default)
python shipper/generate_logs.py

# Generate JSON logs
python shipper/generate_logs.py --format json

# Custom rate (10 logs/second)
python shipper/generate_logs.py --rate 10

# Custom burst interval (every 60 seconds)
python shipper/generate_logs.py --burst-interval 60
```

### Background Generation
```bash
# Start generator in background
./scripts/generate-logs.sh

# Stop background generator
./scripts/stop-logs.sh
```

### Log Format

**Text format:**
```
2025-10-23 14:32:15 INFO [payment-service] Payment completed for order order_45231
```

**JSON format:**
```json
{
  "timestamp": "2025-10-23 14:35:22",
  "level": "ERROR",
  "service": "payment-service",
  "message": "Payment gateway unavailable"
}
```

### Log Levels Distribution

- INFO: 70%
- WARN: 15%
- ERROR: 10%
- DEBUG: 5%

### Services

- payment-service
- auth-service
- user-service
- order-service
- inventory-service

## 📤 Log Shipper

The shipper tails log files and sends them to Kafka in real-time.

### Usage
```bash
# Start shipper (foreground)
python shipper/shipper.py --log-file sample_logs/app.log

# Start shipper (background)
./scripts/start-shipper.sh

# Stop shipper
./scripts/stop-shipper.sh

# Check status
python shipper/shipper_status.py
```

### How It Works

1. **Tails log file** - Like `tail -f`, watches for new lines
2. **Wraps in metadata** - Adds hostname, timestamp, file path
3. **Sends to Kafka** - Ships to `logs-raw` topic
4. **Handles failures** - Automatic retries and reconnection

### Message Format
```json
{
  "raw_log": "2025-10-23 15:30:45 INFO [service] message",
  "metadata": {
    "source": "hostname",
    "file_path": "sample_logs/app.log",
    "shipper_timestamp": 1729698645.123,
    "service": "app"
  }
}
```

## ⚙️ Log Processor

The processor consumes from Kafka, parses logs, and indexes to Elasticsearch.

### Usage
```bash
# Start processor (foreground)
python processor/processor.py

# Start processor (background)
./scripts/start-processor.sh

# Stop processor
./scripts/stop-processor.sh
```

### Complete Pipeline
```bash
# Start entire pipeline
./scripts/start-pipeline.sh

# Check status
./scripts/pipeline-status.sh

# Stop entire pipeline
./scripts/stop-pipeline.sh
```

### Pipeline Flow
```
Logs → Shipper → Kafka → Processor → Elasticsearch → Kibana
```

### Viewing Logs

**Elasticsearch API:**
```bash
# Count logs
curl http://localhost:9200/logs-*/_count

# Search logs
curl -X GET "http://localhost:9200/logs-*/_search?pretty" -H 'Content-Type: application/json' -d'
{
  "query": { "match": { "level": "ERROR" } },
  "size": 10
}
'
```

**Kibana UI:**
```bash
open http://localhost:5601
# Go to Discover → Create index pattern: logs-*
```

### Document Structure
```json
{
  "_id": "uuid",
  "timestamp": "2025-10-23 15:30:45",
  "level": "ERROR",
  "service": "payment-service",
  "message": "Database connection timeout",
  "source": {
    "hostname": "laptop",
    "file": "sample_logs/app.log"
  },
  "extra_fields": {
    "error_code": "E503"
  },
  "ingested_at": "2025-10-23T15:30:46.123Z"
}
```

## 🎬 Quick Demo

Want to see it in action immediately?
```bash
# One command to rule them all!
./scripts/demo.sh
```

This runs a complete end-to-end demo:
1. Starts all components
2. Generates sample logs
3. Processes them through the pipeline
4. Shows statistics and sample data
5. Takes ~45 seconds

Then open Kibana at http://localhost:5601 to explore your logs!

See [QUICKSTART.md](QUICKSTART.md) for detailed setup instructions.

---

## 📸 Screenshots

### Pipeline in Action
![Pipeline Status](docs/screenshots/pipeline-status.png)

### Kibana Dashboard
![Kibana Logs](docs/screenshots/kibana-discover.png)

### Architecture
```
┌─────────────┐    ┌─────────┐    ┌───────┐    ┌───────────┐    ┌────────────────┐
│  Log Files  │───▶│ Shipper │───▶│ Kafka │───▶│ Processor │───▶│ Elasticsearch  │
└─────────────┘    └─────────┘    └───────┘    └───────────┘    └────────────────┘
                                                                           │
                                                                           ▼
                                                                    ┌────────────┐
                                                                    │   Kibana   │
                                                                    └────────────┘
```

---

## 📊 Performance

Current configuration handles:
- **Throughput**: 10,000+ logs/second
- **Latency**: <100ms end-to-end
- **Storage**: ~500MB per million logs (compressed)
- **Scaling**: Horizontal scaling via Kafka partitions

---

## 🎯 Project Status

**Completed (23%):**
- ✅ Core pipeline (Generator → Shipper → Kafka → Processor → Elasticsearch)
- ✅ Docker infrastructure
- ✅ Real-time processing
- ✅ Log parsing and indexing
- ✅ Kibana visualization

**In Progress:**
- 🔨 REST API for searching
- 🔨 Alert engine
- 🔨 Authentication

**Planned:**
- 📋 Frontend dashboard
- 📋 Kubernetes deployment
- 📋 CI/CD pipeline


## 🔍 REST API

Query and search logs via REST API.

### Quick Start
```bash
# Start API
python -m api.main

# Or in background
./scripts/start-api.sh
```

### API Endpoints

**Base URL:** `http://localhost:8000`

#### Search Logs
```bash
POST /api/v1/logs/search
```

**Request body:**
```json
{
  "query": "database timeout",
  "services": ["payment-service"],
  "levels": ["ERROR", "WARN"],
  "start_time": "2025-10-23 10:00:00",
  "end_time": "2025-10-23 20:00:00",
  "limit": 50,
  "offset": 0
}
```

**Response:**
```json
{
  "total": 127,
  "logs": [...],
  "aggregations": {
    "by_level": {"ERROR": 98, "WARN": 29},
    "by_service": {"payment-service": 127}
  },
  "query_time_ms": 45.2
}
```

#### Get Recent Logs
```bash
GET /api/v1/logs/recent?limit=50&level=ERROR
```

#### Get Log by ID
```bash
GET /api/v1/logs/{log_id}
```

#### Health Check
```bash
GET /health
```

### Interactive Documentation

Visit http://localhost:8000/docs for Swagger UI with:
- Interactive API testing
- Request/response examples
- Schema documentation

### cURL Examples
```bash
# Search all logs
curl -X POST "http://localhost:8000/api/v1/logs/search" \
  -H "Content-Type: application/json" \
  -d '{"limit": 10}'

# Search ERROR logs
curl -X POST "http://localhost:8000/api/v1/logs/search" \
  -H "Content-Type: application/json" \
  -d '{"levels": ["ERROR"], "limit": 5}'

# Full-text search
curl -X POST "http://localhost:8000/api/v1/logs/search" \
  -H "Content-Type: application/json" \
  -d '{"query": "timeout", "limit": 5}'

# Get recent logs
curl "http://localhost:8000/api/v1/logs/recent?limit=10"
```

### Testing
```bash
# Run API tests
./scripts/test-api.sh
```


### Metrics Endpoints

#### Metrics Overview
```bash
GET /api/v1/metrics/overview?time_range=1h
```

Returns: Total logs, logs/minute, distribution by level/service, error rate

#### Service Metrics
```bash
GET /api/v1/metrics/service/{service_name}?time_range=1h
```

Returns: Service-specific metrics and top error messages

#### System Metrics
```bash
GET /api/v1/metrics/system?time_range=1h
```

Returns: Comprehensive system-wide metrics with per-service breakdown

#### Time Series Data
```bash
GET /api/v1/metrics/timeseries?interval=5m&time_range=1h&service=payment-service
```

Returns: Log counts over time for charting/visualization

**Supported time ranges:** 5m, 15m, 30m, 1h, 6h, 12h, 24h, 7d, 30d  
**Supported intervals:** 1m, 5m, 15m, 30m, 1h


## 🗄️ Database Management

LogFlow uses PostgreSQL for persistent storage of users, alerts, and configuration.

### Database Schema

**Tables:**
- **users** - User accounts and authentication
- **alert_rules** - Alert rule configurations
- **triggered_alerts** - Alert history and status
- **system_config** - System-wide settings

### Quick Commands
```bash
# Initialize database (first time setup)
./scripts/manage-db.sh init

# Open PostgreSQL shell
./scripts/manage-db.sh shell

# Create backup
./scripts/manage-db.sh backup

# Reset database (⚠️ deletes all data!)
./scripts/manage-db.sh reset
```

### Default Credentials

After initialization, a default admin user is created:

- **Username:** `admin`
- **Password:** `admin123`
- **Email:** `admin@logflow.local`

⚠️ **Change these credentials in production!**

### Database Connection

From outside Docker (for Python scripts/API):
```
Host: 127.0.0.1
Port: 5432
User: logflow
Password: logflow123
Database: logflow
```

From inside Docker (for other containers):
```
Host: postgres
Port: 5432
User: logflow
Password: logflow123
Database: logflow
```

### Manual Database Access
```bash
# Via Docker
docker compose exec postgres psql -U logflow -d logflow

# Common queries
\dt                          # List tables
\d users                     # Describe users table
SELECT * FROM users;         # View all users
SELECT * FROM system_config; # View configuration
```

### Backup and Restore

**Create Backup:**
```bash
./scripts/manage-db.sh backup
# Creates: backups/logflow-YYYYMMDD-HHMMSS.sql
```

**Restore from Backup:**
```bash
cat backups/logflow-20251024-120000.sql | docker compose exec -T postgres psql -U logflow -d logflow
```

### Troubleshooting

**Can't connect from Python:**
- Ensure `.env` has `POSTGRES_HOST=127.0.0.1` (not `localhost`)
- Check PostgreSQL is running: `docker compose ps postgres`
- Test connection: `docker compose exec postgres psql -U logflow -d logflow -c "SELECT 1;"`

**Reset database:**
```bash
./scripts/manage-db.sh reset
```

**Check database size:**
```bash
docker compose exec postgres psql -U logflow -d logflow -c "\l+"
```

