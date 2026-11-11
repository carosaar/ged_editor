"""Line-oriented parser for the GEDCOM fields supported by phase 4."""

import re
from dataclasses import dataclass
from pathlib import Path
from collections.abc import Sequence

_LINE_PATTERN = re.compile(
    r"^(?P<level>\d+)\s+(?:(?P<xref>@[^@\s]+@)\s+)?"
    r"(?P<tag>[^\s]+)(?:\s+(?P<value>.*))?$"
)


class GedcomParseError(ValueError):
    """Raised when a GEDCOM file contains ambiguous supported records."""


@dataclass(frozen=True, slots=True)
class GedcomPerson:
    """Imported INDI fields supported by phase 4."""

    gedcom_xref: str | None
    name: str
    sex: str | None


@dataclass(frozen=True, slots=True)
class GedcomFamily:
    """Imported FAM fields supported by phase 4."""

    gedcom_xref: str | None
    husb_xref: str | None
    wife_xref: str | None


@dataclass(frozen=True, slots=True)
class GedcomSource:
    """Imported SOUR fields supported by phase 4."""

    gedcom_xref: str | None
    title: str | None


@dataclass(frozen=True, slots=True)
class GedcomData:
    """Supported GEDCOM records parsed from one input file."""

    persons: tuple[GedcomPerson, ...]
    families: tuple[GedcomFamily, ...]
    sources: tuple[GedcomSource, ...]


def parse_file(file_path: str | Path) -> GedcomData:
    """Parse supported records from a UTF-8 or Windows-1252 GEDCOM file."""
    path = Path(file_path)
    content = path.read_bytes()
    try:
        text = content.decode("utf-8-sig")
    except UnicodeDecodeError:
        text = content.decode("cp1252")
    return parse_text(text)


def parse_text(text: str) -> GedcomData:
    """Parse INDI, FAM, and SOUR records while ignoring unrelated tags."""
    persons: list[GedcomPerson] = []
    families: list[GedcomFamily] = []
    sources: list[GedcomSource] = []

    current_type: str | None = None
    current_xref: str | None = None
    name = ""
    sex: str | None = None
    husband_xref: str | None = None
    wife_xref: str | None = None
    title: str | None = None

    def finish_record() -> None:
        if current_type == "INDI":
            persons.append(GedcomPerson(current_xref, name, sex))
        elif current_type == "FAM":
            families.append(
                GedcomFamily(current_xref, husband_xref, wife_xref)
            )
        elif current_type == "SOUR":
            sources.append(GedcomSource(current_xref, title))

    for raw_line in text.splitlines():
        line = raw_line.lstrip("\ufeff").strip()
        if not line:
            continue
        match = _LINE_PATTERN.match(line)
        if match is None:
            continue

        level = int(match.group("level"))
        tag = match.group("tag")
        xref = match.group("xref")
        value = (match.group("value") or "").strip()

        if level == 0:
            finish_record()
            current_type = tag if tag in {"INDI", "FAM", "SOUR"} else None
            current_xref = xref
            name = ""
            sex = None
            husband_xref = None
            wife_xref = None
            title = None
            continue

        if level != 1 or current_type is None:
            continue

        if current_type == "INDI":
            if tag == "NAME":
                name = value
            elif tag == "SEX":
                sex = value or None
        elif current_type == "FAM":
            if tag == "HUSB":
                husband_xref = value or None
            elif tag == "WIFE":
                wife_xref = value or None
        elif current_type == "SOUR" and tag == "TITL":
            title = value or None

    finish_record()

    _ensure_unique_xrefs(persons, "INDI")
    _ensure_unique_xrefs(families, "FAM")
    _ensure_unique_xrefs(sources, "SOUR")
    return GedcomData(tuple(persons), tuple(families), tuple(sources))


def _ensure_unique_xrefs(
    records: Sequence[GedcomPerson | GedcomFamily | GedcomSource],
    record_type: str,
) -> None:
    seen: set[str] = set()
    for record in records:
        xref = record.gedcom_xref
        if xref is None:
            raise GedcomParseError(f"{record_type} record is missing its XREF.")
        if xref in seen:
            raise GedcomParseError(
                f"GEDCOM contains duplicate {record_type} XREF {xref}."
            )
        seen.add(xref)
