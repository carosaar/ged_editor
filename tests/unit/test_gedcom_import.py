import sqlite3
from datetime import datetime
from pathlib import Path

from ged_editor.database.connection import DatabaseConnection
from ged_editor.models import Person
from ged_editor.repositories.person_repository import PersonRepository
from ged_editor.services.gedcom_import_service import GEDCOMImportService
from ged_editor.services.project_service import ProjectService
from ged_editor.utils.gedcom_parser import parse_file

_FIXTURE = Path(__file__).parents[1] / "testdata" / "minimal.ged"


def test_parser_reads_only_supported_person_family_and_source_fields() -> None:
    data = parse_file(_FIXTURE)

    assert len(data.persons) == 2
    assert data.persons[0].gedcom_xref == "@I1@"
    assert data.persons[0].name == "Johann /Müller/"
    assert data.persons[0].sex == "M"
    assert len(data.families) == 2
    assert data.families[0].gedcom_xref == "@F1@"
    assert data.families[0].husb_xref == "@I1@"
    assert data.families[0].wife_xref == "@I2@"
    assert len(data.sources) == 1
    assert data.sources[0].gedcom_xref == "@S1@"
    assert data.sources[0].title == "Heiratsregister Sulzbach"


def test_import_persists_records_and_resolves_person_xrefs(tmp_path) -> None:
    database = DatabaseConnection(tmp_path / "import.edg")
    connection = database.connect(create=True)
    database.initialize_schema()

    result = GEDCOMImportService(connection).import_file(_FIXTURE)

    assert result.succeeded
    assert result.persons_imported == 2
    assert result.families_imported == 2
    assert result.sources_imported == 1
    assert len(result.warnings) == 1

    people = {
        row["gedcom_xref"]: row["id"]
        for row in connection.execute(
            "SELECT id, gedcom_xref FROM person"
        )
    }
    family = connection.execute(
        """
        SELECT husb_person_id, wife_person_id, is_existing_record
        FROM family_link WHERE gedcom_xref = '@F1@'
        """
    ).fetchone()
    unresolved_family = connection.execute(
        """
        SELECT husb_person_id, wife_person_id
        FROM family_link WHERE gedcom_xref = '@F2@'
        """
    ).fetchone()
    source = connection.execute(
        "SELECT gedcom_xref, title FROM source"
    ).fetchone()

    assert tuple(family) == (people["@I1@"], people["@I2@"], 1)
    assert tuple(unresolved_family) == (None, people["@I2@"])
    assert tuple(source) == ("@S1@", "Heiratsregister Sulzbach")

    database.close()


def test_reimport_updates_records_without_creating_duplicates(tmp_path) -> None:
    database = DatabaseConnection(tmp_path / "repeat-import.edg")
    connection = database.connect(create=True)
    database.initialize_schema()
    importer = GEDCOMImportService(connection)

    first = importer.import_file(_FIXTURE)
    people = PersonRepository(connection)
    person = people.get_by_xref("@I1@")
    assert person is not None
    modified_person = Person(
        id=person.id,
        gedcom_xref=person.gedcom_xref,
        name=person.name,
        sex=person.sex,
        is_existing_record=person.is_existing_record,
        created_at=person.created_at,
        modified_at=datetime.now(),
        needs_export=True,
        source_snapshot='{"name":"from source"}',
    )
    people.update(modified_person)
    second = importer.import_file(_FIXTURE)

    assert first.succeeded and second.succeeded
    assert connection.execute("SELECT COUNT(*) FROM person").fetchone()[0] == 2
    preserved_person = people.get_by_xref("@I1@")
    assert preserved_person is not None
    assert preserved_person.needs_export
    assert preserved_person.source_snapshot == '{"name":"from source"}'
    assert connection.execute("SELECT COUNT(*) FROM family_link").fetchone()[0] == 2
    assert connection.execute("SELECT COUNT(*) FROM source").fetchone()[0] == 1
    database.close()


def test_schema_v2_migration_adds_source_without_rebuilding_existing_tables(
    tmp_path,
) -> None:
    project_path = tmp_path / "legacy-v2.edg"
    creator = ProjectService()
    created = creator.create_new_project(project_path)
    assert created.succeeded
    creator.close_project()

    database = DatabaseConnection(project_path)
    connection = database.connect()
    with connection:
        connection.execute("DROP TABLE source")
        connection.execute(
            'UPDATE meta SET "value" = "2" WHERE "key" = "schema_version"'
        )
        connection.execute("UPDATE project SET schema_version = '2'")
    database.close()

    with sqlite3.connect(project_path) as connection:
        original_columns = {
            table: tuple(
                row[1]
                for row in connection.execute(f"PRAGMA table_info({table})")
            )
            for table in ("project", "meta", "person", "family_link", "marriage_record")
        }

    service = ProjectService()
    opened = service.open_project(project_path)

    assert opened.succeeded
    assert opened.project is not None
    assert opened.project.schema_version == "4"
    assert service.connection is not None
    assert service.connection.execute(
        "SELECT name FROM sqlite_master WHERE type = 'table' AND name = 'source'"
    ).fetchone() is not None
    with sqlite3.connect(project_path) as connection:
        migrated_columns = {
            table: tuple(
                row[1]
                for row in connection.execute(f"PRAGMA table_info({table})")
            )
            for table in original_columns
        }
    assert migrated_columns == original_columns
    service.close_project()
