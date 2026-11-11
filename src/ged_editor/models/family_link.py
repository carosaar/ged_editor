"""Family link data model."""

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class FamilyLink:
    """GEDCOM family record linked to optional project person records."""

    id: int | None
    gedcom_xref: str | None
    husb_person_id: int | None
    wife_person_id: int | None
    is_existing_record: bool
    created_at: datetime
    modified_at: datetime
