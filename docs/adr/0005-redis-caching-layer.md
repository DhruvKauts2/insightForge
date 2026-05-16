# ADR-0005: Redis as the Caching Layer

**Date:** 2026-05-16  
**Status:** Accepted

## Context

The dashboard polls the API every 30–60 seconds for metrics aggregations (log volume over time, error rate by service, anomaly summaries). These queries fan out to Elasticsearch aggregations that are expensive relative to how often the underlying data changes. Running the same aggregation for every dashboard client on every poll cycle creates unnecessary load on Elasticsearch and increases API latency.

## Decision

Introduce Redis 7 (Alpine) as an in-process cache for computed metrics and search results. A `cache_decorator` utility (`api/utils/cache_decorator.py`) wraps expensive service methods. Cache entries have a default TTL of 5 minutes. The `/api/v1/cache/` endpoint exposes cache management operations for operator use.

Redis is used exclusively as a volatile cache — it is not a source of truth. Cache misses fall through to Elasticsearch. Redis data is not persisted to disk (no AOF or RDB snapshots configured).

## Consequences

**Positive**
- Repeated dashboard polling for the same time-window aggregation hits Redis in memory instead of Elasticsearch, significantly reducing cluster load.
- The cache decorator makes it easy to add caching to new service methods without duplicating cache logic.
- Redis 7 Alpine image is lightweight and starts quickly.
- TTL expiry provides automatic cache invalidation without a separate invalidation bus.

**Negative**
- Stale data window: dashboards may show results up to 5 minutes behind live data. This is acceptable for aggregated metrics but not for real-time alert status.
- Adding Redis as a required service means the API degrades (not just slows) if Redis is unreachable unless circuit-breaker logic is added.
- No cache warming on startup: the first requests after deployment or Redis restart are always slow.
- No distributed cache invalidation: if alert data changes mid-TTL, the cache will return stale results until expiry.
