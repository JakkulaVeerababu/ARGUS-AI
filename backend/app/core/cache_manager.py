import json
import time
import threading
from collections import OrderedDict
from typing import Any, Optional
from loguru import logger
import redis

from backend.app.core.settings import settings

class TTLLRUCache:
    """A thread-safe In-Memory LRU Cache with TTL support."""
    def __init__(self, capacity: int = 2000, default_ttl: int = 300):
        self.capacity = capacity
        self.default_ttl = default_ttl
        self.cache = OrderedDict()
        self.lock = threading.Lock()

    def get(self, key: str) -> Optional[Any]:
        with self.lock:
            if key not in self.cache:
                return None
            value, expiry = self.cache[key]
            if expiry is not None and time.time() > expiry:
                del self.cache[key]
                return None
            # Move key to end to represent most recently used
            self.cache.move_to_end(key)
            return value

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        with self.lock:
            if key in self.cache:
                del self.cache[key]
            elif len(self.cache) >= self.capacity:
                # Evict expired keys first to free space
                now = time.time()
                expired_keys = [k for k, (_, exp) in self.cache.items() if exp is not None and now > exp]
                for k in expired_keys:
                    del self.cache[k]
                
                # If still at capacity, evict the least recently used
                if len(self.cache) >= self.capacity:
                    self.cache.popitem(last=False)
            
            actual_ttl = ttl if ttl is not None else self.default_ttl
            expiry = time.time() + actual_ttl if actual_ttl is not None else None
            self.cache[key] = (value, expiry)


class CacheManager:
    """
    Singleton Cache Manager supporting Redis caching with a robust 
    in-memory TTL LRU fallback when Redis is offline or unavailable.
    """
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(CacheManager, cls).__new__(cls)
                cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        with self._lock:
            if self._initialized:
                return
            self._initialized = True
            self.redis_client = None
            self.use_redis = False
            self.local_cache = TTLLRUCache(capacity=2000, default_ttl=settings.CACHE_TTL)
            
            if settings.REDIS_URL:
                try:
                    logger.info(f"CacheManager: Connecting to Redis at {settings.REDIS_URL}...")
                    # 2-second timeout to avoid hanging FastAPI startup
                    self.redis_client = redis.Redis.from_url(
                        settings.REDIS_URL,
                        socket_connect_timeout=2.0,
                        socket_timeout=2.0,
                        decode_responses=True
                    )
                    self.redis_client.ping()
                    self.use_redis = True
                    logger.info("CacheManager: Successfully connected to Redis.")
                except Exception as e:
                    logger.warning(
                        f"CacheManager: Failed to connect to Redis ({e}). "
                        "Falling back to local in-memory TTL LRU cache."
                    )
                    self.redis_client = None
                    self.use_redis = False
            else:
                logger.info("CacheManager: No REDIS_URL configured. Using local in-memory TTL LRU cache.")

    async def get(self, key: str) -> Optional[Any]:
        """Gets a deserialized item from the cache."""
        if self.use_redis and self.redis_client:
            try:
                val = self.redis_client.get(key)
                if val:
                    return json.loads(val)
                return None
            except Exception as e:
                logger.error(f"CacheManager: Redis get error for key '{key}' ({e}). Falling back to local cache.")

        return self.local_cache.get(key)

    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Sets a serialized item into the cache."""
        if self.use_redis and self.redis_client:
            try:
                serialized = json.dumps(value)
                actual_ttl = ttl if ttl is not None else settings.CACHE_TTL
                self.redis_client.set(key, serialized, ex=actual_ttl)
                return
            except Exception as e:
                logger.error(f"CacheManager: Redis set error for key '{key}' ({e}). Falling back to local cache.")

        self.local_cache.set(key, value, ttl=ttl)

    def is_redis_active(self) -> bool:
        """Helper to verify current Redis socket connection status."""
        if not self.use_redis or not self.redis_client:
            return False
        try:
            return bool(self.redis_client.ping())
        except Exception:
            return False
