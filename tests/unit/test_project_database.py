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
        "family_link",
        "marriage_record",
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
        "year",
        "number",
        "display_number",
        "status",
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
