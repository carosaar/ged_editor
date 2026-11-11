# ADR-009: Einzelplatzanwendung

## Status

Akzeptiert

## Datum

2026-11-11

## Kontext

Das Projekt dient der persönlichen Erfassung genealogischer Urkunden.

Mehrbenutzerbetrieb würde erhebliche zusätzliche Komplexität verursachen.

## Entscheidung

ged_editor wird als Einzelplatzanwendung entwickelt.

## Begründung

- kein tatsächlicher Mehrbenutzerbedarf
- einfachere Architektur
- geringerer Entwicklungsaufwand

## Konsequenzen

- keine Benutzerverwaltung
- keine Rechteverwaltung
- keine Netzwerkfunktionen erforderlich