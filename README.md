# LogFlow - Distributed Log Aggregation System

A production-grade distributed log aggregation and analysis platform built with Python, Kafka, Elasticsearch, and PostgreSQL.

## 🎯 Overview

LogFlow is a real-time log aggregation system that collects, processes, stores, and analyzes logs from multiple services. It features a RESTful API, alerting engine, and full containerized deployment.

## ✨ Features

### Core Capabilities
- **Real-time Log Processing** - Stream logs through Kafka for scalable ingestion
- **Multi-service Support** - Aggregate logs from multiple microservices
- **Advanced Search** - Full-text search with filters (service, level, time range)
- **Metrics & Analytics** - Real-time aggregations and statistics
- **Alerting System** - Rule-based alerts with multiple notification channels
- **RESTful API** - Complete API for log queries and management
- **Containerized Deployment** - Fully Dockerized with Docker Compose

### Technical Features
- Stream processing with Apache Kafka
- Full-text search with Elasticsearch
- PostgreSQL for metadata and alert storage
- Redis for caching (ready to use)
- Health monitoring and status checks
- Scalable microservices architecture

## 🏗️ Architecture
```
┌─────────────┐     ┌─────────┐     ┌───────────┐     ┌──────────────┐
│ Log Sources │────▶│  Kafka  │────▶│ Processor │────▶│Elasticsearch │
└─────────────┘     └─────────┘     └───────────┘     └──────────────┘
                                                              │
                                                              ▼
                    ┌──────────┐                      ┌─────────────┐
                    │PostgreSQL│◀─────────────────────│  REST API   │
                    └──────────┘                      └─────────────┘
                         │                                   ▲
                         ▼                                   │
                  ┌─────────────┐                           │
                  │Alert Engine │───────────────────────────┘
                  └─────────────┘
```

## 🚀 Quick Start

### Prerequisites
- Docker Desktop (with Docker Compose)
- Git

### Installation
```bash
# Clone the repository
git clone <your-repo-url>
cd logflow

# Start all services
./scripts/start-all-docker.sh
```

Wait ~30 seconds for all services to initialize. You should see:
```
✅ LogFlow is running!

📊 Services:
  - API:           http://localhost:8000
  - API Docs:      http://localhost:8000/docs
  - Elasticsearch: http://localhost:9200
  - Kibana:        http://localhost:5601
```

### Verify Installation
```bash
# Check system health
curl http://localhost:8000/health

# View recent logs
curl http://localhost:8000/api/v1/logs/recent?limit=5

# Get metrics
curl http://localhost:8000/api/v1/metrics/overview
```

## 📖 Usage

### API Endpoints

**Interactive Documentation:** http://localhost:8000/docs

#### Search Logs
```bash
# Search all logs
GET /api/v1/logs/search?query=error

# Filter by service
GET /api/v1/logs/search?service=payment-service

# Filter by log level
GET /api/v1/logs/search?level=ERROR

# Recent logs
GET /api/v1/logs/recent?limit=100
```

#### Metrics
```bash
# Overall metrics
GET /api/v1/metrics/overview

# Service-specific metrics
GET /api/v1/metrics/service/{service_name}

# System metrics
GET /api/v1/metrics/system

# Time series data
GET /api/v1/metrics/timeseries?interval=5m
```

#### Alert Management
```bash
# Create alert rule
POST /api/v1/alerts/rules
{
  "name": "High Error Rate",
  "condition": "greater_than",
  "threshold": 100,
  "levels": ["ERROR"],
  "notification_channel": "webhook"
}

# List alert rules
GET /api/v1/alerts/rules

# Update rule
PUT /api/v1/alerts/rules/{rule_id}

# Delete rule
DELETE /api/v1/alerts/rules/{rule_id}

# View triggered alerts
GET /api/v1/alerts/triggered

# Acknowledge alert
POST /api/v1/alerts/triggered/{alert_id}/acknowledge

# Resolve alert
POST /api/v1/alerts/triggered/{alert_id}/resolve
```

## 🔔 Alerting System

### Alert Rules

Alert rules monitor logs and trigger notifications when conditions are met.

**Supported Conditions:**
- `greater_than` - Value > threshold
- `less_than` - Value < threshold  
- `equals` - Value == threshold
- `greater_than_or_equal` - Value >= threshold
- `less_than_or_equal` - Value <= threshold

**Notification Channels:**
- `console` - Print to logs (testing)
- `webhook` - POST to HTTP endpoint
- `email` - Email notifications (extensible)
- `slack` - Slack webhooks (extensible)

