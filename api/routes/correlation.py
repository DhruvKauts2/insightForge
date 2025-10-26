"""
Log correlation API routes
"""
from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from loguru import logger

from api.models.correlation import RequestFlow, DependencyGraph, CorrelatedLog
from api.services.correlation import correlation_service

router = APIRouter(prefix="/api/v1/correlation", tags=["Log Correlation"])


@router.get("/trace/{correlation_id}", response_model=RequestFlow)
async def get_request_trace(correlation_id: str):
    """
    Get complete request trace by correlation ID
    
    Returns all service calls for a specific transaction
    """
    try:
        flow = await correlation_service.get_request_flow(correlation_id)
        
        if not flow:
            raise HTTPException(
                status_code=404,
                detail=f"No logs found for correlation ID: {correlation_id}"
            )
        
        return flow
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting request trace: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/related/{log_id}", response_model=list[CorrelatedLog])
async def get_related_logs(
    log_id: str,
    time_window: int = Query(60, ge=1, le=3600, description="Time window in seconds")
):
    """
    Get logs related to a specific log
    
    Finds logs in the same service or with the same correlation ID
    within the specified time window
    """
    try:
        related_logs = await correlation_service.get_related_logs(log_id, time_window)
        return related_logs
        
    except Exception as e:
        logger.error(f"Error getting related logs: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/dependencies", response_model=DependencyGraph)
async def get_service_dependencies(
    time_window: int = Query(24, ge=1, le=168, description="Time window in hours")
):
    """
    Get service dependency graph
    
    Analyzes correlation IDs to determine which services call each other
    """
    try:
        graph = await correlation_service.get_service_dependencies(time_window)
        return graph
        
    except Exception as e:
        logger.error(f"Error getting service dependencies: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/service/{service_name}/traces")
async def get_service_traces(
    service_name: str,
    limit: int = Query(100, ge=1, le=500)
):
    """
    Get recent correlation IDs for a service
    
    Returns list of correlation IDs that involve the specified service
    """
    try:
        correlation_ids = await correlation_service.find_correlation_ids_by_service(
            service_name,
            limit
        )
        
        return {
            "service": service_name,
            "correlation_ids": correlation_ids,
            "total": len(correlation_ids)
        }
        
    except Exception as e:
        logger.error(f"Error getting service traces: {e}")
        raise HTTPException(status_code=500, detail=str(e))
