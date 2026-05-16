# ADR-0006: FastAPI as the API Framework

**Date:** 2026-05-16  
**Status:** Accepted

## Context

The API service must handle concurrent requests from multiple dashboard clients while performing I/O-bound operations (Elasticsearch queries, PostgreSQL reads, Redis lookups, Kafka interactions). A synchronous WSGI framework (Flask, Django) would block a thread per request during every I/O wait, requiring many threads to achieve concurrency. We also need automatic OpenAPI documentation, request validation from typed schemas, and easy WebSocket support for real-time dashboard updates.

## Decision

Use FastAPI 0.104+ running on Uvicorn (4 workers) as the API framework. All route handlers are `async def` functions. Pydantic 2.5 models are used for request and response validation. WebSocket endpoints under `/ws/` are served by the same Uvicorn process.

The middleware stack is:
1. `RequestIDMiddleware` — attaches a unique `X-Request-ID` to every request
2. `PrometheusMiddleware` — records request duration and count metrics
3. `SlowAPIMiddleware` — enforces per-endpoint rate limits (60/min general, 10/min health)
4. `CORSMiddleware` — currently allows all origins (to be restricted in production)

## Consequences

**Positive**
- Async I/O allows a single Uvicorn worker to handle many concurrent requests efficiently without the overhead of threads.
- Pydantic v2 provides fast, type-safe request/response validation with clear error messages.
- FastAPI generates OpenAPI docs at `/docs` automatically from type annotations — no separate doc maintenance.
- WebSocket support is native, enabling the real-time dashboard update feature without a separate push server.
- The lifespan context manager handles startup (DB pool init, Elasticsearch client) and shutdown (connection cleanup) cleanly.

**Negative**
- Uvicorn with 4 workers means 4 processes sharing no in-process state; any state stored in process memory (e.g., in-memory caches not backed by Redis) will be inconsistent across workers.
- CORS is currently open (`allow_origins=["*"]`); this must be tightened before public exposure.
- Rate limiting via slowapi is per-process, not cluster-wide; a single IP can effectively send 4× the configured limit across workers without a shared counter backend.
- CPU-bound work (ML anomaly detection with scikit-learn) blocks the event loop; these calls should eventually be offloaded to a thread pool or separate worker process.
