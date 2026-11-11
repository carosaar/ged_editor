# ADR-004: Begrenzung des fachlichen Scopes auf Ehepartner

## Status

Akzeptiert

## Datum

2026-11-11

## Kontext

Heiratsurkunden enthalten typischerweise Informationen über:

- Braut
- Bräutigam
- Eltern
- Herkunftsorte
- Randvermerke

Es musste entschieden werden, ob Eltern automatisch als genealogische Objekte erzeugt werden.

## Entscheidung

Es werden ausschließlich die Ehepartner genealogisch verarbeitet.

Eltern erhalten keine eigenen INDI- oder FAM-Datensätze.

## Begründung

- deutliche Reduktion der Komplexität
- Konzentration auf den eigentlichen Zweck des Systems
- schnellere Erfassung
- geringeres Fehlerrisiko

## Konsequenzen

Es werden erzeugt:

- FAM
- HUSB
- WIFE

Es werden nicht erzeugt:

- Vater-INDI
- Mutter-INDI
- Eltern-FAM
- FAMC-Verknüpfungen

Elterninformationen werden ausschließlich als Notizinformationen gespeichert.