import time

from backend.app.core.settings import settings
from backend.app.core.cache_manager import CacheManager, TTLLRUCache
from backend.app.core.model_registry import ModelRegistry


def test_settings_load():
    """Verify that pydantic-settings loads default config values correctly."""
    assert settings.PORT == 8000
    assert settings.HOST == "0.0.0.0"
    assert settings.ENV in ["production", "development", "test"]
    assert settings.DATABASE_PATH is not None


def test_ttl_lru_cache_eviction_and_expiry():
    """Verify in-memory TTL LRU cache eviction and timing policies."""
    # Capacity = 3, default TTL = 2s
    cache = TTLLRUCache(capacity=3, default_ttl=2)

    # 1. Verify get and set
    cache.set("a", 10)
    cache.set("b", 20)
    cache.set("c", 30)
    assert cache.get("a") == 10
    assert cache.get("b") == 20
    assert cache.get("c") == 30

    # 2. Verify LRU Eviction: Accessing 'a' makes it MRU.
    # Adding 'd' should evict 'b' (since 'b' is the least recently accessed of remaining b, c).
    cache.get("a")  # 'a' becomes MRU
    cache.set("d", 40)

    assert cache.get("b") is None  # Evicted
    assert cache.get("a") == 10
    assert cache.get("c") == 30
    assert cache.get("d") == 40

    # 3. Verify TTL Expiry
    cache.set("timed", 99, ttl=1)
    assert cache.get("timed") == 99
    time.sleep(1.1)
    assert cache.get("timed") is None  # Expired


def test_cache_manager_singleton():
    """Verify CacheManager is a singleton."""
    cm1 = CacheManager()
    cm2 = CacheManager()
    assert cm1 is cm2


def test_model_registry_singleton():
    """Verify ModelRegistry is a singleton."""
    mr1 = ModelRegistry()
    mr2 = ModelRegistry()
    assert mr1 is mr2


def test_health_endpoint():
    """Verify the health endpoint responds and contains checks schema by direct call."""
    from backend.app.core.health import health_check
    from fastapi import Response

    response = Response()
    data = health_check(response)
    assert "status" in data
    assert "timestamp" in data
    assert "checks" in data


def test_metrics_endpoint():
    """Verify the metrics endpoint returns correct metrics keys by direct call."""
    from backend.app.core.metrics import get_metrics

    data = get_metrics()
    assert "request_metrics" in data
    assert "cache_metrics" in data
    assert "inference_metrics" in data
