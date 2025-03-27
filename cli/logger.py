import os
import logging
from logging.handlers import TimedRotatingFileHandler
from datetime import datetime

LOG_DIR = os.path.join(os.getcwd(), "logs")

def setup_logger():
    os.makedirs(LOG_DIR, exist_ok=True)

    log_filename = os.path.join(LOG_DIR, "cli.log")

    # Timed rotating handler (1 file per day, max 30 backups)
    handler = TimedRotatingFileHandler(
        filename=log_filename,
        when="midnight",
        interval=1,
        backupCount=30,
        encoding="utf-8"
    )
    handler.suffix = "%Y-%m-%d"
    handler.setFormatter(logging.Formatter(
        fmt="%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    ))
    formatter = logging.Formatter(
        fmt="%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S")

    # Stream handler to stdout
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)


    logger = logging.getLogger("cli_logger")
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)
    logger.addHandler(stream_handler)
    logger.propagate = False

    return logger
