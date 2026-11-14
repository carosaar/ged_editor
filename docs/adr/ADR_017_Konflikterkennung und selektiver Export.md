# ADR-017: Konflikterkennung und selektiver Export

## Status

Akzeptiert

## Datum

2026-11-11

## Kontext

Gemäß ADR-011 wird eine GEDCOM-Datei importiert und anschließend innerhalb einer EDG-Projektdatei bearbeitet.

Zwischen Import und Export kann sich die ursprüngliche GEDCOM-Datei verändert haben.

Insbesondere können:

- bestehende INDI-Datensätze geändert worden sein
- bestehende FAM-Datensätze geändert worden sein
- bestehende INDI-Datensätze gelöscht worden sein
- bestehende FAM-Datensätze gelöscht worden sein

ged_editor muss diese Änderungen erkennen und bewerten.

Dabei soll verhindert werden, dass einzelne Problemfälle den Export des gesamten Projektes blockieren.

Gleichzeitig soll der Benutzer die Kontrolle über alle relevanten Entscheidungen behalten.

---

## Zielsetzung

Vor jedem Export wird geprüft, ob die beim Import verwendeten Datensätze noch in einem Zustand vorliegen, der eine konsistente Übernahme der Projektdaten erlaubt.

Das Ergebnis der Prüfung wird in folgende Kategorien eingeteilt:

- Hinweis
- Maßnahme erforderlich
- Konflikt

Nur echte Konflikte verhindern den Export einer Urkunde.

---

# Grundsatz

Die Konfliktprüfung erfolgt urkundenbezogen.

Entscheidungsobjekt ist immer die Urkunde.

Es werden niemals einzelne INDI- oder FAM-Datensätze unabhängig von ihrer Urkunde exportiert oder zurückgestellt.

---

# Eigenständiger XREF-Nummernkreis

Neue INDI- und FAM-Datensätze erhalten einen projektbezogenen XREF.

Der Projektpräfix wird:

- vom Benutzer festgelegt oder
- automatisch vorgeschlagen

Vor der ersten Verwendung wird geprüft, ob der Präfix bereits innerhalb der Zieldatei existiert.

Beispiele:

```text
@IH19050001@
@IH19050002@

@FH19050001@
@FH19050002@
```

Dadurch können keine XREF-Kollisionen mit dem Ursprungsbestand entstehen.

---

# Konfliktrelevante Datensätze

Konfliktprüfungen werden ausschließlich für Datensätze durchgeführt, die bereits beim Import bestanden haben.

Nicht geprüft werden:

- neue INDI-Datensätze
- neue FAM-Datensätze

Diese werden unabhängig vom Ursprungsbestand behandelt.

---

# Prüfumfang

Verglichen werden ausschließlich Daten, die durch ged_editor bearbeitet werden.

## INDI

Verglichen werden:

```text
NAME

BIRT.DATE
BIRT.PLAC

DEAT.DATE
DEAT.PLAC
```

Für die Konfliktprüfung ist ausschließlich der NAME-Tag maßgeblich.

GIVN und SURN dienen lediglich der Bearbeitung.

---

## FAM

Verglichen werden:

```text
MARR.DATE
MARR.PLAC
```

---

### Mehrere MARR-Ereignisse

Existieren mehrere MARR-Ereignisse, wird ausschließlich das durch ged_editor bearbeitete MARR-Ereignis geprüft.

MARR-Ereignisse des Typs

```text
CIVIL
```

besitzen Vorrang.

---

# Nicht konfliktrelevante Inhalte

Nicht geprüft werden:

```text
REFN
SOUR
NOTE
```

Diese Inhalte werden gemäß ADR-016 neu erzeugt oder ergänzt.

Ebenfalls nicht geprüft werden:

```text
CHIL
FAMC
FAMS
```

Diese liegen außerhalb des fachlichen Projektumfangs.

---

# Behandlung von Mehrfachstrukturen

## NAME

Es wird ausschließlich der erste NAME-Eintrag verarbeitet.

Weitere NAME-Einträge werden ignoriert.

Die Bearbeitung erfolgt über:

```text
GIVN
SURN
```

Der NAME-Tag wird daraus beim Export erzeugt.

---

## BIRT und DEAT

Es wird jeweils nur das erste Ereignis verarbeitet.

Weitere gleichartige Ereignisse werden ignoriert (da sie eigentlich Fehler nach gedcom-Standard sind).

