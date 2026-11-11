"""Project metadata model."""

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class Project:
    """Metadata stored for one EDG project."""

    id: int | None
    project_name: str
    created_at: datetime
    modified_at: datetime
    schema_version: str
    application_version: str
