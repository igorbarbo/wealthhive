"""
Redis cache client with connection pooling
"""

import json
from typing import Any, Optional

import redis.asyncio as redis

from app.config import settings


class RedisCache:
    """Async Redis cache client"""
    
    _instance = None
    _pool = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    async def connect(self):
        """Initialize Redis connection pool"""
        if self._pool is None:
            self._pool = redis.ConnectionPool.from_url(
                str(settings.REDIS_URL),
                max_connections=settings.REDIS_POOL_SIZE,
                decode_responses=True,
            )
            self._client = redis.Redis(connection_pool=self._pool)
    
    async def disconnect(self):
        """Close Redis connections"""
        if self._pool:
            await self._pool.disconnect()
            self._pool = None
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        if not self._pool:
            await self.connect()
        
        try:
            value = await self._client.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception:
            return None
    
    async def set(
        self,
        key: str,
        value: Any,
        ttl: int = 300,  # 5 minutes default
    ) -> bool:
        """Set value in cache"""
        if not self._pool:
            await self.connect()
        
        try:
            serialized = json.dumps(value, default=str)
            await self._client.setex(key, ttl, serialized)
            return True
        except Exception:
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete key from cache"""
        if not self._pool:
            await self.connect()
        
        try:
            await self._client.delete(key)
            return True
        except Exception:
            return False
    
    async def exists(self, key: str) -> bool:
        """Check if key exists"""
        if not self._pool:
            await self.connect()
        
        try:
            return await self._client.exists(key) > 0
        except Exception:
            return False
    
    async def increment(self, key: str, amount: int = 1) -> int:
        """Increment counter"""
        if not self._pool:
            await self.connect()
        
        return await self._client.incrby(key, amount)
    
    async def expire(self, key: str, ttl: int) -> bool:
        """Set expiration on key"""
        if not self._pool:
            await self.connect()
        
        return await self._client.expire(key, ttl)
    
    async def health_check(self) -> bool:
        """Check Redis connectivity"""
        try:
            if not self._pool:
                await self.connect()
            await self._client.ping()
            return True
        except Exception:
            return False
