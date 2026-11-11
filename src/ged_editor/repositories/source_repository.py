"""SQL access for source records."""

import sqlite3
from datetime import datetime

from ged_editor.models.source import Source


class SourceRepository:
    """Create, read, update, and delete imported sources in SQLite."""

    def __init__(self, connection: sqlite3.Connection) -> None:
        """Bind the repository to an open SQLite connection."""
        connection.row_factory = sqlite3.Row
        self._connection = connection

    def create(self, source: Source) -> Source:
        """Insert a source and return the persisted record."""
        cursor = self._connection.execute(
            """
            INSERT INTO source (gedcom_xref, title, created_at, modified_at)
            VALUES (?, ?, ?, ?)
            """,
            (
                source.gedcom_xref,
                source.title,
                source.created_at.isoformat(),
                source.modified_at.isoformat(),
            ),
        )
        created = self.get_by_id(cursor.lastrowid)
        if created is None:
            raise sqlite3.DatabaseError("Inserted source could not be read.")
        return created

    def get_by_id(self, source_id: int | None) -> Source | None:
        """Return a source by primary key, or None if absent."""
        if source_id is None:
            return None
        row = self._connection.execute(
            """
            SELECT id, gedcom_xref, title, created_at, modified_at
            FROM source WHERE id = ?
            """,
            (source_id,),
        ).fetchone()
        return self._source_from_row(row) if row is not None else None

    def get_by_xref(self, gedcom_xref: str | None) -> Source | None:
        """Return a source by GEDCOM XREF, rejecting ambiguous duplicates."""
        if gedcom_xref is None:
            return None
        rows = self._connection.execute(
            """
            SELECT id, gedcom_xref, title, created_at, modified_at
            FROM source WHERE gedcom_xref = ?
            LIMIT 2
            """,
            (gedcom_xref,),
        ).fetchall()
        if len(rows) > 1:
            raise sqlite3.IntegrityError(
                f"Multiple source records use GEDCOM XREF {gedcom_xref}."
            )
        return self._source_from_row(rows[0]) if rows else None

    def update(self, source: Source) -> Source | None:
        """Update a source and return the persisted record."""
        if source.id is None:
            return None
        cursor = self._connection.execute(
            """
            UPDATE source
            SET gedcom_xref = ?, title = ?, created_at = ?, modified_at = ?
            WHERE id = ?
            """,
            (
                source.gedcom_xref,
                source.title,
                source.created_at.isoformat(),
                source.modified_at.isoformat(),
                source.id,
            ),
        )
        return self.get_by_id(source.id) if cursor.rowcount == 1 else None

    def delete(self, source_id: int) -> bool:
        """Delete a source and report whether it existed."""
        cursor = self._connection.execute("DELETE FROM source WHERE id = ?", (source_id,))
        return cursor.rowcount == 1

    @staticmethod
    def _source_from_row(row: sqlite3.Row) -> Source:
        return Source(
            id=row["id"],
            gedcom_xref=row["gedcom_xref"],
            title=row["title"],
            created_at=datetime.fromisoformat(row["created_at"]),
            modified_at=datetime.fromisoformat(row["modified_at"]),
        )
