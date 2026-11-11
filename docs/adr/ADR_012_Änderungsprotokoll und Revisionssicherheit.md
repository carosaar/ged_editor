# ADR-012: Änderungsprotokoll und Revisionssicherheit

## Status

Akzeptiert

## Datum

2026-11-11

## Kontext

ged_editor dient der systematischen Erfassung und Überarbeitung genealogischer Daten auf Basis historischer Urkunden.

Während eines Projektes werden:

- neue INDI-Datensätze angelegt
- bestehende INDI-Datensätze verändert
- neue FAM-Datensätze angelegt
- bestehende FAM-Datensätze ergänzt oder geändert
- Urkundendaten erfasst und korrigiert
- Personenzuordnungen manuell entschieden

Diese Änderungen können sich über viele Arbeitssitzungen erstrecken.

Da genealogische Daten dauerhaft genutzt werden und Änderungen später nachvollziehbar bleiben müssen, ist ein Änderungsprotokoll erforderlich.

## Entscheidung

Jede fachlich relevante Änderung wird innerhalb der EDG-Projektdatei protokolliert.

Zusätzlich wird beim Export einer GEDCOM-Datei ein Exportprotokoll erzeugt.

Das Änderungsprotokoll dient ausschließlich der Nachvollziehbarkeit und Qualitätssicherung.

Es ersetzt kein Versionskontrollsystem.

## Ziele

Das Änderungsprotokoll soll folgende Fragen beantworten können:

- Welche Urkunde wurde bearbeitet?
- Wann wurde sie bearbeitet?
- Welche Personen wurden neu angelegt?
- Welche Familien wurden neu angelegt?
- Welche bestehenden Datensätze wurden verändert?
- Wie wurde eine Personenzuordnung entschieden?
- Welche Änderungen werden beim Export wirksam?

## Grundsatz

Für alle fachlich relevanten Objekte gilt:

> Keine wesentliche Änderung ohne nachvollziehbaren Protokolleintrag.

## Protokollpflichtige Vorgänge

### Urkunden

- Urkunde angelegt
- Urkunde geändert
- Urkunde als fertig markiert
- Urkunde erneut geöffnet
- Urkunde gelöscht

### Personen

- INDI neu angelegt
- bestehende INDI zugeordnet
- Zuordnung geändert
- Stammdaten geändert

### Familien

- FAM neu angelegt
- bestehende FAM zugeordnet
- Familiendaten geändert

### Quellenangaben

- SOUR-Zuordnung geändert
- Exportquelle festgelegt

### Projektebene

- Projekt angelegt
- GEDCOM importiert
- GEDCOM exportiert
- Datenprüfung ausgeführt

## Protokollinhalt

Jeder Protokolleintrag enthält mindestens:

```text
Zeitpunkt
Vorgang
Objekttyp
Objektkennung
Beschreibung
```

Beispiel:

```text
2026-11-11 15:32:12

Objekttyp:
INDI

Objekt:
@I248@

Vorgang:
Zuordnung

Beschreibung:
Urkunde 15/1887 wurde mit bestehender Person
Johann Müller (@I248@) verknüpft.
```

## Protokollierungsumfang

Es werden keine technischen Details protokolliert:

Beispiele:

```text
Fenster geöffnet
Liste sortiert
Filter geändert
Tab gewechselt
```

Derartige Vorgänge besitzen keinen genealogischen Mehrwert.

Protokolliert werden ausschließlich fachlich relevante Ereignisse.

## Exportprotokoll

Jeder GEDCOM-Export erzeugt zusätzlich ein separates Exportprotokoll.

Beispiel:

```text
projekt_2026-11-11_export.log
```

Inhalt:

```text
Projektname
Exportzeitpunkt
Anzahl neuer INDI
Anzahl geänderter INDI
Anzahl neuer FAM
Anzahl geänderter FAM
Verwendeter SOUR-Datensatz
Ausgabedatei
```

## Integration in die Benutzeroberfläche

Das Programm stellt einen Protokollviewer bereit.

Der Benutzer kann:

- Protokolle anzeigen
- filtern
- durchsuchen
- exportieren

Mögliche Filter:

```text
Nur Urkunden
Nur Personen
Nur Familien
Nur Exporte
Nur Fehler
```

## Beziehung zu Undo/Redo

Das Änderungsprotokoll ersetzt keine Undo-Funktion.

Beide Funktionen verfolgen unterschiedliche Ziele:

### Undo

```text
Arbeitskorrektur
```

Beispiel:

```text
Eingabe rückgängig machen
```

### Änderungsprotokoll

```text
Nachvollziehbarkeit
```

Beispiel:

```text
Änderung dokumentieren
```

Eine spätere Undo-/Redo-Funktion darf das Änderungsprotokoll nicht verändern oder löschen.

## Speicherung

Das Änderungsprotokoll wird innerhalb der EDG-Datei gespeichert.

Dadurch bleibt die Änderungshistorie Bestandteil des Projektes.

Beim Kopieren oder Archivieren eines Projektes wird die Historie automatisch mitgeführt.

## Datenschutz

Das Protokoll enthält ausschließlich Projektdaten.

Benutzerkonten, Netzwerkkennungen oder Betriebssysteminformationen werden nicht gespeichert.

Da ged_editor als Einzelplatzanwendung vorgesehen ist, ist keine Benutzerverwaltung erforderlich.

## Konsequenzen

### Vorteile

- vollständige Nachvollziehbarkeit
- bessere Qualitätskontrolle
- vereinfachte Fehlersuche
- transparente Arbeitsdokumentation
- nachvollziehbare Exportvorgänge

### Nachteile

- zusätzlicher Speicherbedarf
- zusätzlicher Implementierungsaufwand

Diese Nachteile werden zugunsten der Revisionssicherheit akzeptiert.

## Architekturprinzip

Für ged_editor gilt dauerhaft:

> Jede genealogisch relevante Änderung muss auch Monate oder Jahre später aus dem Projekt heraus nachvollzogen werden können.

## Verwandte ADRs

- ADR-001 Urkunde ist führendes Fachobjekt
- ADR-002 Verwendung einer EDG-Projektdatei
- ADR-003 SQLite als internes Speicherformat
- ADR-006 Quellenzuordnung erfolgt beim Export
- ADR-011 GEDCOM-Dateien werden niemals direkt bearbeitet