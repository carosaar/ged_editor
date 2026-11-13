import sqlite3
from dataclasses import replace
from datetime import datetime

from ged_editor.app.constants import APP_VERSION
from ged_editor.database.connection import DatabaseConnection
from ged_editor.database.schema import SCHEMA_VERSION
from ged_editor.models import (
    MarriageRecord,
    MarriageRecordExportStatus,
    MarriageRecordStatus,
    Person,
)
from ged_editor.services import MarriageRecordService, PersonService
from ged_editor.services.project_service import ProjectService


def _new_person(name: str) -> Person:
    now = datetime.now()
    return Person(
        id=None,
        gedcom_xref=None,
        name=name,
        sex=None,
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
    assert created.source_snapshot is None
    assert service.get_by_id(created.id) == created
    database.close()

    database = DatabaseConnection(tmp_path / "people.edg")
    service = PersonService(database.connect())
    assert service.get_by_id(created.id) == created

    updated = replace(
        created,
        name="Anna Muster",
        source_snapshot='{"name":"Anna Beispiel"}',
        birth_date_raw="12.01.1900",
        birth_date_gedcom="12 JAN 1900",
        birth_place="Sulzbach",
        death_date_raw="01.02.1980",
        death_date_gedcom="1 FEB 1980",
        death_place="Saarbrücken",
    )
    saved = service.update(updated)
    assert saved == updated
    assert service.get_by_id(created.id) == updated

    assert service.delete(created.id)
    assert service.get_by_id(created.id) is None
    database.close()


def test_record_status_enums_keep_workflow_and_export_status_separate() -> None:
    assert {status.value for status in MarriageRecordStatus} == {
        "In Bearbeitung",
        "Fertig",
    }
    assert {status.value for status in MarriageRecordExportStatus} == {
        "Nicht exportiert",
        "Exportiert",
        "Konflikt",
    }


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
        workflow_status=MarriageRecordStatus.IN_BEARBEITUNG,
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
        gedcom_xref="@F15@",
        source_snapshot='{"marriage_date":"12 MAY 1878"}',
    )

    created = service.create(record)

    assert created.id is not None
    assert created.workflow_status is MarriageRecordStatus.IN_BEARBEITUNG
    assert created.export_status.value == "Nicht exportiert"
    assert service.get_by_id(created.id) == created
    database.close()

    database = DatabaseConnection(tmp_path / "marriages.edg")
    service = MarriageRecordService(database.connect())
    assert service.get_by_id(created.id) == created

    updated = replace(
        created,
        workflow_status=MarriageRecordStatus.FERTIG,
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
    assert values["marr_type"] == ""
    assert values["marriage_place_default"] == ""
    assert values["xref_prefix"] == ""
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
        connection.executemany(
            """
            INSERT INTO marriage_record (
                year, number, display_number, status, created_at, modified_at
            ) VALUES (1900, ?, ?, ?, ?, ?)
            """,
            (
                (2, "2/1900", "Neu", now, now),
                (3, "3/1900", "Geprüft", now, now),
            ),
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
        "SELECT workflow_status, export_status FROM marriage_record WHERE id = 1"
    ).fetchone()
    assert tuple(migrated_record) == ("Fertig", "Exportiert")
    migrated_statuses = service.connection.execute(
        "SELECT workflow_status, export_status FROM marriage_record ORDER BY id"
    ).fetchall()
    assert [tuple(row) for row in migrated_statuses] == [
        ("Fertig", "Exportiert"),
        ("In Bearbeitung", "Nicht exportiert"),
        ("Fertig", "Nicht exportiert"),
    ]
    person_columns = {
        row["name"]
        for row in service.connection.execute("PRAGMA table_info(person)")
    }
    assert "source_snapshot" in person_columns
    assert "needs_export" not in person_columns
    assert "is_existing_record" not in person_columns
    assert service.connection.execute(
        "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = 'family_link'"
    ).fetchone() is None
    service.close_project()


def test_schema_v4_migration_moves_family_data_to_marriage_records(
    tmp_path,
) -> None:
    project_path = tmp_path / "legacy-v4.edg"
    creator = ProjectService()
    created = creator.create_new_project(project_path, "Legacy")
    assert created.succeeded
    creator.close_project()

    now = datetime.now().isoformat()
    with sqlite3.connect(project_path) as connection:
        person_id = connection.execute(
            """
            INSERT INTO person (
                gedcom_xref, name, sex, created_at, modified_at
            ) VALUES ('@I1@', 'Max Beispiel', 'M', ?, ?)
            """,
            (now, now),
        ).lastrowid
        connection.execute(
            "ALTER TABLE person ADD COLUMN is_existing_record INTEGER NOT NULL DEFAULT 0"
        )
        connection.execute(
            "ALTER TABLE person ADD COLUMN needs_export INTEGER NOT NULL DEFAULT 0"
        )
        connection.execute(
            """
            INSERT INTO marriage_record (
                year, number, display_number, workflow_status, created_at, modified_at,
                marriage_date_raw, marriage_date_gedcom, marriage_place
            ) VALUES (1901, 2, '2/1901', 'Fertig', ?, ?, '01.02.1901',
                      '1 FEB 1901', 'Sulzbach')
            """,
            (now, now),
        )
        connection.execute(
            """
            CREATE TABLE family_link (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                gedcom_xref TEXT,
                husb_person_id INTEGER REFERENCES person(id),
                wife_person_id INTEGER REFERENCES person(id),
                is_existing_record INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL,
                modified_at TEXT NOT NULL,
                source_snapshot TEXT
            )
            """
        )
        connection.execute(
            """
            INSERT INTO family_link (
                id, gedcom_xref, husb_person_id, wife_person_id,
                is_existing_record, created_at, modified_at, source_snapshot
            ) VALUES (12, '@F12@', ?, NULL, 1, ?, ?, '{"husb":"@I1@"}')
            """,
            (person_id, now, now),
        )
        connection.execute(
            'UPDATE meta SET "value" = "4" WHERE "key" = "schema_version"'
        )
        connection.execute("UPDATE project SET schema_version = '4'")

    service = ProjectService()
    opened = service.open_project(project_path)

    assert opened.succeeded
    assert service.connection is not None
    record = service.connection.execute(
        """
        SELECT gedcom_xref, source_snapshot, year, number, workflow_status,
               export_status,
               husb_person_id, wife_person_id, created_at, modified_at
        FROM marriage_record WHERE gedcom_xref = '@F12@'
        """
    ).fetchone()
    assert tuple(record) == (
        "@F12@",
        '{"husb":"@I1@"}',
        None,
        None,
        "In Bearbeitung",
        "Nicht exportiert",
        person_id,
        None,
        now,
        now,
    )
    existing_record = service.connection.execute(
        """
        SELECT year, number, display_number, workflow_status, marriage_date_gedcom,
               marriage_place
        FROM marriage_record WHERE id = 1
        """
    ).fetchone()
    assert tuple(existing_record) == (
        1901,
        2,
        "2/1901",
        "Fertig",
        "1 FEB 1901",
        "Sulzbach",
    )
    assert service.connection.execute(
        "SELECT COUNT(*) FROM marriage_record"
    ).fetchone()[0] == 2
    assert service.connection.execute(
        "SELECT COUNT(*) FROM person WHERE gedcom_xref = '@I1@'"
    ).fetchone()[0] == 1
    assert service.connection.execute(
        "SELECT name FROM sqlite_master WHERE type = 'table' AND name = 'family_link'"
    ).fetchone() is None
    service.close_project()
