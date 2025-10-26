"""
Request tracing and debugging routes
"""
from fastapi import APIRouter, Request, Depends
from typing import List, Optional
from loguru import logger
from datetime import datetime

from api.models.trace import RequestTrace, TraceContext, DebugTrace
from api.middleware.request_id import get_request_id, get_correlation_id
from api.utils.auth import get_current_admin, get_current_user
from api.models.database import User

router = APIRouter(prefix="/api/v1/trace", tags=["Tracing"])


@router.get("/context", response_model=TraceContext)
async def get_trace_context(request: Request):
    """
    Get current request trace context
    
    Returns the request ID and correlation ID for the current request
    """
    return TraceContext(
        request_id=request.state.request_id,
        correlation_id=request.state.correlation_id
    )


@router.get("/debug", response_model=DebugTrace)
async def get_debug_trace(
    request: Request,
    current_user: User = Depends(get_current_admin)
):
    """
    Get detailed debug trace for current request (admin only)
    
    Includes headers, query params, and full request context
    """
    # Get headers (exclude sensitive ones)
    headers = dict(request.headers)
    sensitive_headers = ['authorization', 'cookie', 'x-api-key']
    for header in sensitive_headers:
        if header in headers:
            headers[header] = '***REDACTED***'
    
    return DebugTrace(
        request_id=request.state.request_id,
        correlation_id=request.state.correlation_id,
        method=request.method,
        path=str(request.url.path),
        headers=headers,
        query_params=dict(request.query_params),
        timestamp=datetime.now().isoformat(),
        user=current_user.username
    )


@router.post("/log")
async def log_trace_event(
    request: Request,
    event: str,
    details: Optional[dict] = None
):
    """
    Log a custom trace event
    
    Useful for tracking specific events in the request flow
    """
    logger.bind(
        request_id=request.state.request_id,
        correlation_id=request.state.correlation_id,
        event=event,
        details=details or {}
    ).info(f"Trace event: {event}")
    
    return {
        "message": "Event logged",
        "event": event,
        "request_id": request.state.request_id,
        "correlation_id": request.state.correlation_id
    }


@router.get("/health-traced")
async def health_check_traced(request: Request):
    """
    Health check with tracing headers
    
    Use this to test request tracing
    """
    return {
        "status": "healthy",
        "request_id": request.state.request_id,
        "correlation_id": request.state.correlation_id,
        "timestamp": datetime.now().isoformat(),
        "message": "Request tracing is working!"
    }
