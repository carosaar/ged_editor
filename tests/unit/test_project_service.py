import sqlite3
from dataclasses import replace

import pytest

from ged_editor.app.constants import APP_VERSION
from ged_editor.database.schema import SCHEMA_VERSION
from ged_editor.services.project_service import ProjectService


def test_create_new_project_persists_demo_project(tmp_path) -> None:
    project_path = tmp_path / "testprojekt.edg"
    service = ProjectService()

    result = service.create_new_project(project_path)

    assert result.succeeded
    assert result.project is not None
    assert result.project.id == 1
    assert result.project.project_name == "Neues Projekt"
    assert result.project.schema_version == SCHEMA_VERSION
    assert result.project.application_version == APP_VERSION
    assert project_path.is_file()
    assert service.current_project == result.project
    service.close_project()

    with sqlite3.connect(project_path) as connection:
        row = connection.execute(
            "SELECT project_name, schema_version, application_version "
            "FROM project"
        ).fetchone()

    assert row == ("Neues Projekt", SCHEMA_VERSION, APP_VERSION)


def test_open_project_reads_project_information(tmp_path) -> None:
    project_path = tmp_path / "testprojekt.edg"
    creator = ProjectService()
    created = creator.create_new_project(project_path)
    creator.close_project()
    assert created.project is not None

    opener = ProjectService()
    result = opener.open_project(project_path)

    assert result.succeeded
    assert result.project == created.project
    assert opener.current_project == created.project
    opener.close_project()


def test_save_project_updates_metadata(tmp_path) -> None:
    project_path = tmp_path / "testprojekt.edg"
    service = ProjectService()
    created = service.create_new_project(project_path, "Ausgangsname")
    assert created.project is not None

    renamed_project = replace(created.project, project_name="Neuer Name")
    saved = service.save_project(renamed_project)

    assert saved.succeeded
    assert saved.project is not None
    assert saved.project.project_name == "Neuer Name"
    assert saved.project.modified_at > created.project.modified_at
    assert service.current_project == saved.project

    reloaded = ProjectService()
    opened = reloaded.open_project(project_path)
    assert opened.succeeded
    assert opened.project == saved.project
    service.close_project()
    reloaded.close_project()


def test_create_new_project_refuses_to_overwrite_existing_file(tmp_path) -> None:
    project_path = tmp_path / "existing.edg"
    project_path.write_bytes(b"keep")
    service = ProjectService()

    result = service.create_new_project(project_path)

    assert not result.succeeded
    assert result.error_message is not None
    assert project_path.read_bytes() == b"keep"


def test_open_project_reports_non_sqlite_file_without_raising(tmp_path) -> None:
    project_path = tmp_path / "broken.edg"
    project_path.write_text("not a database", encoding="utf-8")
    service = ProjectService()

    result = service.open_project(project_path)

    assert not result.succeeded
    assert result.error_message is not None
    assert service.current_project is None


def test_open_project_rejects_database_without_required_schema(tmp_path) -> None:
    project_path = tmp_path / "incomplete.edg"
    with sqlite3.connect(project_path) as connection:
        connection.execute("CREATE TABLE project (id INTEGER PRIMARY KEY)")

    result = ProjectService().open_project(project_path)

    assert not result.succeeded
    assert result.error_message is not None


@pytest.mark.parametrize("filename", ["wrong.ged", "wrong.txt"])
def test_project_service_rejects_non_edg_suffix(tmp_path, filename: str) -> None:
    service = ProjectService()

    result = service.create_new_project(tmp_path / filename)

    assert not result.succeeded
    assert result.error_message is not None
