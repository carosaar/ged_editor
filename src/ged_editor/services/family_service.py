"""CRUD service for family links."""

import sqlite3

from ged_editor.models.family_link import FamilyLink
from ged_editor.repositories.family_repository import FamilyRepository


class FamilyService:
    """Provide transaction-scoped CRUD operations for family links."""

    def __init__(self, connection: sqlite3.Connection) -> None:
        """Create a family service for an open project connection."""
        self._connection = connection
        self._repository = FamilyRepository(connection)

    def create(self, family_link: FamilyLink) -> FamilyLink:
        """Persist a new family link."""
        with self._connection:
            return self._repository.create(family_link)

    def get_by_id(self, family_link_id: int) -> FamilyLink | None:
        """Read a family link by primary key."""
        return self._repository.get_by_id(family_link_id)

    def update(self, family_link: FamilyLink) -> FamilyLink | None:
        """Persist updates to a family link."""
        with self._connection:
            return self._repository.update(family_link)

    def delete(self, family_link_id: int) -> bool:
        """Delete a family link by primary key."""
        with self._connection:
            return self._repository.delete(family_link_id)
