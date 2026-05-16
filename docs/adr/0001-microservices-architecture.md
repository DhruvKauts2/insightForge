# ADR-0001: Microservices Architecture

**Date:** 2026-05-16  
**Status:** Accepted

## Context

InsightForge needs to ingest high volumes of log data from multiple services, process it in near real-time, run ML-based anomaly detection, evaluate alert rules, and serve a read-heavy analytics API — all with different scaling characteristics. A monolithic application would couple these concerns, making it hard to scale the ingestion path independently from the query path and impossible to deploy them at different cadences.

## Decision

Adopt a microservices architecture composed of five discrete processes:

| Service | Responsibility |
|---|---|
| `api` | REST + WebSocket query surface, auth, rate limiting |
| `consumer` | Kafka → Elasticsearch batch indexer |
| `alerting` | Continuous alert-rule evaluation and notification |
| `shipper` | Log forwarding from sources to Kafka |
| `log_generator` | Synthetic load generation for testing |

Each service has its own `Dockerfile`, its own process boundary, and communicates only through well-defined channels (Kafka topics, shared databases, HTTP).

## Consequences

**Positive**
- The consumer can be scaled independently when ingestion volume spikes without touching the API.
- Alert evaluation runs on its own cadence (60 s) without blocking query serving.
- Services can be developed and deployed independently.
- Failures in one service (e.g., alert engine) do not crash the query API.

**Negative**
- Operational complexity: five services to monitor, deploy, and health-check.
- Distributed tracing and correlation IDs are required to debug cross-service flows.
- Local development requires Docker Compose to wire all dependencies together.
- Data consistency across Elasticsearch + PostgreSQL must be managed by application code, not a single transaction boundary.
