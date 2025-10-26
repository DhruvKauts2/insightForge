"""
Rate limit management routes (admin only)
"""
from fastapi import APIRouter, Depends, Request
from loguru import logger

from api.utils.redis_client import redis_client
from api.utils.auth import get_current_admin
from api.utils.rate_limiter import limiter
from api.models.database import User

router = APIRouter(prefix="/api/v1/rate-limits", tags=["Rate Limits"])


@router.get("/status")
@limiter.limit("30/minute")
async def get_rate_limit_status(
    request: Request,
    current_user: User = Depends(get_current_admin)
):
    """Get rate limit status (admin only)"""
    if not redis_client.is_connected():
        return {
            "backend": "in-memory",
            "message": "Redis not available, using in-memory rate limiting"
        }
    
    keys = redis_client._client.keys("LIMITER*")
    
    return {
        "backend": "redis",
        "total_tracked": len(keys),
        "keys": keys[:50]
    }


@router.delete("/reset/{identifier}")
@limiter.limit("10/minute")
async def reset_rate_limit(
    request: Request,
    identifier: str,
    current_user: User = Depends(get_current_admin)
):
    """Reset rate limit for specific user/IP (admin only)"""
    if not redis_client.is_connected():
        return {"message": "Redis not available, cannot reset limits"}
    
    pattern = f"LIMITER*{identifier}*"
    deleted = redis_client.delete_pattern(pattern)
    
    logger.info(f"Admin {current_user.username} reset rate limits for {identifier}")
    
    return {
        "message": f"Rate limits reset for {identifier}",
        "keys_deleted": deleted
    }


@router.delete("/reset-all")
@limiter.limit("5/hour")
async def reset_all_rate_limits(
    request: Request,
    current_user: User = Depends(get_current_admin)
):
    """Reset ALL rate limits (admin only)"""
    if not redis_client.is_connected():
        return {"message": "Redis not available, cannot reset limits"}
    
    deleted = redis_client.delete_pattern("LIMITER*")
    
    logger.warning(f"Admin {current_user.username} reset ALL rate limits!")
    
    return {
        "message": "All rate limits reset",
        "keys_deleted": deleted
    }
