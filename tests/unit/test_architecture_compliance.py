"""Regression tests for the active architecture and persisted project model."""

import sqlite3
from dataclasses import fields
from pathlib import Path

import pytest

from ged_editor.database.connection import DatabaseConnection
from ged_editor.database.schema import PROJECT_META_DEFAULTS
from ged_editor.models import (
    MarriageRecord,
    MarriageRecordExportStatus,
    MarriageRecordStatus,
    Person,
)
from ged_editor.services.project_service import ProjectService

_PROJECT_ROOT = Path(__file__).resolve().parents[2]

def test_workflow_status_enum_matches_adr_015() -> None:
    assert {status.value for status in MarriageRecordStatus} == {
        "In Bearbeitung",
        "Fertig",
    }


def test_export_status_enum_matches_adr_019() -> None:
    assert {status.value for status in MarriageRecordExportStatus} == {
        "Nicht exportiert",
        "Exportiert",
        "Konflikt",
    }


def test_database_constraints_reject_non_architectural_statuses(tmp_path) -> None:
    database = DatabaseConnection(tmp_path / "statuses.edg")
    connection = database.connect(create=True)
    database.initialize_schema()
    now = "2026-11-13T00:00:00"

    for workflow_status in ("In Bearbeitung", "Fertig"):
        connection.execute(
            """
            INSERT INTO marriage_record (
                display_number, workflow_status, created_at, modified_at
            ) VALUES ('', ?, ?, ?)
            """,
            (workflow_status, now, now),
        )

    for workflow_status in ("Neu", "Geprüft", "Exportiert", "Other"):
        with pytest.raises(sqlite3.IntegrityError):
            connection.execute(
                """
                INSERT INTO marriage_record (
                    display_number, workflow_status, created_at, modified_at
                ) VALUES ('', ?, ?, ?)
                """,
                (workflow_status, now, now),
            )

    for export_status in ("Nicht exportiert", "Exportiert", "Konflikt"):
        connection.execute(
            """
            INSERT INTO marriage_record (
                display_number, workflow_status, export_status, created_at,
                modified_at
            ) VALUES ('', 'In Bearbeitung', ?, ?, ?)
            """,
            (export_status, now, now),
        )

    for export_status in ("Neu", "Geprüft", "Other"):
        with pytest.raises(sqlite3.IntegrityError):
            connection.execute(
                """
                INSERT INTO marriage_record (
                    display_number, workflow_status, export_status, created_at,
                    modified_at
                ) VALUES ('', 'In Bearbeitung', ?, ?, ?)
                """,
                (export_status, now, now),
            )

    database.close()


def test_active_modules_do_not_reference_removed_family_model() -> None:
    """Skip schema.py: v4 migration reads the legacy table and status values."""
    forbidden_terms = (
        "FamilyLink",
        "family_link",
        "FamilyRepository",
        "FamilyService",
        "needs_export",
        "is_existing_record",
    )
    source_root = _PROJECT_ROOT / "src" / "ged_editor"

    for source_file in source_root.rglob("*.py"):
        if source_file.relative_to(source_root).as_posix() == "database/schema.py":
            continue
        contents = source_file.read_text(encoding="utf-8")
        for forbidden_term in forbidden_terms:
            assert forbidden_term not in contents, (
                f"{forbidden_term!r} remains in active module {source_file}."
            )


def test_project_meta_defaults_include_adr_020_keys() -> None:
    expected_keys = {
        "schema_version",
        "application_version",
        "marr_type",
        "marriage_place_default",
        "source_xref",
        "xref_prefix",
        "refn_prefix",
        "refn_suffix",
        "page_prefix",
        "page_suffix",
    }

    assert expected_keys <= PROJECT_META_DEFAULTS.keys()
    assert all(value is not None for value in PROJECT_META_DEFAULTS.values())


