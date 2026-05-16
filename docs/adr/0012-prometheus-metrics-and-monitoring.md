# ADR-0012: Prometheus for Metrics and Observability

**Date:** 2026-05-16  
**Status:** Accepted

## Context

Operating a system with multiple services and a message queue requires visibility into request rates, error rates, latency distributions, and queue consumer lag. Without structured metrics, diagnosing performance regressions requires grepping log files — slow and unreliable. We need a metrics pipeline that developers and on-call engineers can query in real time and that can drive alerts.

## Decision

Expose Prometheus-format metrics from the API service at two endpoints:
- `/metrics` — custom application metrics (log ingestion rate, anomaly counts, alert triggers)
- `/metrics/fastapi` — HTTP request duration histograms and counts via `prometheus-fastapi-instrumentator 7.0+`

Prometheus scrapes both endpoints every 15 seconds as configured in `prometheus.yml`. The `prometheus-client 0.19+` library provides the Python instrumentation primitives (`Counter`, `Histogram`, `Gauge`).

A `PrometheusMiddleware` in the FastAPI middleware stack records per-route latency before any application logic runs, ensuring all requests are measured even if they raise exceptions.

## Consequences

**Positive**
- Standard Prometheus exposition format means any Prometheus-compatible visualization (Grafana, built-in Prometheus UI) works immediately.
- `prometheus-fastapi-instrumentator` instruments all routes automatically without per-route boilerplate.
- 15-second scrape interval gives near-real-time visibility into API health.
- Metrics survive individual request failures; aggregate data is not lost when a single request errors.

**Negative**
- Prometheus is currently defined in `prometheus.yml` but no Grafana service or Alertmanager is included in `docker-compose.yml`; the scraped metrics are not visualized or alerted on out of the box.
- Prometheus's pull model requires the API container to be network-accessible to the Prometheus container; this is satisfied by `insightforge-network` but becomes a firewall concern in production.
- No Kafka consumer lag metrics (e.g., via `kafka-consumer-groups.sh` or JMX exporter); the most important pipeline health signal is currently invisible.
- Cardinality risk: if custom metrics ever use unbounded label values (e.g., `correlation_id` as a label), Prometheus memory usage will grow without bound.
