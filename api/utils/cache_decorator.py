"""
Caching decorator for endpoints
"""
from functools import wraps
from typing import Callable
from loguru import logger

from api.utils.redis_client import redis_client


def cache_response(ttl: int = 300, key_prefix: str = ""):
    """
    Decorator to cache endpoint responses
    
    Args:
        ttl: Time to live in seconds
        key_prefix: Prefix for cache key
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Build cache key from function name and args
            cache_key = f"{key_prefix}:{func.__name__}"
            
            # Add args to key if present
            if kwargs:
                key_suffix = ":".join(f"{k}={v}" for k, v in sorted(kwargs.items()) if v is not None)
                if key_suffix:
                    cache_key = f"{cache_key}:{key_suffix}"
            
            # Try cache
            cached = redis_client.get(cache_key)
            if cached:
                logger.debug(f"Cache HIT: {cache_key}")
                return cached
            
            # Execute function
            logger.debug(f"Cache MISS: {cache_key}")
            result = await func(*args, **kwargs)
            
            # Cache result
            if hasattr(result, 'dict'):
                redis_client.set(cache_key, result.dict(), ttl=ttl)
            else:
                redis_client.set(cache_key, result, ttl=ttl)
            
            return result
        
        return wrapper
    return decorator
