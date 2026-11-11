"""SQLite schema definitions for EDG project files."""

import sqlite3
from typing import Final

from ged_editor.app.constants import APP_VERSION

SCHEMA_VERSION: Final[str] = "4"
PROJECT_META_DEFAULTS: Final[dict[str, str]] = {
    "schema_version": SCHEMA_VERSION,
    "application_version": APP_VERSION,
    "source_xref": "",
    "refn_prefix": "",
    "refn_suffix": "",
    "page_prefix": "",
    "page_suffix": "",
}

_PROJECT_TABLE_SQL: Final[str] = """
CREATE TABLE IF NOT EXISTS project (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    project_name TEXT NOT NULL,
    created_at TEXT NOT NULL,
    modified_at TEXT NOT NULL,
    schema_version TEXT NOT NULL,
    application_version TEXT NOT NULL
)
"""

_META_TABLE_SQL: Final[str] = """
CREATE TABLE IF NOT EXISTS meta (
    "key" TEXT PRIMARY KEY,
    "value" TEXT NOT NULL
)
"""

_PERSON_TABLE_SQL: Final[str] = """
CREATE TABLE IF NOT EXISTS person (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    gedcom_xref TEXT,
    name TEXT NOT NULL,
    sex TEXT,
    is_existing_record INTEGER NOT NULL DEFAULT 0
        CHECK (is_existing_record IN (0, 1)),
    created_at TEXT NOT NULL,
    modified_at TEXT NOT NULL,
    needs_export INTEGER NOT NULL DEFAULT 0
        CHECK (needs_export IN (0, 1)),
    source_snapshot TEXT
)
"""

_FAMILY_LINK_TABLE_SQL: Final[str] = """
CREATE TABLE IF NOT EXISTS family_link (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    gedcom_xref TEXT,
    husb_person_id INTEGER REFERENCES person(id),
    wife_person_id INTEGER REFERENCES person(id),
    is_existing_record INTEGER NOT NULL DEFAULT 0
        CHECK (is_existing_record IN (0, 1)),
    created_at TEXT NOT NULL,
    modified_at TEXT NOT NULL,
    source_snapshot TEXT
)
"""

_MARRIAGE_RECORD_TABLE_SQL: Final[str] = """
CREATE TABLE IF NOT EXISTS marriage_record (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    year INTEGER NOT NULL,
    number INTEGER NOT NULL,
    display_number TEXT NOT NULL,
    status TEXT NOT NULL CHECK (
        status IN ('Neu', 'In Bearbeitung', 'Fertig', 'Geprüft')
    ),
    export_status TEXT NOT NULL DEFAULT 'Nicht exportiert' CHECK (
        export_status IN ('Nicht exportiert', 'Exportiert', 'Konflikt')
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

_SOURCE_TABLE_SQL: Final[str] = """
CREATE TABLE IF NOT EXISTS source (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    gedcom_xref TEXT,
    title TEXT,
    created_at TEXT NOT NULL,
    modified_at TEXT NOT NULL
)
"""

_PROJECT_COLUMNS: Final[frozenset[str]] = frozenset(
    {
        "id",
        "project_name",
        "created_at",
        "modified_at",
        "schema_version",
        "application_version",
    }
)
_META_COLUMNS: Final[frozenset[str]] = frozenset({"key", "value"})
_SCHEMA_COLUMNS: Final[dict[str, frozenset[str]]] = {
    "project": _PROJECT_COLUMNS,
    "meta": _META_COLUMNS,
    "person": frozenset(
        {
            "id",
            "gedcom_xref",
            "name",
            "sex",
            "is_existing_record",
            "created_at",
            "modified_at",
            "needs_export",
            "source_snapshot",
        }
    ),
    "family_link": frozenset(
        {
            "id",
            "gedcom_xref",
            "husb_person_id",
            "wife_person_id",
            "is_existing_record",
            "created_at",
            "modified_at",
            "source_snapshot",
        }
    ),
    "marriage_record": frozenset(
        {
            "id",
            "year",
            "number",
            "display_number",
            "status",
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
    ),
    "source": frozenset(
        {"id", "gedcom_xref", "title", "created_at", "modified_at"}
    ),
}


def initialize_schema(connection: sqlite3.Connection) -> None:
    """Create project, metadata, domain, and source tables if missing."""
    with connection:
        initialize_schema_statements(connection)


def initialize_schema_statements(connection: sqlite3.Connection) -> None:
    """Apply schema DDL and metadata defaults inside the caller's transaction."""
    connection.execute(_PROJECT_TABLE_SQL)
    connection.execute(_META_TABLE_SQL)
    connection.execute(_PERSON_TABLE_SQL)
    connection.execute(_FAMILY_LINK_TABLE_SQL)
    connection.execute(_MARRIAGE_RECORD_TABLE_SQL)
    connection.execute(_SOURCE_TABLE_SQL)
    connection.executemany(
        'INSERT OR IGNORE INTO meta ("key", "value") VALUES (?, ?)',
        PROJECT_META_DEFAULTS.items(),
    )


