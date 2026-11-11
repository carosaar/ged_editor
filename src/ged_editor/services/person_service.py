"""CRUD service for person records."""

import sqlite3

from ged_editor.models.person import Person
from ged_editor.repositories.person_repository import PersonRepository


class PersonService:
    """Provide transaction-scoped CRUD operations for people."""

    def __init__(self, connection: sqlite3.Connection) -> None:
        """Create a person service for an open project connection."""
        self._connection = connection
        self._repository = PersonRepository(connection)

    def create(self, person: Person) -> Person:
        """Persist a new person."""
        with self._connection:
            return self._repository.create(person)

    def get_by_id(self, person_id: int) -> Person | None:
        """Read a person by primary key."""
        return self._repository.get_by_id(person_id)

    def update(self, person: Person) -> Person | None:
        """Persist updates to a person."""
        with self._connection:
            return self._repository.update(person)

    def delete(self, person_id: int) -> bool:
        """Delete a person by primary key."""
        with self._connection:
            return self._repository.delete(person_id)
