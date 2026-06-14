from contextlib import asynccontextmanager
from fastapi import FastAPI
from loguru import logger

from backend.app.core.logger import setup_logger
from backend.app.core.model_registry import ModelRegistry
from backend.app.core.cache_manager import CacheManager
from backend.app.core.exception_handlers import ModelNotFoundError


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    FastAPI lifespan context manager that coordinates startup and shutdown.
    Handles logging initialization, cache manager configuration, DB setup,
    and ONNX model warmup to completely eliminate cold start latencies.
    """
    # 1. Initialize Loguru logger formatting and destinations
    setup_logger()
    logger.info("Lifespan Startup: Launching ARGUS AI Candidate Discovery Engine...")

    # 2. Configure caching layer
    try:
        CacheManager()
    except Exception as e:
        logger.error(f"Lifespan Startup: CacheManager setup failed: {e}")

    # 3. Load models, database mappings, and indexes into memory
    try:
        registry = ModelRegistry()
        registry.initialize()
    except Exception as e:
        logger.critical(
            f"Lifespan Startup: Critical failure in ModelRegistry initialization: {e}"
        )
        raise ModelNotFoundError(f"Model initialization failed: {e}")

    # 4. Perform mock/warmup inference to pre-compile and cache execution graphs
    try:
        logger.info("Lifespan Startup: Warming up model sessions with mock queries...")
        dummy_query = (
            "Python developer with experience in machine learning and faiss search"
        )

        # Warm up Embedding and Semantic Search (FTS & FAISS)
        registry.hybrid_searcher.search(dummy_query, top_k_branch=5, final_top_n=2)

        # Warm up CrossEncoder Reranker
        # Use a dummy candidate ID for the query-document building loop
        registry.reranking_manager.rerank(dummy_query, ["CAND_0000001"], top_n=1)

        logger.info("Lifespan Startup: Warmup complete. System is fully optimized.")
    except Exception as e:
        logger.warning(
            f"Lifespan Startup: Mock queries failed to complete ({e}). Proceeding to startup."
        )

    yield

    # Lifespan Shutdown Actions
    logger.info("Lifespan Shutdown: Closing application resources...")
    try:
        registry = ModelRegistry()
        if registry._sqlite_manager:
            registry.sqlite_manager.close()
            logger.info(
                "Lifespan Shutdown: SQLite database connection closed successfully."
            )
    except Exception as e:
        logger.error(f"Lifespan Shutdown: Error closing SQLite connection: {e}")
    logger.info("Lifespan Shutdown: Shutdown complete.")
