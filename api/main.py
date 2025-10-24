"""
LogFlow REST API with Caching
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
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
from api.routes import search, metrics, alerts, auth, cache

logger.remove()
logger.add(sys.stderr, level="INFO")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan events"""
    # Startup
    logger.info(f"Starting {API_TITLE} v{API_VERSION}")
    redis_client.connect()
    logger.info(f"API docs available at http://{API_HOST}:{API_PORT}/docs")
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

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(search.router)
app.include_router(metrics.router)
app.include_router(alerts.router)
app.include_router(cache.router)


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint"""
    return {
        "name": API_TITLE,
        "version": API_VERSION,
        "status": "running",
        "docs": "/docs",
        "health": "/health",
        "cache": "/api/v1/cache/stats",
        "endpoints": {
            "auth": "/api/v1/auth",
            "search": "/api/v1/logs/search",
            "metrics": "/api/v1/metrics/overview",
            "alerts": "/api/v1/alerts/rules",
            "cache": "/api/v1/cache"
        }
    }


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
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
