# Erfassungsarbeitsplatz
## UI-Spezifikation (Schritt 2.3)

Dieses Dokument konkretisiert ADR-022.

Es beschreibt die konkrete Benutzeroberfläche des Erfassungsarbeitsplatzes.

---

# Grundprinzip

Der Erfassungsarbeitsplatz ist auf die fortlaufende Erfassung genealogischer Heiratsurkunden ausgelegt.

Ziele:

- möglichst wenige Mausaktionen
- vollständige Tastaturbedienung
- kein Informationsverlust
- jederzeit Überblick über die gesamte Urkunde
- schnelle Navigation zwischen Urkunden

---

# Hauptfenster

Startgröße:

```text
1600 × 900
```

Mindestgröße:

```text
1400 × 800
```

---

# Hauptstruktur

Die Anwendung verwendet ein QTabWidget
mit zwei Hauptreitern:

```text
[ Familien / Urkunden ]

[ Erfassung ]
```

Jeder Reiter nutzt die gesamte verfügbare Fläche.

Eine Split-Darstellung wird nicht verwendet.

---

# Reiter "Familien / Urkunden"

Die Tabelle dient:

- Übersicht
- Navigation
- Auswahl bestehender Verbindungen
- Auswahl bestehender Urkunden

## Familien und Urkunden

Die Tabelle enthält sowohl Familienbeziehungen als auch bereits erfasste Urkunden.

Beides wird durch dieselbe fachliche Entität:

```text
MarriageRecord
```

repräsentiert.

Der Unterschied ergibt sich ausschließlich aus dem Erfassungszustand.

---

### Familie

Eine Familie repräsentiert einen aus der ursprünglichen GEDCOM-Datei übernommenen FAM-Datensatz.

Für diesen Datensatz wurde noch keine Urkunde erfasst.

Merkmale:

```text
Jahrgang = leer

Nummer = leer
```

Die Familie repräsentiert somit lediglich die bekannte Beziehung zwischen Ehemann und Ehefrau sowie die bereits im GEDCOM-Bestand vorhandenen FAM-Daten.

Durch Öffnen eines solchen Datensatzes erfolgt die Urkundenerfassung.

---

### Urkunde

Eine Urkunde repräsentiert einen FAM-Datensatz, der bereits mit urkundenspezifischen Informationen ergänzt wurde.

Merkmale:

```text
Jahrgang vorhanden

Nummer vorhanden
```

Zusätzlich können weitere Erfassungsdaten wie:

```text
Herkunft

Todesvermerke

Legitimierungen

Randvermerke

Anmerkungen
```

vorliegen.

Die Urkunde bleibt mit demselben MarriageRecord verknüpft.

Es entsteht kein neuer Datensatz.

---

### Erkennungsmerkmal in der Tabelle

Bereits in der Tabellenansicht kann unterschieden werden:

```text
Jahrgang leer
und
Nummer leer

→ Familie
```

```text
Jahrgang vorhanden
und
Nummer vorhanden

→ Urkunde
```

Der Wechsel von Familie zu Urkunde erfolgt ausschließlich durch die Erfassung der fehlenden Urkundendaten.

---

## Jahrgangsfilter

Die Familien-/Urkundentabelle besitzt einen Jahrgangsfilter.

Der Filter dient ausschließlich der Übersicht innerhalb eines Bearbeitungsjahrgangs.

---

### Funktionsweise

Der Filter wertet das Heiratsdatum aus.

Beispiel:

```text
Jahrgangsfilter = 1887
```

zeigt alle Datensätze, deren Heiratsdatum in das Jahr

```text
1887
```

fällt.

---

### Auswertung von GEDCOM-Datumsangaben

Die Ermittlung des Jahrgangs erfolgt auf Basis der gemäß ADR‑008 interpretierten GEDCOM-Datumsangaben.

Ein Datensatz wird einem Jahrgang zugeordnet, wenn aus der Datumsangabe eindeutig genau ein Kalenderjahr bestimmt werden kann.

Beispiele:

```text
1835
```

→ Jahrgang 1835

