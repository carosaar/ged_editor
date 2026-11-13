"""SQL access for project metadata."""

import sqlite3
from datetime import datetime

from ged_editor.models.project import Project


class ProjectRepository:
    """Read and write project metadata using SQLite statements."""

    def __init__(self, connection: sqlite3.Connection) -> None:
        """Bind the repository to an open SQLite connection."""
        connection.row_factory = sqlite3.Row
        self._connection = connection

    def create_project(self, project: Project) -> Project:
        """Insert project metadata and return the persisted project."""
        cursor = self._connection.execute(
            """
            INSERT INTO project (
                project_name,
                created_at,
                modified_at,
                schema_version,
                application_version
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                project.project_name,
                project.created_at.isoformat(),
                project.modified_at.isoformat(),
                project.schema_version,
                project.application_version,
            ),
        )
        row = self._connection.execute(
            """
            SELECT id, project_name, created_at, modified_at,
                   schema_version, application_version
            FROM project
            WHERE id = ?
            """,
            (cursor.lastrowid,),
        ).fetchone()
        if row is None:
            raise sqlite3.DatabaseError("Inserted project could not be read.")
        return self._project_from_row(row)

    def get_project(self) -> Project | None:
        """Return the project's metadata, or None if no project row exists."""
        row = self._connection.execute(
            """
            SELECT id, project_name, created_at, modified_at,
                   schema_version, application_version
            FROM project
            ORDER BY id
            LIMIT 1
            """
        ).fetchone()
        return self._project_from_row(row) if row is not None else None

    def get_meta_value(self, key: str) -> str | None:
        """Return a project setting stored in meta, or None when absent."""
        row = self._connection.execute(
            'SELECT "value" FROM meta WHERE "key" = ?',
            (key,),
        ).fetchone()
        return row["value"] if row is not None else None

    def update_project(self, project: Project) -> Project | None:
        """Update persisted project metadata and return the stored row."""
        if project.id is None:
            return None

        cursor = self._connection.execute(
            """
            UPDATE project
            SET project_name = ?,
                created_at = ?,
                modified_at = ?,
                schema_version = ?,
                application_version = ?
            WHERE id = ?
            """,
            (
                project.project_name,
                project.created_at.isoformat(),
                project.modified_at.isoformat(),
                project.schema_version,
                project.application_version,
                project.id,
            ),
        )
        if cursor.rowcount != 1:
            return None
        return self.get_project()

    @staticmethod
    def _project_from_row(row: sqlite3.Row) -> Project:
        return Project(
            id=row["id"],
            project_name=row["project_name"],
            created_at=datetime.fromisoformat(row["created_at"]),
            modified_at=datetime.fromisoformat(row["modified_at"]),
            schema_version=row["schema_version"],
            application_version=row["application_version"],
        )
