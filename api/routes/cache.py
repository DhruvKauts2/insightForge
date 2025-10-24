"""
Cache management routes
"""
from fastapi import APIRouter, HTTPException, Depends
from loguru import logger

from api.utils.redis_client import redis_client
from api.utils.auth import get_current_admin
from api.models.database import User

router = APIRouter(prefix="/api/v1/cache", tags=["Cache"])


@router.get("/stats")
async def get_cache_stats():
    """
    Get Redis cache statistics
    """
    try:
        stats = redis_client.get_stats()
        return stats
    except Exception as e:
        logger.error(f"Cache stats error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get cache stats: {str(e)}")


@router.delete("/clear")
async def clear_cache(
    pattern: str = "*",
    current_user: User = Depends(get_current_admin)
):
    """
    Clear cache by pattern (admin only)
    
    Examples:
    - pattern="*" - Clear all cache
    - pattern="metrics:*" - Clear all metrics cache
    - pattern="metrics:service:*" - Clear all service metrics cache
    """
    try:
        if pattern == "*":
            redis_client.flush_all()
            return {"message": "All cache cleared"}
        else:
            deleted = redis_client.delete_pattern(pattern)
            return {
                "message": f"Cache cleared for pattern: {pattern}",
                "keys_deleted": deleted
            }
    except Exception as e:
        logger.error(f"Cache clear error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to clear cache: {str(e)}")
