"""CRUD service for marriage records."""

import sqlite3

from ged_editor.models.marriage_record import MarriageRecord
from ged_editor.repositories.marriage_record_repository import (
    MarriageRecordRepository,
)


class MarriageRecordService:
    """Provide transaction-scoped CRUD operations for marriage records."""

    def __init__(self, connection: sqlite3.Connection) -> None:
        """Create a marriage record service for an open project connection."""
        self._connection = connection
        self._repository = MarriageRecordRepository(connection)

    def create(self, record: MarriageRecord) -> MarriageRecord:
        """Persist a new marriage record."""
        with self._connection:
            return self._repository.create(record)

    def get_by_id(self, record_id: int) -> MarriageRecord | None:
        """Read a marriage record by primary key."""
        return self._repository.get_by_id(record_id)

    def list_all(self) -> list[MarriageRecord]:
        """List records in registration order."""
        return self._repository.list_all()

    def has_spouse_pair(
        self,
        husb_person_id: int,
        wife_person_id: int,
        *,
        excluding_record_id: int | None = None,
    ) -> bool:
        """Check for an existing record with the same husband and wife."""
        return self._repository.has_spouse_pair(
            husb_person_id,
            wife_person_id,
            excluding_record_id=excluding_record_id,
        )

    def update(self, record: MarriageRecord) -> MarriageRecord | None:
        """Persist updates to a marriage record."""
        with self._connection:
            return self._repository.update(record)

    def delete(self, record_id: int) -> bool:
        """Delete a marriage record by primary key."""
        with self._connection:
            return self._repository.delete(record_id)
