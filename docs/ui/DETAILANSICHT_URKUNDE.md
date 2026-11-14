# Detailansicht einer Urkunde

Die Detailansicht dient der kompakten, vollständigen und nicht editierbaren Darstellung einer Urkunde.

Die Reihenfolge der Daten orientiert sich an der historischen Heiratsurkunde.

Die Detailansicht wird verwendet:

- aus der Familien-/Urkundentabelle
- aus dem Erfassungsbereich
- zur Kontrolle vor dem Export
- zur späteren Vorschau exportierter Datensätze

---

## Darstellung

```text
Status:
<Workflowstatus> - <Exportstatus>

--------------------------------------------------

Urkunde:
**<Nummer>/<Jahrgang>**

Datum:
**<Heiratsdatum>**

Ort:
<Heiratsort>

--------------------------------------------------

Ehemann

  **<Name>, <Vorname>**

  <Geburtsdatum>, <Geburtsort>
  
  Herkunft / Eltern:
  <note_origin_husband>
  
  Todesvermerk:
  <note_death_husband>

--------------------------------------------------

Ehefrau

  **<Name>, <Vorname>**
  
  <Geburtsdatum>, <Geburtsort>
  
  Herkunft / Eltern:
  <note_origin_wife>
  
  Todesvermerk:
  <note_death_wife>

--------------------------------------------------

Legitimierungen:

<note_legitimation>

--------------------------------------------------

Randvermerke:

<note_marginal>

--------------------------------------------------

Besonderheiten:

<note_comments>
```

---

## Darstellung leerer Felder

Leere Felder werden in der Detailansicht vollständig unterdrückt.

Dies gilt sowohl für den Feldinhalt als auch für die Feldbezeichnung.

Beispiel:

```text
Todesvermerk:
```

wird nur angezeigt, wenn ein entsprechender Inhalt vorhanden ist.

Sind alle Felder eines Abschnittes leer, wird der gesamte Abschnitt ausgeblendet.

Ziel ist eine kompakte und leicht lesbare Darstellung der tatsächlich vorhandenen Informationen.

---

## Bearbeitbarkeit

Die Detailansicht ist grundsätzlich schreibgeschützt.

Eine Bearbeitung erfolgt ausschließlich über den Erfassungsbereich.

---

## Ziel

Die Detailansicht soll eine vollständige Urkunde auf möglichst kleinem Raum lesbar darstellen.

Sie dient der schnellen Kontrolle und dem Vergleich von Datensätzen.

Die Darstellung ist ausdrücklich keine Simulation der historischen Urkunde.