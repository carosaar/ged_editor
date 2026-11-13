"""Application services for creating and managing EDG projects."""

import logging
import sqlite3
from dataclasses import dataclass, replace
from datetime import datetime
from pathlib import Path

from ged_editor.app.constants import APP_VERSION
from ged_editor.database.connection import DatabaseConnection
from ged_editor.database.schema import SCHEMA_VERSION
from ged_editor.models.project import Project
from ged_editor.repositories.project_repository import ProjectRepository

logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class ProjectOperationResult:
    """Explicit success or failure returned to the user interface."""

    project: Project | None = None
    error_message: str | None = None

    @property
    def succeeded(self) -> bool:
        """Return whether the operation produced a project."""
        return self.project is not None and self.error_message is None


class ProjectService:
    """Coordinate project persistence without exposing SQLite errors to the UI."""

    def __init__(self) -> None:
        """Initialize the service without opening a project."""
        self._database: DatabaseConnection | None = None
        self._repository: ProjectRepository | None = None
        self._project: Project | None = None
        self._project_path: Path | None = None

    @property
    def current_project(self) -> Project | None:
        """Return the currently active project metadata."""
        return self._project

    @property
    def project_path(self) -> Path | None:
        """Return the path of the currently active project file."""
        return self._project_path

    @property
    def connection(self) -> sqlite3.Connection | None:
        """Return the active project's SQLite connection, if one is open."""
        if self._database is None:
            return None
        return self._database.connection

    def get_meta_value(self, key: str) -> str | None:
        """Read a project setting from the active project's meta table."""
        if self._repository is None:
            return None
        return self._repository.get_meta_value(key)

    def create_new_project(
        self,
        project_path: str | Path,
        project_name: str = "Neues Projekt",
    ) -> ProjectOperationResult:
        """Create an EDG SQLite file and save its initial project record."""
        try:
            target = self._project_file_path(project_path)
        except ValueError as error:
            logger.warning("Rejected project path: %s", error)
            return ProjectOperationResult(error_message=str(error))
        if not project_name.strip():
            message = "Der Projektname darf nicht leer sein."
            logger.warning(message)
            return ProjectOperationResult(error_message=message)

        database = DatabaseConnection(target)
        try:
            database.connect(create=True)
            database.initialize_schema()
            repository = ProjectRepository(database.connection)
            now = datetime.now()
            project = repository.create_project(
                Project(
                    id=None,
                    project_name=project_name.strip(),
                    created_at=now,
                    modified_at=now,
                    schema_version=SCHEMA_VERSION,
                    application_version=APP_VERSION,
                )
            )
            database.connection.commit()
        except (sqlite3.Error, OSError, ValueError) as error:
            logger.exception("Could not create EDG project at %s", target)
            self._close_database(database)
            self._discard_incomplete_file(database)
            return ProjectOperationResult(
                error_message=f"Projekt konnte nicht erstellt werden: {error}"
            )

        self._activate(database, repository, project, target)
        logger.info("Created EDG project %s at %s", project.project_name, target)
        return ProjectOperationResult(project=project)

    def open_project(self, project_path: str | Path) -> ProjectOperationResult:
        """Open an existing EDG project and read its project record."""
        try:
            target = self._project_file_path(project_path)
        except ValueError as error:
            logger.warning("Rejected project path: %s", error)
            return ProjectOperationResult(error_message=str(error))

        database = DatabaseConnection(target)
        try:
            database.connect()
            database.ensure_current_schema()
            repository = ProjectRepository(database.connection)
            project = repository.get_project()
            if project is None:
                self._close_database(database)
                return ProjectOperationResult(
                    error_message="Die Datei enthält keinen Projektdatensatz."
                )
        except (sqlite3.Error, OSError, ValueError) as error:
            logger.exception("Could not open EDG project at %s", target)
            self._close_database(database)
            return ProjectOperationResult(
                error_message=f"Projekt konnte nicht geöffnet werden: {error}"
            )

        self._activate(database, repository, project, target)
        logger.info("Opened EDG project %s from %s", project.project_name, target)
        return ProjectOperationResult(project=project)

    def save_project(self, project: Project | None = None) -> ProjectOperationResult:
        """Persist the active project's metadata and update its modification time."""
        repository = self._repository
        database = self._database
        current_project = project or self._project
        if repository is None or database is None or current_project is None:
            message = "Es ist kein Projekt geöffnet."
            logger.warning(message)
            return ProjectOperationResult(error_message=message)

        updated_project = replace(
            current_project,
            modified_at=datetime.now(),
        )
        try:
            persisted_project = repository.update_project(updated_project)
            if persisted_project is None:
                self._rollback_database(database)
                return ProjectOperationResult(
                    error_message="Der Projektdatensatz konnte nicht gespeichert werden."
                )
            database.connection.commit()
        except (sqlite3.Error, ValueError) as error:
            logger.exception("Could not save EDG project %s", self._project_path)
            self._rollback_database(database)
            return ProjectOperationResult(
                error_message=f"Projekt konnte nicht gespeichert werden: {error}"
            )

        self._project = persisted_project
        logger.info("Saved EDG project %s", persisted_project.project_name)
        return ProjectOperationResult(project=persisted_project)

    def close_project(self) -> None:
        """Close the active project connection and clear its in-memory state."""
        database = self._database
        self._database = None
        self._repository = None
        self._project = None
        self._project_path = None
        if database is not None:
            self._close_database(database)

    @staticmethod
    def _project_file_path(project_path: str | Path) -> Path:
        path = Path(project_path)
        if path.suffix.casefold() == "":
            path = path.with_suffix(".edg")
        if path.suffix.casefold() != ".edg":
            raise ValueError("Projektdateien müssen die Dateiendung .edg verwenden.")
        return path

    def _activate(
        self,
        database: DatabaseConnection,
        repository: ProjectRepository,
        project: Project,
        path: Path,
    ) -> None:
        self.close_project()
        self._database = database
        self._repository = repository
        self._project = project
        self._project_path = path

    @staticmethod
    def _close_database(database: DatabaseConnection) -> None:
        try:
            database.close()
        except sqlite3.Error:
            logger.exception("Could not close database connection for %s", database.path)

    @staticmethod
    def _rollback_database(database: DatabaseConnection) -> None:
        try:
            database.connection.rollback()
        except sqlite3.Error:
            logger.exception("Could not roll back database transaction for %s", database.path)

    @staticmethod
    def _discard_incomplete_file(database: DatabaseConnection) -> None:
        if database.created_file:
            try:
                database.path.unlink(missing_ok=True)
            except OSError:
                logger.exception("Could not remove incomplete project file %s", database.path)
