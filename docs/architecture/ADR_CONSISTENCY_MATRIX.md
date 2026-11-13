# ADR-Konsistenzmatrix (Finale Version)

Stand: ADR-001 bis ADR-016
 Bewertung: Freigegeben für Entwicklungsstart v0.1.0

> Historisches Dokument. Die aktuelle verbindliche Architektur ergibt sich aus
> ADR-001 bis ADR-021 und `DATA_MODEL.md`; bei Abweichungen sind insbesondere
> ADR-017 bis ADR-021 und das Datenmodell maßgeblich.

## Übersicht der Verantwortlichkeiten
| ADR | Thema | Verantwortungsbereich |
| --- | --- | --- |
| ADR-001 | Urkunde als führendes Objekt | Fachmodell |
| ADR-002 | EDG-Projektdatei | Arbeitsmodell |
| ADR-003 | SQLite als internes Format | Persistenz |
| ADR-004 | Scope auf Ehepartner | Fachlicher Umfang |
| ADR-005 | Strukturierte Notizen | Datenerfassung |
| ADR-006 | Quellenzuordnung | GEDCOM-Export |
| ADR-007 | Fuzzy-Personensuche | Identifikation |
| ADR-008 | Datumsverarbeitung | Dateneingabe |
| ADR-009 | Einzelplatzanwendung | Betriebsmodell |
| ADR-010 | Zielarchitektur | Technische Architektur |
| ADR-011 | Keine direkte GEDCOM-Bearbeitung | Datensicherheit |
| ADR-012 | Änderungsprotokoll | Nachvollziehbarkeit |
| ADR-013 | Prüf- und Exportberichte | Qualitätssicherung |
| ADR-014 | Backupstrategie | Wiederherstellung |
| ADR-015 | Urkundenstatusmodell | Workflow |
| ADR-016 | REFN / SOUR.PAGE / SOUR.NOTE | Exportsemantik |

## Vertikale Konsistenzprüfung
### Fachmodell
```
ADR-001
    ↓
ADR-004
    ↓
ADR-005
    ↓
ADR-015
    ↓
ADR-016
```

Prüfung:

✅ Urkunde ist führend
✅ Ehepartner sind fachlicher Kern
✅ Eltern werden nur dokumentiert
✅ Statusmodell bezieht sich auf Urkunden
✅ Exportstruktur basiert auf Urkunden
Ergebnis: Konsistent

### Datenhaltung
```
ADR-002
    ↓
ADR-003
    ↓
ADR-010
    ↓
ADR-011
    ↓
ADR-014
```

Prüfung:

✅ EDG-Datei als Arbeitsformat
✅ SQLite als Speichermedium
✅ Python/PySide6 Architektur
✅ GEDCOM nur Import/Export
✅ Backup basiert auf EDG-Projekten
Ergebnis: Konsistent

### Datenfluss
```
GEDCOM
  ↓
Import
  ↓
EDG
  ↓
Bearbeitung
  ↓
Export
  ↓
GEDCOM
```

Beteiligte ADRs:

* ADR-002
* ADR-003
* ADR-010
* ADR-011
* ADR-013


Prüfung:

✅ kein Direktzugriff auf GEDCOM
✅ eindeutiger Lebenszyklus
✅ reproduzierbare Exporte
✅ Exportberichte vorhanden
Ergebnis: Konsistent

### Identifikation
```
ADR-007
    ↓
ADR-004
```

Prüfung:

✅ Kandidatensuche über Fuzzy Matching
✅ manuelle Zuordnung
✅ keine automatische Personenanlage
✅ keine automatische Elternmodellierung
Ergebnis: Konsistent

### Quellenmodell
```
ADR-006
    ↓
ADR-016
```

Prüfung:

✅ SOUR-Zeiger im Projekt konfigurierbar
✅ Export überprüft SOUR-Zuweisung
✅ REFN konfigurierbar
✅ SOUR.PAGE konfigurierbar
✅ SOUR.NOTE deterministisch erzeugbar
Ergebnis: Konsistent

### Qualitätssicherung
```
ADR-012
    ↓
ADR-013
    ↓
ADR-014
```

Prüfung:

| Funktion | Zweck |
| --- | --- |
| Änderungsprotokoll | Historie |
| Prüfbericht | Projektbewertung |
| Exportbericht | Exportdokumentation |
| Backup | Wiederherstellung |

Keine Überschneidungen.
Keine Doppelverantwortungen.
Ergebnis: Konsistent

## Lebenszyklus einer Urkunde

Die ADRs definieren nun vollständig:
```
Urkunde anlegen
       ↓
Status = In Bearbeitung
       ↓
Status = Fertig
       ↓
GEDCOM-Export
       ↓
Exportstatus = Exportiert
```

Unterstützende ADRs:

* 001
* 005
* 012
* 013
* 015
* 016

Ergebnis: Vollständig konsistent

## Lebenszyklus eines Projekts
```
GEDCOM importieren
        ↓
EDG anlegen
        ↓
Bearbeiten
        ↓
Backups
        ↓
Prüfbericht
        ↓
Export
        ↓
Exportbericht
        ↓
Archivierung
```


Unterstützende ADRs:

* 002
* 003
* 010
* 011
* 012
* 013
* 014

Ergebnis: Vollständig konsistent

## Identifizierte Architekturprinzipien

Aus allen ADRs ergeben sich folgende Leitprinzipien:

### P1 - Urkundenorientierung

Die Urkunde ist das fachliche Zentrum.

Festgelegt durch:

* ADR-001
* ADR-015

### P2 - Projektzentrierte Bearbeitung

Die EDG-Datei ist das Arbeitsobjekt.

Festgelegt durch:

* ADR-002
* ADR-011

### P3 - GEDCOM als Austauschformat

GEDCOM wird nicht bearbeitet.

Festgelegt durch:

* ADR-011

### P4 - Reproduzierbarkeit

Jeder Export muss nachvollziehbar sein.

Festgelegt durch:

* ADR-012
* ADR-013
* ADR-014
* ADR-016

### P5 - Kontrollierte Personenzuordnung

Zuordnungen erfolgen manuell.

Festgelegt durch:

* ADR-007

### P6 - Erweiterbarkeit

Weitere Urkundentypen bleiben möglich.

Festgelegt durch:

* ADR-001
* ADR-002
* ADR-010

## Früher offene Architekturthemen

Die nachfolgenden, bei Erstellung dieses Dokuments noch offenen Themen wurden
teilweise durch ADR-017 bis ADR-021 entschieden. Diese Matrix ist kein
Verzeichnis aktueller offener Architekturentscheidungen.

## Abschlussbewertung

| Kriterium | Bewertung |
| --- | --- |
| Fachliche Konsistenz | ✅ |
| Technische Konsistenz | ✅ |
| Datenfluss | ✅ |
| GEDCOM-Strategie | ✅ |
| Backup-Strategie | ✅ |
| Revisionssicherheit | ✅ |
| Erweiterbarkeit | ✅ |
| Widerspruchsfreiheit | ✅ |

## Gesamturteil

Die ADR-Sammlung ADR-001 bis ADR-016 ist in sich konsistent, widerspruchsfrei und ausreichend vollständig, um die Implementierung von ged_editor v0.1.0 zu beginnen.

Architekturreifegrad: 95 %


Die verbleibenden offenen Themen betreffen Erweiterungen und Komfortfunktionen, nicht mehr die Grundarchitektur des Systems. Damit ist ein stabiler Fundamentstand erreicht, auf dessen Basis nun Datenbankschema, UI-Konzept und erste Implementierung aufgebaut werden können.