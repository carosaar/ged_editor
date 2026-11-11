# ADR-006: Quellenzuordnung erfolgt beim Export

## Status

Akzeptiert

## Datum

2026-11-11

## Kontext

Alle während einer Erfassung erzeugten Datensätze verwenden denselben SOUR-Datensatz.

Es musste entschieden werden, wann die Auswahl erfolgt.

## Entscheidung

Die Auswahl eines SOUR-Datensatzes erfolgt spätestens beim Export.
Die SOUR-Auswahl wird im Projekt gespeichert, muss aber erst vor dem ersten Export festgelegt sein.

## Begründung

- während der Erfassung nicht erforderlich
- höhere Flexibilität
- einfacherer Workflow

## Konsequenzen

Der Export prüft:

Ist ein SOUR-Datensatz ausgewählt?

Wenn nein:

- Export wird verweigert

Wenn ja:

- Export wird durchgeführt