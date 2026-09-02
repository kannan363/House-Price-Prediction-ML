# app/logging_config.py
import logging
from logging.handlers import RotatingFileHandler
import os

from app.config import settings

# Create logs directory dynamically based on settings
os.makedirs(os.path.dirname(settings.LOG_FILE_PATH), exist_ok=True)

def setup_logger():
    logger = logging.getLogger("ml_api")
    
    # Use LOG_LEVEL from settings (e.g., INFO, DEBUG, ERROR)
    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
    logger.setLevel(log_level)

    if logger.hasHandlers():
        return logger

    formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    file_handler = RotatingFileHandler(
        settings.LOG_FILE_PATH,
        maxBytes=5 * 1024 * 1024,
        backupCount=3,
        encoding="utf-8"
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger

logger = setup_logger()