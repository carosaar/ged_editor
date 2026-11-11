# ADR-011: GEDCOM-Dateien werden niemals direkt bearbeitet

## Status

Akzeptiert

## Datum

2026-11-11

## Kontext

GEDCOM-Dateien sind das führende Austauschformat zwischen genealogischen Programmen.

Für ged_editor musste entschieden werden, ob:

- Änderungen unmittelbar an einer GEDCOM-Datei erfolgen oder
- GEDCOM-Dateien ausschließlich als Import- und Exportmedium verwendet werden.

Eine direkte Bearbeitung der Ursprungsdatei wirkt zunächst einfacher, birgt jedoch erhebliche Risiken hinsichtlich Datensicherheit, Nachvollziehbarkeit und Erweiterbarkeit.

## Entscheidung

GEDCOM-Dateien werden von ged_editor niemals direkt bearbeitet.

Die Bearbeitung erfolgt ausschließlich innerhalb einer EDG-Projektdatei.

Der Workflow lautet:

```text
GEDCOM importieren
        │
        ▼
EDG-Projekt erzeugen
        │
        ▼
Bearbeitung
        │
        ▼
Export
        │
        ▼
Neue GEDCOM-Datei erzeugen
```

Die ursprüngliche GEDCOM-Datei bleibt während des gesamten Arbeitsprozesses unverändert.

## Begründung

### Datensicherheit

Die Originaldatei bleibt jederzeit erhalten.

Fehler während der Erfassung oder des Exports können die Ursprungsdatei nicht beschädigen.

### Nachvollziehbarkeit

Alle Änderungen existieren innerhalb des Projektes und können jederzeit nachvollzogen werden.

Zwischenstände können archiviert und dokumentiert werden.

### Entkopplung

Programmversionen und Datenbestände werden voneinander getrennt.

Ein Projekt kann unabhängig von der ursprünglich importierten GEDCOM-Datei bearbeitet werden.

### Erweiterbarkeit

Neue Funktionen können entwickelt werden, ohne Risiken für bestehende GEDCOM-Dateien einzugehen.

Das interne Datenmodell kann unabhängig vom GEDCOM-Format erweitert werden.

### Qualitätssicherung

Vor jedem Export können Prüfungen durchgeführt werden.

Beispiele:

- Vollständigkeitsprüfung
- Plausibilitätsprüfung
- Konfliktprüfung
- Pflichtfeldprüfung

Erst nach erfolgreicher Prüfung wird eine neue GEDCOM-Datei erzeugt.

## Konsequenzen

### Import

Beim Import werden relevante Daten aus der GEDCOM-Datei gelesen und in die Projektdatei übernommen.

Der Import ist ein einmaliger Vorgang.

Nach dem Import besteht keine technische Verbindung zur Ursprungsdatei.

### Bearbeitung

Alle Änderungen erfolgen ausschließlich innerhalb der EDG-Datei.

Die Anwendung verändert niemals die Ursprungsdatei.

### Export

Der Export erzeugt stets eine neue GEDCOM-Datei.

Beispiel:

```text
familie.ged
```

↓

```text
familie_export_2026-11-11.ged
```

Die Benennung kann später konfigurierbar gestaltet werden.

### Mehrfache Exporte

Aus demselben Projekt können beliebig viele GEDCOM-Dateien erzeugt werden.

Dies ermöglicht:

- Testexporte
- Zwischenexporte
- verschiedene Exportversionen

ohne Verlust von Projektdaten.

## Backup-Strategie

Die EDG-Projektdatei ist das zentrale Arbeitsobjekt.

Für die Datensicherung genügt grundsätzlich die Sicherung:

```text
Projekt.edg
```

Die Ursprungs-GEDCOM dient zusätzlich als unveränderte Referenz.

## Verbotene Architekturansätze

Nicht zulässig sind:

### Direkte GEDCOM-Bearbeitung

```text
GEDCOM öffnen
↓
Datensatz ändern
↓
GEDCOM überschreiben
```

### Automatisches Überschreiben der Quelldatei

```text
Export → ursprüngliche Datei ersetzen
```

### Gemischte Betriebsarten

```text
teilweise EDG
teilweise direkte GEDCOM-Manipulation
```

Diese Ansätze würden die Trennung zwischen Arbeitsdaten und Austauschformat verletzen.

## Architekturprinzip

Für ged_editor gilt dauerhaft:

> Die GEDCOM-Datei ist eine Quelle und ein Ziel.
> Die EDG-Datei ist der Arbeitsbereich.

## Verwandte ADRs

- ADR-001 Urkunde ist führendes Fachobjekt
- ADR-002 Verwendung einer EDG-Projektdatei
- ADR-003 SQLite als internes Speicherformat
- ADR-006 Quellenzuordnung erfolgt beim Export
- ADR-010 Zielarchitektur und Technologiestack