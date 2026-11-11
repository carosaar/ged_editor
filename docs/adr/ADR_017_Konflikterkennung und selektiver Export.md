# ADR-017: Konflikterkennung, Exportstatus und selektiver Export

## Status

Akzeptiert

## Datum

2026-11-11

## Kontext

Gemäß ADR-011 wird eine GEDCOM-Datei importiert und anschließend innerhalb einer EDG-Projektdatei bearbeitet.

Zwischen Import und Export kann die ursprüngliche GEDCOM-Datei jedoch durch ein Genealogieprogramm oder andere Werkzeuge verändert worden sein.

Insbesondere können:

- bestehende INDI-Datensätze geändert worden sein
- bestehende FAM-Datensätze geändert worden sein
- bestehende INDI-Datensätze gelöscht worden sein
- bestehende FAM-Datensätze gelöscht worden sein

ged_editor muss solche Änderungen erkennen und berücksichtigen.

Gleichzeitig soll verhindert werden, dass Konflikte einzelner Urkunden den Export des gesamten Projektes blockieren.

---

## Korrektur früherer Annahmen

Im Rahmen der Architekturüberprüfung wurde zunächst angenommen, dass Konflikte auch durch die Erzeugung neuer XREFs entstehen könnten.

Diese Annahme wird ausdrücklich verworfen.

Neue Datensätze erhalten einen eigenen projektbezogenen XREF-Präfix und werden in einem vom Ursprungsbestand getrennten Nummernkreis erzeugt.

Konflikte entstehen daher ausschließlich durch Änderungen an bereits existierenden Datensätzen.

---

# Entscheidung

>Vorbemerkung:
Jeder durch ged_editor erzeugte oder bearbeitete FAM-Datensatz ist genau einer Urkunde zugeordnet.
.
>>Innerhalb eines Projektes besteht zwischen
MarriageRecord und FAM eine fachliche 1:1-Beziehung.
Ein FAM-Datensatz repräsentiert die durch die
Urkunde dokumentierte Eheschließung.
Deshalb kann ein exportierter FAM-Datensatz
gemeinsam mit seiner Urkunde gesperrt werden.
Personendatensätze sind hiervon ausdrücklich
ausgenommen, da sie durch mehrere Urkunden
referenziert werden können.

Der Export erfolgt urkundenbezogen.

Konflikte werden auf Ebene der Urkunde behandelt.

Eine konfliktfreie Urkunde darf immer exportiert werden.

Konfliktbehaftete Urkunden werden zurückgestellt.

Der Export anderer Urkunden wird dadurch nicht beeinflusst.

---

# Eigenständiger XREF-Nummernkreis

Neue INDI- und FAM-Datensätze erhalten immer einen neu erzeugten XREF.

Die XREFs werden projektbezogen erzeugt.

Der Projektpräfix wird:

- vom Benutzer festgelegt oder
- automatisch vorgeschlagen

Vor der erstmaligen Verwendung wird geprüft, ob der Präfix bereits innerhalb des Zielbestandes existiert.

---

## Beispiele

Präfix:

```text
H1905
```

Neue Personen:

```text
@IH19050001@
@IH19050002@
```

Neue Familien:

```text
@FH19050001@
@FH19050002@
```

---

## Konsequenz

Zwischen neu angelegten Datensätzen und dem Ursprungsbestand können keine XREF-Kollisionen entstehen.

---

# Konfliktrelevante Datensätze

Konfliktprüfungen erfolgen ausschließlich für bereits vorhandene Datensätze, die tatsächlich bearbeitet werden können.

Nicht konfliktrelevant sind:

- neu angelegte INDI-Datensätze
- neu angelegte FAM-Datensätze

Diese können unabhängig vom Ursprungsbestand exportiert werden.

---

# Konflikttypen

## Typ A – Datensatz gelöscht

Der Datensatz war beim Import vorhanden, existiert beim Export jedoch nicht mehr.

Beispiel:

```text
@I471@
```

oder

```text
@F88@
```

wurden zwischenzeitlich gelöscht.

---

## Typ B – Datensatz fachlich geändert

Der Datensatz existiert weiterhin, enthält jedoch andere Werte als zum Zeitpunkt des Imports.

Beispiel:

Import:

```text
NAME Johann Müller
```

Aktueller GEDCOM-Bestand:

```text
NAME Johann Jakob Müller
```

Der Datensatz wurde außerhalb von ged_editor verändert.

---

# Konfliktrelevante Inhalte

Es werden ausschließlich Inhalte geprüft, die Bestandteil des fachlichen Scopes von ged_editor sind.

---

## INDI

