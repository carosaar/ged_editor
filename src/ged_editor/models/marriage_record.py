"""Marriage record data model and its workflow status values."""

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum


class MarriageRecordStatus(StrEnum):
    """Workflow statuses defined by ADR-015."""

    IN_BEARBEITUNG = "In Bearbeitung"
    FERTIG = "Fertig"


class MarriageRecordExportStatus(StrEnum):
    """Export status values defined independently by ADR-017."""

    NICHT_EXPORTIERT = "Nicht exportiert"
    EXPORTIERT = "Exportiert"
    KONFLIKT = "Konflikt"


@dataclass(frozen=True, slots=True)
class MarriageRecord:
    """Marriage certificate record, the leading domain object."""

    id: int | None
    year: int | None
    number: int | None
    display_number: str
    workflow_status: MarriageRecordStatus
    created_at: datetime
    modified_at: datetime
    husb_person_id: int | None
    wife_person_id: int | None
    marriage_date_raw: str | None
    marriage_date_gedcom: str | None
    marriage_place: str | None
    note_origin_husband: str | None
    note_origin_wife: str | None
    note_death_husband: str | None
    note_death_wife: str | None
    note_legitimation: str | None
    note_marginal: str | None
    note_comments: str | None
    gedcom_xref: str | None = None
    source_snapshot: str | None = None
    export_status: MarriageRecordExportStatus = (
        MarriageRecordExportStatus.NICHT_EXPORTIERT
    )