def test_marriage_record_model_contains_data_model_fields() -> None:
    expected_fields = {
        "gedcom_xref",
        "source_snapshot",
        "year",
        "number",
        "display_number",
        "workflow_status",
        "export_status",
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

    assert expected_fields <= {field.name for field in fields(MarriageRecord)}


def test_person_model_contains_data_model_fields() -> None:
    expected_fields = {
        "gedcom_xref",
        "source_snapshot",
        "name",
        "sex",
        "birth_date_raw",
        "birth_date_gedcom",
        "birth_place",
        "death_date_raw",
        "death_date_gedcom",
        "death_place",
    }

    assert expected_fields <= {field.name for field in fields(Person)}


def test_person_model_has_no_export_or_existing_record_flags() -> None:
    person_fields = {field.name for field in fields(Person)}

    assert "needs_export" not in person_fields
    assert "is_existing_record" not in person_fields


def test_schema_v4_project_migrates_to_current_architecture(tmp_path) -> None:
    project_path = tmp_path / "migrated-v4.edg"
    creator = ProjectService()
    assert creator.create_new_project(project_path, "Schema v4").succeeded
    creator.close_project()

    now = "2026-11-13T00:00:00"
    with sqlite3.connect(project_path) as connection:
        person_id = connection.execute(
            """
            INSERT INTO person (name, sex, created_at, modified_at)
            VALUES ('Max Beispiel', 'M', ?, ?)
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
                year, number, display_number, workflow_status, created_at,
                modified_at, husb_person_id
            ) VALUES (1901, 2, '2/1901', 'Fertig', ?, ?, ?)
            """,
            (now, now, person_id),
        )
        connection.execute(
            """
            CREATE TABLE family_link (
                id INTEGER PRIMARY KEY,
                gedcom_xref TEXT,
                husb_person_id INTEGER,
                wife_person_id INTEGER,
                created_at TEXT NOT NULL,
                modified_at TEXT NOT NULL,
                source_snapshot TEXT
            )
            """
        )
        connection.execute(
            """
            INSERT INTO family_link (
                id, gedcom_xref, husb_person_id, created_at, modified_at,
                source_snapshot
            ) VALUES (8, '@F8@', ?, ?, ?, '{}')
            """,
            (person_id, now, now),
        )
        connection.execute(
            'UPDATE meta SET "value" = "4" WHERE "key" = "schema_version"'
        )
        connection.execute("UPDATE project SET schema_version = '4'")
        assert connection.execute(
            'SELECT "value" FROM meta WHERE "key" = "schema_version"'
        ).fetchone() == ("4",)

    service = ProjectService()
    opened = service.open_project(project_path)

    assert opened.succeeded
    assert opened.project is not None
    assert opened.project.schema_version == "5"
    connection = service.connection
    assert connection is not None

    marriage_columns = {
        row["name"] for row in connection.execute("PRAGMA table_info(marriage_record)")
    }
    assert {
        "gedcom_xref",
        "source_snapshot",
        "year",
        "number",
        "display_number",
        "workflow_status",
        "export_status",
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
    } <= marriage_columns
    person_columns = {
        row["name"] for row in connection.execute("PRAGMA table_info(person)")
    }
    assert {
        "gedcom_xref",
        "source_snapshot",
        "name",
        "sex",
        "birth_date_raw",
        "birth_date_gedcom",
        "birth_place",
        "death_date_raw",
        "death_date_gedcom",
        "death_place",
    } <= person_columns
    assert "is_existing_record" not in person_columns
    assert "needs_export" not in person_columns

    meta_keys = {
        row["key"] for row in connection.execute('SELECT "key" FROM meta')
    }
    assert PROJECT_META_DEFAULTS.keys() <= meta_keys
    assert connection.execute("SELECT COUNT(*) FROM person").fetchone()[0] > 0
    assert connection.execute("SELECT COUNT(*) FROM marriage_record").fetchone()[0] > 0
    assert connection.execute(
        "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = 'family_link'"
    ).fetchone() is None
    service.close_project()