```text
JAN 1835
```

→ Jahrgang 1835

```text
01 JAN 1835
```

→ Jahrgang 1835

```text
BET 01 JAN 1835 AND 30 AUG 1835
```

→ Jahrgang 1835

```text
FROM 1835 TO 1835
```

→ Jahrgang 1835

---

Nicht eindeutig zuordenbare Datumsangaben werden durch den Jahrgangsfilter nicht berücksichtigt.

Beispiele:

```text
BET 1830 AND 1855
```

```text
FROM 1830 TO 1835
```

```text
BET 01 JAN 1834 AND 30 AUG 1835
```

Für diese Angaben kann kein eindeutiger Jahrgang bestimmt werden.

Sie erscheinen daher nicht innerhalb eines jahrgangsbezogenen Filters.


---

### Angezeigte Datensätze

Der Filter berücksichtigt sowohl:

```text
Familien
```

als auch:

```text
Urkunden
```

Innerhalb eines Jahrgangs werden deshalb gemeinsam angezeigt:

- bereits bekannte Familienbeziehungen
- noch nicht erfasste Familien
- bereits erfasste Urkunden

Dadurch entsteht eine vollständige Übersicht aller bekannten Heiraten dieses Jahrgangs.

---

### Zweck

Der Erfassungsarbeitsplatz ist jahrgangsorientiert aufgebaut.

Der Benutzer bearbeitet typischerweise einen Jahrgang vollständig.

Der Jahrgangsfilter ermöglicht dabei eine schnelle Orientierung über:

- bereits bekannte Heiraten
- bereits erfasste Urkunden
- noch offene Erfassungen

---

### Einschränkung

Der Jahrgangsfilter wirkt ausschließlich auf die Familien-/Urkundentabelle.

Die Personensuche innerhalb der Erfassungsmaske verwendet den Filter nicht.

Dort erfolgt die Suche ausschließlich anhand der Personenmerkmale.

Insbesondere wird nach bestehenden Ehebeziehungen gesucht, auch wenn:

```text
kein Heiratsdatum
```

oder

```text
kein Jahrgang
```

vorliegt.


---

## Spalten

```text
NoExport

Jahrgang

Nr

Ehemann

Ehefrau

Heiratsdatum

Workflowstatus

Exportstatus
```

---

## NoExport

```text
☑ = Export zulässig

☐ = vom Export ausgeschlossen
```

Die Checkbox steuert:

```text
MarriageRecord.no_export
```

---

## Personendarstellung

Zweizeilig:

```text
Müller, Horst
(12.12.1815) Hamburg
```

Verwendet werden:

```text
Nachname, Vorname

(Geburtsdatum) Geburtsort
```

---

## Sortierung

Alle Spalten sind sortierbar.

1. Klick

```text
aufsteigend
```

2. Klick

```text
absteigend
```

---

## Aktionsbereich

Unterhalb der Tabelle:

```text
[ Neu ]
```

---

### Wirkung

Der Button erzeugt einen neuen MarriageRecord
und öffnet den Reiter:

```text
Erfassung
```

im Modus:

```text
NEU
```

---

## Doppelklick

Ein Doppelklick öffnet den ausgewählten Datensatz.

Der zugehörige Modus:

```text
ERFASSEN

oder

BEARBEITEN
```

wird automatisch bestimmt.

Der interne Modus wird dem Benutzer nicht angezeigt.

---

# Reiter "Erfassung"

Die Erfassungsmaske besitzt drei Hauptbereiche.

```text
Kopfdaten

Ehepartner

Urkundenvermerke
```

---

# Bereich Kopfdaten

```text
+-- Kopfdaten --------------------------------------+

Nr

Heiratsdatum

Jahrgang

Heiratsort
```

---

## Feldtypen

Alle Felder sind einzeilig.

Jahrgang und Heiratsort werden vorbelegt.

Sie bleiben editierbar.

---

# Bereich Ehepartner

```text
+-- Ehepartner -------------------------------------+
```

Die Darstellung erfolgt zweispaltig.

---

## Linke Spalte

