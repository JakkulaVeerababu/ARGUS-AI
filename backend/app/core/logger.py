import os
import sys
from loguru import logger
from backend.app.core.settings import settings


def setup_logger():
    """Configures Loguru to handle stdout logging and file-based routing."""
    # Remove all pre-existing handlers
    logger.remove()

    log_dir = settings.LOG_DIR
    os.makedirs(log_dir, exist_ok=True)

    # 1. Console Output Handler
    logger.add(
        sys.stdout,
        level=settings.LOG_LEVEL,
        format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        enqueue=True,
    )

    # Filter Functions
    def filter_api(record):
        # Route to api.log if message contains '[API]' prefix or if bound to api=True
        return "api" in record["extra"] or "[API]" in record["message"]

    def filter_ranking(record):
        # Route to ranking.log if message contains '[RANKING]' prefix or if bound to ranking=True
        return "ranking" in record["extra"] or "[RANKING]" in record["message"]

    def filter_errors(record):
        # Route to errors.log if level is ERROR or higher
        return record["level"].no >= logger.level("ERROR").no

    # 2. api.log File Handler
    logger.add(
        os.path.join(log_dir, "api.log"),
        filter=filter_api,
        level="INFO",
        format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} - {message}",
        rotation="10 MB",
        retention="7 days",
        enqueue=True,
    )

    # 3. ranking.log File Handler
    logger.add(
        os.path.join(log_dir, "ranking.log"),
        filter=filter_ranking,
        level="INFO",
        format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} - {message}",
        rotation="10 MB",
        retention="7 days",
        enqueue=True,
    )

    # 4. errors.log File Handler (Stores ERROR and CRITICAL levels)
    logger.add(
        os.path.join(log_dir, "errors.log"),
        filter=filter_errors,
        level="ERROR",
        format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} - {message}\n{exception}",
        rotation="10 MB",
        retention="14 days",
        enqueue=True,
    )

    logger.info("Logger configuration complete. Logs routed to stdout and log files.")
