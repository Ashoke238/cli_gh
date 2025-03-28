import os
import logging
from logging.handlers import TimedRotatingFileHandler
from datetime import datetime

LOG_DIR = os.path.join(os.getcwd(), "logs")

def setup_logger():
    logger = logging.getLogger("cli_logger")

    if logger.handlers:
        return logger  # Prevent duplicate handlers

    logger.setLevel(logging.INFO)

    os.makedirs(LOG_DIR, exist_ok=True)
    log_filename = os.path.join(LOG_DIR, "cli.log")

    # File handler with rotation
    file_handler = TimedRotatingFileHandler(
        filename=log_filename,
        when="midnight",
        interval=1,
        backupCount=30,
        encoding="utf-8"
    )
    file_handler.suffix = "%Y-%m-%d"
    file_handler.setFormatter(logging.Formatter(
        fmt="%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    ))

    # Console stream handler
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(logging.Formatter(
        fmt="%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    ))

    # Add handlers just once
    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)

    logger.propagate = False
    return logger
