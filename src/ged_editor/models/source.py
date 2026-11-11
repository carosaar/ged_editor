"""GEDCOM source data model."""

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class Source:
    """Source record imported from a GEDCOM file."""

    id: int | None
    gedcom_xref: str | None
    title: str | None
    created_at: datetime
    modified_at: datetime
