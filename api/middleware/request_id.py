"""
Request ID and tracing middleware
"""
import uuid
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from loguru import logger
import contextvars

# Context variable to store request ID across async calls
request_id_var = contextvars.ContextVar('request_id', default=None)
correlation_id_var = contextvars.ContextVar('correlation_id', default=None)


class RequestIDMiddleware(BaseHTTPMiddleware):
    """
    Middleware to add request ID and correlation ID to all requests
    """
    
    async def dispatch(self, request: Request, call_next):
        # Generate or extract request ID
        request_id = request.headers.get('X-Request-ID') or str(uuid.uuid4())
        
        # Extract correlation ID (for cross-service tracing)
        correlation_id = request.headers.get('X-Correlation-ID') or request_id
        
        # Store in context variables
        request_id_var.set(request_id)
        correlation_id_var.set(correlation_id)
        
        # Add to request state for easy access
        request.state.request_id = request_id
        request.state.correlation_id = correlation_id
        
        # Log request with IDs
        logger.bind(
            request_id=request_id,
            correlation_id=correlation_id,
            method=request.method,
            path=request.url.path
        ).info(f"Request started: {request.method} {request.url.path}")
        
        # Process request
        response = await call_next(request)
        
        # Add IDs to response headers
        response.headers['X-Request-ID'] = request_id
        response.headers['X-Correlation-ID'] = correlation_id
        
        # Log response
        logger.bind(
            request_id=request_id,
            correlation_id=correlation_id,
            status_code=response.status_code
        ).info(f"Request completed: {response.status_code}")
        
        return response


def get_request_id() -> str:
    """Get current request ID from context"""
    return request_id_var.get()


def get_correlation_id() -> str:
    """Get current correlation ID from context"""
    return correlation_id_var.get()
