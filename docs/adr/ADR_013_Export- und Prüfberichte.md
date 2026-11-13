# ADR-013: Export- und Prüfberichte

## Status

Akzeptiert

## Datum

2026-11-11

## Kontext

ged_editor verarbeitet genealogische Informationen nicht direkt in einer GEDCOM-Datei, sondern innerhalb eines EDG-Projektes.

Vor dem Export müssen Änderungen überprüft werden können. Nach dem Export muss nachvollziehbar bleiben:

- welche Urkunden erfasst wurden
- welche Datensätze erzeugt wurden
- welche Datensätze verändert wurden
- welche GEDCOM-Datei erzeugt wurde
- welche Quelle verwendet wurde
- welche Warnungen oder Auffälligkeiten festgestellt wurden

Das Änderungsprotokoll gemäß ADR-012 dient der vollständigen Historisierung innerhalb des Projektes.

Für die fachliche Kontrolle und Archivierung werden zusätzlich eigenständige Berichte benötigt.

## Entscheidung

ged_editor erzeugt eigenständige Prüf- und Exportberichte.

Berichte sind vom Änderungsprotokoll getrennt.

Berichte stellen den Zustand eines Projektes zu einem bestimmten Zeitpunkt zusammenfassend dar.

Sie dienen:

- der Qualitätskontrolle
- der Dokumentation
- der Archivierung
- dem Nachweis der durchgeführten Arbeiten

## Berichtsarten

### Prüfbericht

Wird auf Anforderung erzeugt.

Der Bericht bewertet die fachliche Qualität des aktuellen Projektstandes.

### Exportbericht

Wird bei jedem erfolgreichen Export automatisch erzeugt.

Er dokumentiert die Inhalte und Ergebnisse des Exports.

## Format

Version 1.0 verwendet standardmäßig:

```text
Markdown (*.md)
```

Begründung:

- menschenlesbar
- langfristig archivierungsfähig
- einfach zu erzeugen
- einfach weiterzugeben
- problemlos in PDF konvertierbar

Spätere Ausbaustufen können zusätzlich unterstützen:

```text
PDF
HTML
```

## Prüfbericht

### Zweck

Unterstützung der fachlichen Endkontrolle vor einem Export.

### Mindestinhalt

#### Projektinformationen

```text
Projektname
Erstellungsdatum
Bearbeitungsstand
Projektversion
```

#### Urkundenstatistik

```text
Anzahl Urkunden gesamt
Anzahl Urkunden neu
Anzahl Urkunden in Bearbeitung
Anzahl Urkunden fertig
```

#### Personenstatistik

```text
Neue Personen
Geänderte Personen
Personenzuordnungen
Offene Personenzuordnungen
```

#### Familienstatistik

```text
Neue Familien
Geänderte Familien
```

#### Auffälligkeiten

```text
fehlende Pflichtfelder
offene Zuordnungen
Urkunden in Bearbeitung
Warnungen
```

### Ziel

Der Benutzer soll erkennen können, ob das Projekt exportbereit ist.

## Exportbericht

### Zweck

Dokumentation eines konkret durchgeführten Exports.

Der Bericht ist Bestandteil der Exportergebnisse.

### Mindestinhalt

#### Allgemeine Informationen

```text
Projektname
Projektversion
Exportdatum
Programmversion
```

#### Quelldateien

```text
Ursprüngliche GEDCOM-Datei
Erzeugte GEDCOM-Datei
```

#### Quellenzuordnung

```text
verwendeter SOUR-Datensatz
```

#### Exportstatistik

```text
Anzahl exportierter Urkunden
Anzahl neuer INDI
Anzahl geänderter INDI
Anzahl neuer FAM
Anzahl geänderter FAM
```

#### Verarbeitete Urkunden

Auflistung aller exportierten Urkunden:

```text
1878-0015
1878-0016
1878-0017
...
```

oder alternativ

```text
15/1878
16/1878
17/1878
...
```

Die konkrete Darstellung kann konfigurierbar sein.

### Auffälligkeiten

Dokumentation von:

```text
Warnungen
Übersprungene Datensätze
Nicht exportierte Datensätze
```

## Dateibenennung

Prüfberichte:

```text
projekt_pruefbericht.md
```

Exportberichte:

```text
projekt_export_YYYY-MM-DD_HH-MM.md
```

Beispiel:

```text
sulzbach_export_2026-11-11_14-35.md
```

## Aufbewahrung

Berichte werden außerhalb der EDG-Datei gespeichert.

Sie können unabhängig vom Projekt:

- archiviert
- versendet
- ausgedruckt
- versioniert

werden.

## Benutzeroberfläche

Das Programm stellt Funktionen bereit für:

### Prüfberichte

```text
Prüfbericht erstellen
Prüfbericht anzeigen
Prüfbericht speichern
```

### Exportberichte

```text
Exportbericht anzeigen
Exportordner öffnen
Exportbericht erneut erzeugen
```

## Beziehung zum Änderungsprotokoll

### Änderungsprotokoll

ADR-012

Zweck:

```text
vollständige Historie
```

Beispiel:

```text
Wer hat wann was geändert?
```

### Prüf- und Exportberichte

ADR-013

Zweck:

```text
fachliche Zusammenfassung
```

Beispiel:

```text
Was enthält dieses Projekt aktuell?
Was wurde exportiert?
```

Beide Funktionen ergänzen sich.

## Architekturprinzip

Für ged_editor gilt:

> Jeder Export muss reproduzierbar und später nachvollziehbar sein.

Zu jeder erzeugten GEDCOM-Datei gehört ein eigener Exportbericht.

## Konsequenzen

### Vorteile

- transparente Projektkontrolle
- nachvollziehbare Exporte
- einfache Archivierung
- bessere Qualitätssicherung
- bessere Zusammenarbeit mit Genealogen

### Nachteile

- zusätzlicher Implementierungsaufwand
- zusätzliche Dateien im Exportverzeichnis

Diese Nachteile werden zugunsten der Nachvollziehbarkeit akzeptiert.

## Verwandte ADRs

- ADR-001 Urkunde ist führendes Fachobjekt
- ADR-002 Verwendung einer EDG-Projektdatei
- ADR-006 Quellenzuordnung erfolgt beim Export
- ADR-011 GEDCOM-Dateien werden niemals direkt bearbeitet
- ADR-012 Änderungsprotokoll und Revisionssicherheit