# Changelog


## 0.4.2

# v0.4.2 – Architekturkonsolidierung und ADR\-Konformität

## Datenmodell

- Das Datenmodell wurde vollständig auf den aktuellen Architekturstand gemäß ADR\-015 bis ADR\-021 vereinheitlicht.
- MarriageRecord ist nun die alleinige fachliche Repräsentation einer Heiratsurkunde und entspricht direkt dem GEDCOM\-FAM\-Datensatz.
- Die frühere FamilyLink\-Architektur wurde vollständig entfernt.
- Personendatensätze wurden um strukturierte Geburts\- und Sterbeinformationen erweitert.
- Konfliktrelevante Importzustände können über source\_snapshot dauerhaft gespeichert werden.

## Workflow und Statusmodell

- Das Workflowmodell wurde auf die fachlich gültigen Zustände reduziert: 
    - In Bearbeitung
    - Fertig
- Das Exportmodell wurde konsequent vom Workflow getrennt: 
    - Nicht exportiert
    - Exportiert
    - Konflikt
- Datenbankmodell, Constraints und Persistenzlogik wurden entsprechend angepasst.

## Projektkonfiguration

- Die Projektparameter wurden auf den Stand von ADR\-020 angehoben.
- Unterstützung für: 
    - MARR.TYPE
    - Quellenzuordnung (SOUR)
    - XREF\-Präfixe
    - REFN\-Präfixe und Suffixe
    - PAGE\-Präfixe und Suffixe
    - Standard\-Heiratsorte

## Migration und Kompatibilität

- Bestehende Projektdateien älterer Schema\-Versionen werden weiterhin unterstützt.
- Die Migrationslogik wurde an das neue Datenmodell angepasst.
- Historische Tabellen\- und Statusstrukturen verbleiben ausschließlich innerhalb der Kompatibilitätsschicht.

## Qualitätssicherung

- Einführung automatisierter Architekturtests zur Absicherung der ADR\-Vorgaben.
- Prüfung der Statusmodelle, Datenstrukturen und Projektparameter.
- Prüfung verbotener Legacy\-Komponenten.
- Prüfung der Datenbankmigrationen.
- Prüfung der Modellkonformität gegenüber DATA\_MODEL.md.

## Dokumentation

- Architektur\- und Datenmodelldokumentation synchronisiert.
- Historische Konzepte und überholte Statusmodelle gekennzeichnet.
- ADR\-021 in die Projektdokumentation integriert.

## Technische Auswirkungen

Dieses Release enthält keine neuen Benutzerfunktionen. Der Schwerpunkt liegt auf der Bereinigung historischer Architekturentscheidungen und der Schaffung einer stabilen Grundlage für die weitere Entwicklung der Import\-, Konflikt\- und Exportfunktionen.


## 0.4.1

### Korrigiert

- Projektmenü überarbeitet: Öffnen und Speichern funktionieren nun korrekt.

### Hinzugefügt

- Exportstatus für Urkunden gemäß ADR-017 eingeführt.
- Vorbereitung der späteren Konflikterkennung zwischen Projekt- und GEDCOM-Stand.

### Geändert

- Datenbankschema auf Version 4 erweitert.
- Migration bestehender Projekte implementiert.
- GEDCOM-Import an neue Status- und Snapshotfelder angepasst.

### Architektur

- ADR-001, ADR-015 und ADR-017 umgesetzt.
- Grundlage für selektiven Export und Konfliktbehandlung geschaffen.

---
## 0.4.0

- GEDCOM-Import für Personen, Familien und Quellen ergänzt, ohne die Quelldatei zu verändern.
- Das Schema um die Tabelle `source` erweitert; bestehende Tabellen bleiben unverändert.
- Importstatistik und Hinweise zu nicht auflösbaren Familienverknüpfungen ergänzt.

---
## 0.3.0

> Historischer Releaseeintrag. Das damalige Statusmodell wurde durch ADR-015
> abgelöst; die folgenden Statusbegriffe beschreiben nicht den aktuellen
> Workflow.

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

---
## 0.2.0

- EDG-Projektdateien mit SQLite-Projektschema erstellen und öffnen.
- Projektmetadaten über Repository und Service speichern.
- Neues Projekt über das Dateimenü anlegen.

---
## 0.1.0

- Initiales Projektgerüst für `ged_editor`.
