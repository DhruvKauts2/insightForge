"""
InsightForge REST API with Anomaly Detection
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from prometheus_fastapi_instrumentator import Instrumentator
from datetime import datetime
from loguru import logger
import sys
from pathlib import Path
from contextlib import asynccontextmanager

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from api.config import API_TITLE, API_VERSION, API_DESCRIPTION, API_HOST, API_PORT
from api.models.log import HealthResponse
from api.utils.elasticsearch_client import es_client
from api.utils.database import check_database_health
from api.utils.redis_client import redis_client
from api.utils.rate_limiter import limiter
from api.middleware.metrics import PrometheusMiddleware
from api.middleware.request_id import RequestIDMiddleware
from api.routes import (
    search, metrics, alerts, auth, cache, 
    rate_limits, metrics_prometheus, tracing, websocket, correlation, anomaly
)

logger.remove()
logger.add(sys.stderr, level="INFO")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan events"""
    # Startup
    logger.info(f"Starting {API_TITLE} v{API_VERSION}")
    redis_client.connect()
    logger.info(f"API docs available at http://{API_HOST}:{API_PORT}/docs")
    logger.info(f"Prometheus metrics at http://{API_HOST}:{API_PORT}/metrics")
    logger.info(f"WebSocket endpoints available at ws://{API_HOST}:{API_PORT}/ws/*")
    logger.info(f"ML-based anomaly detection enabled")
    yield
    # Shutdown
    logger.info("Shutting down API")


app = FastAPI(
    title=API_TITLE,
    version=API_VERSION,
    description=API_DESCRIPTION,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Add Request ID middleware FIRST
app.add_middleware(RequestIDMiddleware)

# Add Prometheus instrumentator
Instrumentator().instrument(app).expose(app, endpoint="/metrics/fastapi")

# Add custom Prometheus middleware
app.add_middleware(PrometheusMiddleware)

# Add rate limiter state
app.state.limiter = limiter

# Add slowapi middleware for rate limiting
app.add_middleware(SlowAPIMiddleware)

# Add rate limit exceeded handler
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(websocket.router)
app.include_router(metrics_prometheus.router)
app.include_router(tracing.router)
app.include_router(correlation.router)
app.include_router(anomaly.router)
app.include_router(auth.router)
app.include_router(search.router)
app.include_router(metrics.router)
app.include_router(alerts.router)
app.include_router(cache.router)
app.include_router(rate_limits.router)


@app.get("/", tags=["Root"])
@limiter.limit("60/minute")
async def root(request: Request):
    """Root endpoint"""
    return {
        "name": API_TITLE,
        "version": API_VERSION,
        "status": "running",
        "request_id": request.state.request_id,
        "correlation_id": request.state.correlation_id,
        "docs": "/docs",
        "health": "/health",
        "features": {
            "websocket": "ws://localhost:8000/ws/*",
            "metrics": "/metrics",
            "tracing": "/api/v1/trace",
            "correlation": "/api/v1/correlation",
            "anomaly_detection": "/api/v1/anomaly"
        },
        "endpoints": {
            "auth": "/api/v1/auth",
            "search": "/api/v1/logs/search",
            "metrics": "/api/v1/metrics/overview",
            "alerts": "/api/v1/alerts/rules",
            "cache": "/api/v1/cache",
            "trace": "/api/v1/trace",
            "correlation": "/api/v1/correlation",
            "anomaly": "/api/v1/anomaly"
        }
    }


@app.get("/health", response_model=HealthResponse, tags=["Health"])
@limiter.exempt
async def health_check(request: Request):
    """Health check endpoint"""
    es_health = es_client.health()
    db_health = check_database_health()
    redis_stats = redis_client.get_stats()
    
    services = {
        "elasticsearch": es_health.get("status", "unknown"),
        "database": db_health.get("status", "unknown"),
        "redis": "healthy" if redis_stats.get("connected") else "unhealthy"
    }
    
    overall_status = "healthy" if all(
        status in ["healthy", "green", "yellow"] 
        for status in services.values()
    ) else "unhealthy"
    
    return HealthResponse(
        status=overall_status,
        timestamp=datetime.now().isoformat(),
        services=services
    )


if __name__ == "__main__":
    import uvicorn
    
    logger.info(f"Starting API server on {API_HOST}:{API_PORT}")
    uvicorn.run(
        app,
        host=API_HOST,
        port=API_PORT,
        log_level="info"
    )
