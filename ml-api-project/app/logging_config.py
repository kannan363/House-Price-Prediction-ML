import logging
from logging.handlers import RotatingFileHandler
import os

# Create logs directory if it doesn't exist
os.makedirs("logs", exist_ok=True)

def setup_logger():
    logger = logging.getLogger("ml_api")
    logger.setLevel(logging.INFO)

    # Avoid duplicate handlers if setup_logger is called multiple times
    if logger.hasHandlers():
        return logger

    # Log format: Timestamp | Level | Message
    formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # 1. Console Handler (outputs to terminal)
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # 2. Rotating File Handler (logs to logs/app.log, max 5MB per file, 3 backups)
    file_handler = RotatingFileHandler(
        "logs/app.log",
        maxBytes=5 * 1024 * 1024,
        backupCount=3,
        encoding="utf-8"
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger

logger = setup_logger()