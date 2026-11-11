# ADR-010: Zielarchitektur und Technologiestack

## Status

Akzeptiert

## Datum

2026-11-11

## Kontext

Für die Entwicklung von ged_editor muss frühzeitig ein verbindlicher Technologiestack festgelegt werden.

Die Anwendung soll:

- große genealogische Datenbestände verarbeiten können
- auf Windows als Desktop-Anwendung laufen
- langfristig wartbar bleiben
- später um weitere Urkundentypen erweitert werden können
- eine komfortable Benutzeroberfläche bereitstellen
- Such-, Filter- und Prüfmechanismen unterstützen
- GEDCOM-Dateien importieren und exportieren

Zusätzlich sollen Programmlogik, Datenhaltung und Benutzeroberfläche klar voneinander getrennt werden.

## Entscheidung

Die Anwendung wird als klassische Desktop-Anwendung entwickelt.

Folgende Technologien werden verbindlich festgelegt:

### Programmiersprache

Python 3.13 oder neuer

### GUI-Framework

PySide6 (Qt6)

### Interne Datenspeicherung

SQLite

### Projektdateiformat

.edg

Die .edg-Datei enthält eine SQLite-Datenbank mit sämtlichen Projektdaten.

### Testframework

pytest

### Fuzzy-Suche

rapidfuzz

### Entwicklungsumgebung

Visual Studio Code

### Versionsverwaltung

Git

## Begründung

### Python

Python bietet:

- schnelle Entwicklungszyklen
- gute Lesbarkeit
- einfache Wartbarkeit
- umfangreiche Bibliotheksunterstützung
- ausgezeichnete SQLite-Integration
- plattformübergreifende Nutzbarkeit

Genealogische Anwendungen stellen keine hohen Performance-Anforderungen, so dass Python hierfür ausreichend leistungsfähig ist.

### PySide6

Qt stellt ein leistungsfähiges GUI-Framework bereit.

Vorteile:

- native Desktop-Anwendung
- moderne Benutzeroberfläche
- Tabellenansichten
- Suchdialoge
- Splitter-Fenster
- Docking-Fenster
- langfristige Wartbarkeit

Die für ged_editor erforderlichen Datenlisten und Auswahlmasken lassen sich damit effizient umsetzen.

### SQLite

SQLite ermöglicht:

- eine einzelne Projektdatei
- transaktionssichere Speicherung
- hohe Suchgeschwindigkeit
- einfache Sicherung
- keine Installation eines Datenbankservers

### Git

Git ermöglicht:

- nachvollziehbare Entwicklung
- reproduzierbare Versionen
- kontrollierte Releases
- sichere Zusammenarbeit mit KI-Werkzeugen

## Zielarchitektur

Die Anwendung besteht aus vier Schichten:

### Präsentationsschicht

Benutzeroberfläche

Verantwortlich für:

- Fenster
- Dialoge
- Listenansichten
- Dateneingabe
- Benutzerinteraktion

Verzeichnis:

```text
ui/
```

### Anwendungsschicht

Geschäftslogik und Workflow-Steuerung

Verantwortlich für:

- Projekterstellung
- Urkundenbearbeitung
- Validierungen
- Suchvorgänge
- Exportsteuerung

Verzeichnis:

```text
services/
```

### Persistenzschicht

Datenzugriff

Verantwortlich für:

- SQLite-Zugriffe
- Datenbanktransaktionen
- Datenverwaltung

Verzeichnis:

```text
repositories/
database/
```

### Domänenschicht

Fachliche Objekte

Verantwortlich für:

- Urkunden
- Personen
- Familien
- Quellen
- Projektinformationen

Verzeichnis:

```text
models/
```

## Datenfluss

```text
GEDCOM-Datei
      │
      ▼
Importmodul
      │
      ▼
EDG-Projektdatei
(SQLite)
      │
      ▼
Bearbeitung
      │
      ▼
Exportmodul
      │
      ▼
Neue GEDCOM-Datei
```

## Architekturgrundsätze

### Import-Export-Trennung

GEDCOM dient ausschließlich als:

- Importformat
- Exportformat

Während der Bearbeitung wird niemals direkt auf einer GEDCOM-Datei gearbeitet.

### Projektzentrierte Arbeitsweise

Die EDG-Datei ist das zentrale Arbeitsobjekt.

Alle Bearbeitungsschritte erfolgen innerhalb der Projektdatei.

### Erweiterbarkeit

Die Architektur muss spätere Unterstützung weiterer Urkundentypen ermöglichen:

- Geburtsurkunden
- Sterbeurkunden
- Kirchenbucheinträge

ohne grundlegende Änderungen der Kernarchitektur.

### Domänenorientierung

Die fachliche Sicht bestimmt die Architektur.

Technische Datenstrukturen dürfen die Arbeitsweise des Genealogen nicht beeinflussen.

Die führende fachliche Einheit bleibt die Urkunde.

## Konsequenzen

### Positiv

- klare Schichtenarchitektur
- gute Wartbarkeit
- einfache Testbarkeit
- intuitive Erweiterbarkeit
- saubere Trennung von Daten und Programm

### Negativ

- höherer initialer Architekturaufwand
- zusätzliche Repository- und Service-Schichten
- größerer Entwicklungsumfang in der Anfangsphase

Diese Nachteile werden zugunsten der langfristigen Wartbarkeit akzeptiert.

## Verwandte ADRs

- ADR-001 Urkunde ist führendes Fachobjekt
- ADR-002 Verwendung einer EDG-Projektdatei
- ADR-003 SQLite als internes Speicherformat
- ADR-006 Quellenzuordnung erfolgt beim Export
- ADR-009 Einzelplatzanwendung