def upgrade_schema_v4(connection: sqlite3.Connection) -> None:
    """Add ADR-017 persistence fields and normalize the legacy workflow status."""
    person_columns = _table_columns(connection, "person")
    if "needs_export" not in person_columns:
        connection.execute(
            "ALTER TABLE person ADD COLUMN needs_export INTEGER NOT NULL "
            "DEFAULT 0 CHECK (needs_export IN (0, 1))"
        )
    if "source_snapshot" not in person_columns:
        connection.execute("ALTER TABLE person ADD COLUMN source_snapshot TEXT")

    family_columns = _table_columns(connection, "family_link")
    if "source_snapshot" not in family_columns:
        connection.execute("ALTER TABLE family_link ADD COLUMN source_snapshot TEXT")

    marriage_columns = _table_columns(connection, "marriage_record")
    if "export_status" not in marriage_columns:
        temporary_table_sql = _MARRIAGE_RECORD_TABLE_SQL.replace(
            "CREATE TABLE IF NOT EXISTS marriage_record",
            "CREATE TABLE marriage_record_v4",
            1,
        )
        connection.execute(temporary_table_sql)
        connection.execute(
            f"""
            INSERT INTO marriage_record_v4 (
                id, year, number, display_number, status, export_status,
                created_at, modified_at, husb_person_id, wife_person_id,
                marriage_date_raw, marriage_date_gedcom, marriage_place,
                note_origin_husband, note_origin_wife, note_death_husband,
                note_death_wife, note_legitimation, note_marginal, note_comments
            )
            SELECT id, year, number, display_number,
                   CASE WHEN status = 'Exportiert' THEN 'Geprüft' ELSE status END,
                   CASE WHEN status = 'Exportiert'
                       THEN 'Exportiert' ELSE 'Nicht exportiert' END,
                   created_at, modified_at, husb_person_id, wife_person_id,
                   marriage_date_raw, marriage_date_gedcom, marriage_place,
                   note_origin_husband, note_origin_wife, note_death_husband,
                   note_death_wife, note_legitimation, note_marginal, note_comments
            FROM marriage_record
            """
        )
        connection.execute("DROP TABLE marriage_record")
        connection.execute(
            "ALTER TABLE marriage_record_v4 RENAME TO marriage_record"
        )


def _table_columns(connection: sqlite3.Connection, table_name: str) -> set[str]:
    return {
        row[1] for row in connection.execute(f"PRAGMA table_info({table_name})")
    }


def validate_schema(connection: sqlite3.Connection) -> None:
    """Verify SQLite integrity and the complete current EDG schema."""
    integrity_result = connection.execute("PRAGMA quick_check").fetchone()
    if integrity_result is None or integrity_result[0] != "ok":
        raise sqlite3.DatabaseError("Project database integrity check failed.")

    for table_name, required_columns in _SCHEMA_COLUMNS.items():
        columns = _table_columns(connection, table_name)
        if not required_columns.issubset(columns):
            raise sqlite3.DatabaseError(
                f"Project database table '{table_name}' has an invalid schema."
            )

    meta_keys = {
        row[0]
        for row in connection.execute('SELECT "key" FROM meta')
    }
    if not PROJECT_META_DEFAULTS.keys() <= meta_keys:
        raise sqlite3.DatabaseError("Project database metadata is incomplete.")


def validate_project_schema(connection: sqlite3.Connection) -> None:
    """Validate the phase-2 project tables before applying a schema upgrade."""
    integrity_result = connection.execute("PRAGMA quick_check").fetchone()
    if integrity_result is None or integrity_result[0] != "ok":
        raise sqlite3.DatabaseError("Project database integrity check failed.")

    for table_name, required_columns in (
        ("project", _PROJECT_COLUMNS),
        ("meta", _META_COLUMNS),
    ):
        columns = _table_columns(connection, table_name)
        if not required_columns.issubset(columns):
            raise sqlite3.DatabaseError(
                f"Project database table '{table_name}' has an invalid schema."
            )

    project_row = connection.execute("SELECT 1 FROM project LIMIT 1").fetchone()
    if project_row is None:
        raise sqlite3.DatabaseError("Project database has no project record.")
