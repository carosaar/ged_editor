# ADR-018: Exportmodell und GEDCOM-Erzeugung

## Status

Akzeptiert

## Datum

2026-11-11

## Kontext

ged_editor bearbeitet keine GEDCOM-Datei direkt.

Gemäß ADR-011 erfolgt die Bearbeitung ausschließlich innerhalb einer EDG-Projektdatei.

Der Export ist die kontrollierte Übernahme der Projektdaten in eine bestehende GEDCOM-Datei.

Hierbei müssen:

- neue Datensätze erzeugt werden
- bestehende Datensätze ergänzt werden
- vorhandene Informationen erhalten bleiben
- Doppelungen vermieden werden

Konflikterkennung und Konfliktbehandlung werden durch ADR-017 geregelt und sind nicht Bestandteil dieser ADR.

---

# Zielsetzung

Der Export überträgt die fachlich freigegebenen Urkunden in eine bestehende GEDCOM-Datei.

Dabei wird:

- die bestehende GEDCOM-Datei gelesen
- selektiv ergänzt oder geändert
- als neue GEDCOM-Datei gespeichert

Die Ursprungsdatei wird niemals überschrieben.

---

# Identifikation der Zieldatei

Vor dem Export wird die gewählte GEDCOM-Datei untersucht.

Ausgewertet werden:

```gedcom
0 HEAD
1 FILE <Dateiname>
1 DATE <Datum>
2 TIME <Zeit>
```

---

## Abweichender Header

Unterscheiden sich diese Werte vom Importbestand, wird:

- eine Warnung angezeigt mit der Möglichkeit zum Abbruch des Exportvorganges
- ein internes File-Flag gesetzt

Das File-Flag verhindert den Export nicht.

Es dient ausschließlich der Information des Benutzers und möglichen späteren Auswertungen.

---

# Projektfestlegungen

Vor dem Export müssen folgende Werte festgelegt sein:

## Quellenverweis

```text
SOUR @S...@
```

Der SOUR-Datensatz wird aus der Zieldatei ausgewählt.

---

## MARR.TYPE

Zulässige Werte:

```text
NONE
CIVIL
RELIGIOUS
```

Bedeutung:

### NONE

Es wird kein TYPE-Tag erzeugt.

Beispiel:

```gedcom
1 MARR
2 DATE ...
2 PLAC ...
```

### CIVIL

```gedcom
1 MARR
2 TYPE CIVIL
```

### RELIGIOUS

```gedcom
1 MARR
2 TYPE RELIGIOUS
```

---

# Exportreihenfolge

Exportiert werden ausschließlich Urkunden, die gemäß ADR-017 exportierbar sind.

Für jede Urkunde erfolgt:

```text
1. FAM exportieren
2. Zugehörige INDI-Daten exportieren
3. Exportstatus setzen
```

---

# Fall 1: Bestehender FAM-Datensatz

Der FAM-Datensatz existiert bereits in der Zieldatei.

---

## HUSB

Der HUSB-Verweis wird aktualisiert.

---

## WIFE

Der WIFE-Verweis wird aktualisiert.

---

## MARR

Für jedes Projekt wird ein bevorzugter MARR.TYPE festgelegt.

Zulässige Werte:

- CIVIL
- RELIGIOUS

Ein Projekt ohne MARR.TYPE-Festlegung ist nicht zulässig.

Bei der Bearbeitung oder beim Export eines bestehenden FAM-Datensatzes wird das relevante MARR-Ereignis wie folgt ermittelt:

1. Suche ein MARR-Ereignis mit einem TYPE, der der Projektfestlegung entspricht.

2. Wird kein solches MARR-Ereignis gefunden, suche ein MARR-Ereignis ohne TYPE-Angabe.

Ein MARR-Ereignis ohne TYPE wird als kompatibel zur Projektfestlegung betrachtet.

3. Erst wenn weder ein passendes MARR-Ereignis noch ein MARR-Ereignis ohne TYPE vorhanden ist, gilt kein passendes MARR-Ereignis als vorhanden.

In diesem Fall wird beim Export ein neues MARR-Ereignis mit dem projektspezifischen TYPE erzeugt.

---

### MARR vorhanden

Vorhandene Werte werden aktualisiert:

```text
DATE
PLAC
```

---

### MARR nicht vorhanden

Es wird erzeugt:

```gedcom
1 MARR
```

Optional zusätzlich:

```gedcom
2 TYPE ...
```

