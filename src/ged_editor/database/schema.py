"""SQLite schema definitions for EDG project files."""

import sqlite3
from typing import Final

from ged_editor.app.constants import APP_VERSION

SCHEMA_VERSION: Final[str] = "5"

PROJECT_META_DEFAULTS: Final[dict[str, str]] = {
    # Application-maintained compatibility metadata.
    "schema_version": SCHEMA_VERSION,
    "application_version": APP_VERSION,
    # Project-wide GEDCOM marriage and source settings.
    "marr_type": "",
    "marriage_place_default": "",
    "source_xref": "",
    # Prefix/suffix values may be empty.
    "xref_prefix": "",
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
    created_at TEXT NOT NULL,
    modified_at TEXT NOT NULL,
    source_snapshot TEXT,
    birth_date_raw TEXT,
    birth_date_gedcom TEXT,
    birth_place TEXT,
    death_date_raw TEXT,
    death_date_gedcom TEXT,
    death_place TEXT
)
"""

_MARRIAGE_RECORD_TABLE_SQL: Final[str] = """
CREATE TABLE IF NOT EXISTS marriage_record (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    gedcom_xref TEXT,
    source_snapshot TEXT,
    year INTEGER,
    number INTEGER,
    display_number TEXT NOT NULL DEFAULT '',
    workflow_status TEXT NOT NULL CHECK (
        workflow_status IN ('In Bearbeitung', 'Fertig')
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

# Kept only to convert projects written before the current two-state workflow.
_MARRIAGE_RECORD_V4_TABLE_SQL: Final[str] = """
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

_PERSON_COLUMNS: Final[frozenset[str]] = frozenset(
    {
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
)
_MARRIAGE_RECORD_COLUMNS: Final[frozenset[str]] = frozenset(
    {
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
)
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
    "person": _PERSON_COLUMNS,
    "marriage_record": _MARRIAGE_RECORD_COLUMNS,
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
    connection.execute(_MARRIAGE_RECORD_TABLE_SQL)
    connection.execute(_SOURCE_TABLE_SQL)
    connection.executemany(
        'INSERT OR IGNORE INTO meta ("key", "value") VALUES (?, ?)',
        PROJECT_META_DEFAULTS.items(),
    )


def upgrade_schema_v4(connection: sqlite3.Connection) -> None:
    """Upgrade pre-v4 records to the legacy v4 layout before the v5 migration."""
    person_columns = _table_columns(connection, "person")
    if "source_snapshot" not in person_columns:
        connection.execute("ALTER TABLE person ADD COLUMN source_snapshot TEXT")

    family_columns = _table_columns(connection, "family_link")
    if family_columns and "source_snapshot" not in family_columns:
        connection.execute("ALTER TABLE family_link ADD COLUMN source_snapshot TEXT")

    marriage_columns = _table_columns(connection, "marriage_record")
    if marriage_columns and "export_status" not in marriage_columns:
        temporary_table_sql = _MARRIAGE_RECORD_V4_TABLE_SQL.replace(
            "CREATE TABLE IF NOT EXISTS marriage_record",
            "CREATE TABLE marriage_record_v4",
            1,
        )
        connection.execute(temporary_table_sql)
        connection.execute(
            """
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


def upgrade_schema_v5(connection: sqlite3.Connection) -> None:
    """Normalize domain tables and migrate FAM records into MarriageRecord."""
    # Read the v4-only table before dropping it so imported FAM data survives.
    family_columns = _table_columns(connection, "family_link")
    family_rows = (
        connection.execute("SELECT * FROM family_link").fetchall()
        if family_columns
        else ()
    )

    person_columns = _table_columns(connection, "person")
    person_rows = (
        connection.execute("SELECT * FROM person").fetchall()
        if person_columns
        else ()
    )
    connection.execute(
        _PERSON_TABLE_SQL.replace(
            "CREATE TABLE IF NOT EXISTS person",
            "CREATE TABLE person_v5",
            1,
        )
    )
    for row in person_rows:
        values = _row_values(
            row,
            (
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
            ),
        )
        connection.execute(
            """
            INSERT INTO person_v5 (
                id, gedcom_xref, name, sex, created_at, modified_at,
                source_snapshot, birth_date_raw, birth_date_gedcom, birth_place,
                death_date_raw, death_date_gedcom, death_place
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            values,
        )
    if person_columns:
        connection.execute("DROP TABLE person")
    connection.execute("ALTER TABLE person_v5 RENAME TO person")

    marriage_columns = _table_columns(connection, "marriage_record")
    marriage_rows = (
        connection.execute("SELECT * FROM marriage_record").fetchall()
        if marriage_columns
        else ()
    )
    connection.execute(
        _MARRIAGE_RECORD_TABLE_SQL.replace(
            "CREATE TABLE IF NOT EXISTS marriage_record",
            "CREATE TABLE marriage_record_v5",
            1,
        )
    )
    for row in marriage_rows:
        workflow_status = _migrate_workflow_status(
            _row_value(row, "workflow_status", _row_value(row, "status"))
        )
        export_status = _row_value(
            row, "export_status", "Nicht exportiert"
        )
        if export_status not in {"Nicht exportiert", "Exportiert", "Konflikt"}:
            raise sqlite3.IntegrityError(
                f"Unsupported legacy export status: {export_status!r}."
            )
        values = (
            _row_value(row, "id"),
            _row_value(row, "gedcom_xref"),
            _row_value(row, "source_snapshot"),
            _row_value(row, "year"),
            _row_value(row, "number"),
            _row_value(row, "display_number", ""),
            workflow_status,
            export_status,
            _row_value(row, "created_at"),
            _row_value(row, "modified_at"),
            _row_value(row, "husb_person_id"),
            _row_value(row, "wife_person_id"),
            _row_value(row, "marriage_date_raw"),
            _row_value(row, "marriage_date_gedcom"),
            _row_value(row, "marriage_place"),
            _row_value(row, "note_origin_husband"),
            _row_value(row, "note_origin_wife"),
            _row_value(row, "note_death_husband"),
            _row_value(row, "note_death_wife"),
            _row_value(row, "note_legitimation"),
            _row_value(row, "note_marginal"),
            _row_value(row, "note_comments"),
        )
        connection.execute(
            """
            INSERT INTO marriage_record_v5 (
                id, gedcom_xref, source_snapshot, year, number, display_number,
                workflow_status, export_status, created_at, modified_at,
                husb_person_id,
                wife_person_id, marriage_date_raw, marriage_date_gedcom,
                marriage_place, note_origin_husband, note_origin_wife,
                note_death_husband, note_death_wife, note_legitimation,
                note_marginal, note_comments
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            values,
        )

    for row in family_rows:
        values = (
            _row_value(row, "gedcom_xref"),
            _row_value(row, "created_at"),
            _row_value(row, "modified_at"),
            _row_value(row, "husb_person_id"),
            _row_value(row, "wife_person_id"),
            _row_value(row, "source_snapshot"),
        )
        connection.execute(
            """
            INSERT INTO marriage_record_v5 (
                gedcom_xref, year, number, display_number, workflow_status,
                export_status,
                created_at, modified_at, husb_person_id, wife_person_id,
                source_snapshot
            ) VALUES (?, NULL, NULL, '', 'In Bearbeitung', 'Nicht exportiert',
                      ?, ?, ?, ?, ?)
            """,
            values,
        )

    if marriage_columns:
        connection.execute("DROP TABLE marriage_record")
    connection.execute(
        "ALTER TABLE marriage_record_v5 RENAME TO marriage_record"
    )
    if family_columns:
        connection.execute("DROP TABLE family_link")


def _row_values(
    row: sqlite3.Row,
    column_names: tuple[str, ...],
) -> tuple[object, ...]:
    return tuple(_row_value(row, column_name) for column_name in column_names)


def _row_value(row: sqlite3.Row, column_name: str, default: object = None) -> object:
    return row[column_name] if column_name in row.keys() else default


def _migrate_workflow_status(status: object) -> str:
    if status in {"Fertig", "Geprüft", "Exportiert"}:
        return "Fertig"
    if status in {"Neu", "In Bearbeitung"}:
        return "In Bearbeitung"
    raise sqlite3.IntegrityError(
        f"Unsupported legacy workflow status: {status!r}."
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

    table_names = {
        row[0]
        for row in connection.execute(
            "SELECT name FROM sqlite_master WHERE type = 'table' "
            "AND name NOT LIKE 'sqlite_%'"
        )
    }
    if table_names != _SCHEMA_COLUMNS.keys():
        raise sqlite3.DatabaseError("Project database has an invalid set of tables.")

    for table_name, required_columns in _SCHEMA_COLUMNS.items():
        columns = _table_columns(connection, table_name)
        if columns != required_columns:
            raise sqlite3.DatabaseError(
                f"Project database table '{table_name}' has an invalid schema."
            )

    meta_keys = {row[0] for row in connection.execute('SELECT "key" FROM meta')}
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
