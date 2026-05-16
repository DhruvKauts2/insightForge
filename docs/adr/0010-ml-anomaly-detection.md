# ADR-0010: Statistical and ML-Based Anomaly Detection

**Date:** 2026-05-16  
**Status:** Accepted

## Context

InsightForge needs to surface abnormal patterns in log metrics (error rate, log volume, latency) without requiring users to manually define thresholds for every service. Static thresholds require domain knowledge and become stale as traffic patterns change. The system should detect anomalies in both simple univariate metrics (error rate over time) and multivariate patterns that individual threshold rules cannot capture.

## Decision

Implement three complementary anomaly detection algorithms in `api/services/anomaly_detector.py`, all operating on time-windowed metric snapshots fetched from Elasticsearch:

| Algorithm | Use Case | Implementation |
|---|---|---|
| Z-Score | Point anomalies in a univariate series (e.g., sudden spike in error count) | `scipy.stats.zscore` with configurable threshold |
| Moving Average | Trend deviation detection over a sliding window | Rolling mean ± N standard deviations |
| Isolation Forest | Multivariate anomaly detection without labeled training data | `sklearn.ensemble.IsolationForest` |

Detection is triggered on demand via `GET /api/v1/anomaly/detect/{metric_type}?window_minutes=N`. Results include a severity score and category. Detected anomalies are stored in PostgreSQL for historical review.

## Consequences

**Positive**
- Three algorithms with different sensitivities allow operators to tune detection to their signal type.
- Isolation Forest requires no labeled anomaly data — it learns the "normal" envelope from recent history alone.
- On-demand detection avoids the overhead of continuous background ML inference against every metric stream.
- scikit-learn and scipy are already in the dependency tree for other analytics use cases.

**Negative**
- All three algorithms run synchronously in the FastAPI async event loop; CPU-bound scikit-learn calls will block other requests for the duration of inference. These should be moved to a `ThreadPoolExecutor` or separate worker.
- Detection quality depends on having sufficient history in the `window_minutes` lookback. A freshly started system with sparse data produces noisy results.
- Isolation Forest has no online/incremental training mode; the contamination parameter is fixed at initialization, not learned from feedback.
- No feedback loop: false positives are not used to retrain or tune the model. Over time, models may drift as traffic patterns evolve.
- Z-Score and Moving Average assume approximate stationarity and normality of the underlying metric; they perform poorly on metrics with strong daily or weekly seasonality (e.g., log volume that's 10× higher during business hours).