```text
Ehemann
```

---

### Personenidentifikation

```text
Nachname
```

ist ein Such- und Auswahlfeld.

Technisch:

```text
Editable ComboBox
```

mit intelligenter Suche.

---

### Suchlogik

Mehrere Suchbegriffe werden UND-verknüpft.

Beispiel:

```text
Mü ho 78
```

findet:

```text
Horst Müller

Geburtsjahr 1878
```

---

### Durchsuchte Felder

```text
Nachname

Vorname

Geburtsdatum

Geburtsort
```

---

### Trefferliste

Darstellung:

```text
Nachname

Vorname

Geburtsdatum

Geburtsort
```

Beispiel:

```text
Müller   Horst    06.05.1878   Hamburg
```

---

### Neuanlage Person

Sonderzeichen:

```text
#
```

öffnet:

```text
Neue Person
```

als Popup-Fenster.

---

### Personenfelder

```text
Nachname

Vorname

Geburtsdatum

Geburtsort
```

werden nach Auswahl automatisch übernommen.

---

### Herkunft / Eltern

Mehrzeilig.

Standard:

```text
2 Zeilen sichtbar
```

---

### Todesvermerk

Mehrzeilig.

Standard:

```text
2 Zeilen sichtbar
```

---

## Rechte Spalte

Analog zur linken Spalte.

```text
Ehefrau
```

mit identischem Verhalten.

---

## Schutz bestehender Personen

Wird eine bereits zugeordnete Person verändert:

```text
Nachname

Vorname

Geburtsdatum

Geburtsort
```

erfolgt die Änderung niemals direkt.

Stattdessen wird automatisch ein Popup geöffnet.

---

### Änderungsdialog

Bearbeitung der Person.

Anschließend Sicherheitsabfrage:

```text
Sie ändern die Stammdaten
einer vorhandenen Person.

Die Änderung wirkt sich auf alle
Verwendungen dieser Person aus.

Änderung übernehmen?
```

---

# Bereich Urkundenvermerke

```text
+-- Urkundenvermerke -------------------------------+
```

---

## Legitimierungen

Mehrzeilig.

```text
2 Zeilen sichtbar
```

---

## Randvermerke

Mehrzeilig.

```text
2 Zeilen sichtbar
```

---

## Anmerkungen

Mehrzeilig.

```text
2 Zeilen sichtbar
```

Volle Breite.

---

# Mehrzeilige Felder

Betroffene Felder:

```text
Herkunft / Eltern Mann

Herkunft / Eltern Frau

Todesvermerk Mann

Todesvermerk Frau

Legitimierungen

Randvermerke

Anmerkungen
```

---

## Standarddarstellung

```text
2 Zeilen sichtbar
```

---

## Fokusdarstellung

Beim Eintritt des Fokus:

```text
automatische Vergrößerung
```

beispielsweise:

```text
2 Zeilen → 8 Zeilen
```

---

## Fokusverlust

Beim Verlassen:

```text
zurück auf 2 Zeilen
```

---

## Manuelle Vergrößerung

Der Benutzer kann Felder zusätzlich mit der Maus vergrößern.

---

# Detailansicht

Die Anwendung stellt eine vollständige Lesedarstellung einer Urkunde bereit.

---

## Zweck

- Kontrolle
- Korrekturlesen
- Übersicht

---

## Inhalt

Die Detailansicht zeigt:

```text
Kopfdaten

Ehemann

Ehefrau

Urkundenvermerke
```

als vollständige Lesedarstellung.

---

## Verwendung

Die gleiche Detailansicht wird verwendet aus:

```text
Erfassungsmaske

Familien-/Urkundenliste

späteren Exportfunktionen
```

---

## Hinweis

Das konkrete Layout der Detailansicht wird in einem separaten Schritt definiert.

---

# Aktionsbereich

Unterhalb der Erfassungsmaske:

```text
[ Abbrechen ]

[ Rückgängig ]

[ Speichern ]
```

---

## Abbrechen

Bearbeitung vollständig verlassen.

Anschließend:

