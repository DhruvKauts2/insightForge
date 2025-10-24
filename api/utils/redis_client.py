"""
Redis client for caching
"""
import redis
import json
from typing import Optional, Any
from loguru import logger
from config import settings

class RedisClient:
    """Redis client wrapper for caching"""
    
    def __init__(self):
        self._client = None
        self._connected = False
    
    def connect(self):
        """Connect to Redis"""
        try:
            self._client = redis.Redis(
                host=settings.redis_host,
                port=settings.redis_port,
                db=settings.redis_db,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5
            )
            # Test connection
            self._client.ping()
            self._connected = True
            logger.info(f"✅ Connected to Redis at {settings.redis_host}:{settings.redis_port}")
        except Exception as e:
            logger.warning(f"⚠️ Redis connection failed: {e}. Caching disabled.")
            self._connected = False
    
    def is_connected(self) -> bool:
        """Check if Redis is connected"""
        return self._connected
    
    def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None if not found/error
        """
        if not self._connected:
            return None
        
        try:
            value = self._client.get(key)
            if value:
                logger.debug(f"Cache HIT: {key}")
                return json.loads(value)
            logger.debug(f"Cache MISS: {key}")
            return None
        except Exception as e:
            logger.error(f"Redis GET error: {e}")
            return None
    
    def set(self, key: str, value: Any, ttl: int = 300) -> bool:
        """
        Set value in cache
        
        Args:
            key: Cache key
            value: Value to cache (will be JSON serialized)
            ttl: Time to live in seconds (default: 5 minutes)
            
        Returns:
            True if successful, False otherwise
        """
        if not self._connected:
            return False
        
        try:
            serialized = json.dumps(value)
            self._client.setex(key, ttl, serialized)
            logger.debug(f"Cache SET: {key} (TTL: {ttl}s)")
            return True
        except Exception as e:
            logger.error(f"Redis SET error: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """
        Delete key from cache
        
        Args:
            key: Cache key
            
        Returns:
            True if successful, False otherwise
        """
        if not self._connected:
            return False
        
        try:
            self._client.delete(key)
            logger.debug(f"Cache DELETE: {key}")
            return True
        except Exception as e:
            logger.error(f"Redis DELETE error: {e}")
            return False
    
    def delete_pattern(self, pattern: str) -> int:
        """
        Delete all keys matching pattern
        
        Args:
            pattern: Key pattern (e.g., "metrics:*")
            
        Returns:
            Number of keys deleted
        """
        if not self._connected:
            return 0
        
        try:
            keys = self._client.keys(pattern)
            if keys:
                deleted = self._client.delete(*keys)
                logger.debug(f"Cache DELETE pattern '{pattern}': {deleted} keys")
                return deleted
            return 0
        except Exception as e:
            logger.error(f"Redis DELETE pattern error: {e}")
            return 0
    
    def flush_all(self) -> bool:
        """
        Clear all cache (use with caution!)
        
        Returns:
            True if successful, False otherwise
        """
        if not self._connected:
            return False
        
        try:
            self._client.flushdb()
            logger.warning("Cache FLUSHED: All keys deleted")
            return True
        except Exception as e:
            logger.error(f"Redis FLUSH error: {e}")
            return False
    
    def get_stats(self) -> dict:
        """
        Get Redis statistics
        
        Returns:
            Dictionary with Redis stats
        """
        if not self._connected:
            return {"connected": False}
        
        try:
            info = self._client.info()
            return {
                "connected": True,
                "used_memory": info.get("used_memory_human"),
                "connected_clients": info.get("connected_clients"),
                "total_commands": info.get("total_commands_processed"),
                "keyspace_hits": info.get("keyspace_hits", 0),
                "keyspace_misses": info.get("keyspace_misses", 0),
                "keys": self._client.dbsize()
            }
        except Exception as e:
            logger.error(f"Redis STATS error: {e}")
            return {"connected": False, "error": str(e)}


# Global Redis client instance
redis_client = RedisClient()
