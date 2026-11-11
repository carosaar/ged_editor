# ADR-003: SQLite als internes Speicherformat

## Status

Akzeptiert

## Datum

2026-11-11

## Kontext

Für die Projektdatei musste ein geeignetes internes Speicherformat gewählt werden.

Zur Diskussion standen:

- GEDCOM
- JSON
- CSV
- SQLite

## Entscheidung

Eine EDG-Datei ist eine SQLite-Datei.

## Begründung

- schnelle Suchfunktionen
- Fuzzy-Suche auf Personen
- Filter und Auswertungen
- Transaktionssicherheit
- Integration in Python
- geringer Wartungsaufwand

## Konsequenzen

- GEDCOM ist ausschließlich Import- und Exportformat.
- Die Geschäftslogik arbeitet auf Datenbankobjekten.
- Die EDG-Datei enthält eine SQLite-Datenbank.