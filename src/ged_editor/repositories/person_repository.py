"""SQL access for person records."""

import sqlite3
from datetime import datetime

from ged_editor.models.person import Person


class PersonRepository:
    """Create, read, update, and delete people in SQLite."""

    def __init__(self, connection: sqlite3.Connection) -> None:
        """Bind the repository to an open SQLite connection."""
        connection.row_factory = sqlite3.Row
        self._connection = connection

    def create(self, person: Person) -> Person:
        """Insert a person and return the persisted record."""
        cursor = self._connection.execute(
            """
            INSERT INTO person (
                gedcom_xref, name, sex, is_existing_record, created_at, modified_at,
                needs_export, source_snapshot
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                person.gedcom_xref,
                person.name,
                person.sex,
                int(person.is_existing_record),
                person.created_at.isoformat(),
                person.modified_at.isoformat(),
                int(person.needs_export),
                person.source_snapshot,
            ),
        )
        created = self.get_by_id(cursor.lastrowid)
        if created is None:
            raise sqlite3.DatabaseError("Inserted person could not be read.")
        return created

    def get_by_id(self, person_id: int | None) -> Person | None:
        """Return a person by primary key, or None if absent."""
        if person_id is None:
            return None
        row = self._connection.execute(
            """
            SELECT id, gedcom_xref, name, sex, is_existing_record,
                   created_at, modified_at, needs_export, source_snapshot
            FROM person
            WHERE id = ?
            """,
            (person_id,),
        ).fetchone()
        return self._person_from_row(row) if row is not None else None

    def get_by_xref(self, gedcom_xref: str | None) -> Person | None:
        """Return a person by GEDCOM XREF, or None when no XREF is supplied."""
        if gedcom_xref is None:
            return None
        rows = self._connection.execute(
            """
            SELECT id, gedcom_xref, name, sex, is_existing_record,
                   created_at, modified_at, needs_export, source_snapshot
            FROM person
            WHERE gedcom_xref = ?
            LIMIT 2
            """,
            (gedcom_xref,),
        ).fetchall()
        if len(rows) > 1:
            raise sqlite3.IntegrityError(
                f"Multiple person records use GEDCOM XREF {gedcom_xref}."
            )
        return self._person_from_row(rows[0]) if rows else None

    def update(self, person: Person) -> Person | None:
        """Update a person and return the persisted record."""
        if person.id is None:
            return None
        cursor = self._connection.execute(
            """
            UPDATE person
            SET gedcom_xref = ?, name = ?, sex = ?, is_existing_record = ?,
                created_at = ?, modified_at = ?, needs_export = ?,
                source_snapshot = ?
            WHERE id = ?
            """,
            (
                person.gedcom_xref,
                person.name,
                person.sex,
                int(person.is_existing_record),
                person.created_at.isoformat(),
                person.modified_at.isoformat(),
                int(person.needs_export),
                person.source_snapshot,
                person.id,
            ),
        )
        return self.get_by_id(person.id) if cursor.rowcount == 1 else None

    def delete(self, person_id: int) -> bool:
        """Delete a person by primary key and report whether it existed."""
        cursor = self._connection.execute("DELETE FROM person WHERE id = ?", (person_id,))
        return cursor.rowcount == 1

    @staticmethod
    def _person_from_row(row: sqlite3.Row) -> Person:
        return Person(
            id=row["id"],
            gedcom_xref=row["gedcom_xref"],
            name=row["name"],
            sex=row["sex"],
            is_existing_record=bool(row["is_existing_record"]),
            created_at=datetime.fromisoformat(row["created_at"]),
            modified_at=datetime.fromisoformat(row["modified_at"]),
            needs_export=bool(row["needs_export"]),
            source_snapshot=row["source_snapshot"],
        )