Die Validierung der GEDCOM-Struktur ist nicht Aufgabe von ged_editor.

---

# Prüfungsergebnis: Hinweis

Ein Hinweis liegt vor, wenn ein Datensatz weiterhin existiert, sich jedoch seit dem Import verändert hat.

Beispiel:

Import:

```text
NAME Johann Müller
```

Aktueller Bestand:

```text
NAME Johann Jakob Müller
```

---

## Bedeutung

Ein Hinweis stellt keinen Konflikt dar.

Die Änderung wird dokumentiert und dem Benutzer angezeigt.

Der Benutzer kann:

- die Meldung einzeln bestätigen
- alle gleichartigen Hinweise gesammelt bestätigen

---

## Export

Hinweise verhindern den Export nicht.

---

# Prüfungsergebnis: Maßnahme erforderlich

Eine Maßnahme ist erforderlich, wenn ein beim Import vorhandener Datensatz nicht mehr existiert.

Beispiel:

```text
@I471@
```

oder

```text
@F88@
```

wurde gelöscht.

---

## Vorgeschlagene Lösung

ged_editor kann vorschlagen:

```text
Datensatz als neuen Datensatz erzeugen
```

Dabei wird ein neuer projektbezogener XREF vergeben.

---

## Benutzerentscheidung

Der Benutzer kann:

### Einzelentscheidung

```text
Vorschlag übernehmen

oder

Vorschlag ablehnen
```

### Sammelentscheidung

```text
Für alle übernehmen

oder

Für alle ablehnen
```

---

## Übernahme

Bei Übernahme wird die Urkunde normal exportiert.

---

## Ablehnung

Bei Ablehnung wird die Urkunde vom aktuellen Export ausgeschlossen.

Die Urkunde verbleibt unverändert im Projekt und kann später erneut exportiert werden.

---

# Prüfungsergebnis: Konflikt

Ein Konflikt liegt vor, wenn die vorgeschlagene Korrektur zu einem inkonsistenten Projektzustand führen würde.

---

## Beispiel

Ein beim Import vorhandener INDI-Datensatz wurde gelöscht.

Die vorgeschlagene Neuanlage würde einen neuen XREF erzeugen.

Dieser Datensatz wird jedoch bereits von einer früher exportierten Urkunde referenziert.

Eine automatische Korrektur würde dadurch Änderungen an bereits exportierten Projektbestandteilen erfordern.

---

## Bedeutung

Der Konflikt kann nicht automatisch aufgelöst werden.

---

## Folge

Die betroffene Urkunde wird nicht exportiert.

Sie bleibt zur weiteren Bearbeitung im Projekt erhalten.

Andere konfliktfreie Urkunden können weiterhin exportiert werden.

---


---

# Manueller Exportausschluss

Zusätzlich zum Exportstatus kann eine Urkunde ausdrücklich vom Export ausgeschlossen werden.

Der Exportausschluss erfolgt durch den Benutzer.

---

## Speicherung

Der Exportausschluss wird im MarriageRecord gespeichert:

```text
no_export
```

Zulässige Werte:

```text
TRUE

FALSE
```

---

## Bedeutung

```text
FALSE
```

Die Urkunde darf exportiert werden.

```text
TRUE
```

Die Urkunde wird bei Exportläufen übersprungen.

---

## Beziehung zum Exportstatus

Der Exportausschluss ist kein Exportstatus.

Er verändert weder:

```text
workflow_status
```

noch:

```text
export_status
```

---

## Verwendung

Der Exportausschluss dient beispielsweise:

- zum Zurückstellen einzelner Urkunden
- zur vorübergehenden Auslassung
- für Testzwecke
- zur manuellen Qualitätskontrolle

---

## Benutzeroberfläche

Die Familien- und Urkundenliste enthält eine Auswahlspalte:

```text
☑
```

bedeutet:

```text
Export zulässig
```

```text
☐
```

bedeutet:

```text
Vom Export ausgeschlossen
```
---

## Exportlauf

Während des Exports werden ausschließlich Urkunden verarbeitet, für die gilt:

```text
workflow_status = Fertig

UND

export_status != Exportiert

UND

NoExport = FALSE
```

---

## Beispiel

```text
Urkunde 15/1887
    Hinweis
    → Export

Urkunde 16/1887
    Maßnahme erforderlich
    → Benutzer übernimmt Vorschlag
    → Export

Urkunde 17/1887
    Konflikt
    → kein Export

Urkunde 18/1887
    konfliktfrei
    → Export
```

