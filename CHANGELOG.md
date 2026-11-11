# Changelog

## 0.3.0

### Hinzugefügt

- EDG-Projektdatei als zentrales Arbeitsformat auf Basis von SQLite
- Datenbankschema mit Projekt- und Konfigurationstabellen
- Meta-Konfiguration für projektweite Einstellungen
- Domänenmodell für Urkunden, Personen und Familienverknüpfungen
- Urkundenstatusmodell (Neu, In Bearbeitung, Fertig, Geprüft, Exportiert)
- Repository-Schicht für den Datenzugriff
- Service-Schicht für die Fachlogik
- Automatisierte Tests für Datenbank und Domänenobjekte

### Architektur

- Umsetzung der ADRs 002, 003, 011 und 015
- Trennung von Domänenmodell, Persistenz und Service-Schicht
- Vorbereitung der Exportkonfiguration für SOUR, REFN und SOUR.PAGE

### Technische Grundlage

- SQLite als internes Speicherformat etabliert
- CRUD-Grundfunktionen für alle Kernobjekte verfügbar
- Infrastruktur für spätere GEDCOM-Import- und Exportfunktionen vorbereitet

## 0.2.0

- EDG-Projektdateien mit SQLite-Projektschema erstellen und öffnen.
- Projektmetadaten über Repository und Service speichern.
- Neues Projekt über das Dateimenü anlegen.

## 0.1.0

- Initiales Projektgerüst für `ged_editor`.
