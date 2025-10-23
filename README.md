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
