# LogFlow - Distributed Log Aggregation System

A production-grade distributed log aggregation and analysis platform built with Python, Kafka, Elasticsearch, and PostgreSQL.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Docker](https://img.shields.io/badge/docker-required-blue.svg)](https://www.docker.com/)

## 🎯 Overview

LogFlow is a **real-time log aggregation system** that collects, processes, stores, and analyzes logs from multiple microservices. It features a RESTful API, intelligent alerting, caching, rate limiting, and full authentication - all containerized and production-ready.

### Key Features

- 🚀 **Real-time Processing** - Stream logs through Kafka for scalable ingestion
- 🔍 **Advanced Search** - Full-text search with Elasticsearch
- 📊 **Metrics & Analytics** - Real-time aggregations and statistics
- 🚨 **Smart Alerting** - Rule-based alerts with multiple notification channels
- 🔐 **Authentication** - JWT-based security with role-based access
- ⚡ **Redis Caching** - 10-100x performance improvement on cached queries
- 🚦 **Rate Limiting** - Prevent API abuse and ensure fair usage
- 🐳 **Fully Containerized** - Docker Compose deployment
- 📖 **Interactive API Docs** - Swagger UI at `/docs`

---

## 📋 Table of Contents

- [Quick Start](#-quick-start)
- [Architecture](#-architecture)
- [Features](#-features-in-detail)
- [API Endpoints](#-api-endpoints)
- [Authentication](#-authentication--security)
- [Alerting System](#-alerting-system)
- [Caching](#-caching)
- [Rate Limiting](#-rate-limiting)
- [Database Management](#-database-management)
- [Monitoring](#-monitoring)
- [Development](#-development)
- [Testing](#-testing)
- [Deployment](#-deployment)
- [Troubleshooting](#-troubleshooting)

---

## 🚀 Quick Start

### Prerequisites

- Docker Desktop (with Docker Compose)
- Git
- 8GB RAM minimum
- 10GB free disk space

### Installation
```bash
# 1. Clone the repository
git clone <your-repo-url>
cd logflow

# 2. Start all services
./scripts/start-all-docker.sh

# Wait ~30 seconds for services to initialize
```

### Verify Installation
```bash
# Check system health
curl http://localhost:8000/health | python3 -m json.tool

# View API documentation
open http://localhost:8000/docs
```

**Expected Output:**
```json
{
  "status": "healthy",
  "timestamp": "2025-10-24T08:30:00.000000",
  "services": {
    "elasticsearch": "green",
    "database": "healthy",
    "redis": "healthy"
  }
}
```

### Default Credentials

**Admin Account:**
- Username: `admin`
- Password: `admin123`
- ⚠️ **Change in production!**

---

## 🏗️ Architecture
```
┌─────────────────┐
│  Log Sources    │ (Multiple Services)
│  (Generators)   │
└────────┬────────┘
         │ Logs
         ▼
┌─────────────────┐
│   Log Shipper   │ (Kafka Producer)
│   (Producer)    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│      Kafka      │ (Message Queue)
│  (Stream Queue) │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Log Processor  │ (Kafka Consumer)
│   (Consumer)    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Elasticsearch   │ (Search & Storage)
└────────┬────────┘
         │
         ▼
┌─────────────────┐     ┌──────────────┐
│   REST API      │────▶│ PostgreSQL   │ (Metadata)
│  (FastAPI)      │     │  (Alerts DB) │
└────────┬────────┘     └──────────────┘
         │
         ├──────▶ Redis (Caching)
         │
         └──────▶ Alert Engine (Background)
```

**Components:**
- **Log Generator**: Simulates multi-service logs
- **Kafka**: Message streaming and buffering
- **Elasticsearch**: Log storage and search
- **PostgreSQL**: Users, alerts, configuration
- **Redis**: Caching and rate limiting
- **REST API**: FastAPI-based interface
- **Alert Engine**: Background alert processing

---

## ✨ Features in Detail

### 1. Log Aggregation Pipeline

- **Multi-Service Support**: Aggregate logs from unlimited services
- **Real-time Processing**: Stream processing with Kafka
- **Scalable**: Handle millions of logs per day
- **Fault Tolerant**: Kafka ensures no log loss

### 2. Advanced Search
```bash
# Search by query
GET /api/v1/logs/search?query=error

# Filter by service
GET /api/v1/logs/search?service=payment-service

# Filter by log level
GET /api/v1/logs/search?level=ERROR

# Combine filters
GET /api/v1/logs/search?service=auth-service&level=WARN&query=timeout
```

### 3. Metrics & Analytics
```bash
# Overall system metrics
GET /api/v1/metrics/overview

# Service-specific metrics
GET /api/v1/metrics/service/payment-service

# System-wide metrics
GET /api/v1/metrics/system

# Time series data
GET /api/v1/metrics/timeseries?interval=5m
```

**Metrics Include:**
- Total log count
- Logs per minute/second
- Error rates by service
- Log distribution by level
- Top error messages
- Service health indicators

### 4. Smart Alerting

Create rules that trigger notifications:
```json
{
  "name": "High Error Rate",
  "condition": "greater_than",
  "threshold": 100,
  "levels": ["ERROR"],
  "notification_channel": "webhook"
}
```

**Alert Features:**
- Multiple conditions (>, <, =, >=, <=)
- Filter by service and log level
- Multiple notification channels
- Alert history and tracking
- Acknowledge/resolve workflow

### 5. Authentication & Authorization

- **JWT Tokens**: Secure token-based auth
- **Role-Based Access**: User and admin roles
- **Protected Endpoints**: Secure write operations
- **Password Hashing**: Bcrypt encryption

### 6. Redis Caching

- **Automatic**: Transparent caching on metrics endpoints
- **Fast**: 10-100x performance improvement
- **Configurable TTL**: Different cache times per endpoint
- **Graceful Degradation**: Works without Redis

### 7. Rate Limiting

- **Per-User**: Track authenticated users by ID
- **Per-IP**: Track anonymous users by IP
- **Configurable**: Different limits per endpoint
- **Fair Usage**: Prevents API abuse

---

## 📡 API Endpoints

### Authentication

| Method | Endpoint | Rate Limit | Description |
|--------|----------|------------|-------------|
| POST | `/api/v1/auth/register` | 10/hour | Register new user |
| POST | `/api/v1/auth/login` | 20/hour | Login and get JWT token |
| GET | `/api/v1/auth/me` | 100/min | Get current user |
| PUT | `/api/v1/auth/me` | 30/hour | Update profile |
| GET | `/api/v1/auth/users` | 50/min | List all users (admin) |

### Logs

| Method | Endpoint | Rate Limit | Description |
|--------|----------|------------|-------------|
| GET | `/api/v1/logs/search` | 50/min | Search logs with filters |
| GET | `/api/v1/logs/recent` | 100/min | Get recent logs |
| GET | `/api/v1/logs/{id}` | 200/min | Get specific log by ID |

### Metrics

| Method | Endpoint | Cache TTL | Description |
|--------|----------|-----------|-------------|
| GET | `/api/v1/metrics/overview` | 30s | Overall metrics |
| GET | `/api/v1/metrics/service/{name}` | 60s | Service metrics |
| GET | `/api/v1/metrics/system` | 45s | System metrics |
| GET | `/api/v1/metrics/timeseries` | 120s | Time series data |

### Alerts

| Method | Endpoint | Auth Required | Description |
|--------|----------|---------------|-------------|
| POST | `/api/v1/alerts/rules` | ✅ | Create alert rule |
| GET | `/api/v1/alerts/rules` | ❌ | List alert rules |
| GET | `/api/v1/alerts/rules/{id}` | ❌ | Get specific rule |
| PUT | `/api/v1/alerts/rules/{id}` | ✅ Owner/Admin | Update rule |
| DELETE | `/api/v1/alerts/rules/{id}` | ✅ Owner/Admin | Delete rule |
| GET | `/api/v1/alerts/triggered` | ❌ | List triggered alerts |
| POST | `/api/v1/alerts/triggered/{id}/acknowledge` | ✅ | Acknowledge alert |
| POST | `/api/v1/alerts/triggered/{id}/resolve` | ✅ | Resolve alert |

### Cache Management

| Method | Endpoint | Auth Required | Description |
|--------|----------|---------------|-------------|
| GET | `/api/v1/cache/stats` | ❌ | Cache statistics |
| DELETE | `/api/v1/cache/clear` | ✅ Admin | Clear cache |

### Rate Limit Management

| Method | Endpoint | Auth Required | Description |
|--------|----------|---------------|-------------|
| GET | `/api/v1/rate-limits/status` | ✅ Admin | View rate limit status |
| DELETE | `/api/v1/rate-limits/reset/{id}` | ✅ Admin | Reset specific limit |
| DELETE | `/api/v1/rate-limits/reset-all` | ✅ Admin | Reset all limits |

---

## 🔐 Authentication & Security

### Register & Login
```bash
# 1. Register new user
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "alice",
    "email": "alice@example.com",
    "password": "secure123",
    "full_name": "Alice Smith"
  }'

# 2. Login and get token
TOKEN=$(curl -s -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=alice&password=secure123" \
  | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])")

# 3. Use token for authenticated requests
curl -X POST "http://localhost:8000/api/v1/alerts/rules" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{...}'
```

### Security Features

- ✅ **Bcrypt Password Hashing**: Industry-standard encryption
- ✅ **JWT Tokens**: Stateless authentication
- ✅ **Token Expiration**: 30-minute default (configurable)
- ✅ **Role-Based Access**: User and admin permissions
- ✅ **Rate Limiting**: Prevent brute force attacks
- ✅ **CORS Protection**: Configurable origins

---

## 🚨 Alerting System

### Create Alert Rule
```bash
POST /api/v1/alerts/rules
Authorization: Bearer <token>

{
  "name": "Critical Error Spike",
  "description": "Alert when errors exceed threshold",
  "condition": "greater_than",
  "threshold": 50,
  "time_window": 5,
  "levels": ["ERROR"],
  "services": ["payment-service"],
  "notification_channel": "webhook",
  "notification_config": {
    "url": "https://hooks.slack.com/..."
  },
  "is_active": true
}
```

### Alert Conditions

- `greater_than`: Value > threshold
- `less_than`: Value < threshold
- `equals`: Value == threshold
- `greater_than_or_equal`: Value >= threshold
- `less_than_or_equal`: Value <= threshold

### Notification Channels

- **Console**: Print to logs (development)
- **Webhook**: POST to HTTP endpoint
- **Email**: Send email (extensible)
- **Slack**: Slack webhooks (extensible)

### Alert Workflow

1. Engine checks rules every 60 seconds
2. Evaluates conditions against Elasticsearch
3. If triggered, creates `triggered_alert` record
4. Sends notification via configured channel
5. Updates rule statistics

---

## ⚡ Caching

### Performance Impact

| Metric | Without Cache | With Cache | Improvement |
|--------|---------------|------------|-------------|
| Overview | 250ms | 8ms | **31x faster** |
| Service Metrics | 180ms | 12ms | **15x faster** |
| System Metrics | 400ms | 15ms | **27x faster** |

### Cache Configuration
```bash
# View cache stats
GET /api/v1/cache/stats

# Clear cache (admin only)
DELETE /api/v1/cache/clear?pattern=metrics:*
```

### Cache TTLs

- Overview: 30 seconds
- Service metrics: 60 seconds
- System metrics: 45 seconds
- Time series: 120 seconds

---

## 🚦 Rate Limiting

### Rate Limits by Endpoint

| Endpoint Type | Limit | Window |
|---------------|-------|--------|
| Default | 100 | per minute |
| Search | 50 | per minute |
| Recent Logs | 100 | per minute |
| Direct Lookup | 200 | per minute |
| Auth Login | 20 | per hour |
| Auth Register | 10 | per hour |
| Metrics | 100 | per minute |

### Testing Rate Limits
```bash
# Automated test
./scripts/test-rate-limit.sh

# Manual test
for i in {1..70}; do
  curl -s -o /dev/null -w "%{http_code} " http://localhost:8000/
done
```

### Rate Limit Response
```http
HTTP/1.1 429 Too Many Requests
Content-Type: application/json

{
  "error": "Rate limit exceeded: 60 per 1 minute"
}
```

---

## 🗄️ Database Management

### Quick Commands
```bash
# Initialize database
./scripts/manage-db.sh init

# Open PostgreSQL shell
./scripts/manage-db.sh shell

# Create backup
./scripts/manage-db.sh backup

# Reset database (⚠️ deletes all data!)
./scripts/manage-db.sh reset
```

### Database Schema

**Tables:**
- `users` - User accounts and authentication
- `alert_rules` - Alert configurations
- `triggered_alerts` - Alert history
- `system_config` - System settings

### Common Queries
```sql
-- List all users
SELECT username, email, is_admin FROM users;

-- List active alert rules
SELECT name, condition, threshold, is_active 
FROM alert_rules 
WHERE is_active = true;

-- Recent triggered alerts
SELECT r.name, a.triggered_at, a.status 
FROM triggered_alerts a 
JOIN alert_rules r ON a.rule_id = r.id 
ORDER BY a.triggered_at DESC 
LIMIT 10;
```

---

## 📊 Monitoring

### Service Health
```bash
# Check all services
curl http://localhost:8000/health | python3 -m json.tool

# View cache statistics
curl http://localhost:8000/api/v1/cache/stats | python3 -m json.tool

# Check rate limit status (admin only)
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/v1/rate-limits/status
```

### Docker Services
```bash
# View all services
docker compose ps

# Check service logs
docker compose logs api
docker compose logs alerting
docker compose logs elasticsearch

# Resource usage
docker stats
```

### Performance Metrics
```bash
# Elasticsearch cluster health
curl http://localhost:9200/_cluster/health?pretty

# Redis info
docker compose exec redis redis-cli INFO

# PostgreSQL connections
docker compose exec postgres psql -U logflow -d logflow \
  -c "SELECT count(*) FROM pg_stat_activity;"
```

---

## 🛠️ Development

### Project Structure
```
logflow/
├── api/                      # REST API
│   ├── routes/              # API endpoints
│   ├── models/              # Pydantic & SQLAlchemy models
│   ├── utils/               # Utilities (DB, ES, Redis, Auth)
│   └── config.py            # Configuration
├── alerting/                # Alert engine
│   ├── engine.py            # Main alert loop
│   ├── alert_evaluator.py  # Rule evaluation
│   └── notifier.py          # Notifications
├── producer/                # Log shipper (Kafka producer)
├── consumer/                # Log processor (Kafka consumer)
├── log_generator/           # Synthetic log generation
├── scripts/                 # Utility scripts
├── docker-compose.yml       # Service orchestration
├── Dockerfile.*             # Container definitions
└── requirements.txt         # Python dependencies
```

### Local Development
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run tests
pytest

# Run specific service locally
python -m api.main
python -m alerting.engine
```

### Environment Variables

Create `.env` for local development:
```bash
# Copy Docker environment
cp .env.docker .env

# Update for local use
POSTGRES_HOST=127.0.0.1
KAFKA_BOOTSTRAP_SERVERS=localhost:9092
ELASTICSEARCH_HOSTS=http://localhost:9200
REDIS_HOST=localhost
```

---

## 🧪 Testing

### Automated Tests
```bash
# Test authentication
./scripts/test-auth.sh

# Test caching
./scripts/test-cache.sh

# Test rate limiting
./scripts/test-rate-limit.sh

# Test log pipeline
./scripts/pipeline-status.sh
```

### Manual Testing
```bash
# Generate test logs
python log_generator/generator.py --duration 60

# Test search
curl "http://localhost:8000/api/v1/logs/search?level=ERROR&limit=10"

# Test metrics
curl http://localhost:8000/api/v1/metrics/overview

# Test alerts
curl -X POST http://localhost:8000/api/v1/alerts/rules \
  -H "Authorization: Bearer $TOKEN" \
  -d '{...}'
```

---

## 🚀 Deployment

### Docker Compose (Current)
```bash
# Start everything
./scripts/start-all-docker.sh

# Stop everything
docker compose down

# Stop and remove volumes
docker compose down -v
```

### Production Checklist

- [ ] Change default admin password
- [ ] Set strong SECRET_KEY in environment
- [ ] Configure proper CORS origins
- [ ] Enable HTTPS/TLS
- [ ] Set up log rotation
- [ ] Configure backups
- [ ] Set up monitoring alerts
- [ ] Review rate limits
- [ ] Enable Elasticsearch security
- [ ] Set up firewall rules

### Environment Configuration

**Production `.env.docker`:**
```bash
SECRET_KEY=<generate-with-openssl-rand-hex-32>
ENVIRONMENT=production
POSTGRES_PASSWORD=<strong-password>
ACCESS_TOKEN_EXPIRE_MINUTES=15
```

---

## 🔧 Troubleshooting

### Common Issues

**1. Services not starting**
```bash
# Check Docker resources
docker system df

# Clean up
docker system prune -a --volumes

# Restart services
docker compose up -d
```

**2. Elasticsearch yellow health**
```bash
# Normal for single-node development
# Check status
curl http://localhost:9200/_cluster/health?pretty
```

**3. API connection errors**
```bash
# Check API logs
docker compose logs api --tail 50

# Rebuild API
docker compose build --no-cache api
docker compose up -d api
```

**4. Database connection issues**
```bash
# Check PostgreSQL
docker compose exec postgres psql -U logflow -d logflow -c "SELECT 1;"

# Reinitialize
./scripts/manage-db.sh reset
```

**5. Redis not connected**
```bash
# Check Redis
docker compose exec redis redis-cli PING

# Restart Redis
docker compose restart redis
```

### Logs & Debugging
```bash
# View all logs
docker compose logs -f

# View specific service
docker compose logs -f api

# Check service status
docker compose ps

# Inspect container
docker inspect logflow-api
```

---

## 📚 Additional Resources

- **API Documentation**: http://localhost:8000/docs
- **Elasticsearch**: http://localhost:9200
- **Kibana**: http://localhost:5601
- **Database Guide**: `docs/DATABASE.md`

---

## 🎓 Technology Stack

| Component | Technology | Version |
|-----------|-----------|---------|
| Language | Python | 3.11+ |
| API Framework | FastAPI | 0.104+ |
| Message Queue | Apache Kafka | 7.5 |
| Search Engine | Elasticsearch | 8.11 |
| Database | PostgreSQL | 16 |
| Cache | Redis | 7 |
| ORM | SQLAlchemy | 2.0 |
| Auth | JWT (python-jose) | 3.3 |
| Password Hash | bcrypt | 4.0 |
| Rate Limiting | slowapi | 0.1.9 |
| Containerization | Docker Compose | - |

---

## 📊 Project Statistics

- **Lines of Code**: ~5,000+
- **API Endpoints**: 30+
- **Docker Services**: 7
- **Database Tables**: 4
- **Test Scripts**: 5
- **Documentation**: Comprehensive

---

## 🤝 Contributing

This is a portfolio/learning project. Feel free to fork and extend!

---

## 📄 License

MIT License - See LICENSE file for details

---

## 👨‍💻 Author

Built by [Your Name]

- GitHub: [@yourusername]
- Email: your.email@example.com
- LinkedIn: [Your Profile]

---

## ⭐ Acknowledgments

Built as a demonstration of:
- Distributed systems architecture
- Real-time data processing
- RESTful API design
- Authentication & security
- Caching strategies
- Rate limiting
- Docker containerization
- Production-ready practices

---

**🎉 LogFlow - Production-Ready Log Aggregation**

If you found this project helpful, please star the repository!

## 📊 Prometheus Metrics

LogFlow exports metrics in Prometheus format for monitoring and observability.

### Metrics Endpoints

- **Application Metrics**: `http://localhost:8000/metrics`
- **FastAPI Metrics**: `http://localhost:8000/metrics/fastapi`

### Available Metrics

#### HTTP Metrics
```
http_requests_total{method, endpoint, status}          # Total requests
http_request_duration_seconds{method, endpoint}        # Request latency
```

#### Business Metrics
```
logs_processed_total                                   # Logs processed
logs_indexed_total{service, level}                     # Logs indexed
elasticsearch_queries_total{operation}                 # ES queries
elasticsearch_query_duration_seconds{operation}        # ES query time
```

#### Alert Metrics
```
alerts_triggered_total{rule_name}                      # Alerts triggered
alerts_checked_total                                   # Alert checks
```

#### Cache Metrics
```
cache_hits_total{cache_key_prefix}                     # Cache hits
cache_misses_total{cache_key_prefix}                   # Cache misses
```

#### Database Metrics
```
database_queries_total{operation}                      # DB queries
database_connections                                   # Active connections
```

#### Authentication Metrics
```
auth_attempts_total{result}                            # Auth attempts
users_registered_total                                 # Users registered
```

#### Rate Limit Metrics
```
rate_limit_exceeded_total{endpoint}                    # Rate limits hit
```

### Scraping with Prometheus

Add to your `prometheus.yml`:
```yaml
scrape_configs:
  - job_name: 'logflow'
    static_configs:
      - targets: ['localhost:8000']
    metrics_path: '/metrics'
    scrape_interval: 15s
```

### Example Queries
```promql
# Request rate per endpoint
rate(http_requests_total[5m])

# 95th percentile response time
histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))

# Error rate
rate(http_requests_total{status=~"5.."}[5m])

# Cache hit rate
rate(cache_hits_total[5m]) / (rate(cache_hits_total[5m]) + rate(cache_misses_total[5m]))

# Alert trigger rate
rate(alerts_triggered_total[1h])
```

### Grafana Dashboard

Import the included Grafana dashboard for visualization:

1. Open Grafana
2. Import dashboard
3. Use `grafana-dashboard.json` from the project
4. Select Prometheus data source

### Testing Metrics
```bash
# Run metrics test
./scripts/test-metrics.sh

# View metrics in browser
open http://localhost:8000/metrics

# Generate traffic for testing
for i in {1..100}; do
  curl -s http://localhost:8000/ > /dev/null
  curl -s http://localhost:8000/api/v1/metrics/overview > /dev/null
done

# View updated metrics
curl http://localhost:8000/metrics | grep http_requests_total
```


## 🔍 Request Tracing & Correlation

LogFlow implements distributed request tracing to track requests across the system.

### Request IDs

Every request gets a unique ID automatically:
```bash
curl -i http://localhost:8000/

# Response headers include:
X-Request-ID: 550e8400-e29b-41d4-a716-446655440000
X-Correlation-ID: 550e8400-e29b-41d4-a716-446655440000
```

### Correlation IDs

Track related requests across services:
```bash
# Send custom correlation ID
curl -H "X-Correlation-ID: my-transaction-123" \
  http://localhost:8000/api/v1/logs/search

# The correlation ID is preserved in the response
X-Correlation-ID: my-transaction-123
```

### Trace Context API

**Get current trace context:**
```bash
GET /api/v1/trace/context

Response:
{
  "request_id": "550e8400-e29b-41d4-a716-446655440000",
  "correlation_id": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2025-10-24T08:50:00.000000"
}
```

**Get debug trace (admin only):**
```bash
GET /api/v1/trace/debug
Authorization: Bearer <token>

Response:
{
  "request_id": "550e8400-e29b-41d4-a716-446655440000",
  "correlation_id": "my-transaction-123",
  "method": "GET",
  "path": "/api/v1/trace/debug",
  "headers": {...},
  "query_params": {...},
  "timestamp": "2025-10-24T08:50:00.000000",
  "user": "admin"
}
```

**Log custom trace event:**
```bash
POST /api/v1/trace/log
{
  "event": "payment_processed",
  "details": {
    "amount": 99.99,
    "status": "success"
  }
}
```

### Using Trace Context in Code
```python
from api.middleware.request_id import get_request_id, get_correlation_id

# Get current request ID
request_id = get_request_id()

# Get correlation ID
correlation_id = get_correlation_id()

# Log with context
logger.bind(
    request_id=request_id,
    correlation_id=correlation_id
).info("Processing payment")
```

### Trace Headers Flow
```
Client Request
  ↓ (X-Correlation-ID: abc-123)
API Gateway
  ↓ (X-Request-ID: req-456)
  ↓ (X-Correlation-ID: abc-123)
Service A
  ↓ (X-Request-ID: req-789)
  ↓ (X-Correlation-ID: abc-123)
Service B
  ↓ Response includes both IDs
Client
```

### Log Correlation Example
```bash
# Start a transaction
CORRELATION_ID="txn-$(date +%s)"

# Make multiple related requests
curl -H "X-Correlation-ID: $CORRELATION_ID" \
  http://localhost:8000/api/v1/auth/login

curl -H "X-Correlation-ID: $CORRELATION_ID" \
  http://localhost:8000/api/v1/logs/search

curl -H "X-Correlation-ID: $CORRELATION_ID" \
  http://localhost:8000/api/v1/alerts/rules

# All logs will have the same correlation_id
# Search logs: grep "$CORRELATION_ID" logs/*.log
```

### Testing Tracing
```bash
# Run tracing test
./scripts/test-tracing.sh

# Test with custom correlation ID
CORR_ID="my-test-$(date +%s)"
curl -H "X-Correlation-ID: $CORR_ID" \
  http://localhost:8000/ | python3 -m json.tool

# Verify correlation ID in response headers
curl -i -H "X-Correlation-ID: $CORR_ID" \
  http://localhost:8000/ | grep -i correlation
```

### Benefits

- **Debugging**: Track requests across services
- **Performance**: Identify slow request paths
- **Monitoring**: Correlate logs and metrics
- **Troubleshooting**: Follow user transactions
- **Analytics**: Analyze user journeys

### Best Practices

1. **Always preserve correlation IDs** across service boundaries
2. **Include IDs in all logs** for easy searching
3. **Use correlation IDs for transactions** spanning multiple requests
4. **Add trace context to error reports** for debugging
5. **Monitor request chains** to identify bottlenecks