Verglichen werden:

```text
NAME

BIRT.DATE
BIRT.PLAC

DEAT.DATE
DEAT.PLAC
```

Der NAME-Tag gilt gemäß GEDCOM als Hauptname.

GIVN und SURN werden lediglich zur Bearbeitung verwendet und aus dem Hauptnamen abgeleitet.

Für die Konfliktprüfung ist ausschließlich der NAME-Tag maßgeblich.

---

## FAM

Verglichen werden:

```text
MARR.DATE
MARR.PLAC
```

---

### Mehrere MARR-Ereignisse

Es können mehrere MARR-Ereignisse existieren.

Beispielsweise:

```text
MARR TYPE CIVIL
MARR TYPE RELIGIOUS
MARR ohne TYPE
```

Der Benutzer darf alle vorhandenen MARR-Ereignisse einsehen.

Für die Bearbeitung besitzt ein MARR-Ereignis des Typs

```text
CIVIL
```

Vorrang.

Die Konfliktprüfung erfolgt ausschließlich für das MARR-Ereignis, das durch ged_editor tatsächlich bearbeitet wurde.

---

# Nicht konfliktrelevante Inhalte

Nicht verglichen werden:

```text
REFN
SOUR
NOTE
```

Begründung:

Diese Informationen werden gemäß ADR-016 durch ged_editor neu erzeugt oder ergänzt.

---

Ebenfalls nicht berücksichtigt werden:

```text
CHIL
FAMC
FAMS
```

Diese liegen außerhalb des fachlichen Scopes gemäß ADR-004.

---

# Behandlung von Mehrfachstrukturen

## NAME

Gemäß GEDCOM-Standard wird ausschließlich der erste NAME-Eintrag verarbeitet.

Weitere NAME-Einträge werden ignoriert.

Die Bearbeitung erfolgt über:

```text
GIVN
SURN
```

Beim Export wird daraus ein NAME-Tag erzeugt.

---

## BIRT und DEAT

Es wird jeweils das erste Ereignis verarbeitet.

Existieren weitere gleichartige Ereignisse, werden diese ignoriert.

Die Validierung der GEDCOM-Struktur ist nicht Aufgabe von ged_editor.

---

## SOUR

Vorhandene SOUR-Tags in bestehenden FAM-Datensätzen werden ignoriert.

Diese können andere Ereignisse oder Fakten dokumentieren.

ged_editor erzeugt ausschließlich neue SOUR-Verweise auf einen vorhandenen SOUR-Datensatz gemäß ADR-006.

Es werden keine SOUR-Datensätze erzeugt.

---

## REFN

Vorhandene REFN-Tags werden ignoriert.

ged_editor erzeugt REFN gemäß ADR-016 neu.

---

# Exportstatus

Diese ADR ergänzt das Workflowmodell aus ADR-015.

Die Workflow-Status bleiben unverändert.

Zusätzlich wird ein unabhängiger Exportstatus eingeführt.

---

## Workflowstatus

Gemäß ADR-015:

```text
Neu
In Bearbeitung
Fertig
Geprüft
```

---

## Exportstatus

Neu eingeführt:

```text
Nicht exportiert
Exportiert
Konflikt
```

---

# Trennung der Statussysteme

Beispiel:

```text
Workflowstatus:
Geprüft

Exportstatus:
Konflikt
```

ist zulässig.

Beide Status beschreiben unterschiedliche fachliche Sachverhalte.

---

# Änderungskennzeichen für Personen

Personendatensätze erhalten zusätzlich ein technisches Merkmal:

```text
needs_export
```

Bedeutung:

```text
false
    Person entspricht dem letzten Exportstand

true
    Person enthält noch nicht exportierte Änderungen
```

---

## Zweck

Eine Person kann in mehreren Urkunden verwendet werden.

Beispiel:

```text
Urkunde 15/1887
    ↘

Urkunde 42/1891
    ↘

Urkunde 78/1894
```

zeigen auf dieselbe Person.

Änderungen an einer Person müssen deshalb projektweit sichtbar bleiben.

---

## Nutzen

Wird eine Person in einer späteren Urkunde ergänzt oder korrigiert:

```text
Joseph Müller
```

↓

```text
Joseph (Josef) Müller
```

wird

```text
needs_export = true
```

gesetzt.

Dadurch erkennt der Bearbeiter sofort, dass an dieser Person bereits nicht exportierte Änderungen existieren.

Dies hilft insbesondere bei widersprüchlichen Schreibweisen und unterschiedlichen Angaben aus mehreren Urkunden.

---

# Exportverhalten

Vor jedem Export erfolgt eine Konfliktprüfung.

