# ADR-019: Exportstatus, Sperrlogik und Wiederholungsexporte

## Status

Akzeptiert

## Datum

2026-11-12

## Kontext

ADR-017 definiert, welche Urkunden exportiert werden dürfen und wie Konflikte behandelt werden.

ADR-018 definiert die technische Durchführung des Exports.

Es fehlt die Festlegung, welchen Zustand eine Urkunde nach einem Export besitzt und wie mit bereits exportierten Daten umzugehen ist.

Da ged_editor ein urkundenorientiertes Erfassungssystem ist, muss eindeutig geregelt werden:

- wann eine Urkunde als abgeschlossen gilt
- welche Daten noch bearbeitet werden dürfen
- welche Daten gesperrt werden
- wie Wiederholungsexporte behandelt werden

---

# Grundsatz

Eine erfolgreich exportierte Urkunde gilt als fachlich abgeschlossen.

ged_editor dient der strukturierten Übernahme von Urkunden in einen GEDCOM-Bestand.

Der Export stellt den Abschluss dieses Arbeitsvorganges dar.

---

# Exportstatus

Zusätzlich zum Workflowstatus gemäß ADR-015 besitzt jede Urkunde einen Exportstatus.

## Zulässige Werte

```text
Nicht exportiert
Exportiert
Konflikt
```

---

## Bedeutung

### Nicht exportiert

Die Urkunde wurde noch nicht erfolgreich exportiert.

Die Urkunde ist vollständig bearbeitbar.

---

### Exportiert

Die Urkunde wurde erfolgreich exportiert.

Die Urkunde gilt als abgeschlossen.

---

### Konflikt

Die Urkunde konnte nicht exportiert werden.

Die Ursache ergibt sich aus der Konfliktprüfung gemäß ADR-017.

Die Urkunde bleibt bearbeitbar.

---

# Statusübergänge

## Erfolgreicher Export

```text
Nicht exportiert
        ↓
    Exportiert
```

---

## Konfliktfall

```text
Nicht exportiert
        ↓
     Konflikt
```

---

## Konfliktbehebung

Nach Bearbeitung durch den Benutzer:

```text
Konflikt
        ↓
Nicht exportiert
```

Danach kann erneut exportiert werden.

---

# Schreibschutz

## Gesperrt werden

Nach erfolgreichem Export:

- die Urkunde
- alle urkundenspezifischen Erfassungsdaten
- der zur Urkunde gehörende FAM-Datensatz

---

## Begründung

Innerhalb eines Projektes besteht gemäß ADR-017 eine fachliche 1:1-Beziehung zwischen:

```text
Urkunde
↔
FAM-Datensatz
```

Der FAM-Datensatz repräsentiert die durch die Urkunde dokumentierte Eheschließung.

Mit dem erfolgreichen Export gilt dieser Arbeitsvorgang als abgeschlossen.

---

## Nicht gesperrt werden

Auch nach erfolgreichem Export weiterhin bearbeitbar:

- Personendatensätze
- Quellenzuordnungen
- Projekteinstellungen

---

## Begründung

Personendatensätze stellen projektweite Stammdatenobjekte dar.

Eine Person kann:

- in mehreren Urkunden vorkommen
- durch spätere Urkunden ergänzt werden
- durch spätere Urkunden korrigiert werden

Die Bearbeitung einer Person darf deshalb nicht vom Exportstatus einer einzelnen Urkunde abhängig sein.

---

# Wiederholungsexporte

Bereits exportierte Urkunden werden bei späteren Exportläufen grundsätzlich übersprungen.

Exportiert werden ausschließlich Urkunden mit dem Status:

```text
Nicht exportiert
```

---

## Konsequenz

Ein Export ist grundsätzlich inkrementell.

Jeder Exportlauf verarbeitet nur die seit dem letzten Export neu hinzugekommenen oder korrigierten Urkunden.

---

# Konfliktstatus

Urkunden mit dem Status:

```text
Konflikt
```

werden nicht exportiert.

Sie bleiben:

- sichtbar
- bearbeitbar
- erneut prüfbar

---

## Ziel

Konflikte sollen niemals den Export anderer Urkunden blockieren.

---

# Benutzerprinzip

ged_editor trifft keine genealogischen Entscheidungen.

Die Anwendung darf:

- Konflikte erkennen
- Hinweise anzeigen
- Vorschläge erzeugen

Die endgültige Entscheidung trifft immer der Benutzer.

---

# Exporthistorie

Der Exportstatus dokumentiert den Bearbeitungszustand der Urkunde.

Er ersetzt keine Exportprotokolle gemäß ADR-013.

---

## Exportbericht

Jeder erfolgreiche Export erzeugt weiterhin:

- Exportbericht
- Konfliktbericht
- Änderungsprotokoll

gemäß ADR-012 und ADR-013.

---

# Auswirkungen auf bestehende ADRs

## ADR-015

Der Exportstatus ergänzt das Workflowmodell.

Workflowstatus:

```text
Neu
In Bearbeitung
Fertig
Geprüft
```

Exportstatus:

```text
Nicht exportiert
Exportiert
Konflikt
```

Beide Statussysteme sind unabhängig voneinander.

---

## ADR-017

Definiert die Bedingungen für:

```text
Exportiert
```

oder

```text
Konflikt
```

---

## ADR-018

Definiert die technische Durchführung des Exports.

ADR-019 definiert die fachlichen Folgen des Exports.

---

# Architekturprinzip

Für ged_editor gilt:

> Eine erfolgreich exportierte Urkunde gilt als fachlich abgeschlossen.

> Bereits exportierte Urkunden werden nicht erneut bearbeitet.

> Konflikte verhindern ausschließlich den Export der betroffenen Urkunde.

> Personendatensätze bleiben projektweit bearbeitbar.

---

# Verwandte ADRs

- ADR-001 Urkunde als führendes Fachobjekt
- ADR-011 GEDCOM-Dateien werden niemals direkt bearbeitet
- ADR-012 Änderungsprotokoll und Revisionssicherheit
- ADR-013 Export- und Prüfberichte
- ADR-015 Workflowstatusmodell
- ADR-017 Konflikterkennung und selektiver Export
- ADR-018 Exportmodell und GEDCOM-Erzeugung