---

# Konfliktprotokoll

Alle Hinweise, Maßnahmen und Konflikte werden dokumentiert.

Das Protokoll enthält mindestens:

- Urkunde
- Datensatztyp
- betroffener XREF
- Prüfungsart
- Entscheidung
- Ergebnis

---

# Auswirkungen auf bestehende ADRs

## ADR-011

Wird ergänzt.

Die Trennung zwischen GEDCOM-Datei und EDG-Projekt bleibt bestehen.

Zusätzlich wird definiert, wie Änderungen des Ursprungsbestandes erkannt und bewertet werden.

---

## ADR-015

Wird ergänzt.

Der Exportstatus einer Urkunde kann durch das Ergebnis der Konfliktprüfung beeinflusst werden.

---

## ADR-016

Bleibt unverändert.

REFN, SOUR.PAGE und SOUR.NOTE sind nicht Bestandteil der Konfliktprüfung.

---

# Architekturprinzip

Für ged_editor gilt:

> Konflikte werden auf Urkundenebene behandelt.

> Der Benutzer trifft die fachlichen Entscheidungen.

> Hinweise dürfen den Export nicht verhindern.

> Echte Konflikte dürfen niemals automatisch aufgelöst werden.

> Konfliktfreie Urkunden sollen jederzeit exportierbar bleiben.

---

# Verwandte ADRs

- ADR-001 Urkunde als führendes Fachobjekt
- ADR-004 Begrenzung des fachlichen Scopes auf Ehepartner
- ADR-006 Quellenzuordnung erfolgt beim Export
- ADR-011 GEDCOM-Dateien werden niemals direkt bearbeitet
- ADR-015 Workflowstatusmodell
- ADR-016 Bildung von REFN, SOUR.PAGE und SOUR.NOTE

# Ergänzungen 
## 13.11.2026
Zur Durchführung der Konfliktprüfung wird für relevante importierte INDI-
und MarriageRecord-Datensätze ein source_snapshot gespeichert.

Der Aufbau des Snapshots ist Implementierungsdetail.

---
---

# Entscheidungsmatrix Exportprüfung

| Prüfergebnis | Ursache | Benutzerentscheidung erforderlich | Export dieser Urkunde möglich | Exportstatus | Protokollierung |
|--------------|----------|----------------------------------|------------------------------|--------------|----------------|
| Kein Befund | Keine Abweichungen festgestellt | Nein | Ja | Exportiert | Erfolgreicher Export |
| Hinweis | Datensatz existiert weiterhin, relevante Inhalte haben sich seit dem Import geändert | Ja, Bestätigung möglich (einzeln oder global) | Ja | Exportiert | Hinweis dokumentieren |
| Maßnahme erforderlich | Datensatz existiert nicht mehr, kann jedoch als neuer Datensatz erzeugt werden | Ja, Entscheidung erforderlich | Ja, wenn Vorschlag angenommen wird | Exportiert | Entscheidung dokumentieren |
| Maßnahme erforderlich | Datensatz existiert nicht mehr, Vorschlag wird abgelehnt | Ja | Nein | Nicht exportiert | Ablehnung dokumentieren |
| Konflikt | Datensatz existiert nicht mehr und eine automatische Neuanlage würde bereits exportierte Projektbestandteile inkonsistent machen | Nein, nicht automatisch lösbar | Nein | Konflikt | Konflikt dokumentieren |

---

# Ablauflogik in Kurzform

```TEXT
Datensatz vorhanden?
│
├─ Ja
│   │
│   ├─ Inhalt unverändert
│   │      → Export
│   │
│   └─ Inhalt geändert
│          → Hinweis
│          → Benutzer bestätigen
│          → Export
│
└─ Nein
    │
    ├─ Neuer Datensatz möglich
    │      │
    │      ├─ Benutzer übernimmt Vorschlag
    │      │      → Export
    │      │
    │      └─ Benutzer lehnt ab
    │             → Nicht exportiert
    │
    └─ Neuanlage würde bereits exportierte
        Projektbestandteile inkonsistent machen
               → Konflikt
               → Kein Export
```

* Ein Hinweis beschreibt eine festgestellte Abweichung.
* Eine Maßnahme beschreibt einen Fall, der durch eine Benutzerentscheidung lösbar ist.
* Ein Konflikt beschreibt einen Fall, der innerhalb des aktuellen Projektzustands nicht konsistent aufgelöst werden kann.