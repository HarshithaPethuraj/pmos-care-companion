import logging
from backend.config import get_settings


def get_logger(name: str) -> logging.Logger:
    settings = get_settings()
    logging.basicConfig(level=settings.log_level)
    return logging.getLogger(name)
