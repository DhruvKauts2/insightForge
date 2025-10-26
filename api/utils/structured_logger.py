"""
Structured logging with request context
"""
from loguru import logger
import sys
import json
from typing import Any, Dict
from api.middleware.request_id import get_request_id, get_correlation_id


def setup_structured_logging():
    """
    Setup structured JSON logging with request context
    """
    
    def serialize(record):
        """Serialize log record to JSON"""
        subset = {
            "timestamp": record["time"].isoformat(),
            "level": record["level"].name,
            "message": record["message"],
            "module": record["name"],
            "function": record["function"],
            "line": record["line"],
        }
        
        # Add request context if available
        try:
            request_id = get_request_id()
            correlation_id = get_correlation_id()
            
            if request_id:
                subset["request_id"] = request_id
            if correlation_id:
                subset["correlation_id"] = correlation_id
        except:
            pass
        
        # Add extra fields from record
        if record["extra"]:
            subset["extra"] = record["extra"]
        
        return json.dumps(subset)
    
    def patching(record):
        """Add serialized version to record"""
        record["extra"]["serialized"] = serialize(record)
    
    # Remove default logger
    logger.remove()
    
    # Add structured JSON logger
    logger = logger.patch(patching)
    logger.add(
        sys.stderr,
        format="{extra[serialized]}",
        level="INFO"
    )
    
    return logger


def log_with_context(level: str, message: str, **kwargs):
    """
    Log message with request context
    
    Args:
        level: Log level (info, warning, error, etc.)
        message: Log message
        **kwargs: Additional context
    """
    try:
        request_id = get_request_id()
        correlation_id = get_correlation_id()
        
        log_func = getattr(logger, level.lower())
        log_func(
            message,
            request_id=request_id,
            correlation_id=correlation_id,
            **kwargs
        )
    except Exception as e:
        logger.error(f"Error logging with context: {e}")
