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
    created_at: datetime
    modified_at: datetime
    source_snapshot: str | None = None
    birth_date_raw: str | None = None
    birth_date_gedcom: str | None = None
    birth_place: str | None = None
    death_date_raw: str | None = None
    death_date_gedcom: str | None = None
    death_place: str | None = None
