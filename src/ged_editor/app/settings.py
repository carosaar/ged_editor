"""Central application settings."""

import logging
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Settings:
    """Settings shared by application components."""

    log_level: int = logging.INFO


settings = Settings()
