import sqlite3
from dataclasses import replace
from datetime import datetime

from ged_editor.app.constants import APP_VERSION
from ged_editor.database.connection import DatabaseConnection
from ged_editor.database.schema import SCHEMA_VERSION
from ged_editor.models import (
    FamilyLink,
    MarriageRecord,
    MarriageRecordStatus,
    Person,
)
from ged_editor.services import FamilyService, MarriageRecordService, PersonService
from ged_editor.services.project_service import ProjectService


def _new_person(name: str) -> Person:
    now = datetime.now()
    return Person(
        id=None,
        gedcom_xref=None,
        name=name,
        sex=None,
        is_existing_record=False,
        created_at=now,
        modified_at=now,
    )


def test_person_crud_round_trip(tmp_path) -> None:
    database = DatabaseConnection(tmp_path / "people.edg")
    connection = database.connect(create=True)
    database.initialize_schema()
    service = PersonService(connection)

    created = service.create(_new_person("Anna Beispiel"))

    assert created.id is not None
    assert created.gedcom_xref is None
    assert created.needs_export is False
    assert created.source_snapshot is None
    assert service.get_by_id(created.id) == created
    database.close()

    database = DatabaseConnection(tmp_path / "people.edg")
    service = PersonService(database.connect())
    assert service.get_by_id(created.id) == created

    updated = replace(created, name="Anna Muster", is_existing_record=True)
    updated = replace(
        updated,
        needs_export=True,
        source_snapshot='{"name":"Anna Beispiel"}',
    )
    saved = service.update(updated)
    assert saved == updated
    assert service.get_by_id(created.id) == updated

    assert service.delete(created.id)
    assert service.get_by_id(created.id) is None
    database.close()


def test_family_link_crud_round_trip(tmp_path) -> None:
    database = DatabaseConnection(tmp_path / "families.edg")
    connection = database.connect(create=True)
    database.initialize_schema()
    people = PersonService(connection)
    husband = people.create(_new_person("Max Beispiel"))
    wife = people.create(_new_person("Eva Beispiel"))
    service = FamilyService(connection)
    now = datetime.now()
    family = FamilyLink(
        id=None,
        gedcom_xref=None,
        husb_person_id=husband.id,
        wife_person_id=wife.id,
        is_existing_record=False,
        created_at=now,
        modified_at=now,
    )

    created = service.create(family)

    assert created.id is not None
    assert service.get_by_id(created.id) == created
    assert created.source_snapshot is None
    database.close()

    database = DatabaseConnection(tmp_path / "families.edg")
    service = FamilyService(database.connect())
    assert service.get_by_id(created.id) == created

    updated = replace(
        created,
        gedcom_xref="@F1@",
        is_existing_record=True,
        source_snapshot='{"husb":"@I1@","wife":"@I2@"}',
    )
    assert service.update(updated) == updated
    assert service.get_by_id(created.id) == updated

    assert service.delete(created.id)
    assert service.get_by_id(created.id) is None
    database.close()


def test_marriage_record_crud_round_trip(tmp_path) -> None:
    database = DatabaseConnection(tmp_path / "marriages.edg")
    connection = database.connect(create=True)
    database.initialize_schema()
    people = PersonService(connection)
    husband = people.create(_new_person("Max Beispiel"))
    wife = people.create(_new_person("Eva Beispiel"))
    service = MarriageRecordService(connection)
    now = datetime.now()
    record = MarriageRecord(
        id=None,
        year=1878,
        number=15,
        display_number="15/1878",
        status=MarriageRecordStatus.NEU,
        created_at=now,
        modified_at=now,
        husb_person_id=husband.id,
        wife_person_id=wife.id,
        marriage_date_raw="12.05.1878",
        marriage_date_gedcom="12 MAY 1878",
        marriage_place="Sulzbach",
        note_origin_husband="Herkunft des Mannes",
        note_origin_wife="Herkunft der Frau",
        note_death_husband=None,
        note_death_wife=None,
        note_legitimation=None,
        note_marginal=None,
        note_comments=None,
    )

    created = service.create(record)

    assert created.id is not None
    assert created.status is MarriageRecordStatus.NEU
    assert created.export_status.value == "Nicht exportiert"
    assert service.get_by_id(created.id) == created
    database.close()

    database = DatabaseConnection(tmp_path / "marriages.edg")
    service = MarriageRecordService(database.connect())
    assert service.get_by_id(created.id) == created

    from ged_editor.models import MarriageRecordExportStatus

    updated = replace(
        created,
        status=MarriageRecordStatus.FERTIG,
        export_status=MarriageRecordExportStatus.KONFLIKT,
    )
    assert service.update(updated) == updated
    assert service.get_by_id(created.id) == updated

    assert service.delete(created.id)
    assert service.get_by_id(created.id) is None
    database.close()


