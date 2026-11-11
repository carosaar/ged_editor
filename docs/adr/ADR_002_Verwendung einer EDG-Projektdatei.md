# ADR-002: Verwendung einer EDG-Projektdatei

## Status

Akzeptiert

## Datum

2026-11-11

## Kontext

Programmdateien, Arbeitsdaten und GEDCOM-Bestände sollen voneinander getrennt werden.

Die Erfassung mehrerer hundert Urkunden erstreckt sich typischerweise über einen längeren Zeitraum.

## Entscheidung

Das Projekt verwendet eine eigenständige Projektdatei mit der Endung:

.edg

(edit-ged)

Die Projektdatei enthält alle Arbeitsdaten einer Erfassung.

## Begründung

- Trennung von Programm und Daten
- Datensicherheit
- Weitergabe von Zwischenergebnissen
- Archivierung von Projektständen
- spätere Erweiterung auf andere Urkundentypen möglich

## Konsequenzen

- GEDCOM-Dateien werden importiert.
- GEDCOM-Dateien werden exportiert.
- Die eigentliche Bearbeitung erfolgt innerhalb der Projektdatei.
