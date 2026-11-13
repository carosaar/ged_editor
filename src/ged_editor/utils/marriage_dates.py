"""Local and GEDCOM date conversion used by the marriage entry form."""

import calendar
import re
from datetime import date, timedelta

_LOCAL_DATE_PATTERN = re.compile(r"\d{2}\.\d{2}\.\d{4}\Z")
_GEDCOM_DATE_PATTERN = re.compile(r"(\d{1,2}) ([A-Z]{3}) (\d{4})\Z", re.IGNORECASE)
_GEDCOM_MONTHS = (
    "JAN",
    "FEB",
    "MAR",
    "APR",
    "MAY",
    "JUN",
    "JUL",
    "AUG",
    "SEP",
    "OCT",
    "NOV",
    "DEC",
)


def parse_local_date(value: str) -> date | None:
    """Parse a complete date in the local DD.MM.YYYY format."""
    if not _LOCAL_DATE_PATTERN.fullmatch(value):
        return None
    try:
        day, month, year = (int(part) for part in value.split("."))
        return date(year, month, day)
    except ValueError:
        return None


def to_gedcom_date(value: date) -> str:
    """Format a date using the GEDCOM day-month-year representation."""
    return f"{value.day} {_GEDCOM_MONTHS[value.month - 1]} {value.year:04d}"


def _format_local_date(value: date) -> str:
    return f"{value.day:02d}.{value.month:02d}.{value.year:04d}"


def local_date_for_display(raw_value: str | None, gedcom_value: str | None) -> str:
    """Return a local date, converting a complete imported GEDCOM date if needed."""
    raw = raw_value or ""
    if parse_local_date(raw) is not None or not raw:
        return raw
    gedcom = gedcom_value or raw
    match = _GEDCOM_DATE_PATTERN.fullmatch(gedcom.strip())
    if match is None:
        return raw
    day, month_name, year = match.groups()
    try:
        month = _GEDCOM_MONTHS.index(month_name.upper()) + 1
        value = date(int(year), month, int(day))
    except (ValueError, OverflowError):
        return raw
    return _format_local_date(value)


def step_local_date(
    value: str,
    *,
    days: int = 0,
    months: int = 0,
    years: int = 0,
) -> str | None:
    """Adjust a complete local date, clamping month and year steps to valid days."""
    parsed = parse_local_date(value)
    if parsed is None:
        return None
    if days:
        try:
            parsed += timedelta(days=days)
        except OverflowError:
            return None
    if months or years:
        target_year = parsed.year + years
        target_month = parsed.month + months
        target_year += (target_month - 1) // 12
        target_month = (target_month - 1) % 12 + 1
        try:
            last_day = calendar.monthrange(target_year, target_month)[1]
            parsed = date(target_year, target_month, min(parsed.day, last_day))
        except ValueError:
            return None
    return _format_local_date(parsed)
