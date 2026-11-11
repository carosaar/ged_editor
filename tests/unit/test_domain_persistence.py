import sqlite3
from dataclasses import replace
from datetime import datetime

from ged_editor.app.constants import APP_VERSION
from ged_editor.database.connection import DatabaseConnection
from ged_editor.models import (
    FamilyLink,
    MarriageRecord,
    MarriageRecordStatus,
    Person,
)
from ged_editor.services import FamilyService, MarriageRecordService, PersonService


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
    assert service.get_by_id(created.id) == created
    database.close()

    database = DatabaseConnection(tmp_path / "people.edg")
    service = PersonService(database.connect())
    assert service.get_by_id(created.id) == created

    updated = replace(created, name="Anna Muster", is_existing_record=True)
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
    database.close()

    database = DatabaseConnection(tmp_path / "families.edg")
    service = FamilyService(database.connect())
    assert service.get_by_id(created.id) == created

    updated = replace(created, gedcom_xref="@F1@", is_existing_record=True)
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
    assert service.get_by_id(created.id) == created
    database.close()

    database = DatabaseConnection(tmp_path / "marriages.edg")
    service = MarriageRecordService(database.connect())
    assert service.get_by_id(created.id) == created

    updated = replace(created, status=MarriageRecordStatus.FERTIG)
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

    from ged_editor.services.project_service import ProjectService

    result = ProjectService().open_project(project_path)

    assert result.succeeded
    assert result.project is not None
    assert result.project.schema_version == "2"
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
    assert values["schema_version"] == "2"
    assert values["application_version"] == APP_VERSION
    assert values["source_xref"] == "@S1@"
    assert values["refn_prefix"] == ""
    assert values["refn_suffix"] == ""
    assert values["page_prefix"] == ""
    assert values["page_suffix"] == ""
    assert version == "2"