def test_phase_two_project_is_backed_up_before_schema_upgrade(tmp_path) -> None:
    project_path = tmp_path / "legacy.edg"
    now = datetime.now().isoformat()
    with sqlite3.connect(project_path) as connection:
        connection.execute(
            """
            CREATE TABLE project (
                id INTEGER PRIMARY KEY,
                project_name TEXT NOT NULL,
                created_at TEXT NOT NULL,
                modified_at TEXT NOT NULL,
                schema_version TEXT NOT NULL,
                application_version TEXT NOT NULL
            )
            """
        )
        connection.execute('CREATE TABLE meta ("key" TEXT PRIMARY KEY, "value" TEXT NOT NULL)')
        connection.execute(
            'INSERT INTO meta ("key", "value") VALUES (?, ?)',
            ("source_xref", "@S1@"),
        )
        connection.execute(
            """
            INSERT INTO project VALUES (1, ?, ?, ?, '1', '0.2.0')
            """,
            ("Legacy", now, now),
        )

    result = ProjectService().open_project(project_path)

    assert result.succeeded
    assert result.project is not None
    assert result.project.schema_version == SCHEMA_VERSION
    backups = list(tmp_path.joinpath("legacy_backups").glob("*.edg"))
    assert len(backups) == 1

    with sqlite3.connect(backups[0]) as backup:
        old_tables = {
            row[0]
            for row in backup.execute(
                "SELECT name FROM sqlite_master WHERE type = 'table' "
                "AND name NOT LIKE 'sqlite_%'"
            )
        }
    assert old_tables == {"project", "meta"}

    with sqlite3.connect(project_path) as upgraded:
        values = dict(upgraded.execute('SELECT "key", "value" FROM meta'))
        version = upgraded.execute(
            "SELECT schema_version FROM project WHERE id = 1"
        ).fetchone()[0]
    assert values["schema_version"] == SCHEMA_VERSION
    assert values["application_version"] == APP_VERSION
    assert values["source_xref"] == "@S1@"
    assert values["refn_prefix"] == ""
    assert values["refn_suffix"] == ""
    assert values["page_prefix"] == ""
    assert values["page_suffix"] == ""
    assert version == SCHEMA_VERSION


def test_schema_v3_migration_separates_legacy_exported_status(tmp_path) -> None:
    project_path = tmp_path / "legacy-v3.edg"
    creator = ProjectService()
    assert creator.create_new_project(project_path, "Legacy").succeeded
    creator.close_project()

    with sqlite3.connect(project_path) as connection:
        connection.execute("PRAGMA foreign_keys = OFF")
        connection.execute("DROP TABLE family_link")
        connection.execute("DROP TABLE marriage_record")
        connection.execute("DROP TABLE person")
        connection.execute(
            """
            CREATE TABLE person (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                gedcom_xref TEXT,
                name TEXT NOT NULL,
                sex TEXT,
                is_existing_record INTEGER NOT NULL DEFAULT 0
                    CHECK (is_existing_record IN (0, 1)),
                created_at TEXT NOT NULL,
                modified_at TEXT NOT NULL
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE family_link (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                gedcom_xref TEXT,
                husb_person_id INTEGER REFERENCES person(id),
                wife_person_id INTEGER REFERENCES person(id),
                is_existing_record INTEGER NOT NULL DEFAULT 0
                    CHECK (is_existing_record IN (0, 1)),
                created_at TEXT NOT NULL,
                modified_at TEXT NOT NULL
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE marriage_record (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                year INTEGER NOT NULL,
                number INTEGER NOT NULL,
                display_number TEXT NOT NULL,
                status TEXT NOT NULL CHECK (
                    status IN ('Neu', 'In Bearbeitung', 'Fertig', 'Geprüft', 'Exportiert')
                ),
                created_at TEXT NOT NULL,
                modified_at TEXT NOT NULL,
                husb_person_id INTEGER REFERENCES person(id),
                wife_person_id INTEGER REFERENCES person(id),
                marriage_date_raw TEXT,
                marriage_date_gedcom TEXT,
                marriage_place TEXT,
                note_origin_husband TEXT,
                note_origin_wife TEXT,
                note_death_husband TEXT,
                note_death_wife TEXT,
                note_legitimation TEXT,
                note_marginal TEXT,
                note_comments TEXT
            )
            """
        )
        now = datetime.now().isoformat()
        connection.execute(
            """
            INSERT INTO marriage_record (
                year, number, display_number, status, created_at, modified_at
            ) VALUES (1900, 1, '1/1900', 'Exportiert', ?, ?)
            """,
            (now, now),
        )
        connection.execute(
            'UPDATE meta SET "value" = "3" WHERE "key" = "schema_version"'
        )
        connection.execute("UPDATE project SET schema_version = '3'")

    service = ProjectService()
    opened = service.open_project(project_path)

    assert opened.succeeded
    assert opened.project is not None
    assert opened.project.schema_version == SCHEMA_VERSION
    assert service.connection is not None
    migrated_record = service.connection.execute(
        "SELECT status, export_status FROM marriage_record WHERE id = 1"
    ).fetchone()
    assert tuple(migrated_record) == ("Geprüft", "Exportiert")
    assert {
        row["name"]
        for row in service.connection.execute("PRAGMA table_info(person)")
    } >= {"needs_export", "source_snapshot"}
    assert {
        row["name"]
        for row in service.connection.execute("PRAGMA table_info(family_link)")
    } >= {"source_snapshot"}
    service.close_project()
