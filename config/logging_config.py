import logging
import logging.handlers
from pathlib import Path
from .settings import LOG_DIR, LOG_FORMAT, LOG_LEVEL, LOG_FILE

def setup_logging():
    """Configure logging for the application"""
    # Create logs directory if it doesn't exist
    LOG_DIR.mkdir(exist_ok=True)

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(LOG_LEVEL)

    # Create formatters
    formatter = logging.Formatter(LOG_FORMAT)

    # File handler (rotating file handler)
    file_handler = logging.handlers.RotatingFileHandler(
        LOG_FILE,
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(LOG_LEVEL)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(LOG_LEVEL)

    # Add handlers to root logger
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)

    # Create specific loggers
    loggers = {
        'api': logging.getLogger('api'),
        'processor': logging.getLogger('processor'),
        'frontend': logging.getLogger('frontend')
    }

    # Configure specific loggers
    for logger in loggers.values():
        logger.setLevel(LOG_LEVEL)
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

    return loggers 