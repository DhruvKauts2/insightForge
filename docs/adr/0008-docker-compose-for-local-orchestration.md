# ADR-0008: Docker Compose for Local and Development Orchestration

**Date:** 2026-05-16  
**Status:** Accepted

## Context

InsightForge depends on six external systems: Zookeeper, Kafka, Elasticsearch, PostgreSQL, Redis, and the Next.js dashboard — in addition to the Python API. Running all of these processes manually during development is error-prone and not reproducible across machines. We need a way to start the full stack deterministically with a single command, ensure services start in dependency order, and provide health checks so dependent services do not start before their dependencies are ready.

## Decision

Use Docker Compose 3.8 to define and orchestrate the full development stack. Each service runs in its own container, built from either an official image (Kafka, Elasticsearch, PostgreSQL, Redis) or a project-local `Dockerfile`. All containers are connected via a custom bridge network `insightforge-network`. Persistent data (Elasticsearch index data, PostgreSQL tables) is stored in named Docker volumes (`elasticsearch-data`, `postgres-data`).

Health checks with `condition: service_healthy` enforce startup order:
```
Zookeeper → Kafka → Elasticsearch + PostgreSQL + Redis → API
```

Docker images for Python services use multi-stage builds and run as non-root user `1000` to follow the principle of least privilege.

## Consequences

**Positive**
- `docker compose up` starts the entire stack reproducibly on any machine with Docker installed.
- Health checks prevent the common race condition where the API starts before PostgreSQL is ready to accept connections.
- Named volumes preserve data between container restarts during development.
- Non-root containers reduce the blast radius of a container escape vulnerability.
- Each service's environment is isolated — no Python version or library conflicts between services.

**Negative**
- Docker Compose is not the right tool for production; Kubernetes or a managed container platform is needed for autoscaling, rolling deploys, and multi-node resilience.
- The Compose file hard-codes credentials and configuration that should be supplied via an external secrets manager in production.
- `insightforge-network` is a single flat network; there is no network segmentation between, for example, the API and Kafka (any container can reach any other).
- Heavy resource usage: running all containers simultaneously requires significant RAM (Elasticsearch alone defaults to 1 GB JVM heap).
- The PostgreSQL container is only reachable from inside `insightforge-network`; developer tooling (DBeaver, pgAdmin) must connect via the exposed port mapping.
