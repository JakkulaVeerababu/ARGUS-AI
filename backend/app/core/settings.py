import os
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    ENV: str = "production"
    DEBUG: bool = False
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # Paths
    BASE_DIR: str = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
    DATABASE_PATH: str = os.path.join(BASE_DIR, "data/argus_ai.db")
    CANDIDATES_PATH: str = os.path.join(BASE_DIR, "data/candidates.jsonl")
    SUBMISSION_PATH: str = os.path.join(BASE_DIR, "submission.csv")
    FAISS_INDEX_PATH: str = os.path.join(BASE_DIR, "artifacts/faiss_index.bin")

    # Redis Cache Settings
    REDIS_URL: Optional[str] = None
    CACHE_TTL: int = 300  # Default to 5 minutes

    # Search & Tuning Hyperparameters
    RRF_K: int = 60
    TOP_K_BRANCH: int = 1000
    RERANK_N: int = 200
    FINAL_TOP_N: int = 300

    # Logging Config
    LOG_LEVEL: str = "INFO"
    LOG_DIR: str = os.path.join(BASE_DIR, "logs")

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )


settings = Settings()
