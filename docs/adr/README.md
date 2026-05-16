# Architecture Decision Records

This directory contains Architecture Decision Records (ADRs) for InsightForge. Each ADR documents a significant architectural choice: the context that motivated it, the decision made, and its consequences (positive and negative).

## Format

Each ADR follows this structure:

```
# ADR-XXXX: Title
Date | Status
## Context   — why this decision was needed
## Decision  — what was decided and key details
## Consequences — trade-offs, risks, and follow-on work
```

Statuses: **Proposed** → **Accepted** → **Deprecated** / **Superseded by ADR-XXXX**

## Index

| ID | Title | Status |
|---|---|---|
| [ADR-0001](0001-microservices-architecture.md) | Microservices Architecture | Accepted |
| [ADR-0002](0002-kafka-for-log-ingestion.md) | Apache Kafka for Log Ingestion | Accepted |
| [ADR-0003](0003-elasticsearch-for-log-storage.md) | Elasticsearch as Primary Log Storage | Accepted |
| [ADR-0004](0004-postgresql-for-relational-data.md) | PostgreSQL for Relational and Operational Data | Accepted |
| [ADR-0005](0005-redis-caching-layer.md) | Redis as the Caching Layer | Accepted |
| [ADR-0006](0006-fastapi-as-api-framework.md) | FastAPI as the API Framework | Accepted |
| [ADR-0007](0007-nextjs-typescript-dashboard.md) | Next.js with TypeScript for the Dashboard | Accepted |
| [ADR-0008](0008-docker-compose-for-local-orchestration.md) | Docker Compose for Local Orchestration | Accepted |
| [ADR-0009](0009-jwt-authentication.md) | JWT Authentication with HS256 | Accepted |
| [ADR-0010](0010-ml-anomaly-detection.md) | Statistical and ML-Based Anomaly Detection | Accepted |
| [ADR-0011](0011-distributed-tracing-with-correlation-ids.md) | Distributed Tracing with Correlation IDs | Accepted |
| [ADR-0012](0012-prometheus-metrics-and-monitoring.md) | Prometheus for Metrics and Observability | Accepted |

## Adding a New ADR

1. Copy an existing ADR file as a template.
2. Number it sequentially (`0013-your-title.md`).
3. Set status to **Proposed** until the decision is confirmed.
4. Add a row to the index table above.
5. If the new ADR supersedes an old one, update the old ADR's status to `Superseded by ADR-XXXX`.
