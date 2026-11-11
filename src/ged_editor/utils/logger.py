"""Central logging configuration and logger access."""

import logging
from typing import Final

LOG_FORMAT: Final = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"


def configure_logging(level: int = logging.INFO) -> None:
    """Configure console logging for the application."""
    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    if not root_logger.handlers:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(logging.Formatter(LOG_FORMAT))
        root_logger.addHandler(console_handler)


def get_logger(name: str) -> logging.Logger:
    """Return a named logger for an application component."""
    return logging.getLogger(name)
