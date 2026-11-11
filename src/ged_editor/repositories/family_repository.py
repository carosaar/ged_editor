"""SQL access for family links."""

import sqlite3
from datetime import datetime

from ged_editor.models.family_link import FamilyLink


class FamilyRepository:
    """Create, read, update, and delete family links in SQLite."""

    def __init__(self, connection: sqlite3.Connection) -> None:
        """Bind the repository to an open SQLite connection."""
        connection.row_factory = sqlite3.Row
        self._connection = connection

    def create(self, family_link: FamilyLink) -> FamilyLink:
        """Insert a family link and return the persisted record."""
        cursor = self._connection.execute(
            """
            INSERT INTO family_link (
                gedcom_xref, husb_person_id, wife_person_id,
                is_existing_record, created_at, modified_at
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                family_link.gedcom_xref,
                family_link.husb_person_id,
                family_link.wife_person_id,
                int(family_link.is_existing_record),
                family_link.created_at.isoformat(),
                family_link.modified_at.isoformat(),
            ),
        )
        created = self.get_by_id(cursor.lastrowid)
        if created is None:
            raise sqlite3.DatabaseError("Inserted family link could not be read.")
        return created

    def get_by_id(self, family_link_id: int | None) -> FamilyLink | None:
        """Return a family link by primary key, or None if absent."""
        if family_link_id is None:
            return None
        row = self._connection.execute(
            """
            SELECT id, gedcom_xref, husb_person_id, wife_person_id,
                   is_existing_record, created_at, modified_at
            FROM family_link
            WHERE id = ?
            """,
            (family_link_id,),
        ).fetchone()
        return self._family_from_row(row) if row is not None else None

    def update(self, family_link: FamilyLink) -> FamilyLink | None:
        """Update a family link and return the persisted record."""
        if family_link.id is None:
            return None
        cursor = self._connection.execute(
            """
            UPDATE family_link
            SET gedcom_xref = ?, husb_person_id = ?, wife_person_id = ?,
                is_existing_record = ?, created_at = ?, modified_at = ?
            WHERE id = ?
            """,
            (
                family_link.gedcom_xref,
                family_link.husb_person_id,
                family_link.wife_person_id,
                int(family_link.is_existing_record),
                family_link.created_at.isoformat(),
                family_link.modified_at.isoformat(),
                family_link.id,
            ),
        )
        return self.get_by_id(family_link.id) if cursor.rowcount == 1 else None

    def delete(self, family_link_id: int) -> bool:
        """Delete a family link by primary key and report whether it existed."""
        cursor = self._connection.execute(
            "DELETE FROM family_link WHERE id = ?",
            (family_link_id,),
        )
        return cursor.rowcount == 1

    @staticmethod
    def _family_from_row(row: sqlite3.Row) -> FamilyLink:
        return FamilyLink(
            id=row["id"],
            gedcom_xref=row["gedcom_xref"],
            husb_person_id=row["husb_person_id"],
            wife_person_id=row["wife_person_id"],
            is_existing_record=bool(row["is_existing_record"]),
            created_at=datetime.fromisoformat(row["created_at"]),
            modified_at=datetime.fromisoformat(row["modified_at"]),
        )
