# ADR-007: Personenzuordnung über Fuzzy-Suche

## Status

Akzeptiert

## Datum

2026-11-11

## Kontext

Bereits vorhandene Personen sollen nach Möglichkeit wiederverwendet werden.

Eine reine Exaktsuche ist bei historischen Daten ungeeignet.

## Entscheidung

Das System verwendet eine Fuzzy-Suche zur Kandidatenermittlung.

Die endgültige Auswahl erfolgt manuell durch den Benutzer.

## Begründung

- unterschiedliche Schreibweisen historischer Namen
- Schreibfehler
- Varianten von Vor- und Familiennamen

## Konsequenzen

- automatische Kandidatenliste
- keine automatische Zuordnung
- Benutzerentscheidung bleibt erforderlich