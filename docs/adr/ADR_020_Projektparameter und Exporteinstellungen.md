# ADR-020: Projektparameter und Exporteinstellungen

## Status

Akzeptiert

## Datum

2026-11-11

## Kontext

Während der Projektbearbeitung werden Informationen benötigt, die nicht Bestandteil einzelner Urkunden, Personen oder Familien sind.

Diese Informationen gelten projektweit und beeinflussen insbesondere:

- Importverhalten
- Konfliktprüfung
- XREF-Erzeugung
- GEDCOM-Export
- Quellenzuordnung

Die Einstellungen müssen dauerhaft innerhalb der EDG-Projektdatei gespeichert werden.

Hierzu wird die bereits vorhandene Tabelle:

```text
meta
```

verwendet.

---

# Entscheidung

Alle projektweiten Einstellungen werden zentral in der Projekttabelle `meta` gespeichert.

Diese Einstellungen gelten für das gesamte Projekt.

Eine Änderung wirkt sich auf alle zukünftigen Exporte aus.

---

# Projektparameter

---
## Übersicht 
* schema_version
* application_version

* marr_type
* marriage_place_default

* source_xref

* xref_prefix

* refn_prefix
* refn_suffix

* page_prefix
* page_suffix

---


## MARR.TYPE

Beschreibung:

Legt fest, welchen Typ die innerhalb des Projektes erfassten Heiratsurkunden repräsentieren.

Zulässige Werte:

```text
CIVIL
RELIGIOUS
```

Der Wert ist verpflichtend.

Ein Projekt ohne MARR.TYPE ist nicht zulässig.

---

### Verwendung

Bei der Bearbeitung bestehender FAM-Datensätze:

Suche zunächst ein:

```text
MARR.TYPE = Projektwert
```

Falls kein solches Ereignis existiert:

Suche ein MARR-Ereignis ohne TYPE.

Erst wenn beides fehlt, wird beim Export ein neues MARR-Ereignis erzeugt.

---

### Export neuer FAM-Datensätze

Neue FAM-Datensätze erhalten immer:

```gedcom
1 MARR
2 DATE ...
2 PLAC ...
2 TYPE <Projektwert>
```

TYPE ist hierbei verpflichtend.

---

## marriage_place_default

Beschreibung:
Legt den Standardort für neue Heiratsurkunden fest.

### Verwendung:
Der Wert wird als Standardwert vorbelegt und kann individuell geändert werden.
- Vorbelegung neuer Urkunden
- vom Benutzer pro Urkunde änderbar
- tatsächlicher Urkundeneintrag hat Vorrang

Der initiale Wert darf leer sein.

---

## SOUR-Zeiger

Beschreibung:

GEDCOM-XREF auf den Quellendatensatz, der für den Export verwendet wird.

Beispiel:

```text
@S42@
```

---

### Festlegung

Die Auswahl erfolgt spätestens vor dem Export.

Der Quellendatensatz muss bereits in der Ziel-GEDCOM vorhanden sein.

ged_editor erzeugt keine neuen SOUR-Datensätze.

---

### Verwendung

Beim Export wird erzeugt:

```gedcom
1 SOUR @S42@
2 PAGE ...
2 NOTE ...
2 QUAY 3
```

---

## XREF-Präfix

Beschreibung:

Präfix für alle neu erzeugten GEDCOM-XREFs.

Beispiel:

```text
H1905
```

---

### Verwendung

Neue Personen:

```text
@IH19050001@
```

Neue Familien:

```text
@FH19050001@
```

---

### Prüfung

Vor der ersten Verwendung wird geprüft, ob der Präfix bereits innerhalb der Ziel-GEDCOM verwendet wird.

Der Präfix muss innerhalb des Zielbestandes eindeutig sein.

---

## REFN-Präfix

Beschreibung:

Freitext vor der Urkundennummer.

Beispiel:

```text
Heirat Nr.
```

---

## REFN-Suffix

Beschreibung:

Freitext nach der Urkundennummer.

Beispiel:

```text
Standesamt Sulzbach
```

---

### Bildung

```text
REFN_PREFIX
+
Urkundennummer
+
REFN_SUFFIX
```

Beispiel:

```text
Heirat Nr. 15/1887
```

---

## PAGE-Präfix

Beschreibung:

Freitext vor der Urkundennummer innerhalb von SOUR.PAGE.

---

## PAGE-Suffix

Beschreibung:

Freitext nach der Urkundennummer innerhalb von SOUR.PAGE.

---

### Bildung

```text
PAGE_PREFIX
+
Urkundennummer
+
PAGE_SUFFIX
```

---

# Systemparameter

Diese Parameter werden intern verwendet.

## Schema-Version

Beispiel:

```text
5
```

Verwendung:

Migrationen.

---

## Programmversion

Beispiel:

```text
0.5.0
```

Verwendung:

Projektprüfung.

---

# Beziehung zu anderen ADRs

## ADR-006

Definiert die Verwendung des SOUR-Zeigers.

ADR-018 definiert seine Speicherung.

---

## ADR-016

Definiert die Bildung von:

- REFN
- SOUR.PAGE
- SOUR.NOTE

ADR-018 definiert die dafür erforderlichen Projektparameter.

---

## ADR-017

Definiert die Konfliktprüfung.

ADR-018 definiert den für neue Datensätze verwendeten XREF-Präfix.

---

# Architekturprinzip

Für ged_editor gilt:

> Projektweite Entscheidungen werden zentral gespeichert und nicht auf einzelne Urkunden verteilt.

Dadurch bleiben Exportverhalten, Konfliktprüfung und XREF-Erzeugung über das gesamte Projekt hinweg konsistent.