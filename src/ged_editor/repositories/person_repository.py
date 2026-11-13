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
                gedcom_xref, name, sex, created_at, modified_at, source_snapshot,
                birth_date_raw, birth_date_gedcom, birth_place, death_date_raw,
                death_date_gedcom, death_place
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                person.gedcom_xref,
                person.name,
                person.sex,
                person.created_at.isoformat(),
                person.modified_at.isoformat(),
                person.source_snapshot,
                person.birth_date_raw,
                person.birth_date_gedcom,
                person.birth_place,
                person.death_date_raw,
                person.death_date_gedcom,
                person.death_place,
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
            SELECT id, gedcom_xref, name, sex, created_at, modified_at,
                   source_snapshot, birth_date_raw, birth_date_gedcom,
                   birth_place, death_date_raw, death_date_gedcom, death_place
            FROM person
            WHERE id = ?
            """,
            (person_id,),
        ).fetchone()
        return self._person_from_row(row) if row is not None else None

    def search(
        self,
        name_fragment: str = "",
        *,
        sex: str | None = None,
    ) -> list[Person]:
        """Match all search terms across person details, optionally filtered by sex."""
        select = """
            SELECT id, gedcom_xref, name, sex, created_at, modified_at,
                   source_snapshot, birth_date_raw, birth_date_gedcom,
                   birth_place, death_date_raw, death_date_gedcom, death_place
            FROM person
        """
        conditions: list[str] = []
        parameters: list[str] = []
        if sex is not None:
            conditions.append("sex = ?")
            parameters.append(sex)
        query = select
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        rows = self._connection.execute(
            query + " ORDER BY name COLLATE NOCASE, id",
            parameters,
        ).fetchall()
        people = [self._person_from_row(row) for row in rows]
        terms = tuple(term.casefold() for term in name_fragment.split())
        if not terms:
            return people
        return [
            person
            for person in people
            if all(
                any(
                    term in value.casefold()
                    for value in (
                        person.name,
                        person.birth_date_raw or "",
                        person.birth_place or "",
                    )
                )
                for term in terms
            )
        ]

    def get_by_xref(self, gedcom_xref: str | None) -> Person | None:
        """Return a person by GEDCOM XREF, or None when no XREF is supplied."""
        if gedcom_xref is None:
            return None
        rows = self._connection.execute(
            """
            SELECT id, gedcom_xref, name, sex, created_at, modified_at,
                   source_snapshot, birth_date_raw, birth_date_gedcom,
                   birth_place, death_date_raw, death_date_gedcom, death_place
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
            SET gedcom_xref = ?, name = ?, sex = ?, created_at = ?,
                modified_at = ?, source_snapshot = ?, birth_date_raw = ?,
                birth_date_gedcom = ?, birth_place = ?, death_date_raw = ?,
                death_date_gedcom = ?, death_place = ?
            WHERE id = ?
            """,
            (
                person.gedcom_xref,
                person.name,
                person.sex,
                person.created_at.isoformat(),
                person.modified_at.isoformat(),
                person.source_snapshot,
                person.birth_date_raw,
                person.birth_date_gedcom,
                person.birth_place,
                person.death_date_raw,
                person.death_date_gedcom,
                person.death_place,
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
            created_at=datetime.fromisoformat(row["created_at"]),
            modified_at=datetime.fromisoformat(row["modified_at"]),
            source_snapshot=row["source_snapshot"],
            birth_date_raw=row["birth_date_raw"],
            birth_date_gedcom=row["birth_date_gedcom"],
            birth_place=row["birth_place"],
            death_date_raw=row["death_date_raw"],
            death_date_gedcom=row["death_date_gedcom"],
            death_place=row["death_place"],
        )