### Example Alert Rule
```json
{
  "name": "Critical Error Spike",
  "description": "Alert when ERROR logs exceed 50 in 5 minutes",
  "condition": "greater_than",
  "threshold": 50,
  "time_window": 5,
  "levels": ["ERROR"],
  "services": ["payment-service", "auth-service"],
  "notification_channel": "webhook",
  "notification_config": {
    "url": "https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
  },
  "is_active": true
}
```

## 🗄️ Database Management

### Access Database
```bash
# Open PostgreSQL shell
./scripts/manage-db.sh shell

# Create backup
./scripts/manage-db.sh backup

# Initialize/reset database
./scripts/manage-db.sh init
```

### Default Credentials

**Admin User:**
- Username: `admin`
- Password: `admin123`
- Email: `admin@logflow.local`

⚠️ **Change credentials in production!**

## 🐳 Docker Services

### Service List

| Service | Port | Description |
|---------|------|-------------|
| API | 8000 | REST API server |
| Elasticsearch | 9200 | Log storage and search |
| Kibana | 5601 | Elasticsearch UI |
| Kafka | 9092 | Message queue |
| PostgreSQL | 5432 | Metadata storage |
| Redis | 6379 | Caching layer |
| Alerting Engine | - | Background alert processor |

### Managing Services
```bash
# Start all services
docker compose up -d

# Stop all services
docker compose down

# View logs
docker compose logs -f api
docker compose logs -f alerting

# Restart a service
docker compose restart api

# Check status
docker compose ps
```

## 📊 Monitoring

### Health Check
```bash
curl http://localhost:8000/health
```

Response:
```json
{
  "status": "healthy",
  "timestamp": "2025-10-23T21:35:00.000000",
  "services": {
    "elasticsearch": "green",
    "database": "healthy"
  }
}
```

### Service Logs
```bash
# API logs
docker compose logs -f api

# Alerting engine logs
docker compose logs -f alerting

# All logs
docker compose logs -f
```

## 🛠️ Development

### Project Structure
```
logflow/
├── api/                    # REST API
│   ├── routes/            # API endpoints
│   ├── models/            # Pydantic & SQLAlchemy models
│   └── utils/             # Database, ES clients
├── alerting/              # Alert engine
│   ├── engine.py          # Main alert loop
│   ├── alert_evaluator.py # Rule evaluation
│   └── notifier.py        # Notifications
├── producer/              # Log shipper (Kafka producer)
├── consumer/              # Log processor (Kafka consumer)
├── log_generator/         # Synthetic log generation
├── scripts/               # Utility scripts
├── docker-compose.yml     # Service orchestration
└── Dockerfile.*           # Container definitions
```

### Local Development

If you want to run services locally (outside Docker):
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows

# Install dependencies
pip install -r requirements.txt

# Set environment variables (use localhost instead of service names)
export POSTGRES_HOST=127.0.0.1
export KAFKA_BOOTSTRAP_SERVERS=localhost:9092
export ELASTICSEARCH_HOSTS=http://localhost:9200

# Note: Database connections from outside Docker may require 
# additional PostgreSQL configuration. Running in Docker is recommended.
```

## 🧪 Testing
```bash
# Run log pipeline
./scripts/start-pipeline.sh

# Generate sample logs
python log_generator/generator.py --duration 60

# Check pipeline status
./scripts/pipeline-status.sh

# Stop pipeline
./scripts/stop-pipeline.sh
```

## 🎓 Technology Stack

- **Python 3.11+** - Core language
- **FastAPI** - REST API framework
- **Apache Kafka** - Message streaming
- **Elasticsearch 8.x** - Search and analytics
- **PostgreSQL 16** - Relational database
- **Redis 7** - Caching layer
- **Docker & Docker Compose** - Containerization
- **SQLAlchemy 2.0** - ORM
- **Pydantic v2** - Data validation

## 📝 API Documentation

Interactive API documentation is available at:
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

## 🔐 Security Notes

**For Production:**
- Change default admin password
- Use environment variables for secrets
- Enable Elasticsearch security
- Add API authentication (JWT)
- Use HTTPS/TLS
- Implement rate limiting
- Regular security updates

## 🤝 Contributing

This is a portfolio/learning project. Feel free to fork and extend!

## 📄 License

MIT License - See LICENSE file for details

## 🎯 Roadmap

- [x] Core log aggregation pipeline
- [x] REST API with search and metrics
- [x] Alert rules and notifications
- [x] Containerized deployment
- [ ] JWT authentication
- [ ] Redis caching implementation
- [ ] WebSocket real-time streaming
- [ ] Web dashboard (React)
- [ ] Kubernetes deployment
- [ ] Anomaly detection with ML

## 📧 Contact

Built by [Your Name]
- GitHub: [@yourusername]
- Email: your.email@example.com

---

**⭐ If you found this project helpful, please star the repository!**
