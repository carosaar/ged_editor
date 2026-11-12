# ADR-015: Workflowstatusmodell für Urkunden

## Status

Akzeptiert

## Datum

2026-11-11

## Kontext

Die Urkunde ist gemäß ADR-001 das führende Fachobjekt.

Für die Bearbeitung mehrerer hundert Urkunden wird ein einfaches und eindeutig nachvollziehbares Workflowmodell benötigt.

Das Workflowmodell dient:

- der Arbeitsorganisation
- der Fortschrittskontrolle
- der Filterung von exportierbaren Urkunden
- der Qualitätssicherung durch Pflichtfeldprüfung

Der Workflowstatus beschreibt ausschließlich den Bearbeitungszustand einer Urkunde.

Der Exportstatus wird getrennt davon in ADR-019 definiert.

---

## Entscheidung

Jede Urkunde besitzt genau einen Workflowstatus.

Folgende Status werden definiert:

### In Bearbeitung

Die Erfassung der Urkunde ist noch nicht abgeschlossen.

Mindestens eine der folgenden Bedingungen trifft zu:

- Dateneingabe läuft noch
- Pflichtfelder fehlen
- Der Benutzer hat die Exportfreigabe=`Fertig`-Status noch nicht erteilt
- Eine zuvor freigegebene Urkunde wurde wieder zur Bearbeitung geöffnet

---

### Fertig

Die Erfassung ist abgeschlossen.

Alle Pflichtfelder sind vorhanden.

Die Urkunde wurde durch den Benutzer ausdrücklich zur Exportfreigabe markiert.

---

## Pflichtfelder für Heiratsurkunden

Für die Freigabe einer Heiratsurkunde müssen mindestens folgende Informationen vorhanden sein:

### Bräutigam

```text
Name
```

### Braut

```text
Name
```

### Urkundenidentifikation

```text
Registriernummer
Jahrgang
```

### Heirat

```text
Datum
Ort (MARR.PLAC)
```

---

## Nicht verpflichtende Angaben

Folgende Informationen können leer bleiben:

```text
Eltern und Herkunft

Todesvermerke

Legitimierungen

Randvermerke

Auffälligkeiten
```

---

## Freigabe einer Urkunde

Die Vergabe des Status

```text
Fertig
```

erfolgt ausschließlich durch den Benutzer.

Die Anwendung prüft zuvor automatisch die Pflichtfelder.

Sind Pflichtfelder nicht vorhanden, wird die Freigabe verweigert.

---

### Freigabe aus dem Erfassungsfenster

Die Freigabe kann beispielsweise erfolgen durch:

```text
Fertig-Button
```

oder

```text
STRG+ENTER
```

Die konkrete Tastenkombination ist Implementierungsdetail.

---

### Freigabe aus der Urkundenübersicht

Die Freigabe kann alternativ aus einer Urkunden- oder FAM-Übersicht erfolgen.

Auch hier wird die Pflichtfeldprüfung automatisch durchgeführt.

---

## Rücknahme der Freigabe

Eine freigegebene Urkunde kann jederzeit wieder zur Bearbeitung geöffnet werden.

Statuswechsel:

```text
Fertig
    ↓
In Bearbeitung
```

---

## Zulässige Statusübergänge

```text
In Bearbeitung
        ↓
      Fertig
```

und

```text
In Bearbeitung
        ↑
      Fertig
```

Weitere Workflowzustände existieren nicht.

---

## Beziehung zum Export

Nur Urkunden mit dem Status

```text
Fertig
```

werden in der Exportliste angezeigt.

Urkunden mit dem Status

```text
In Bearbeitung
```

sind vom Export ausgeschlossen.

Die weiteren Exportregeln werden durch ADR-017 und ADR-019 definiert.

---

## Konsequenzen

Mögliche Projektstatistiken:

```text
Urkunden in Bearbeitung

Fertige Urkunden
```

Diese Informationen stehen für Projektübersichten und Prüfberichte zur Verfügung.

---

## Architekturprinzip

Der Workflow wird ausschließlich auf Urkundenebene geführt.

Personen- und Familiendatensätze besitzen keinen eigenen Workflowstatus.

Die Freigabe einer Urkunde ist immer eine bewusste Benutzerentscheidung.

Eine Urkunde ist entweder:

```text
In Bearbeitung
```

oder

```text
Fertig
```

---

## Verwandte ADRs

- ADR-001 Urkunde als führendes Fachobjekt
- ADR-013 Export- und Prüfberichte
- ADR-017 Konflikterkennung und selektiver Export
- ADR-019 Exportstatus, Sperrlogik und Wiederholungsexporte
- ADR-020 Projektparameter