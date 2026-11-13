"""SQL access for marriage records."""

import sqlite3
from datetime import datetime

from ged_editor.models.marriage_record import (
    MarriageRecord,
    MarriageRecordExportStatus,
    MarriageRecordStatus,
)


class DuplicateMarriageRegistrationError(sqlite3.IntegrityError):
    """Raised when a year and registration number are already in use."""

    def __init__(self, year: int, number: int) -> None:
        self.year = year
        self.number = number
        super().__init__(
            f"Die Registriernummer {number}/{year} ist bereits vergeben."
        )


class MarriageRecordRepository:
    """Create, read, update, and delete marriage records in SQLite."""

    _COLUMNS = """
        id, gedcom_xref, source_snapshot, year, number, display_number,
        workflow_status, export_status, created_at, modified_at, husb_person_id,
        wife_person_id, marriage_date_raw, marriage_date_gedcom, marriage_place,
        note_origin_husband, note_origin_wife, note_death_husband,
        note_death_wife, note_legitimation, note_marginal, note_comments
    """

    def __init__(self, connection: sqlite3.Connection) -> None:
        """Bind the repository to an open SQLite connection."""
        connection.row_factory = sqlite3.Row
        self._connection = connection

    def create(self, record: MarriageRecord) -> MarriageRecord:
        """Insert a marriage record and return the persisted record."""
        self._ensure_unique_registration(record)
        cursor = self._connection.execute(
            """
            INSERT INTO marriage_record (
                gedcom_xref, source_snapshot, year, number, display_number,
                workflow_status, export_status, created_at, modified_at,
                husb_person_id, wife_person_id, marriage_date_raw, marriage_date_gedcom,
                marriage_place, note_origin_husband, note_origin_wife,
                note_death_husband, note_death_wife, note_legitimation,
                note_marginal, note_comments
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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

    def list_all(self) -> list[MarriageRecord]:
        """Return all records ordered by year and registration number."""
        rows = self._connection.execute(
            f"""
            SELECT {self._COLUMNS}
            FROM marriage_record
            ORDER BY year IS NULL, year, number IS NULL, number, id
            """
        ).fetchall()
        return [self._record_from_row(row) for row in rows]

    def has_registration(
        self,
        year: int | None,
        number: int | None,
        *,
        excluding_record_id: int | None = None,
    ) -> bool:
        """Return whether another record already uses this registration."""
        if year is None or number is None:
            return False
        query = """
            SELECT 1
            FROM marriage_record
            WHERE year = ? AND number = ?
        """
        parameters: tuple[object, ...] = (year, number)
        if excluding_record_id is not None:
            query += " AND id != ?"
            parameters += (excluding_record_id,)
        return (
            self._connection.execute(query + " LIMIT 1", parameters).fetchone()
            is not None
        )

    def has_spouse_pair(
        self,
        husb_person_id: int,
        wife_person_id: int,
        *,
        excluding_record_id: int | None = None,
    ) -> bool:
        """Return whether another record already uses this spouse pair."""
        query = """
            SELECT 1
            FROM marriage_record
            WHERE husb_person_id = ? AND wife_person_id = ?
        """
        parameters: tuple[object, ...] = (husb_person_id, wife_person_id)
        if excluding_record_id is not None:
            query += " AND id != ?"
            parameters += (excluding_record_id,)
        return self._connection.execute(query + " LIMIT 1", parameters).fetchone() is not None

    def get_by_xref(self, gedcom_xref: str | None) -> MarriageRecord | None:
        """Return a marriage record by GEDCOM XREF, or None when absent."""
        if gedcom_xref is None:
            return None
        rows = self._connection.execute(
            f"SELECT {self._COLUMNS} FROM marriage_record "
            "WHERE gedcom_xref = ? LIMIT 2",
            (gedcom_xref,),
        ).fetchall()
        if len(rows) > 1:
            raise sqlite3.IntegrityError(
                f"Multiple marriage records use GEDCOM XREF {gedcom_xref}."
            )
        return self._record_from_row(rows[0]) if rows else None

    def update(self, record: MarriageRecord) -> MarriageRecord | None:
        """Update a marriage record and return the persisted record."""
        if record.id is None:
            return None
        current = self.get_by_id(record.id)
        if current is None:
            return None
        if (current.year, current.number) != (record.year, record.number):
            self._ensure_unique_registration(
                record,
                excluding_record_id=record.id,
            )
        cursor = self._connection.execute(
            """
            UPDATE marriage_record
            SET gedcom_xref = ?, source_snapshot = ?, year = ?, number = ?,
                display_number = ?, workflow_status = ?, export_status = ?,
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

    def _ensure_unique_registration(
        self,
        record: MarriageRecord,
        *,
        excluding_record_id: int | None = None,
    ) -> None:
        if self.has_registration(
            record.year,
            record.number,
            excluding_record_id=excluding_record_id,
        ):
            if record.year is not None and record.number is not None:
                raise DuplicateMarriageRegistrationError(
                    record.year,
                    record.number,
                )

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
            record.gedcom_xref,
            record.source_snapshot,
            record.year,
            record.number,
            record.display_number,
            record.workflow_status.value,
            record.export_status.value,
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
            gedcom_xref=row["gedcom_xref"],
            source_snapshot=row["source_snapshot"],
            year=row["year"],
            number=row["number"],
            display_number=row["display_number"],
            workflow_status=MarriageRecordStatus(row["workflow_status"]),
            export_status=MarriageRecordExportStatus(row["export_status"]),
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