---

## Konfliktfreie Urkunde

Die Urkunde wird exportiert.

Der Exportstatus wird gesetzt auf:

```text
Exportiert
```

---

## Konfliktbehaftete Urkunde

Die Urkunde wird nicht exportiert.

Der Exportstatus wird gesetzt auf:

```text
Konflikt
```

---

## Projektverhalten

Ein Konflikt führt niemals zum Abbruch des gesamten Exportvorgangs.

Beispiel:

```text
15/1887
    Exportiert

16/1887
    Konflikt

17/1887
    Exportiert
```

Dieses Verhalten ist ausdrücklich gewünscht.

---

# Bearbeitung exportierter Urkunden

## Grundsatz

Erfolgreich exportierte Urkunden gelten als abgeschlossen.

Nach erfolgreichem Export wird die betreffende Urkunde schreibgeschützt.

Eine nachträgliche Bearbeitung innerhalb desselben Projektes ist nicht zulässig.

---

## Begründung

ged_editor dient der strukturierten Erfassung und Übernahme von Urkunden.

Nach erfolgreichem Export ist der fachliche Zweck einer Urkunde erfüllt.

Die Sperrung verhindert:

- unbeabsichtigte Änderungen
- mehrfache Bearbeitung derselben Urkunde
- widersprüchliche Exportstände
- komplexe Nachverfolgung mehrerer Exportversionen

---

# Schreibschutz

## Gesperrt werden

Nach erfolgreichem Export:

- die Urkunde selbst
- die urkundenspezifischen Erfassungsdaten
- der zugehörige FAM-Datensatz

---

## Nicht gesperrt werden

Auch nach erfolgreichem Export weiterhin bearbeitbar:

- Personendatensätze
- Quellenzuordnungen
- Projekteinstellungen

---

## Begründung

Eine Person kann in mehreren Urkunden verwendet werden.

Der Export einer einzelnen Urkunde darf niemals dazu führen, dass gemeinsam genutzte Personendatensätze dauerhaft gesperrt werden.

---

## Konfliktfälle

Urkunden mit Exportstatus

```text
Konflikt
```

bleiben vollständig bearbeitbar.

Nur erfolgreich exportierte Urkunden werden gesperrt.

---

## Weitere Exporte

Bereits exportierte Urkunden werden bei späteren Exportvorgängen grundsätzlich übersprungen.

Exportiert werden ausschließlich Urkunden mit dem Status:

```text
Nicht exportiert
```

und ohne Konflikte.

Personen mit

```text
needs_export = true
```

werden dabei erneut berücksichtigt.

---

# Konfliktbericht

Nach jedem Export wird ein Konfliktbericht erzeugt.

Beispiel:

```text
Urkunde 16/1887

INDI @I471@

Import:
Johann Müller

Aktueller Bestand:
Johann Jakob Müller

Status:
Konflikt
```

Der Konfliktbericht dient der späteren Nachbearbeitung.

---

# Auswirkungen auf bestehende ADRs

## ADR-011

Wird ergänzt.

Die Trennung zwischen GEDCOM-Datei und EDG-Projekt bleibt unverändert bestehen.

Zusätzlich wird definiert, wie Änderungen des Ursprungsbestandes erkannt werden.

---

## ADR-015

Wird ergänzt.

Zusätzlich zu den Workflow-Status existiert ein unabhängiger Exportstatus.

Die Definition des Workflow-Status bleibt gültig.

---

## ADR-016

Bleibt unverändert.

Die Bildung von REFN, SOUR.PAGE und SOUR.NOTE wird durch diese ADR nicht verändert.

Diese Inhalte sind ausdrücklich nicht konfliktrelevant.

---

# Architekturprinzip

Für ged_editor gilt:

> Konflikte werden auf Urkundenebene behandelt. Konfliktfreie Urkunden sollen jederzeit exportierbar bleiben.

und

> Eine erfolgreich exportierte Urkunde gilt als abgeschlossen und wird innerhalb des Projektes nicht erneut bearbeitet.

und

> Personendaten sind projektweite Wissensobjekte und können durch weitere Urkunden jederzeit ergänzt oder korrigiert werden.

---

# Verwandte ADRs

- ADR-001 Urkunde als führendes Fachobjekt
- ADR-004 Begrenzung des fachlichen Scopes auf Ehepartner
- ADR-006 Quellenzuordnung erfolgt beim Export
- ADR-011 GEDCOM-Dateien werden niemals direkt bearbeitet
- ADR-015 Workflowstatusmodell
- ADR-016 Bildung von REFN, SOUR.PAGE und SOUR.NOTE