"""
Rate limiting utility using Redis
"""
from slowapi import Limiter
from slowapi.util import get_remote_address
from fastapi import Request
from typing import Callable
from loguru import logger

from api.utils.redis_client import redis_client


def get_user_id_or_ip(request: Request) -> str:
    """
    Get user ID if authenticated, otherwise IP address
    
    This allows different rate limits for authenticated vs anonymous users
    """
    # Try to get user from request state (set by auth middleware)
    if hasattr(request.state, "user"):
        user = request.state.user
        identifier = f"user:{user.id}"
        logger.debug(f"Rate limit identifier: {identifier}")
        return identifier
    
    # Fall back to IP address
    ip = get_remote_address(request)
    identifier = f"ip:{ip}"
    logger.debug(f"Rate limit identifier: {identifier}")
    return identifier


def get_redis_for_limiter():
    """
    Get Redis connection for rate limiter
    
    Returns Redis client or None if not connected
    """
    if redis_client.is_connected():
        return redis_client._client
    logger.warning("Redis not available for rate limiting")
    return None


# Create limiter instance
limiter = Limiter(
    key_func=get_user_id_or_ip,
    storage_uri="memory://",  # Fallback to in-memory if Redis unavailable
    default_limits=["100/minute"],  # Default limit for all endpoints
    enabled=True
)


def setup_redis_storage():
    """
    Setup Redis as storage backend for rate limiting
    
    Call this after Redis is connected
    """
    if redis_client.is_connected():
        try:
            # Update limiter to use Redis
            from slowapi.util import get_ipaddr
            limiter.storage_uri = f"redis://{redis_client._client.connection_pool.connection_kwargs['host']}:{redis_client._client.connection_pool.connection_kwargs['port']}"
            logger.info("✅ Rate limiter using Redis storage")
        except Exception as e:
            logger.warning(f"Could not setup Redis for rate limiting: {e}")
