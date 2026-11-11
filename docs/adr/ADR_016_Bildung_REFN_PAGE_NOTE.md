# ADR-016: Bildung von REFN, SOUR.PAGE und SOUR.NOTE

## Status

Akzeptiert

## Datum

2026-11-11

## Kontext

Für den GEDCOM-Export müssen die Inhalte der Tags

- REFN
- SOUR.PAGE
- SOUR.NOTE

einheitlich und reproduzierbar erzeugt werden.

Gleichzeitig soll die Darstellung archiv- und quellenabhängig konfigurierbar sein.

## Entscheidung

Die Bildung von REFN und SOUR.PAGE erfolgt konfigurierbar.

Die Bildung von SOUR.NOTE erfolgt nach einer festen Struktur.

REFN, SOUR.PAGE und SOUR.NOTE existieren nicht als persistente GEDCOM-Strukturen innerhalb des Projektes.

Sie werden ausschließlich während des Exportvorgangs aus den Erfassungsdaten generiert.

## REFN

REFN dient der Darstellung der Urkundenkennung.

Grundlage:

```text
Urkundennummer = Nr/Jahr
```

Beispiel:

```text
15/1878
```

### Aufbau

```text
PRE_TEXT + URKUNDENNUMMER + SUFFIX_TEXT
```

Beispiel:

```text
Heirat-Nr. 15/1878
```

oder

```text
Standesamt Sulzbach Nr. 15/1878
```

### Einstellungen

Folgende Einstellungen werden projektweit gespeichert:

```text
REFN_PRE_TEXT
REFN_SUFFIX_TEXT
```

## SOUR.PAGE

SOUR.PAGE wird analog aufgebaut. 

### Aufbau

```text
PRE_TEXT + URKUNDENNUMMER + SUFFIX_TEXT
```

Beispiel:

```text
Heiratsregister 15/1878
```

oder

```text
Band III Nr. 15/1878
```

### Einstellungen

Folgende Einstellungen werden projektweit gespeichert:

```text
PAGE_PRE_TEXT
PAGE_SUFFIX_TEXT
```

## SOUR.NOTE

SOUR.NOTE wird aus den strukturierten Notizfeldern erzeugt.

Die Reihenfolge der Bereiche ist fest definiert.

### Bereich 1

```text
Herkunft
* Mann: ...
* Frau: ...
```

### Bereich 2

```text
Gestorben:
* Mann: ...
* Frau: ...
```

### Bereich 3

```text
Legitimierung(en):
...
```

### Bereich 4

```text
Randvermerke:
...
```

### Bereich 5

```text
Anmerkungen:
...
```

## Exportregeln

Leere Bereiche werden beim Export unterdrückt.

Beispiel:

Wenn keine Legitimierungen vorliegen:

```text
Legitimierung(en):
...
```

wird vollständig weggelassen.

## Beispiel

```text
Herkunft
* Mann: Sohn des Bergmannes Johann Müller aus Sulzbach
* Frau: Tochter des Hüttenarbeiters Peter Schmitt aus Dudweiler

Gestorben:
* Mann: Randvermerk vom 15.03.1928
* Frau:

Legitimierung(en):
Durch Eheschließung legitimiert: Anna Müller

Randvermerke:
Scheidung eingetragen am 03.06.1912

Anmerkungen:
Namensschreibweise im Register schwer lesbar.
```

## Konsequenzen

- Einheitliche Darstellung aller Notizen
- Vergleichbarkeit der Exportdaten
- reproduzierbare GEDCOM-Ausgaben
- einfache spätere Erweiterbarkeit

## Architekturprinzip

Die Erfassung erfolgt strukturiert.

Die GEDCOM-NOTE wird erst beim Export generiert.

## Verwandte ADRs

- ADR-005 Strukturierte Erfassung von Urkundennotizen
- ADR-006 Quellenzuordnung
- ADR-013 Exportberichte