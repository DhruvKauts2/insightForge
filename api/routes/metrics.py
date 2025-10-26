"""
Metrics and aggregation routes using metrics service
"""
from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from loguru import logger

from api.services.metrics import metrics_service

router = APIRouter(prefix="/api/v1/metrics", tags=["Metrics"])


@router.get("/overview")
async def get_metrics_overview():
    """Get metrics overview for all logs"""
    try:
        return await metrics_service.get_overview()
    except Exception as e:
        logger.error(f"Metrics overview error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get metrics: {str(e)}"
        )


@router.get("/services")
async def get_service_metrics(
    minutes: int = Query(60, ge=1, le=10080, description="Time window in minutes")
):
    """Get metrics by service"""
    try:
        return await metrics_service.get_service_metrics(minutes=minutes)
    except Exception as e:
        logger.error(f"Service metrics error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get service metrics: {str(e)}"
        )


@router.get("/log-volume")
async def get_log_volume(
    minutes: int = Query(60, ge=1, le=10080, description="Time window in minutes")
):
    """Get log volume over time"""
    try:
        return await metrics_service.get_log_volume(minutes=minutes)
    except Exception as e:
        logger.error(f"Log volume error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get log volume: {str(e)}"
        )
