import threading
from typing import Optional
from loguru import logger

from backend.app.core.settings import settings
from backend.app.database.sqlite_manager import SQLiteManager
from backend.app.inference.model_manager import ModelManager
from backend.app.retrieval.hybrid_search import HybridSearcher
from backend.app.ranking.reranker import CrossEncoderRerankingManager

class ModelRegistry:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(ModelRegistry, cls).__new__(cls)
                cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        with self._lock:
            if self._initialized:
                return
            self._initialized = True
            self._sqlite_manager: Optional[SQLiteManager] = None
            self._model_manager: Optional[ModelManager] = None
            self._hybrid_searcher: Optional[HybridSearcher] = None
            self._reranking_manager: Optional[CrossEncoderRerankingManager] = None

    def initialize(self):
        """Loads and warms up all models, databases, and indexes once."""
        with self._lock:
            logger.info("ModelRegistry: Initializing SQLiteManager...")
            self._sqlite_manager = SQLiteManager(db_path=settings.DATABASE_PATH)

            logger.info("ModelRegistry: Initializing ModelManager & warming up ONNX models...")
            self._model_manager = ModelManager()
            # MiniLM Embedding model
            self._model_manager.get_model_and_tokenizer("all-MiniLM-L6-v2")
            # CrossEncoder model
            self._model_manager.get_model_and_tokenizer("ms-marco-MiniLM-L-6-v2")

            logger.info("ModelRegistry: Initializing HybridSearcher (loads FAISS and lexical mappings)...")
            self._hybrid_searcher = HybridSearcher(faiss_path=settings.FAISS_INDEX_PATH)

            logger.info("ModelRegistry: Initializing CrossEncoderRerankingManager...")
            self._reranking_manager = CrossEncoderRerankingManager(candidates_file=settings.CANDIDATES_PATH)
            self._reranking_manager.reranker.load_model()
            
            logger.info("ModelRegistry: Warmup completed successfully. All models loaded into memory.")

    @property
    def sqlite_manager(self) -> SQLiteManager:
        if self._sqlite_manager is None:
            raise RuntimeError("ModelRegistry is not initialized. Call initialize() first.")
        return self._sqlite_manager

    @property
    def hybrid_searcher(self) -> HybridSearcher:
        if self._hybrid_searcher is None:
            raise RuntimeError("ModelRegistry is not initialized. Call initialize() first.")
        return self._hybrid_searcher

    @property
    def reranking_manager(self) -> CrossEncoderRerankingManager:
        if self._reranking_manager is None:
            raise RuntimeError("ModelRegistry is not initialized. Call initialize() first.")
        return self._reranking_manager
