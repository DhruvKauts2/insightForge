"""
LogFlow REST API
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from loguru import logger
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from api.config import API_TITLE, API_VERSION, API_DESCRIPTION, API_HOST, API_PORT
from api.models.log import HealthResponse
from api.utils.elasticsearch_client import es_client

# Configure logging
logger.remove()
logger.add(sys.stderr, level="INFO")

# Create FastAPI app
app = FastAPI(
    title=API_TITLE,
    version=API_VERSION,
    description=API_DESCRIPTION,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """Run on startup"""
    logger.info(f"Starting {API_TITLE} v{API_VERSION}")
    logger.info(f"API docs available at http://{API_HOST}:{API_PORT}/docs")


@app.on_event("shutdown")
async def shutdown_event():
    """Run on shutdown"""
    logger.info("Shutting down API")


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint"""
    return {
        "name": API_TITLE,
        "version": API_VERSION,
        "status": "running",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """
    Health check endpoint
    
    Returns the health status of the API and connected services.
    """
    es_health = es_client.health()
    
    services = {
        "elasticsearch": es_health.get("status", "unknown")
    }
    
    overall_status = "healthy" if es_health.get("status") in ["green", "yellow"] else "unhealthy"
    
    return HealthResponse(
        status=overall_status,
        timestamp=datetime.now().isoformat(),
        services=services
    )


# This will be extended in Step 8 with search routes
# and Step 9 with metrics routes


if __name__ == "__main__":
    import uvicorn
    
    logger.info(f"Starting API server on {API_HOST}:{API_PORT}")
    uvicorn.run(
        app,
        host=API_HOST,
        port=API_PORT,
        log_level="info"
    )