gemäß Projekteinstellung.

Danach:

```gedcom
2 DATE ...
2 PLAC ...
```

---

## REFN

Existiert bereits ein REFN mit identischem Inhalt:

```text
nichts ändern
```

Existiert kein identischer REFN:

```text
REFN ergänzen
```

Vorhandene REFN-Tags bleiben erhalten.

---

## SOUR

Vorhandene SOUR-Strukturen bleiben unverändert erhalten.

Es wird zusätzlich erzeugt:

```gedcom
1 SOUR @S...@
2 PAGE ...
2 NOTE ...
2 QUAY 3
```

Die Bildung von PAGE und NOTE erfolgt gemäß ADR-016.

---

# Fall 2: Neuer FAM-Datensatz

Der FAM-Datensatz existiert noch nicht.

Es wird erzeugt:

```gedcom
0 @F...@ FAM
1 HUSB @I...@
1 WIFE @I...@

1 MARR
2 DATE ...
2 PLAC ...
2 TYPE ... 
```

TYPE gemäß Projekteinstellung.

Anschließend:

```gedcom
1 REFN ...
1 SOUR @S...@
2 PAGE ...
2 NOTE ...
2 QUAY 3
```

---

# Export von Personen

Personen werden immer im aktuellen Projektzustand exportiert.

Es gibt keinen personenbezogenen Exportstatus.

---

# Fall 1: Bestehender INDI-Datensatz

Der Datensatz existiert bereits.

Folgende Inhalte werden aktualisiert:

```text
NAME

BIRT.DATE
BIRT.PLAC

DEAT.DATE
DEAT.PLAC
```

---

## Fehlende Strukturen

Fehlende BIRT- oder DEAT-Strukturen dürfen erzeugt werden.

Beispiel:

Vorher:

```gedcom
0 @I471@ INDI
1 NAME Johann /Müller/
```

Nachher:

```gedcom
0 @I471@ INDI
1 NAME Johann /Müller/
1 BIRT
2 DATE ...
2 PLAC ...
```

---

# Fall 2: Neuer INDI-Datensatz

Es wird erzeugt:

```gedcom
0 @I...@ INDI

1 NAME ...
1 SEX M|F
1 BIRT
...
1 DEAT
...
```

soweit entsprechende Daten vorhanden sind.
Geschlecht wird Rollenspezifisch (HUSB/WIFE) festgelegt. Auf neuere Besonderheiten gleichgeschlechtlicher Beziehungen wird nicht Rücksicht genommen, da es sich um archivierte Akten handelt 

---

## FAMS

Für einen neu angelegten FAM-Datensatz wird zusätzlich erzeugt:

```gedcom
1 FAMS @F...@
```

Eine Prüfung auf bestehende FAMS-Einträge erfolgt nicht.

---

# Protokollierung

Alle Änderungen an bestehenden Datensätzen werden protokolliert.

Das Protokoll enthält mindestens:

- Datensatztyp
- XREF
- Art der Änderung
- Urkunde
- Zeitpunkt

---

# Exportergebnis

Nach erfolgreichem Export:

- Bearbeitungshinweis in HEAD.NOTE bzw. HEAD.NOTE.CONT eintragen
- neue GEDCOM-Datei erzeugen
- Exportbericht erzeugen
- Exportstatus der Urkunde aktualisieren

Die weitere Behandlung des Exportstatus ist nicht Bestandteil dieser ADR.

---

# Auswirkungen auf bestehende ADRs

## ADR-006

Projektweite Quellenzuordnung wird verwendet.

---

## ADR-016

REFN, SOUR.PAGE und SOUR.NOTE werden gemäß ADR-016 erzeugt.

---

## ADR-017

Exportiert werden ausschließlich die dort freigegebenen Urkunden.

Konfliktbehandlung erfolgt vollständig in ADR-017.

---

# Architekturprinzip

Für ged_editor gilt:

> Der Export ergänzt und aktualisiert bestehende GEDCOM-Datenbestände, ohne vorhandene fachlich unabhängige Informationen zu entfernen.

> Vorhandene Quellen- und Referenzinformationen bleiben grundsätzlich erhalten.

> Die Projektdaten bilden beim Export die fachlich maßgebliche Wahrheit.

# Ergänzungen 
## 13.11.2026
Der Begriff FAM-Datensatz bezeichnet die GEDCOM-Repräsentation eines MarriageRecord.

Eine eigenständige Entität für den FAM-Datensatz existiert nicht.

---