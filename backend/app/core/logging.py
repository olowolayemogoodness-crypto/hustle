import logging
from app.config import settings

LOG_FORMAT = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"


def configure_logging() -> None:
    level = getattr(logging, settings.logging_level.upper(), logging.INFO)
    logging.basicConfig(level=level, format=LOG_FORMAT, force=True)
    logging.getLogger("uvicorn").setLevel(level)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    configure_logging()
    return logging.getLogger(name)
