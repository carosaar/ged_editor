"""Persistence repositories."""

from ged_editor.repositories.marriage_record_repository import (
    MarriageRecordRepository,
)
from ged_editor.repositories.person_repository import PersonRepository
from ged_editor.repositories.project_repository import ProjectRepository
from ged_editor.repositories.source_repository import SourceRepository

__all__ = [
    "MarriageRecordRepository",
    "PersonRepository",
    "ProjectRepository",
    "SourceRepository",
]
