import os
import sys
from loguru import logger

# Create logs directory in the project root
LOGS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../logs"))
os.makedirs(LOGS_DIR, exist_ok=True)

# Define log file paths
API_LOG = os.path.join(LOGS_DIR, "api.log")
RANKING_LOG = os.path.join(LOGS_DIR, "ranking.log")
ERRORS_LOG = os.path.join(LOGS_DIR, "errors.log")

# Clear default handler
logger.remove()

# 1. Console Handler - Info level and above
logger.add(
    sys.stdout,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level="INFO",
    backtrace=True,
    diagnose=True,
)

# Filter functions for routing logs
def filter_api(record):
    return record["extra"].get("channel") == "api"

def filter_ranking(record):
    return record["extra"].get("channel") == "ranking"

# 2. API Log Handler - Log requests and api flows
logger.add(
    API_LOG,
    rotation="10 MB",
    retention="7 days",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
    level="INFO",
    filter=filter_api,
    backtrace=True,
    diagnose=True,
)

# 3. Ranking Log Handler - Log ranking and search pipeline steps
logger.add(
    RANKING_LOG,
    rotation="10 MB",
    retention="7 days",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
    level="INFO",
    filter=filter_ranking,
    backtrace=True,
    diagnose=True,
)

# 4. Errors Log Handler - All errors across channels
logger.add(
    ERRORS_LOG,
    rotation="10 MB",
    retention="30 days",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}\n{exception}",
    level="ERROR",
    backtrace=True,
    diagnose=True,
)

# Export pre-configured channel-specific loggers
api_logger = logger.bind(channel="api")
ranking_logger = logger.bind(channel="ranking")
