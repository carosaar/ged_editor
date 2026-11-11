"""SQL access for marriage records."""

import sqlite3
from datetime import datetime

from ged_editor.models.marriage_record import MarriageRecord, MarriageRecordStatus


class MarriageRecordRepository:
    """Create, read, update, and delete marriage records in SQLite."""

    _COLUMNS = """
        id, year, number, display_number, status, created_at, modified_at,
        husb_person_id, wife_person_id, marriage_date_raw, marriage_date_gedcom,
        marriage_place, note_origin_husband, note_origin_wife, note_death_husband,
        note_death_wife, note_legitimation, note_marginal, note_comments
    """

    def __init__(self, connection: sqlite3.Connection) -> None:
        """Bind the repository to an open SQLite connection."""
        connection.row_factory = sqlite3.Row
        self._connection = connection

    def create(self, record: MarriageRecord) -> MarriageRecord:
        """Insert a marriage record and return the persisted record."""
        cursor = self._connection.execute(
            """
            INSERT INTO marriage_record (
                year, number, display_number, status, created_at, modified_at,
                husb_person_id, wife_person_id, marriage_date_raw,
                marriage_date_gedcom, marriage_place, note_origin_husband,
                note_origin_wife, note_death_husband, note_death_wife,
                note_legitimation, note_marginal, note_comments
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            self._values(record),
        )
        created = self.get_by_id(cursor.lastrowid)
        if created is None:
            raise sqlite3.DatabaseError("Inserted marriage record could not be read.")
        return created

    def get_by_id(self, record_id: int | None) -> MarriageRecord | None:
        """Return a marriage record by primary key, or None if absent."""
        if record_id is None:
            return None
        row = self._connection.execute(
            f"SELECT {self._COLUMNS} FROM marriage_record WHERE id = ?",
            (record_id,),
        ).fetchone()
        return self._record_from_row(row) if row is not None else None

    def update(self, record: MarriageRecord) -> MarriageRecord | None:
        """Update a marriage record and return the persisted record."""
        if record.id is None:
            return None
        cursor = self._connection.execute(
            """
            UPDATE marriage_record
            SET year = ?, number = ?, display_number = ?, status = ?,
                created_at = ?, modified_at = ?, husb_person_id = ?,
                wife_person_id = ?, marriage_date_raw = ?,
                marriage_date_gedcom = ?, marriage_place = ?,
                note_origin_husband = ?, note_origin_wife = ?,
                note_death_husband = ?, note_death_wife = ?,
                note_legitimation = ?, note_marginal = ?, note_comments = ?
            WHERE id = ?
            """,
            (*self._values(record), record.id),
        )
        return self.get_by_id(record.id) if cursor.rowcount == 1 else None

    def delete(self, record_id: int) -> bool:
        """Delete a marriage record by primary key and report whether it existed."""
        cursor = self._connection.execute(
            "DELETE FROM marriage_record WHERE id = ?",
            (record_id,),
        )
        return cursor.rowcount == 1

    @staticmethod
    def _values(record: MarriageRecord) -> tuple[object, ...]:
        return (
            record.year,
            record.number,
            record.display_number,
            record.status.value,
            record.created_at.isoformat(),
            record.modified_at.isoformat(),
            record.husb_person_id,
            record.wife_person_id,
            record.marriage_date_raw,
            record.marriage_date_gedcom,
            record.marriage_place,
            record.note_origin_husband,
            record.note_origin_wife,
            record.note_death_husband,
            record.note_death_wife,
            record.note_legitimation,
            record.note_marginal,
            record.note_comments,
        )

    @staticmethod
    def _record_from_row(row: sqlite3.Row) -> MarriageRecord:
        return MarriageRecord(
            id=row["id"],
            year=row["year"],
            number=row["number"],
            display_number=row["display_number"],
            status=MarriageRecordStatus(row["status"]),
            created_at=datetime.fromisoformat(row["created_at"]),
            modified_at=datetime.fromisoformat(row["modified_at"]),
            husb_person_id=row["husb_person_id"],
            wife_person_id=row["wife_person_id"],
            marriage_date_raw=row["marriage_date_raw"],
            marriage_date_gedcom=row["marriage_date_gedcom"],
            marriage_place=row["marriage_place"],
            note_origin_husband=row["note_origin_husband"],
            note_origin_wife=row["note_origin_wife"],
            note_death_husband=row["note_death_husband"],
            note_death_wife=row["note_death_wife"],
            note_legitimation=row["note_legitimation"],
            note_marginal=row["note_marginal"],
            note_comments=row["note_comments"],
        )
