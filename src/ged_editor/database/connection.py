"""SQLite connection management for EDG project files."""

import logging
import sqlite3
from datetime import datetime
from pathlib import Path

from ged_editor.database.schema import (
    SCHEMA_VERSION,
    initialize_schema,
    initialize_schema_statements,
    upgrade_schema_v4,
    validate_project_schema,
    validate_schema,
)

logger = logging.getLogger(__name__)


class DatabaseConnection:
    """Manage a connection to one SQLite-backed project file."""

    def __init__(self, database_path: str | Path) -> None:
        """Create a connection manager for the given project path."""
        self.path = Path(database_path)
        self._connection: sqlite3.Connection | None = None
        self._created_file = False

    @property
    def connection(self) -> sqlite3.Connection:
        """Return the active connection or raise a SQLite programming error."""
        if self._connection is None:
            raise sqlite3.ProgrammingError("Database connection is not open.")
        return self._connection

    @property
    def created_file(self) -> bool:
        """Indicate whether this manager created the project file."""
        return self._created_file

    def connect(self, *, create: bool = False) -> sqlite3.Connection:
        """Open an existing database or exclusively create a new database file."""
        if self._connection is not None:
            return self._connection

        if create:
            with self.path.open("xb"):
                self._created_file = True
        elif not self.path.is_file():
            raise FileNotFoundError(f"Project file does not exist: {self.path}")

        try:
            self._connection = sqlite3.connect(self.path)
        except sqlite3.Error:
            self._remove_created_file()
            raise

        self._connection.row_factory = sqlite3.Row
        self._connection.execute("PRAGMA foreign_keys = ON")
        return self._connection

    def initialize_schema(self) -> None:
        """Initialize the EDG schema on the active database connection."""
        initialize_schema(self.connection)

    def validate_schema(self) -> None:
        """Validate the database integrity and required EDG schema."""
        validate_schema(self.connection)

    def ensure_current_schema(self) -> None:
        """Upgrade an older project after preserving its original file."""
        connection = self.connection
        validate_project_schema(connection)

        schema_row = connection.execute(
            'SELECT "value" FROM meta WHERE "key" = ?',
            ("schema_version",),
        ).fetchone()
        current_version = int(schema_row["value"]) if schema_row is not None else 1
        expected_version = int(SCHEMA_VERSION)
        if current_version > expected_version:
            raise sqlite3.DatabaseError(
                f"Project schema version {current_version} is newer than "
                f"supported version {expected_version}."
            )

        if current_version < expected_version:
            self.create_migration_backup()
            with connection:
                initialize_schema_statements(connection)
                upgrade_schema_v4(connection)
                connection.execute(
                    'UPDATE meta SET "value" = ? WHERE "key" = ?',
                    (SCHEMA_VERSION, "schema_version"),
                )
                connection.execute(
                    "UPDATE project SET schema_version = ?",
                    (SCHEMA_VERSION,),
                )
            logger.info("Upgraded project schema to version %s", SCHEMA_VERSION)

        self.validate_schema()

    def create_migration_backup(self) -> Path:
        """Create a SQLite backup beside the project before a schema upgrade."""
        backup_directory = self.path.with_name(f"{self.path.stem}_backups")
        backup_directory.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S-%f")
        backup_path = backup_directory / f"backup_{timestamp}.edg"
        backup_connection = sqlite3.connect(backup_path)
        try:
            self.connection.backup(backup_connection)
        except sqlite3.Error:
            backup_connection.close()
            backup_path.unlink(missing_ok=True)
            logger.exception("Could not back up project before migration: %s", self.path)
            raise
        else:
            backup_connection.close()
        return backup_path

    def close(self) -> None:
        """Close the active SQLite connection, if one is open."""
        connection = self._connection
        self._connection = None
        if connection is not None:
            connection.close()

    def _remove_created_file(self) -> None:
        if self._created_file:
            self.path.unlink(missing_ok=True)
            self._created_file = False