```text
zum Reiter
Familien / Urkunden
```

wechseln.

---

## Rückgängig

Bearbeitungszustand zurücksetzen.

In der Erfassungsmaske verbleiben.

---

## Speichern

Urkunde speichern.

Anschließend:

```text
zum Reiter
Familien / Urkunden
```

wechseln.

## Gesamtlayout der Erfassungsmaske

```
┌────────────────────────────────────────────────────────────────────────────┐
│ Reiter: [ Familien / Urkunden ] [ Erfassung ]                              │
└────────────────────────────────────────────────────────────────────────────┘


+-- Kopfdaten ---------------------------------------------------------------+

  Registriernummer*     Heiratsdatum*       Jahrgang*       Heiratsort*

  [____________]        [____________]      [______]        [______________]


+-- Ehepartner --------------------------------------------------------------+

┌─────────────────────────────────┬─────────────────────────────────────────┐
│ Ehemann                         │ Ehefrau                                 │
├─────────────────────────────────┼─────────────────────────────────────────┤
│ Nachname* (Eingabe # für neu)   │ Nachname* (Eingabe # für neu)           │
│ [ Such-/Auswahlfeld ]           │ [ Such-/Auswahlfeld ]                   │
│                                 │                                         │
│ Vorname*                        │ Vorname*                                │
│ [____________________]          │ [____________________]                  │
│                                 │                                         │
│ Geburtsdatum                    │ Geburtsdatum                            │
│ [__.__.____]                    │ [__.__.____]                            │
│                                 │                                         │
│ Geburtsort                      │ Geburtsort                              │
│ [_________________________]     │ [_________________________]             │
│                                 │                                         │
│ Herkunft / Eltern               │ Herkunft / Eltern                       │
│ [_________________________]     │ [_________________________]             │
│ [_________________________]     │ [_________________________]             │
│                                 │                                         │
│ Todesvermerk                    │ Todesvermerk                            │
│ [_________________________]     │ [_________________________]             │
│ [_________________________]     │ [_________________________]             │
└─────────────────────────────────┴─────────────────────────────────────────┘


+-- Urkundenvermerke --------------------------------------------------------+

┌─────────────────────────────────┬─────────────────────────────────────────┐
│ Legitimierungen                 │ Randvermerke                            │
├─────────────────────────────────┼─────────────────────────────────────────┤
│ [_________________________]     │ [_________________________]             │
│ [_________________________]     │ [_________________________]             │
└─────────────────────────────────┴─────────────────────────────────────────┘


Anmerkungen

┌───────────────────────────────────────────────────────────────────────────┐
│ [_______________________________________________________________]         │
│ [_______________________________________________________________]         │
└───────────────────────────────────────────────────────────────────────────┘
* sind Pflichtfelder                   
Eingabe # im Nachnamenfeld erzeugt einen neuen Personendatensatz.

+--------------------------------------------------------------------------+

[Abbrechen]                    [Rückgängig]                    [Speichern]

+--------------------------------------------------------------------------+
```

---

# Behandlung neu angelegter Personen

Wurden während einer Sitzung neue Personen angelegt:

```text
#
→ Neue Person
```

dann gelten diese als Teil der laufenden Bearbeitung.

---

## Abbrechen

Neu angelegte Personen werden gelöscht.

---

## Rückgängig

Neu angelegte Personen werden gelöscht.

---

## Speichern

Neu angelegte Personen werden dauerhaft übernommen.

---

# Mehrzeilige Felder im Datenmodell

Folgende Felder speichern Zeilenumbrüche unverändert:

```text
note_origin_husband

note_origin_wife

note_death_husband

note_death_wife

note_legitimation

note_marginal

note_comments
```

---

# Exportregel

Beim Export werden Zeilenumbrüche in GEDCOM-Strukturen umgesetzt.

Beispiel:

Eingabe:

```text
Zeile 1
Zeile 2
Zeile 3
```

Export:

```text
1 NOTE Zeile 1
2 CONT Zeile 2
2 CONT Zeile 3
```

Die interne Speicherung bleibt unverändert.
