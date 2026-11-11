# ADR-008: Datumsverarbeitung

## Status

Akzeptiert

## Datum

2026-11-11

## Kontext

GEDCOM verwendet ein Datumsformat, das von Anwendern nur eingeschränkt gelesen werden kann.

Beispiel:

12 MAY 1898

Der Bearbeiter erwartet das gewohnte Datumsformat.

## Entscheidung

Die Eingabe erfolgt im lokalen Datumsformat.

Beispiel:

12.05.1898

Parallel wird die GEDCOM-Darstellung erzeugt und angezeigt.

## Begründung

- bessere Benutzerfreundlichkeit
- sofortige Plausibilitätskontrolle
- korrekte GEDCOM-Ausgabe

## Konsequenzen

Das System speichert Datumsinformationen strukturiert und erzeugt die GEDCOM-Darstellung beim Export.