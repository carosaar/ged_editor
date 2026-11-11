"""Person data model."""

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class Person:
    """Person record stored in an EDG project."""

    id: int | None
    gedcom_xref: str | None
    name: str
    sex: str | None
    is_existing_record: bool
    created_at: datetime
    modified_at: datetime
    needs_export: bool = False
    source_snapshot: str | None = None
