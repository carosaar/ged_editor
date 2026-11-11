"""Import supported GEDCOM records into an active EDG project."""

import logging
import sqlite3
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from ged_editor.models.family_link import FamilyLink
from ged_editor.models.person import Person
from ged_editor.models.source import Source
from ged_editor.repositories.family_repository import FamilyRepository
from ged_editor.repositories.person_repository import PersonRepository
from ged_editor.repositories.source_repository import SourceRepository
from ged_editor.utils.gedcom_parser import (
    GedcomFamily,
    GedcomParseError,
    GedcomPerson,
    GedcomSource,
    parse_file,
)

logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class GedcomImportResult:
    """Counts and warnings returned after one GEDCOM import."""

    persons_imported: int = 0
    families_imported: int = 0
    sources_imported: int = 0
    warnings: tuple[str, ...] = ()
    error_message: str | None = None

    @property
    def succeeded(self) -> bool:
        """Return whether the entire import transaction succeeded."""
        return self.error_message is None


class GEDCOMImportService:
    """Import INDI, FAM, and SOUR data without modifying the input file."""

    def __init__(self, connection: sqlite3.Connection) -> None:
        """Bind the importer to an open EDG database connection."""
        connection.row_factory = sqlite3.Row
        self._connection = connection
        self._persons = PersonRepository(connection)
        self._families = FamilyRepository(connection)
        self._sources = SourceRepository(connection)

    def import_file(self, file_path: str | Path) -> GedcomImportResult:
        """Parse and atomically import all supported records from a GEDCOM file."""
        path = Path(file_path)
        try:
            data = parse_file(path)
            warnings: list[str] = []
            with self._connection:
                persons_count = self._import_persons(data.persons)
                families_count = self._import_families(data.families, warnings)
                sources_count = self._import_sources(data.sources)
        except (OSError, UnicodeError, GedcomParseError, sqlite3.Error, ValueError) as error:
            logger.exception("GEDCOM import failed for %s", path)
            return GedcomImportResult(error_message=str(error))

        logger.info(
            "Imported GEDCOM file %s: %d persons, %d families, %d sources",
            path,
            persons_count,
            families_count,
            sources_count,
        )
        return GedcomImportResult(
            persons_imported=persons_count,
            families_imported=families_count,
            sources_imported=sources_count,
            warnings=tuple(warnings),
        )

    def import_persons(self, persons: tuple[GedcomPerson, ...]) -> int:
        """Import parsed persons and return the number of records processed."""
        with self._connection:
            return self._import_persons(persons)

    def import_families(self, families: tuple[GedcomFamily, ...]) -> int:
        """Import parsed families and resolve their XREFs to person IDs."""
        warnings: list[str] = []
        with self._connection:
            imported = self._import_families(families, warnings)
        for warning in warnings:
            logger.warning("%s", warning)
        return imported

    def import_sources(self, sources: tuple[GedcomSource, ...]) -> int:
        """Import parsed source records and return the number processed."""
        with self._connection:
            return self._import_sources(sources)

    def _import_persons(self, persons: tuple[GedcomPerson, ...]) -> int:
        now = datetime.now()
        for record in persons:
            existing = self._persons.get_by_xref(record.gedcom_xref)
            if existing is None:
                self._persons.create(
                    Person(
                        id=None,
                        gedcom_xref=record.gedcom_xref,
                        name=record.name,
                        sex=record.sex,
                        is_existing_record=True,
                        created_at=now,
                        modified_at=now,
                    )
                )
                continue

            updated = Person(
                id=existing.id,
                gedcom_xref=record.gedcom_xref,
                name=record.name,
                sex=record.sex,
                is_existing_record=True,
                created_at=existing.created_at,
                modified_at=now,
                needs_export=existing.needs_export,
                source_snapshot=existing.source_snapshot,
            )
            if self._persons.update(updated) is None:
                raise sqlite3.DatabaseError(
                    f"Person {record.gedcom_xref} could not be updated."
                )
        return len(persons)

    def _import_families(
        self,
        families: tuple[GedcomFamily, ...],
        warnings: list[str],
    ) -> int:
        now = datetime.now()
        for record in families:
            husband = self._persons.get_by_xref(record.husb_xref)
            wife = self._persons.get_by_xref(record.wife_xref)
            if record.husb_xref is not None and husband is None:
                warnings.append(
                    f"Family {record.gedcom_xref}: unknown HUSB XREF "
                    f"{record.husb_xref}; link left empty."
                )
            if record.wife_xref is not None and wife is None:
                warnings.append(
                    f"Family {record.gedcom_xref}: unknown WIFE XREF "
                    f"{record.wife_xref}; link left empty."
                )

            existing = self._families.get_by_xref(record.gedcom_xref)
            if existing is None:
                self._families.create(
                    FamilyLink(
                        id=None,
                        gedcom_xref=record.gedcom_xref,
                        husb_person_id=husband.id if husband else None,
                        wife_person_id=wife.id if wife else None,
                        is_existing_record=True,
                        created_at=now,
                        modified_at=now,
                    )
                )
                continue

            updated = FamilyLink(
                id=existing.id,
                gedcom_xref=record.gedcom_xref,
                husb_person_id=husband.id if husband else None,
                wife_person_id=wife.id if wife else None,
                is_existing_record=True,
                created_at=existing.created_at,
                modified_at=now,
                source_snapshot=existing.source_snapshot,
            )
            if self._families.update(updated) is None:
                raise sqlite3.DatabaseError(
                    f"Family {record.gedcom_xref} could not be updated."
                )
        return len(families)

    def _import_sources(self, sources: tuple[GedcomSource, ...]) -> int:
        now = datetime.now()
        for record in sources:
            existing = self._sources.get_by_xref(record.gedcom_xref)
            if existing is None:
                self._sources.create(
                    Source(
                        id=None,
                        gedcom_xref=record.gedcom_xref,
                        title=record.title,
                        created_at=now,
                        modified_at=now,
                    )
                )
                continue

            updated = Source(
                id=existing.id,
                gedcom_xref=record.gedcom_xref,
                title=record.title,
                created_at=existing.created_at,
                modified_at=now,
            )
            if self._sources.update(updated) is None:
                raise sqlite3.DatabaseError(
                    f"Source {record.gedcom_xref} could not be updated."
                )
        return len(sources)
