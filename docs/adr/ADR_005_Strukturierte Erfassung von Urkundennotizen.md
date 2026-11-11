# ADR-005: Strukturierte Erfassung von Urkundennotizen

## Status

Akzeptiert

## Datum

2026-11-11

## Kontext

Heiratsurkunden enthalten zahlreiche Zusatzinformationen.

Eine reine Freitextnotiz erschwert spätere Auswertungen.

## Entscheidung

Notizen werden während der Erfassung strukturiert gespeichert.

Folgende Kategorien werden vorgesehen:

- Randvermerke zum Tod der Eheleute
- Legitimierungsvermerke vorehelicher Kinder
- Sonstige Randvermerke
- Hinweise zu Eltern und Herkunft
- Sonstige Auffälligkeiten

## Begründung

- bessere Übersicht für den Bearbeiter
- einheitliche Erfassungsqualität
- spätere Auswertbarkeit

## Konsequenzen

Beim GEDCOM-Export werden die Bereiche zu einem gemeinsamen NOTE-Inhalt zusammengeführt.