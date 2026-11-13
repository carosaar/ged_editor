import sqlite3

import pytest

from ged_editor.database.connection import DatabaseConnection
from ged_editor.database.schema import PROJECT_META_DEFAULTS


def test_database_connection_creates_edg_schema(tmp_path) -> None:
    project_path = tmp_path / "testprojekt.edg"
    database = DatabaseConnection(project_path)

    database.connect(create=True)
    database.initialize_schema()

    table_names = {
        row["name"]
        for row in database.connection.execute(
            "SELECT name FROM sqlite_master WHERE type = 'table' "
            "AND name NOT LIKE 'sqlite_%'"
        )
    }
    assert table_names == {
        "project",
        "meta",
        "person",
        "marriage_record",
        "source",
    }

    project_columns = {
        row["name"]
        for row in database.connection.execute("PRAGMA table_info(project)")
    }
    assert project_columns == {
        "id",
        "project_name",
        "created_at",
        "modified_at",
        "schema_version",
        "application_version",
    }

    meta_columns = {
        row["name"]
        for row in database.connection.execute("PRAGMA table_info(meta)")
    }
    assert meta_columns == {"key", "value"}
    meta_values = dict(
        database.connection.execute('SELECT "key", "value" FROM meta').fetchall()
    )
    assert meta_values == PROJECT_META_DEFAULTS

    record_columns = {
        row["name"]
        for row in database.connection.execute("PRAGMA table_info(marriage_record)")
    }
    assert record_columns == {
        "id",
        "gedcom_xref",
        "source_snapshot",
        "year",
        "number",
        "display_number",
        "workflow_status",
        "export_status",
        "created_at",
        "modified_at",
        "husb_person_id",
        "wife_person_id",
        "marriage_date_raw",
        "marriage_date_gedcom",
        "marriage_place",
        "note_origin_husband",
        "note_origin_wife",
        "note_death_husband",
        "note_death_wife",
        "note_legitimation",
        "note_marginal",
        "note_comments",
    }
    source_columns = {
        row["name"]
        for row in database.connection.execute("PRAGMA table_info(source)")
    }
    assert source_columns == {
        "id",
        "gedcom_xref",
        "title",
        "created_at",
        "modified_at",
    }
    person_columns = {
        row["name"]
        for row in database.connection.execute("PRAGMA table_info(person)")
    }
    assert person_columns == {
        "id",
        "gedcom_xref",
        "name",
        "sex",
        "created_at",
        "modified_at",
        "source_snapshot",
        "birth_date_raw",
        "birth_date_gedcom",
        "birth_place",
        "death_date_raw",
        "death_date_gedcom",
        "death_place",
    }
    with pytest.raises(sqlite3.IntegrityError):
        database.connection.execute(
            """
            INSERT INTO marriage_record (
                year, number, display_number, workflow_status, created_at, modified_at
            ) VALUES (1900, 1, '1/1900', 'Neu', 'now', 'now')
            """
        )
    database.close()

    with project_path.open("rb") as project_file:
        assert project_file.read(16) == b"SQLite format 3\x00"


def test_database_connection_does_not_create_when_opening_missing_file(
    tmp_path,
) -> None:
    project_path = tmp_path / "missing.edg"
    database = DatabaseConnection(project_path)

    with pytest.raises(FileNotFoundError):
        database.connect()

    assert not project_path.exists()
