import time
from fastapi import APIRouter, Response, status
from loguru import logger

from backend.app.core.model_registry import ModelRegistry
from backend.app.core.cache_manager import CacheManager

router = APIRouter()

@router.get("/health")
def health_check(response: Response):
    """
    Comprehensive health check verifying SQLite connectivity,
    cache health (Redis connection status or local LRU active), 
    and ONNX model registry warmup status.
    """
    health_status = "healthy"
    checks = {}

    # 1. Verify SQLite Database
    try:
        registry = ModelRegistry()
        db = registry.sqlite_manager
        db.execute_read("SELECT 1")
        checks["database"] = "healthy"
    except Exception as e:
        logger.error(f"Health Check: SQLite database check failed: {e}")
        checks["database"] = f"unhealthy: {str(e)}"
        health_status = "unhealthy"

    # 2. Verify Cache System
    try:
        cache = CacheManager()
        if cache.redis_client:
            if cache.is_redis_active():
                checks["cache"] = "healthy (Redis)"
            else:
                # Cache is degraded but local fallback still keeps the app functional
                checks["cache"] = "degraded (Redis connection lost, local LRU active)"
        else:
            checks["cache"] = "healthy (local TTL LRU)"
    except Exception as e:
        logger.error(f"Health Check: Cache check failed: {e}")
        checks["cache"] = f"unhealthy: {str(e)}"
        # Degraded cache doesn't fully fail the app health because local fallback is available

    # 3. Verify Model Registry
    try:
        registry = ModelRegistry()
        if registry._hybrid_searcher is not None and registry._reranking_manager is not None:
            checks["models"] = "healthy (warmed up)"
        else:
            checks["models"] = "unhealthy (not initialized)"
            health_status = "unhealthy"
    except Exception as e:
        logger.error(f"Health Check: Model registry check failed: {e}")
        checks["models"] = f"unhealthy: {str(e)}"
        health_status = "unhealthy"

    if health_status == "unhealthy":
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE

    return {
        "status": health_status,
        "timestamp": time.time(),
        "checks": checks
    }
