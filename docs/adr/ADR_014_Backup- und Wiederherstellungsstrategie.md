# ADR-014: Backup- und Wiederherstellungsstrategie

## Status

Akzeptiert

## Datum

2026-11-11

## Kontext

ged_editor wird für die Erfassung und Pflege genealogischer Datenbestände eingesetzt.

Ein Projekt kann:

- mehrere hundert Urkunden enthalten
- über Wochen oder Monate bearbeitet werden
- zahlreiche Personen- und Familiendatensätze verändern

Der Verlust eines Projektes hätte einen erheblichen Arbeitsaufwand zur Folge.

Da die EDG-Datei das primäre Arbeitsmedium darstellt, muss eine verbindliche Backup- und Wiederherstellungsstrategie festgelegt werden.

## Entscheidung

ged_editor implementiert eine mehrstufige Backupstrategie.

Die Sicherung basiert auf folgenden Grundprinzipien:

1. Die Original-GEDCOM-Datei bleibt unverändert.
2. Die EDG-Datei ist das zentrale Arbeitsobjekt.
3. Backups erfolgen automatisch.
4. Wiederherstellungen müssen ohne Fachwissen möglich sein.
5. Kein Arbeitsstand darf durch Programmfehler unbemerkt verloren gehen.

## Schutzebenen

### Ebene 1: Original-GEDCOM

Die importierte GEDCOM-Datei bleibt unverändert erhalten.

Sie dient als:

- Referenzbestand
- Ausgangsdatenbestand
- Notfallsicherung

Gemäß ADR-011 wird sie niemals überschrieben.

## Ebene 2: Projektdatei

Die EDG-Datei stellt den aktuellen Arbeitsstand dar.

Beispiel:

```text
heiratsregister_sulzbach.edg
```

Alle Änderungen erfolgen ausschließlich innerhalb dieser Datei.

## Ebene 3: Automatische Projektsicherungen

ged_editor erzeugt automatisch Sicherungskopien der EDG-Datei.

Backups erfolgen:

- beim Öffnen eines Projektes
- vor jedem Export
- vor Datenbankmigrationen
- vor Wiederherstellungsoperationen

## Backup-Verzeichnis

Standardstruktur:

```text
Projektname.edg

Projektname_backups/
    backup_2026-11-11_08-15.edg
    backup_2026-11-11_18-42.edg
    backup_2026-11-12_09-03.edg
```

Backups werden niemals innerhalb der eigentlichen Projektdatei gespeichert.

## Automatische Aufbewahrung

Standardwerte:

```text
letzte 20 Sicherungen
```

oder

```text
90 Tage
```

je nachdem, was zuerst erreicht wird.

Die Werte sollen später konfigurierbar sein.

## Manuelle Sicherungen

Der Benutzer kann jederzeit eine Projektsicherung erstellen.

Menüfunktion:

```text
Projekt → Sicherung erstellen
```

Die manuelle Sicherung erhält eine eigene Kennzeichnung.

Beispiel:

```text
backup_manual_vor_export_2026-11-11.edg
```

## Wiederherstellung

Das Programm stellt eine Wiederherstellungsfunktion bereit.

Funktionen:

```text
Verfügbare Sicherungen anzeigen
Sicherungszeitpunkt anzeigen
Projekt wiederherstellen
```

Vor einer Wiederherstellung wird automatisch eine Sicherung des aktuellen Projektes angelegt.

Beispiel:

```text
aktueller Stand
        ↓
Sicherheitsbackup
        ↓
Wiederherstellung
```

Dadurch bleibt auch der zuletzt bearbeitete Zustand erhalten.

## Umgang mit beschädigten Dateien

Beim Öffnen eines Projektes prüft das System:

```text
SQLite-Datei lesbar?
Schema gültig?
Integritätsprüfung erfolgreich?
```

Wird ein Fehler erkannt:

```text
Projekt nicht öffnen
```

sondern:

```text
Wiederherstellung anbieten
```

Mögliche Optionen:

- letzte Sicherung öffnen
- Sicherung auswählen
- Projektprüfung starten

## Projektmigrationen

Ändert sich das Datenbankschema zwischen Programmversionen, muss vor jeder Migration automatisch eine Sicherung erzeugt werden.

Ablauf:

```text
Projekt öffnen
        ↓
Versionsprüfung
        ↓
Automatisches Backup
        ↓
Migration
        ↓
Projekt öffnen
```

Eine Migration darf niemals auf der einzigen vorhandenen Projektdatei ausgeführt werden.

## Exportschutz

Vor jedem GEDCOM-Export wird automatisch eine Projektsicherung erstellt.

Dadurch bleibt der genaue Projektstand des Exportzeitpunktes erhalten.

Dies ermöglicht:

- reproduzierbare Exporte
- spätere Fehleranalysen
- Vergleich unterschiedlicher Exportstände

## Sicherungsinformationen

Jede Sicherung enthält:

```text
Zeitpunkt
Programmversion
Projektversion
Projektname
```

Diese Informationen werden innerhalb der Projektdaten gespeichert.

## Nicht Bestandteil des Backups

Folgende Inhalte werden nicht gesichert:

```text
temporäre Dateien
Cache-Dateien
Suchindizes
Logdateien
```

Solche Daten können jederzeit neu erzeugt werden.

## Benutzeroberfläche

Das Programm stellt einen Backup-Manager bereit.

Mindestfunktionen:

```text
Liste vorhandener Sicherungen
Erstellungsdatum anzeigen
Speichergröße anzeigen
Backup löschen
Backup wiederherstellen
Backup exportieren
```

## Beziehung zu anderen ADRs

### ADR-011

Die Original-GEDCOM-Datei bleibt unverändert.

### ADR-012

Änderungsprotokolle dokumentieren den Projektverlauf.

### ADR-013

Exportberichte dokumentieren einzelne Exportvorgänge.

### ADR-014

Backups sichern den tatsächlichen Projektstand.

Die drei Konzepte ergänzen sich:

```text
Änderungsprotokoll
    = Was wurde geändert?

Exportbericht
    = Was wurde exportiert?

Backup
    = Welcher Zustand kann wiederhergestellt werden?
```

## Architekturprinzip

Für ged_editor gilt:

> Jeder Arbeitsstand muss mit vertretbarem Aufwand wiederherstellbar sein.

Kein Benutzer darf durch Programmfehler, Fehlbedienung oder Systemausfall seine genealogische Erfassungsarbeit verlieren.

## Konsequenzen

### Vorteile

- hohe Datensicherheit
- einfache Wiederherstellung
- sichere Migrationen
- sichere Exporte
- reproduzierbare Projektstände

### Nachteile

- zusätzlicher Speicherbedarf
- zusätzlicher Implementierungsaufwand

Diese Nachteile werden zugunsten der Datensicherheit akzeptiert.

## Verwandte ADRs

- ADR-002 Verwendung einer EDG-Projektdatei
- ADR-003 SQLite als internes Speicherformat
- ADR-011 GEDCOM-Dateien werden niemals direkt bearbeitet
- ADR-012 Änderungsprotokoll und Revisionssicherheit
- ADR-013 Export- und Prüfberichte