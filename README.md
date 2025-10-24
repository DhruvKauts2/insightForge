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

## 🔐 Authentication & Security

LogFlow uses JWT (JSON Web Token) authentication to secure API endpoints.

### User Registration

Register a new user account:
```bash
POST /api/v1/auth/register

{
  "username": "johndoe",
  "email": "john@example.com",
  "password": "securepassword123",
  "full_name": "John Doe"
}
```

**Response:**
```json
{
  "id": 2,
  "username": "johndoe",
  "email": "john@example.com",
  "full_name": "John Doe",
  "is_active": true,
  "is_admin": false
}
```

### Login

Get an access token:
```bash
POST /api/v1/auth/login
Content-Type: application/x-www-form-urlencoded

username=johndoe&password=securepassword123
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### Using Authentication

Include the token in the Authorization header:
```bash
curl -X GET "http://localhost:8000/api/v1/auth/me" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### Protected Endpoints

The following endpoints require authentication:

**User Management:**
- `POST /api/v1/auth/register` - Register new user (public)
- `POST /api/v1/auth/login` - Login (public)
- `GET /api/v1/auth/me` - Get current user (authenticated)
- `PUT /api/v1/auth/me` - Update profile (authenticated)

**Alert Rules:**
- `POST /api/v1/alerts/rules` - Create rule (authenticated)
- `PUT /api/v1/alerts/rules/{id}` - Update rule (owner or admin)
- `DELETE /api/v1/alerts/rules/{id}` - Delete rule (owner or admin)
- `POST /api/v1/alerts/triggered/{id}/acknowledge` - Acknowledge (authenticated)
- `POST /api/v1/alerts/triggered/{id}/resolve` - Resolve (authenticated)

**Public Endpoints:**
- `GET /api/v1/logs/*` - Search logs
- `GET /api/v1/metrics/*` - View metrics
- `GET /api/v1/alerts/rules` - List rules
- `GET /api/v1/alerts/triggered` - List triggered alerts

### Default Admin Account

**Username:** `admin`  
**Password:** `admin123`

⚠️ **Change this password immediately in production!**
```bash
# Login as admin
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin123"
```

### Token Configuration

Tokens expire after 30 minutes by default. Configure in `.env`:
```bash
SECRET_KEY=your-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### Security Best Practices

**For Production:**
1. Change default admin password
2. Use strong SECRET_KEY (generate with `openssl rand -hex 32`)
3. Enable HTTPS/TLS
4. Set short token expiration times
5. Implement token refresh mechanism
6. Add rate limiting
7. Use environment variables for secrets
8. Enable CORS restrictions
9. Regular security audits
10. Keep dependencies updated

### Password Requirements

- Minimum 8 characters
- Maximum 72 characters (bcrypt limitation)
- No specific complexity requirements (customize as needed)

### Example: Complete Authentication Flow
```bash
# 1. Register
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "alice",
    "email": "alice@example.com",
    "password": "alicepass123",
    "full_name": "Alice Smith"
  }'

# 2. Login
TOKEN=$(curl -s -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=alice&password=alicepass123" \
  | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])")

# 3. Use authenticated endpoints
curl -X POST "http://localhost:8000/api/v1/alerts/rules" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My Alert",
    "condition": "greater_than",
    "threshold": 50,
    "levels": ["ERROR"],
    "notification_channel": "console"
  }'

# 4. Get user profile
curl -X GET "http://localhost:8000/api/v1/auth/me" \
  -H "Authorization: Bearer $TOKEN"
```


## ⚡ Caching with Redis

LogFlow uses Redis to cache frequently accessed data, dramatically improving API performance.

### Cached Endpoints

The following endpoints are cached:

| Endpoint | Cache TTL | Description |
|----------|-----------|-------------|
| `/api/v1/metrics/overview` | 30s | Overall metrics |
| `/api/v1/metrics/service/{name}` | 60s | Service-specific metrics |
| `/api/v1/metrics/system` | 45s | System-wide metrics |
| `/api/v1/metrics/timeseries` | 120s | Time series data |

### Cache Management

**View cache statistics:**
```bash
GET /api/v1/cache/stats

# Response
{
  "connected": true,
  "used_memory": "1.23M",
  "connected_clients": 2,
  "keyspace_hits": 156,
  "keyspace_misses": 12,
  "keys": 8
}
```

**Clear cache (admin only):**
```bash
# Clear all cache
DELETE /api/v1/cache/clear

# Clear specific pattern
DELETE /api/v1/cache/clear?pattern=metrics:*

# Clear service metrics only
DELETE /api/v1/cache/clear?pattern=metrics:service:*
```

### Performance Impact

Typical performance improvements with caching:

- **First request (cache miss):** ~200-500ms (Elasticsearch query)
- **Cached request (cache hit):** ~5-20ms (Redis lookup)
- **Performance gain:** 10-100x faster! ⚡

### Cache Keys

Cache keys follow this pattern:
```
metrics:overview
metrics:service:{service_name}
metrics:system
metrics:timeseries:{interval}:{service}
```

### Redis Configuration

Configure Redis in `.env.docker`:
```bash
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_DB=0
```

### Manual Cache Operations
```bash
# Check Redis directly
docker compose exec redis redis-cli

# View all keys
KEYS *

# View metrics keys
KEYS "metrics:*"

# Get specific key
GET "metrics:overview"

# Delete key
DEL "metrics:overview"

# Flush all cache
FLUSHDB

# Exit
exit
```

### Cache Invalidation

Cache is automatically invalidated by TTL (Time To Live):
- Overview metrics: 30 seconds
- Service metrics: 60 seconds
- System metrics: 45 seconds
- Time series: 120 seconds

For manual invalidation, use the admin cache clear endpoint.

### Graceful Degradation

If Redis is unavailable:
- API continues to work normally
- Queries go directly to Elasticsearch
- Performance returns to non-cached speed
- No errors or failures

The system automatically detects Redis availability and adapts.

