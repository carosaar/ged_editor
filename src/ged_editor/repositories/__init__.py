"""Repository package for data access."""
"""Persistence repositories."""

from ged_editor.repositories.family_repository import FamilyRepository
from ged_editor.repositories.marriage_record_repository import (
    MarriageRecordRepository,
)
from ged_editor.repositories.person_repository import PersonRepository
from ged_editor.repositories.project_repository import ProjectRepository

__all__ = [
    "FamilyRepository",
    "MarriageRecordRepository",
    "PersonRepository",
    "ProjectRepository",
]
