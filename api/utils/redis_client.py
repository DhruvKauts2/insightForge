"""
Redis client for caching
"""
import redis
from typing import Optional, Any
import json
from loguru import logger

from api.config import settings


class RedisClient:
    """Redis client for caching"""
    
    def __init__(self):
        self.client: Optional[redis.Redis] = None
        self.enabled = False
    
    def connect(self):
        """Connect to Redis"""
        try:
            self.client = redis.Redis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                db=settings.REDIS_DB,
                decode_responses=True,
                socket_connect_timeout=5
            )
            
            # Test connection
            self.client.ping()
            self.enabled = True
            logger.info(f"✅ Connected to Redis at {settings.REDIS_HOST}:{settings.REDIS_PORT}")
            
        except Exception as e:
            logger.warning(f"⚠️ Redis connection failed: {e}. Caching disabled.")
            self.enabled = False
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        if not self.enabled or not self.client:
            return None
        
        try:
            value = self.client.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            logger.error(f"Redis GET error: {e}")
            return None
    
    def set(self, key: str, value: Any, ttl: int = 300):
        """Set value in cache with TTL"""
        if not self.enabled or not self.client:
            return False
        
        try:
            serialized = json.dumps(value)
            self.client.setex(key, ttl, serialized)
            return True
        except Exception as e:
            logger.error(f"Redis SET error: {e}")
            return False
    
    def delete(self, key: str):
        """Delete key from cache"""
        if not self.enabled or not self.client:
            return False
        
        try:
            self.client.delete(key)
            return True
        except Exception as e:
            logger.error(f"Redis DELETE error: {e}")
            return False
    
    def health_check(self) -> bool:
        """Check if Redis is healthy"""
        if not self.enabled or not self.client:
            return False
        
        try:
            return self.client.ping()
        except:
            return False


# Global Redis client instance
redis_client = RedisClient()
